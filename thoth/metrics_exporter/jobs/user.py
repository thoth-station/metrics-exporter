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

"""Metrics related to users of Thoth."""

import logging

from thoth.storages.graph.enums import SoftwareStackTypeEnum
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class UserInformationMetrics(MetricsBase):
    """Class to discover information from Users."""

    @classmethod
    @register_metric_job
    def get_user_python_software_stack_count(cls) -> None:
        """Get the total number of User Python Software Stacks in Thoth Knowledge Graph."""
        thoth_graphdb_total_software_stacks = cls.graph().get_python_software_stack_count_all(
            software_stack_type=SoftwareStackTypeEnum.USER.value
        )
        metrics.graphdb_user_software_stacks_records.set(thoth_graphdb_total_software_stacks)
        _LOGGER.debug("graphdb_user_software_stacks_records=%r", thoth_graphdb_total_software_stacks)

    @classmethod
    @register_metric_job
    def get_user_unique_run_software_environment_count(cls) -> None:
        """Get the total number of users unique software environment for run in Thoth Knowledge Graph."""
        user_run_software_environment = cls.graph().get_run_software_environment_all(is_external=True)
        if user_run_software_environment:
            thoth_graphdb_total_user_run_software_environment = len(
                set(user_run_software_environment)
            )
        else:
            thoth_graphdb_total_user_run_software_environment = 0

        metrics.graphdb_total_user_run_software_environment.set(thoth_graphdb_total_user_run_software_environment)
        _LOGGER.debug(
            "graphdb_total_unique_user_run_software_environment=%r", thoth_graphdb_total_user_run_software_environment
        )
