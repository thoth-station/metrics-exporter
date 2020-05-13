#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019, 2020 Christoph Görn, Francesco Murdaca, Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Knowledge graph metrics."""

import logging
import os

from datetime import datetime, timedelta

from thoth.storages.exceptions import DatabaseNotInitialized
import thoth.metrics_exporter.metrics as metrics
from prometheus_api_client import PrometheusConnect

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class DBMetrics(MetricsBase):
    """Class to evaluate Metrics for Thoth Database."""

    _NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]

    _URL = os.environ["PROMETHEUS_HOST_URL"]
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)
    _METRICS_EXPORTER_INSTANCE = os.environ["METRICS_EXPORTER_FRONTEND_PROMETHEUS_INSTANCE"]

    _SCRAPE_COUNT = 0
    _BLOAT_DATA_SCRAPE_INTERVAL_DAYS = 7

    @classmethod
    @register_metric_job
    def get_graphdb_connection_error_status(cls) -> None:
        """Raise a flag if there is an error connecting to database."""
        try:
            cls.graph()._engine.execute("SELECT 1")
        except Exception as excptn:
            metrics.graphdb_connection_error_status.set(0)
            _LOGGER.exception(excptn)
        else:
            metrics.graphdb_connection_error_status.set(1)

    @classmethod
    @register_metric_job
    def get_tot_main_records_count(cls) -> None:
        """Get the total number of Records for Main Tables in Thoth Knowledge Graph."""
        main_models_record_count = sum(cls.graph().get_main_table_count().values())
        metrics.graphdb_main_table_total_records.set(main_models_record_count)
        _LOGGER.debug("thoth_graphdb_main_table_total_records=%r", main_models_record_count)

    @classmethod
    @register_metric_job
    def get_tot_relation_records_count(cls) -> None:
        """Get the total number of Records for Relation Tables in Thoth Knowledge Graph."""
        relation_models_record_count = sum(cls.graph().get_relation_table_count().values())
        metrics.graphdb_relation_table_total_records.set(relation_models_record_count)
        _LOGGER.debug("thoth_graphdb_relation_table_total_records=%r", relation_models_record_count)

    @classmethod
    @register_metric_job
    def get_tot_performance_records_count(cls) -> None:
        """Get the total number of Records for Performance Tables in Thoth Knowledge Graph."""
        performance_models_record_count = sum(cls.graph().get_performance_table_count().values())
        metrics.graphdb_performance_table_total_records.set(performance_models_record_count)
        _LOGGER.debug("thoth_graphdb_performance_table_total_records=%r", performance_models_record_count)

    @classmethod
    @register_metric_job
    def get_main_records_count_per_table(cls) -> None:
        """Get the total number of Records per Main Tables in Thoth Knowledge Graph."""
        main_models_records = cls.graph().get_main_table_count()

        for main_table, main_table_records_count in main_models_records.items():
            metrics.graphdb_total_main_records.labels(main_table).set(main_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_main_records=%r", main_models_records)

    @classmethod
    @register_metric_job
    def get_relation_records_count_per_table(cls) -> None:
        """Get the total number of Records per Relation Tables in Thoth Knowledge Graph."""
        relation_models_records = cls.graph().get_relation_table_count()

        for relation_table, relation_table_records_count in relation_models_records.items():
            metrics.graphdb_total_relation_records.labels(relation_table).set(relation_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_relation_records=%r", relation_models_records)

    @classmethod
    @register_metric_job
    def get_bloat_data(cls) -> None:
        """Get bloat data from database."""
        if cls._SCRAPE_COUNT != 0:
            metric_name = "thoth_graphdb_last_evaluation_bloat_data"
            metric = cls._PROM.get_current_metric_value(
                metric_name=metric_name, label_config={"instance": cls._METRICS_EXPORTER_INSTANCE}
            )

            last_prometheus_scrape = datetime.fromtimestamp(float(metric[0]["value"][0]))
            last_evaluation = datetime.fromtimestamp(float(metric[0]["value"][1]))

            if (
                not (last_prometheus_scrape - last_evaluation).total_seconds()
                > timedelta(days=cls._BLOAT_DATA_SCRAPE_INTERVAL_DAYS).total_seconds()
            ):
                return

        bloat_data = cls.graph().get_bloat_data()

        if bloat_data:
            for table_data in bloat_data:
                metrics.graphdb_pct_bloat_data_table.labels(table_data["tablename"]).set(table_data["pct_bloat"])
                _LOGGER.debug(
                    "thoth_graphdb_pct_bloat_data_table(%r)=%r", table_data["tablename"], table_data["pct_bloat"]
                )

                metrics.graphdb_mb_bloat_data_table.labels(table_data["tablename"]).set(table_data["mb_bloat"])
                _LOGGER.debug("thoth_graphdb_mb_bloat_data_table(%r)=%r", table_data["tablename"], 0)
        else:
            metrics.graphdb_pct_bloat_data_table.labels("No table pct").set(0)
            _LOGGER.debug("thoth_graphdb_pct_bloat_data_table is empty")

            metrics.graphdb_mb_bloat_data_table.labels("No table mb").set(0)
            _LOGGER.debug("thoth_graphdb_mb_bloat_data_table is empty")

        metrics.graphdb_last_evaluation_bloat_data.set(datetime.utcnow().timestamp())
        _LOGGER.debug("thoth_graphdb_last_evaluation_bloat_data=%r", datetime.utcnow().timestamp())

        cls._SCRAPE_COUNT += 1
        _LOGGER.info("Next bloat data evaluation in %r days", cls._BLOAT_DATA_SCRAPE_INTERVAL_DAYS)

    @classmethod
    @register_metric_job
    def get_is_schema_up2date(cls) -> None:
        """Check if the schema running on metrics-exporter is same as the schema present in the database."""
        try:
            metrics.graphdb_is_schema_up2date.set(int(cls.graph().is_schema_up2date()))
        except DatabaseNotInitialized as exc:
            _LOGGER.warning("Database schema is not initialized yet: %s", str(exc))
            metrics.graphdb_is_schema_up2date.set(0)
