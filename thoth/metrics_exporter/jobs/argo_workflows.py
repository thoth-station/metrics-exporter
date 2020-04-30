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
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase
from .utils import get_namespace_object_labels_map

_LOGGER = logging.getLogger(__name__)


class ArgoWorkflowsMetrics(MetricsBase):
    """Class to evaluate Metrics for Argo Workflows."""

    _OPENSHIFT = OpenShift()
    _WORKFLOW_MANAGER = WorkflowManager(openshift=_OPENSHIFT)

    _MIDDLETIER_WORKFLOWS_LABELS = ["component=solver"]

    _AMUN_INSPECTION_WORKFLOWS_LABELS = ["component=amun-inspection-job"]

    _BACKEND_WORKFLOWS_LABELS = ["component=adviser", "component=qeb-hwt"]

    _NAMESPACES_VARIABLES_WORKFLOWS_MAP = {
        "THOTH_MIDDLETIER_NAMESPACE": _MIDDLETIER_WORKFLOWS_LABELS,
        "THOTH_BACKEND_NAMESPACE": _BACKEND_WORKFLOWS_LABELS,
        "THOTH_AMUN_INSPECTION_NAMESPACE": _AMUN_INSPECTION_WORKFLOWS_LABELS,
    }

    @classmethod
    @register_metric_job
    def get_thoth_workflows_status_per_namespace_per_label(cls) -> None:
        """Get the workflows and tasks per label per namespace with corresponding status."""
        namespace_workflows_map = get_namespace_object_labels_map(cls._NAMESPACES_VARIABLES_WORKFLOWS_MAP)

        for namespace, workflows_labels in namespace_workflows_map.items():
            for label_selector in workflows_labels:
                _LOGGER.info(
                    "Evaluating workflows(label_selector=%r) metrics for namespace: %r", label_selector, namespace
                )
                workflows_and_tasks_status = cls._WORKFLOW_MANAGER.get_workflows_and_tasks_status(
                    label_selector=label_selector, namespace=namespace
                )
                cls._analyze_workflows(
                    label_selector=label_selector, namespace=namespace, workflows=workflows_and_tasks_status
                )

    @classmethod
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
