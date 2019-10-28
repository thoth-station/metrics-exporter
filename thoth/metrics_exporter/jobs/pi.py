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

"""Performance indicator metrics."""

import logging

from thoth.storages import GraphDatabase
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class PIMetrics(MetricsBase):
    """Class to discover Content for Performance Indicators inside Thoth database."""

    _ML_FRAMEWORKS = ["tensorflow"]

    @classmethod
    @register_metric_job
    def get_observations_count_per_framework(cls) -> None:
        """Get the total number of PI per framework in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()
        thoth_number_of_pi_per_type = {}

        for framework in cls._ML_FRAMEWORKS:
            thoth_number_of_pi_per_type[framework] = graph_db.get_all_pi_per_framework_count(framework=framework)

            for pi, pi_count in thoth_number_of_pi_per_type[framework].items():
                metrics.graphdb_total_number_of_pi_per_framework.labels(framework, pi).set(pi_count)

        _LOGGER.debug("graphdb_total_number_of_pi_per_framework=%r", thoth_number_of_pi_per_type)

    @staticmethod
    @register_metric_job
    def get_tot_performance_records_count() -> None:
        """Get the total number of Records for Performance tables in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        performance_models_records = graph_db.get_number_performance_tables_records()

        for performance_table, performance_table_records_count in performance_models_records.items():
            metrics.graphdb_total_performance_records.labels(performance_table).set(performance_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_performance_records=%r", performance_models_records)
