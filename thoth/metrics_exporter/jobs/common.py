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

"""A collection of methods that can be resued in different metric classes."""

import logging

from datetime import datetime
from prometheus_api_client import PrometheusConnect
import thoth.metrics_exporter.metrics as metrics

_LOGGER = logging.getLogger(__name__)


def get_workflow_duration(
    service_name: str,
    prometheus: PrometheusConnect,
    instance: str,
    namespace: str,
    check_time: datetime,
    metric_type: metrics
) -> datetime:
    """Get the time spent for each worflow for a certain service."""
    workflow_status_metric_name = "argo_workflow_status_phase"
    workflow_status_metrics = prometheus.get_current_metric_value(
        metric_name=workflow_status_metric_name,
        label_config={
            'instance': instance,
            "namespace": namespace,
            "phase": "Succeeded"}
            )

    if workflow_status_metrics:
        new_time = datetime.now()
        new_workflows_count = 0

        for metric in workflow_status_metrics:

            workflow_status = int(metric['value'][1])
            workflow_name = metric['metric']['name']

            if service_name in workflow_name and workflow_status == 1:
                workflow_completion_time_metric_name = "argo_workflow_completion_time"
                workflow_completion_time = prometheus.get_current_metric_value(
                    metric_name=workflow_completion_time_metric_name,
                    label_config={
                        'instance': instance,
                        "namespace": namespace,
                        "name": workflow_name}
                        )
                completion_time = datetime.fromtimestamp(
                        int(workflow_completion_time[0]['value'][1])
                        )

                if check_time < completion_time < new_time:
                    new_workflows_count += 1
                    workflow_start_time_metric_name = "argo_workflow_start_time"
                    workflow_start_time = prometheus.get_current_metric_value(
                        metric_name=workflow_start_time_metric_name,
                        label_config={
                            'instance': instance,
                            "namespace": namespace,
                            "name": workflow_name}
                            )

                    start_time = datetime.fromtimestamp(
                        int(workflow_start_time[0]['value'][1])
                        )
                    metric_type.observe(
                        (completion_time - start_time).total_seconds()
                    )
                    _LOGGER.debug("Worflow duration for %r is %r s" % (
                        workflow_name,
                        (completion_time - start_time).total_seconds()
                        )
                    )

                if not new_workflows_count:
                    _LOGGER.debug("No new %r workflow identified" % service_name)

        return new_time

    else:
        _LOGGER.debug("No metrics identified for %r", workflow_status_metric_name)
        return check_time
