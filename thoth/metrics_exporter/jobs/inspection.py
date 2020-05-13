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
from prometheus_api_client import PrometheusConnect

from thoth.storages import InspectionResultsStore
from thoth.storages.graph.enums import SoftwareStackTypeEnum

from .base import register_metric_job
from .base import MetricsBase
from .argo_workflows import ArgoWorkflowsMetrics
from .ceph import get_ceph_results_per_type

_LOGGER = logging.getLogger(__name__)


class InspectionMetrics(MetricsBase):
    """Class to evaluate Metrics for Amun Inspections."""

    _URL = os.environ["PROMETHEUS_HOST_URL"]
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _INSTANCE = os.environ["WORKFLOW_METRICS_AMUN_INSPECTION_PROMETHEUS_INSTANCE"]
    _NAMESPACE = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]

    _PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)

    _INSPECTION_CHECK_TIME = datetime.utcnow()

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
    def get_workflow_status(cls) -> None:
        """Get the workflow status for each workflow."""
        ArgoWorkflowsMetrics().get_thoth_workflows_status_per_namespace_per_label(
            label_selector="component=amun-inspection-job", namespace=cls._NAMESPACE
        )

    @classmethod
    @register_metric_job
    def get_inspection_quality(cls) -> None:
        """Get the quality for inspection workflows."""
        ArgoWorkflowsMetrics().get_workflow_quality(
            service_name="inspection",
            prometheus=cls._PROM,
            instance=cls._INSTANCE,
            namespace=cls._NAMESPACE,
            metric_type=metrics.workflow_inspection_quality,
        )

    @classmethod
    @register_metric_job
    def get_ceph_count(cls) -> None:
        """Get number of reports stored in the database for a type of store."""
        get_ceph_results_per_type(store=InspectionResultsStore())
