#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019 Christoph Görn, Francesco Murdaca, Fridolin Pokorny
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

from thoth.storages import GraphDatabase
from thoth.storages.exceptions import DatabaseNotInitialized
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class DBMetrics(MetricsBase):
    """Class to evaluate Metrics for Thoth Database."""

    @staticmethod
    @register_metric_job
    def get_graphdb_connection_error_status() -> None:
        """Raise a flag if there is an error connecting to database."""
        graph_db = GraphDatabase()
        try:
            graph_db.connect()
        except Exception as excptn:
            metrics.graphdb_connection_error_status.set(0)
            _LOGGER.exception(excptn)
        else:
            metrics.graphdb_connection_error_status.set(1)

    @staticmethod
    @register_metric_job
    def get_tot_records_count() -> None:
        """Get the total number of Records in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        main_models_record_count = sum(graph_db.get_number_main_tables_records().values())
        relation_models_record_count = sum(graph_db.get_number_relation_tables_records().values())
        performance_models_record_count = sum(graph_db.get_number_performance_tables_records().values())

        total_records_count = main_models_record_count + relation_models_record_count + performance_models_record_count
        metrics.graphdb_total_records.set(total_records_count)

        _LOGGER.debug("thoth_graphdb_total_records=%r", total_records_count)

    @staticmethod
    @register_metric_job
    def get_tot_main_records_count() -> None:
        """Get the total number of Records for Main Tables in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        main_models_records = graph_db.get_number_main_tables_records()

        for main_table, main_table_records_count in main_models_records.items():
            metrics.graphdb_total_main_records.labels(main_table).set(main_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_main_records=%r", main_models_records)

    @staticmethod
    @register_metric_job
    def get_tot_relation_records_count() -> None:
        """Get the total number of Records for Relation Tables in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        relation_models_records = graph_db.get_number_relation_tables_records()

        for relation_table, relation_table_records_count in relation_models_records.items():
            metrics.graphdb_total_relation_records.labels(relation_table).set(relation_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_relation_records=%r", relation_models_records)

    @staticmethod
    @register_metric_job
    def get_is_schema_up2date() -> None:
        """Check if the schema running on metrics-exporter is same as the schema present in the database."""
        graph_db = GraphDatabase()
        graph_db.connect()
        try:
            metrics.graphdb_is_schema_up2date.set(int(graph_db.is_schema_up2date()))
        except DatabaseNotInitialized as exc:
            _LOGGER.warning("Database schema is not initialized yet: %s", str(exc))
            metrics.graphdb_is_schema_up2date.set(0)
