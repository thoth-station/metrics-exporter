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
from typing import Optional

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase
from ..configuration import Configuration
from thoth.common import format_datetime

_LOGGER = logging.getLogger(__name__)


class DBMetrics(MetricsBase):
    """Class to evaluate Metrics for Thoth Database."""

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
    def get_graphdb_alembic_version_rows(cls) -> None:
        """Raise a flag if there is more than one row in alembic version table."""
        alembic_version_rows = cls.graph().get_alembic_version_count_all()

        metrics.graphdb_alembic_version_rows.set(alembic_version_rows)

        if alembic_version_rows > 1:
            # Alarm required, database is corrupted
            metrics.graphdb_alembic_table_check.set(1)
        else:
            metrics.graphdb_alembic_table_check.set(0)

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
            metrics.graph_db_component_revision_check.labels("no-component", Configuration.DEPLOYMENT_NAME).set(2)

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
                metrics.graph_db_component_revision_check.labels(component_name, Configuration.DEPLOYMENT_NAME).set(2)
                continue

            database_script_revision = metric["metric"]["revision"]

            if database_table_revision != database_script_revision:
                # alarm is required: component is probably using old thoth-storages
                metrics.graph_db_component_revision_check.labels(component_name, Configuration.DEPLOYMENT_NAME).set(1)
            else:
                # component is using same revision head as in the database
                metrics.graph_db_component_revision_check.labels(component_name, Configuration.DEPLOYMENT_NAME).set(0)

    @classmethod
    @register_metric_job
    def set_last_solver_datetime(
        cls, os_name: Optional[str] = None, os_version: Optional[str] = None, python_version: Optional[str] = None
    ) -> None:
        """Get datetime of the last solver synced in the database."""
        last_solver_datetime = cls.graph().get_last_solver_datetime(
            os_name=os_name, os_version=os_version, python_version=python_version
        )
        metrics.graphdb_last_solver_datetime.labels(format_datetime(last_solver_datetime)).inc()
