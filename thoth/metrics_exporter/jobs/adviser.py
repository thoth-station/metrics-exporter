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

"""Adviser metrics."""

import logging
import os
from datetime import datetime

from thoth.storages import GraphDatabase
from thoth.storages.graph.enums import SoftwareStackTypeEnum
import thoth.metrics_exporter.metrics as metrics
from prometheus_api_client import PrometheusConnect

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class AdviserMetrics(MetricsBase):
    """Class to evaluate Metrics for Adviser."""

    _URL = "https://prometheus-dh-prod-monitoring.cloud.datahub.psi.redhat.com"
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _NAMESPACE = os.environ["THOTH_FRONTEND_NAMESPACE"]

    _PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)

    _ADVISER_CHECK_TIME = 0

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
    def get_adviser_evaluation_time(cls) -> None:
        """Get the time spent for each adviser worflow."""
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
                if "adviser" in metric['metric']['name']:
                    completion_time = datetime.fromtimestamp(
                            int(metric['value'][1])
                            )
                    new_time = datetime.now()

                    if cls._ADVISER_CHECK_TIME < completion_time < new_time: 
                        inspection_workflows[metric['metric']['name']] = completion_time

            cls._ADVISER_CHECK_TIME = new_time

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
                    metrics.workflow_adviser_latency.observe(
                        (completion_time - start_time).total_seconds()
                        )

            else:
                _LOGGER.debug("No adviser workflow identified")

        else:
            _LOGGER.debug("No metrics identified for %r", workflow_completion_time_metric_name)
