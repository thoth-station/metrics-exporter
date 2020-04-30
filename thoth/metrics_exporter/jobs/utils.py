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

"""A collection of methods that can be reused in different metric classes."""

import logging
import os

from typing import Dict, Any, List
from datetime import datetime
from prometheus_api_client import PrometheusConnect
import thoth.metrics_exporter.metrics as metrics

_LOGGER = logging.getLogger(__name__)


_WORKFLOW_COMPLETION_TIME_METRIC_NAME = "argo_workflow_completion_time"
_WORKFLOW_START_TIME_METRIC_NAME = "argo_workflow_start_time"
_WORKFLOW_STATUS_METRIC_NAME = "argo_workflow_status_phase"
_WORKFLOW_STATUSES = ["Succeeded", "Failed", "Error", "Running", "Skipped", "Pending"]


def get_workflow_duration(
    service_name: str,
    prometheus: PrometheusConnect,
    instance: str,
    namespace: str,
    check_time: datetime,
    metric_type: metrics,
) -> datetime:
    """Get the time spent for each workflow for a certain service."""
    workflow_status_metric_name = _WORKFLOW_STATUS_METRIC_NAME
    workflow_status_metrics = prometheus.get_current_metric_value(
        metric_name=workflow_status_metric_name,
        label_config={"instance": instance, "namespace": namespace, "phase": "Succeeded"},
    )

    if not workflow_status_metrics:
        _LOGGER.debug("No metrics identified for %r", workflow_status_metric_name)
        return check_time

    new_time = datetime.utcnow()
    new_workflows_count = 0
    service_workflow_status_metrics = [
        w for w in workflow_status_metrics if (service_name in w["metric"]["name"]) and (int(w["value"][1]) == 1)
    ]

    for metric in service_workflow_status_metrics:

        workflow_status = int(metric["value"][1])
        workflow_name = metric["metric"]["name"]

        workflow_completion_time = prometheus.get_current_metric_value(
            metric_name=_WORKFLOW_COMPLETION_TIME_METRIC_NAME,
            label_config={"instance": instance, "namespace": namespace, "name": workflow_name},
        )

        if workflow_completion_time:
            completion_time = datetime.fromtimestamp(int(workflow_completion_time[0]["value"][1]))

            if check_time < completion_time < new_time:
                new_workflows_count += 1
                workflow_start_time = prometheus.get_current_metric_value(
                    metric_name=_WORKFLOW_START_TIME_METRIC_NAME,
                    label_config={"instance": instance, "namespace": namespace, "name": workflow_name},
                )

                start_time = datetime.fromtimestamp(int(workflow_start_time[0]["value"][1]))
                metric_type.observe((completion_time - start_time).total_seconds())
                _LOGGER.debug(
                    "Workflow duration for %r is %r s", workflow_name, (completion_time - start_time).total_seconds()
                )

        if not new_workflows_count:
            _LOGGER.debug("No new %r workflow identified", service_name)

    return new_time


def get_workflow_quality(
    service_name: str, prometheus: PrometheusConnect, instance: str, namespace: str, metric_type: metrics
) -> None:
    """Get the status for workflows for a certain service."""
    workflow_status_metric_name = _WORKFLOW_STATUS_METRIC_NAME

    workflows_count = {}
    tot_workflows = 0
    for workflow_status in _WORKFLOW_STATUSES:
        workflow_status_metrics = prometheus.get_current_metric_value(
            metric_name=workflow_status_metric_name,
            label_config={"instance": instance, "namespace": namespace, "phase": workflow_status},
        )
        service_workflows = [
            w for w in workflow_status_metrics if (int(w["value"][1]) == 1) and (service_name in w["metric"]["name"])
        ]
        workflows_count[workflow_status] = len(service_workflows)
        tot_workflows += len(service_workflows)

    for w_status, counts in workflows_count.items():
        if tot_workflows:
            metric_type.labels(service_name, w_status).set(counts / tot_workflows)
            _LOGGER.debug(
                "Workflow metrics status/counts for service_name=%r, status=%r, counts=%r",
                service_name,
                w_status,
                counts,
            )


def get_namespace_object_labels_map(namespace_objects: Dict[str, Any]) -> Dict[str, List[str]]:
    """Retrieve namespace/objects map that shall be monitored by metrics-exporter."""
    namespace_objects_map = {}
    for environment_variable, objects_labels in namespace_objects.items():

        namespace_objects_map = _retrieve_namespace_object_labels(
            environment_variable=environment_variable,
            objects_labels=objects_labels,
            namespace_objects_map=namespace_objects_map,
        )

    return namespace_objects_map


def _retrieve_namespace_object_labels(
    environment_variable: str, objects_labels: Dict[str, Any], namespace_objects_map: Dict[str, Any]
):
    """Retrieve namespace and labels."""
    if os.getenv(environment_variable):
        if os.getenv(environment_variable) not in namespace_objects_map.keys():
            namespace_objects_map[os.environ[environment_variable]] = objects_labels
        else:
            namespace_objects_map[os.environ[environment_variable]] += objects_labels
    else:
        _LOGGER.warning("Namespace variable not provided for %r", environment_variable)

    return namespace_objects_map
