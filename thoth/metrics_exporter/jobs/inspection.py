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

_LOGGER = logging.getLogger(__name__)


class InspectionMetrics(MetricsBase):
    """Class to evaluate Metrics for Amun Inspections."""

    _URL = "https://prometheus-dh-prod-monitoring.cloud.datahub.psi.redhat.com"
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _NAMESPACE = os.environ["THOTH_FRONTEND_NAMESPACE"]

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
        workflow_completion_time_metric_name = "argo_workflow_completion_time"
        workflow_completion_time = cls._PROM.get_current_metric_value(
            metric_name=workflow_completion_time_metric_name,
            label_config={
                'instance': f"workflow-controller-metrics-{cls._NAMESPACE}.cloud.paas.psi.redhat.com:80",
                "namespace": cls._NAMESPACE}
                )

        if workflow_completion_time:
            inspection_workflows = {}
            for metric in workflow_completion_time:
                if "inspection" in metric['metric']['name']:
                    completion_time = datetime.fromtimestamp(
                            int(metric['value'][1])
                            )
                    new_time = datetime.now()

                    if cls._INSPECTION_CHECK_TIME < completion_time < new_time: 
                        inspection_workflows[metric['metric']['name']] = completion_time

            cls._INSPECTION_CHECK_TIME = new_time

            if inspection_workflows:
                for workflow_name, completion_time in inspection_workflows.items():
                    workflow_start_time_metric_name = "argo_workflow_start_time"
                    workflow_start_time = cls._PROM.get_current_metric_value(
                        metric_name=workflow_start_time_metric_name,
                        label_config={
                            'instance': f"workflow-controller-metrics-{cls._NAMESPACE}.cloud.paas.psi.redhat.com:80",
                            "namespace": cls._NAMESPACE,
                            "name": workflow_name}
                            )

                    start_time = datetime.fromtimestamp(
                        int(workflow_start_time[0]['value'][1])
                        )
                    metrics.workflow_inspection_latency.observe(
                        (completion_time - start_time).total_seconds()
                        )

            else:
                _LOGGER.debug("No inspection workflow identified")

        else:
            _LOGGER.debug("No metrics identified for %r", workflow_completion_time_metric_name)
