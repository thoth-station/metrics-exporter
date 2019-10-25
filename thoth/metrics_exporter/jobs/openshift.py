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

"""Metrics related to OpenShift resources and objects."""

import logging
from typing import Set
import os

from thoth.common import OpenShift
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class OpenshiftMetrics(MetricsBase):
    """Class to evaluate Metrics for OpenShift."""

    _OPENSHIFT = OpenShift()

    _JOBS_LABELS = [
        "component=dependency-monkey",
        "component=amun-inspection-job",
        "component=solver",
        "component=package-extract",
        "component=package-analyzer",
        "component=provenance-checker",
        "component=adviser",
        "graph-sync-type=adviser",
        "graph-sync-type=dependency-monkey",
        "graph-sync-type=inspection",
        "graph-sync-type=package-analyzer",
        "graph-sync-type=package-extract",
        "graph-sync-type=provenance-checker",
        "graph-sync-type=solver",
    ]

    _NAMESPACES_VARIABLES = [
        "THOTH_FRONTEND_NAMESPACE",
        "THOTH_MIDDLETIER_NAMESPACE",
        "THOTH_BACKEND_NAMESPACE",
        "THOTH_AMUN_NAMESPACE",
        "THOTH_AMUN_INSPECTION_NAMESPACE",
    ]

    @classmethod
    def get_namespaces(cls) -> Set[str]:
        """Retrieve namespaces that shall be monitored by metrics-exporter."""
        namespaces = []
        for environment_varibale in cls._NAMESPACES_VARIABLES:
            if os.getenv(environment_varibale):
                namespaces.append(os.environ[environment_varibale])
            else:
                _LOGGER.warning("Namespace variable not provided for %r", environment_varibale)
        return set(namespaces)

    @classmethod
    @register_metric_job
    def get_thoth_jobs_per_label(cls) -> None:
        """Get the total number of Jobs per label with corresponding status."""
        namespaces = cls.get_namespaces()

        for label_selector in cls._JOBS_LABELS:
            for namespace in namespaces:
                _LOGGER.info("Evaluating jobs(label_selector=%r) metrics for namespace: %r", label_selector, namespace)
                jobs_status_evaluated = cls._OPENSHIFT.get_job_status_count(
                    label_selector=label_selector, namespace=namespace
                )

                for j_status, j_counts in jobs_status_evaluated.items():
                    metrics.jobs_status.labels(label_selector, j_status, namespace).set(j_counts)

                _LOGGER.debug("thoth_jobs=%r", jobs_status_evaluated)

    @staticmethod
    def count_configmaps(config_map_list_items: dict) -> int:
        """Count the number of ConfigMaps for a certain label in a specific namespace."""
        return len(config_map_list_items["items"])

    @classmethod
    @register_metric_job
    def get_configmaps_per_namespace_per_label(cls) -> None:
        """Get the total number of configmaps in the namespace based on labels."""
        namespaces = cls.get_namespaces()

        for namespace in namespaces:

            for label in cls._JOBS_LABELS + ["operator=graph-sync", "operator=workload"]:
                _LOGGER.info("Evaluating ConfigMaps(label_selector=%r) metrics for namespace: %r", label, namespace)
                config_maps_items = cls._OPENSHIFT.get_configmaps(namespace=namespace, label_selector=label)
                number_configmaps = cls.count_configmaps(config_maps_items)
                metrics.config_maps_number.labels(namespace, label).set(number_configmaps)
                _LOGGER.debug(
                    "thoth_config_maps_number=%r, in namespace=%r for label=%r", number_configmaps, namespace, label
                )
