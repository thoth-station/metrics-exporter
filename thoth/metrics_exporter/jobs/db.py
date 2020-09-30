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

from typing import List, Any, Optional

from datetime import datetime, timedelta

from thoth.storages.exceptions import DatabaseNotInitialized
import thoth.metrics_exporter.metrics as metrics
from prometheus_api_client import PrometheusConnect
from thoth.python import Source

from .base import register_metric_job
from .base import MetricsBase
from ..configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class DBMetrics(MetricsBase):
    """Class to evaluate Metrics for Thoth Database."""

    _METRICS_EXPORTER_INSTANCE = os.environ["METRICS_EXPORTER_INFRA_PROMETHEUS_INSTANCE"]
    _MANAGEMENT_API_INSTANCE = os.environ["MANAGEMENT_API_PROMETHEUS_INSTANCE"]

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
    def get_is_management_api_storages_up2date(cls) -> None:
        """Check if management-API deployed contains latest thoth-storages library."""
        latest_version = _retrieve_latest_version()

        if not latest_version:
            return

        metric_name = "management_api_info"
        query_labels = f'{{instance="{cls._MANAGEMENT_API_INSTANCE}"}}'
        query = f"management_api_info{query_labels}"
        metrics = Configuration.PROM.custom_query(query=query)

        if not metrics:
            _LOGGER.warning("No metrics identified from Prometheus for query: %r", query)
            return

        management_api_storage_version = _parse_metric(metrics=metrics)

        if management_api_storage_version != latest_version:
            _LOGGER.info(
                "latest thoth-storages version %r is not in sync with Management-API: %r ",
                latest_version,
                management_api_storage_version,
            )
            metrics.management_api_is_storages_latest.set(0)
        else:
            metrics.management_api_is_storages_latest.set(1)


def _retrieve_latest_version() -> Optional[str]:
    """Retrieve storages latest version."""
    python_package_name = "thoth-storages"
    python_package_index = "https://pypi.org/simple"
    source = Source(python_package_index)

    try:
        latest_version = source.get_latest_package_version(python_package_name)
    except Exception as exc:
        _LOGGER.warning("Could not retrieve version for package %r from %r", python_package_name, python_package_index)

    return latest_version


def _parse_metric(metrics: List[Any]) -> str:
    """Parse metric to obtain current version."""
    for metric in metrics:
        if metric["value"][1] == "1":
            complete_versions = metric["metric"]["version"]
            libraries_versions = complete_versions.split("+")[1]
            management_api_storage_version = (
                libraries_versions.split("common")[0].rsplit(".", 1)[0].split("storage.", 1)[1]
            )
            break

    return management_api_storage_version
