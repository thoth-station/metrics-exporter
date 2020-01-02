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
import os
from datetime import datetime

import thoth.metrics_exporter.metrics as metrics
from prometheus_api_client import PrometheusConnect

from thoth.storages import InspectionResultsStore
from thoth.storages.graph.enums import SoftwareStackTypeEnum

from .base import register_metric_job
from .base import MetricsBase
from .common import get_workflow_duration

_LOGGER = logging.getLogger(__name__)


class InspectionMetrics(MetricsBase):
    """Class to evaluate Metrics for Amun Inspections."""

    _URL = "https://prometheus-dh-prod-monitoring.cloud.datahub.psi.redhat.com"
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _NAMESPACE = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]

    _PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)

    _INSPECTION_CHECK_TIME = datetime.now()

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
        thoth_graphdb_total_inspection_software_stacks = cls.graph().get_python_software_stack_count_all(
            software_stack_type=SoftwareStackTypeEnum.INSPECTION.value
        )
        metrics.graphdb_inspection_software_stacks_records.set(thoth_graphdb_total_inspection_software_stacks)
        _LOGGER.debug("graphdb_inspection_software_stacks_records=%r", thoth_graphdb_total_inspection_software_stacks)

    @classmethod
    @register_metric_job
    def get_inspection_evaluation_time(cls) -> None:
        """Get the time spent for each inspection worflow."""
        cls._INSPECTION_CHECK_TIME = get_workflow_duration(
            service_name="inspection",
            prometheus=cls._PROM,
            namespace=cls._NAMESPACE,
            check_time=cls._INSPECTION_CHECK_TIME,
            metric_type=metrics.workflow_inspection_latency)
