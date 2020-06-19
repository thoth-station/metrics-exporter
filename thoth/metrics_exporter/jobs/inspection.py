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

"""Inspection metrics."""

import logging
import os
from datetime import datetime

import thoth.metrics_exporter.metrics as metrics

from thoth.storages import InspectionResultsStore
from thoth.storages.graph.enums import SoftwareStackTypeEnum

from .base import register_metric_job
from .base import MetricsBase
from ..configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class InspectionMetrics(MetricsBase):
    """Class to evaluate Metrics for Amun Inspections."""

    @classmethod
    @register_metric_job
    def get_inspection_python_software_stack_count(cls) -> None:
        """Get the total number of Inspection Python Software Stacks in Thoth Knowledge Graph."""
        thoth_graphdb_total_inspection_software_stacks = cls.graph().get_python_software_stack_count_all(
            software_stack_type=SoftwareStackTypeEnum.INSPECTION.value
        )
        metrics.graphdb_inspection_software_stacks_records.set(thoth_graphdb_total_inspection_software_stacks)
        _LOGGER.debug("graphdb_inspection_software_stacks_records=%r", thoth_graphdb_total_inspection_software_stacks)
