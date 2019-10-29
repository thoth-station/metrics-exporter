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

"""Metrics related to users of Thoth."""

import logging

from thoth.storages import GraphDatabase
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class UserInformationMetrics(MetricsBase):
    """Class to discover information from Users."""

    @staticmethod
    @register_metric_job
    def get_user_python_software_stack_count() -> None:
        """Get the total number of User Python Software Stacks in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_software_stacks = graph_db.get_python_software_stack_count_all(software_stack_type="USER")
        metrics.graphdb_user_software_stacks_records.set(thoth_graphdb_total_software_stacks)
        _LOGGER.debug("graphdb_user_software_stacks_records=%r", thoth_graphdb_total_software_stacks)

    @staticmethod
    @register_metric_job
    def get_user_unique_run_software_environment_count() -> None:
        """Get the total number of users unique software environment for run in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_user_run_software_environment = len(
            set(graph_db.get_run_software_environment_all(is_external=True))
        )

        metrics.graphdb_total_user_run_software_environment.set(thoth_graphdb_total_user_run_software_environment)
        _LOGGER.debug(
            "graphdb_total_unique_user_run_software_environment=%r", thoth_graphdb_total_user_run_software_environment
        )
