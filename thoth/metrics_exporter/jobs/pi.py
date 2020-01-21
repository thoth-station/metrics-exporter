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

"""Performance indicator metrics."""

import logging

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class PIMetrics(MetricsBase):
    """Class to discover Content for Performance Indicators inside Thoth database."""

    @classmethod
    @register_metric_job
    def get_observations_count_per_component(cls) -> None:
        """Get the total number of PI per component in Thoth Knowledge Graph."""
        PI_COMPONENTS = cls.graph().get_pi_component_all()
        thoth_number_of_pi_per_type = {}

        if PI_COMPONENTS:
            for component in PI_COMPONENTS:
                thoth_number_of_pi_per_type[component] = cls.graph().get_pi_count(component=component)

                for pi, pi_count in thoth_number_of_pi_per_type[component].items():
                    metrics.graphdb_total_number_of_pi_per_component.labels(component, pi).set(pi_count)
            _LOGGER.debug("graphdb_total_number_of_pi_per_component=%r", thoth_number_of_pi_per_type)
        else:
            thoth_number_of_pi_per_type["No component"] = 0
            metrics.graphdb_total_number_of_pi_per_component.labels("No component", "No pi").set(0)
            _LOGGER.debug("graphdb_total_number_of_pi_per_component=%r", thoth_number_of_pi_per_type)

    @classmethod
    @register_metric_job
    def get_tot_performance_records_count(cls) -> None:
        """Get the total number of Records for Performance tables in Thoth Knowledge Graph."""
        performance_models_records = cls.graph().get_performance_table_count()

        for performance_table, performance_table_records_count in performance_models_records.items():
            metrics.graphdb_total_performance_records.labels(performance_table).set(performance_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_performance_records=%r", performance_models_records)
