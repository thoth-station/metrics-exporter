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

"""Inspection metrics."""

import logging

from thoth.storages import InspectionResultsStore
from thoth.storages.graph.enums import SoftwareStackTypeEnum
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class InspectionMetrics(MetricsBase):
    """Class to evaluate Metrics for Amun Inspections."""

    @staticmethod
    @register_metric_job
    def get_inspection_results_per_identifier() -> None:
        """Get the total number of inspections in Ceph per identifier."""
        store = InspectionResultsStore()
        if not store.is_connected():
            store.connect()

        specific_list_ids = {"without_identifier": 0}
        for ids in store.get_document_listing():
            inspection_filter = "_".join(ids.split("-")[1:(len(ids.split("-")) - 1)])
            if inspection_filter:
                if inspection_filter not in specific_list_ids.keys():
                    specific_list_ids[inspection_filter] = 1
                else:
                    specific_list_ids[inspection_filter] += 1
            else:
                specific_list_ids["without_identifier"] += 1

        for identifier, identifier_list in specific_list_ids.items():
            metrics.inspection_results_ceph.labels(identifier).set(identifier_list)
            _LOGGER.debug(f"inspection_results_ceph for {identifier} ={identifier_list}")

    @classmethod
    @register_metric_job
    def get_inspection_python_software_stack_count(cls) -> None:
        """Get the total number of Inspection Python Software Stacks in Thoth Knowledge Graph."""
        thoth_graphdb_total_inspection_software_stacks = cls.GRAPH.get_python_software_stack_count_all(
            software_stack_type=SoftwareStackTypeEnum.INSPECTION.value
        )
        metrics.graphdb_inspection_software_stacks_records.set(thoth_graphdb_total_inspection_software_stacks)
        _LOGGER.debug("graphdb_inspection_software_stacks_records=%r", thoth_graphdb_total_inspection_software_stacks)
