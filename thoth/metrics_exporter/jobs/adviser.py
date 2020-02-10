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
from .common import get_workflow_duration

_LOGGER = logging.getLogger(__name__)


class AdviserMetrics(MetricsBase):
    """Class to evaluate Metrics for Adviser."""

    _URL = os.environ["PROMETHEUS_HOST_URL"]
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _INSTANCE = os.environ["WORKFLOW_METRICS_BACKEND_PROMETHEUS_INSTANCE"]
    _NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]

    _PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)

    _ADVISER_CHECK_TIME = datetime.now()
    _QEBHWT_CHECK_TIME = datetime.now()

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
        cls._ADVISER_CHECK_TIME = get_workflow_duration(
            service_name="adviser",
            prometheus=cls._PROM,
            instance=cls._INSTANCE,
            namespace=cls._NAMESPACE,
            check_time=cls._ADVISER_CHECK_TIME,
            metric_type=metrics.workflow_adviser_latency)

    @classmethod
    @register_metric_job
    def get_adviser_evaluation_time(cls) -> None:
        """Get the time spent for each adviser worflow."""
        cls._QEBHWT_CHECK_TIME = get_workflow_duration(
            service_name="qeb-hwt",
            prometheus=cls._PROM,
            instance=cls._INSTANCE,
            namespace=cls._NAMESPACE,
            check_time=cls._QEBHWT_CHECK_TIME,
            metric_type=metrics.workflow_qebhwt_latency)
