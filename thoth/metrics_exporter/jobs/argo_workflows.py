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

"""Metrics related to Argo workflows resources and objects."""

import logging
from typing import Dict, List, Any
import os

from thoth.common import OpenShift, WorkflowManager
from datetime import datetime
from prometheus_api_client import PrometheusConnect
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase
from .utils import get_namespace_object_labels_map

_LOGGER = logging.getLogger(__name__)


class ArgoWorkflowsMetrics:
    """Class to evaluate Metrics for Argo Workflows."""

    _OPENSHIFT = OpenShift()
    _WORKFLOW_MANAGER = WorkflowManager(openshift=_OPENSHIFT)

    _WORKFLOW_STATUS_METRIC_NAME = "argo_workflow_status_phase"
    _WORKFLOW_STATUSES = ["Failed", "Error", "Running", "Skipped", "Pending"]

    def get_workflow_quality(
        cls, service_name: str, prometheus: PrometheusConnect, instance: str, namespace: str, metric_type: metrics
    ) -> None:
        """Get the status for workflows for a certain service."""
        workflow_status_metric_name = cls._WORKFLOW_STATUS_METRIC_NAME

        workflows_count = {}
        tot_workflows = 0
        for workflow_status in cls._WORKFLOW_STATUSES:
            workflow_status_metrics = prometheus.get_current_metric_value(
                metric_name=workflow_status_metric_name,
                label_config={"instance": instance, "namespace": namespace, "phase": workflow_status},
            )
            service_workflows = [
                w
                for w in workflow_status_metrics
                if (int(w["value"][1]) == 1) and (service_name in w["metric"]["name"])
            ]
            workflows_count[workflow_status] = len(service_workflows)
            tot_workflows += len(service_workflows)

        for w_status, counts in workflows_count.items():
            metric_type.labels(service_name, w_status).set(counts)
            _LOGGER.debug(
                "Workflow metrics status/counts for service_name=%r, status=%r, counts=%r",
                service_name,
                w_status,
                counts,
            )
        if tot_workflows:
            metric_type.labels(service_name, "total_workflows").set(counts)
            _LOGGER.debug(
                "Workflow metrics status/counts for service_name=%r, status=%r, counts=%r",
                service_name,
                "total_workflows",
                tot_workflows,
            )

    def get_thoth_workflows_status_per_namespace_per_label(cls, label_selector: str, namespace: str) -> None:
        """Get the workflows and tasks per label per namespace with corresponding status."""
        _LOGGER.info("Evaluating workflows(label_selector=%r) metrics for namespace: %r", label_selector, namespace)
        workflows_and_tasks_status = cls._WORKFLOW_MANAGER.get_workflows_and_tasks_status(
            label_selector=label_selector, namespace=namespace
        )
        cls._analyze_workflows(label_selector=label_selector, namespace=namespace, workflows=workflows_and_tasks_status)

    def _analyze_workflows(cls, label_selector: str, namespace: str, workflows: Dict[str, Any]):
        """Process workflows tasks."""
        for workflows_info in workflows.values():
            _LOGGER.info("workflow_type=%r", workflows_info["component"])

            for workflow_status, workflow_status_count in workflows_info["status"].items():
                metrics.workflows_status.labels(label_selector, workflow_status, namespace).set(workflow_status_count)
                _LOGGER.info(
                    "workflow_status=(%r, %r, %r)=%r", label_selector, workflow_status, namespace, workflow_status_count
                )

            cls._analyze_workflows_tasks(
                label_selector=label_selector,
                namespace=namespace,
                component=workflows_info["component"],
                tasks=workflows_info["tasks"],
            )

    @staticmethod
    def _analyze_workflows_tasks(label_selector: str, namespace: str, component: str, tasks: Dict[str, Any]):
        """Process workflows tasks."""
        for task, task_info in tasks.items():
            _LOGGER.info("workflow_type=%r, task=%r", component, task)

            for task_status, task_status_count in task_info.items():
                metrics.workflow_task_status.labels(label_selector, task, task_status, namespace).set(task_status_count)
                _LOGGER.info(
                    "workflow_task_status=(%r, %r, %r, %r)=%r",
                    label_selector,
                    task,
                    task_status,
                    namespace,
                    task_status_count,
                )
