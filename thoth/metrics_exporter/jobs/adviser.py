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

"""Adviser metrics."""

import logging

import thoth.metrics_exporter.metrics as metrics

from thoth.storages.graph.enums import SoftwareStackTypeEnum
from thoth.common.enums import ThothAdviserIntegrationEnum

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class AdviserMetrics(MetricsBase):
    """Class to evaluate Metrics for Adviser."""

    @classmethod
    @register_metric_job
    def get_advised_python_software_stack_count(cls) -> None:
        """Get the total number of Advised Python Software Stacks in Thoth Knowledge Graph."""
        thoth_graphdb_total_advised_software_stacks = cls.graph().get_python_software_stack_count_all(
            software_stack_type=SoftwareStackTypeEnum.ADVISED.value
        )
        metrics.graphdb_advised_software_stacks_records.set(thoth_graphdb_total_advised_software_stacks)
        _LOGGER.debug("graphdb_advised_software_stacks_records=%r", thoth_graphdb_total_advised_software_stacks)

    @classmethod
    @register_metric_job
    def get_adviser_count_per_source_type(cls) -> None:
        """Get the total number of Adviser Runs per Thoth Integration provided."""
        adviser_count_per_source_type = cls.graph().get_adviser_run_count_per_source_type()
        for thoth_integration in ThothAdviserIntegrationEnum._member_names_:

            if thoth_integration in adviser_count_per_source_type:

                counts = adviser_count_per_source_type[thoth_integration]
                metrics.graphdb_adviser_count_per_source_type.labels(thoth_integration).set(counts)
                _LOGGER.debug("graphdb_adviser_count_per_source_type(%r)=%r", thoth_integration, counts)
            else:

                metrics.graphdb_adviser_count_per_source_type.labels(thoth_integration).set(0)
                _LOGGER.debug("graphdb_adviser_count_per_source_type(%r)=%r", thoth_integration, 0)

    @classmethod
    @register_metric_job
    def get_uniquer_usage_count_per_source_type(cls) -> None:
        """Get unique number of users per Thoth Integration provided."""
        users_count_per_source_type = cls.graph().get_origin_count_per_source_type(distinct=True)
        for thoth_integration in ThothAdviserIntegrationEnum._member_names_:

            if thoth_integration in users_count_per_source_type:

                counts = users_count_per_source_type[thoth_integration]
                metrics.graphdb_users_count_per_source_type.labels(thoth_integration).set(counts)
                _LOGGER.debug("graphdb_users_count_per_source_type(%r)=%r", thoth_integration, counts)
            else:

                metrics.graphdb_users_count_per_source_type.labels(thoth_integration).set(0)
                _LOGGER.debug("graphdb_users_count_per_source_type(%r)=%r", thoth_integration, 0)
