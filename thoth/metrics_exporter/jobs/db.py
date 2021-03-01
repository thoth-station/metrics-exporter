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

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase
from ..configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class DBMetrics(MetricsBase):
    """Class to evaluate Metrics for Thoth Database."""

    _METRICS_EXPORTER_INSTANCE = os.environ["METRICS_EXPORTER_INFRA_PROMETHEUS_INSTANCE"]

    _SCRAPE_COUNT = 0
    _BLOAT_DATA_SCRAPE_INTERVAL_DAYS = 7

    @classmethod
    @register_metric_job
    def get_database_size(cls) -> None:
        """Get size of the database in bytes."""
        size = cls.graph().get_database_size()
        metrics.graphdb_size.set(size)

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
    def get_bloat_data(cls) -> None:
        """Get bloat data from database."""
        if cls._SCRAPE_COUNT != 0:
            metric_name = "thoth_graphdb_last_evaluation_bloat_data"
            metric = Configuration.PROM.get_current_metric_value(
                metric_name=metric_name, label_config={"instance": cls._METRICS_EXPORTER_INSTANCE}
            )

            if not metric:
                _LOGGER.warning("No metrics identified from Prometheus for %r", metric_name)
                return

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
    def set_is_corrupted_metric(cls):
        """Set metric for indicating whether database corruption has been **detected**."""
        if cls.graph().is_database_corrupted():
            metrics.graphdb_is_corrupted.set(1)
        else:
            metrics.graphdb_is_corrupted.set(0)

    @classmethod
    @register_metric_job
    def set_script_head_revision(cls):
        """Set metric for indicating database revision exposed by script."""
        metrics.database_schema_revision_script.labels(
            "metrics-exporter", cls.graph().get_script_alembic_version_head(), Configuration.DEPLOYMENT_NAME
        ).set(1)

    @classmethod
    @register_metric_job
    def set_table_head_revision(cls):
        """Set metric for indicating database revision exposed by alembic table."""
        table_revision_head = None
        try:
            table_revision_head = cls.graph().get_table_alembic_version_head()
        except Exception as e:
            _LOGGER.exception("Database revision table could not be retrieved: %r", e)

        if table_revision_head:
            metrics.database_schema_revision_table.labels(
                "metrics-exporter", table_revision_head, Configuration.DEPLOYMENT_NAME
            ).set(1)

    @classmethod
    @register_metric_job
    def check_is_schema_up2date(cls) -> None:
        """Check if the schema running on metrics-exporter is same as the one present in database."""
        is_schema_up2date = int(cls.graph().is_schema_up2date())

        if is_schema_up2date:
            metrics.graph_db_component_revision_check.labels("metrics-exporter", Configuration.DEPLOYMENT_NAME).set(0)
        else:
            metrics.graph_db_component_revision_check.labels("metrics-exporter", Configuration.DEPLOYMENT_NAME).set(1)

    @classmethod
    @register_metric_job
    def check_is_schema_up2date_for_components(cls) -> None:
        """Check if schema is up to date for all components."""
        try:
            database_table_revision = cls.graph().get_table_alembic_version_head()
        except Exception as e:
            _LOGGER.exception("Database revision table could not be retrieved: %r", e)
            return

        query = "thoth_database_schema_revision_script"
        metrics_retrieved = Configuration.PROM.custom_query(query=query)

        if not metrics_retrieved:
            _LOGGER.warning("No metrics identified from Prometheus for query: %r", query)
            metrics.graph_db_component_revision_check.labels("no-component").set(-1)

        for metric in metrics_retrieved:

            component_name = metric["metric"]["component"]

            if "env" not in metric["metric"]:
                continue

            deployment_environment = metric["metric"]["env"]

            if str(deployment_environment) != Configuration.DEPLOYMENT_NAME:
                _LOGGER.debug("Metric skipped because of deployment environment in metric: %r!", deployment_environment)
                continue

            is_revision_up = metric["value"][1]

            if int(is_revision_up) != 1:
                _LOGGER.warning("Metric retrieved for %r is not up!", component_name)
                metrics.graph_db_component_revision_check.labels(component_name).set(-1)
                continue

            database_script_revision = metric["metric"]["revision"]

            if database_table_revision != database_script_revision:
                # alarm is required: component is probably using old thoth-storages
                metrics.graph_db_component_revision_check.labels(component_name, Configuration.DEPLOYMENT_NAME).set(1)
            else:
                # component is using same revision head as in the database
                metrics.graph_db_component_revision_check.labels(component_name, Configuration.DEPLOYMENT_NAME).set(0)
