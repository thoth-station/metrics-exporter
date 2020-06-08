#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2020 Sai Sankar Gochhayat
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


"""Kebechet metrics."""

import logging

from .base import register_metric_job
from .base import MetricsBase

import thoth.metrics_exporter.metrics as metrics
from ..configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class KebechetMetrics(MetricsBase):
    """Class to evaluate Metrics for Kebechet."""

    @classmethod
    @register_metric_job
    def get_active_kebechet_repo_count(cls) -> None:
        """Get number of repositories Kebechet currently supports."""
        count = cls.graph().get_kebechet_github_installations_count_per_is_active()
        metrics.kebechet_total_active_repo_count.set(count)
        _LOGGER.debug("kebechet_total_active_repo_count=%r", count)

    @classmethod
    @register_metric_job
    def get_workflow_status(cls) -> None:
        """Get the workflow status for each workflow."""
        ArgoWorkflowsMetrics().get_thoth_workflows_status_per_namespace_per_label(
            label_selector="component=kebechet", namespace=Configuration._THOTH_BACKEND_NAMESPACE
        )

    @classmethod
    @register_metric_job
    def get_kebechet_quality(cls) -> None:
        """Get the quality for Kebechet workflows."""
        ArgoWorkflowsMetrics().get_workflow_quality(
            service_name="kebechet",
            prometheus=Configuration._PROM,
            instance=Configuration._WORKFLOW_CONTROLLER_INSTANCE_BACKEND_NAMESPACE,
            namespace=Configuration._THOTH_BACKEND_NAMESPACE,
            metric_type=metrics.workflow_kebechet_quality,
        )
