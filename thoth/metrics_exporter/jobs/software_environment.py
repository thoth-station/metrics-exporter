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

"""Metrics related to software environments.."""

import logging

from thoth.storages import GraphDatabase
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class SoftwareEnvironmentMetrics(MetricsBase):
    """Class to discover Content for Software Environment (Build and Run) inside Thoth database."""

    @staticmethod
    @register_metric_job
    def get_unique_run_software_environment_count() -> None:
        """Get the total number of unique software environment for run in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_run_software_environment = len(set(graph_db.run_software_environment_listing()))
        metrics.graphdb_total_run_software_environment.set(thoth_graphdb_total_run_software_environment)
        _LOGGER.debug("graphdb_total_unique_run_software_environment=%r", thoth_graphdb_total_run_software_environment)

    @staticmethod
    @register_metric_job
    def get_unique_build_software_environment_count() -> None:
        """Get the total number of unique software environment for build in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_build_software_environment = len(set(graph_db.build_software_environment_listing()))

        metrics.graphdb_total_build_software_environment.set(thoth_graphdb_total_build_software_environment)
        _LOGGER.debug(
            "graphdb_total_unique_build_software_environment=%r", thoth_graphdb_total_build_software_environment
        )
