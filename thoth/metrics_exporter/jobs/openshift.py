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

"""Metrics related to OpenShift resources and objects."""

import logging
from typing import Dict, List
import os

from thoth.common import OpenShift
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class OpenshiftMetrics(MetricsBase):
    """Class to evaluate Metrics for OpenShift."""

    _OPENSHIFT = OpenShift()

    _MIDDLETIER_JOBS_LABELS = [
        "component=dependency-monkey",
        "component=package-extract",
        "component=package-analyzer",
        "component=solver",
        "component=build-analyze",
        "graph-sync-type=dependency-monkey",
        "graph-sync-type=package-analyzer",
        "graph-sync-type=package-extract",
        "graph-sync-type=solver",
        "graph-sync-type=build-analyze",
    ]

    _AMUN_INSPECTION_JOBS_LABELS = ["component=amun-inspection-job", "graph-sync-type=inspection"]

    _BACKEND_JOBS_LABELS = [
        "component=adviser",
        "component=provenance-checker",
        "graph-sync-type=adviser",
        "graph-sync-type=provenance-checker",
    ]

    _NAMESPACES_VARIABLES_JOBS_MAP = {
        "THOTH_MIDDLETIER_NAMESPACE": _MIDDLETIER_JOBS_LABELS,
        "THOTH_BACKEND_NAMESPACE": _BACKEND_JOBS_LABELS,
        "THOTH_AMUN_INSPECTION_NAMESPACE": _AMUN_INSPECTION_JOBS_LABELS,
    }

    @classmethod
    def get_namespace_job_labels_map(cls) -> Dict[str, List[str]]:
        """Retrieve namespace/jobs map that shall be monitored by metrics-exporter."""
        namespace_jobs_map = {}
        for environment_variable, job_labels in cls._NAMESPACES_VARIABLES_JOBS_MAP.items():
            if os.getenv(environment_variable):
                if os.getenv(environment_variable) not in namespace_jobs_map.keys():
                    namespace_jobs_map[os.environ[environment_variable]] = job_labels
                else:
                    namespace_jobs_map[os.environ[environment_variable]] += job_labels
            else:
                _LOGGER.warning("Namespace variable not provided for %r", environment_variable)

        return namespace_jobs_map

    @classmethod
    @register_metric_job
    def get_thoth_jobs_per_namespace_per_label(cls) -> None:
        """Get the total number of Jobs per label per namespace with corresponding status."""
        namespace_jobs_map = cls.get_namespace_job_labels_map()

        for namespace, job_labels in namespace_jobs_map.items():
            for label_selector in job_labels:
                _LOGGER.debug("Evaluating jobs(label_selector=%r) metrics for namespace: %r", label_selector, namespace)
                jobs_status_evaluated = cls._OPENSHIFT.get_job_status_count(
                    label_selector=label_selector, namespace=namespace
                )

                for j_status, j_counts in jobs_status_evaluated.items():
                    metrics.jobs_status.labels(label_selector, j_status, namespace).set(j_counts)

                _LOGGER.debug("thoth_jobs=%r", jobs_status_evaluated)

    @classmethod
    @register_metric_job
    def get_configmaps_per_namespace_per_label(cls) -> None:
        """Get the total number of configmaps in the namespace based on labels."""
        namespace_jobs_map = cls.get_namespace_job_labels_map()

        for namespace, job_labels in namespace_jobs_map.items():
            for label_selector in job_labels + ["operator=graph-sync", "operator=workload"]:
                _LOGGER.debug(
                    "Evaluating ConfigMaps(label_selector=%r) metrics for namespace: %r", label_selector, namespace
                )
                response = cls._OPENSHIFT.get_configmaps(namespace=namespace, label_selector=label_selector)
                number_configmaps = len(response["items"])
                metrics.config_maps_number.labels(namespace, label_selector).set(number_configmaps)
                _LOGGER.debug(
                    "thoth_config_maps_number=%r, in namespace=%r for label_selector=%r",
                    number_configmaps,
                    namespace,
                    label_selector,
                )

    @classmethod
    @register_metric_job
    def get_image_streams_per_namespace_per_label(cls) -> None:
        """Get the total number of image streams in the namespace based on labels."""
        label_selector = "component=amun-inspection-imagestream"
        namespace = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]
        _LOGGER.debug(
            "Evaluating ImageStreams(label_selector=%r) metrics for namespace: %r", label_selector, namespace
        )
        response = cls._OPENSHIFT.get_image_streams(namespace=namespace, label_selector=label_selector)
        number_image_streams = len(response["items"])
        metrics.image_streams_maps_number.labels(namespace, label_selector).set(number_image_streams)
        _LOGGER.debug(
            "thoth_image_streams_number=%r, in namespace=%r for label_selector=%r",
            number_image_streams,
            namespace,
            label_selector,
        )
