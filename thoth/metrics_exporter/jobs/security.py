#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2020, 2021 Francesco Murdaca
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

"""Security related metrics."""

import logging
import os

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase
from ..configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class SecurityMetrics(MetricsBase):
    """Class to evaluate Metrics for Security."""

    _METRICS_EXPORTER_INSTANCE = os.environ["METRICS_EXPORTER_INFRA_PROMETHEUS_INSTANCE"]

    @classmethod
    @register_metric_job
    def get_si_unanalyzed_python_packages_versions(cls) -> None:
        """Get the change in security unanalyzed Python Packages in Thoth Knowledge Graph."""
        count_si_unanalyzed = cls.graph().get_si_unanalyzed_python_package_versions_count_all(distinct=True)

        metrics.graphdb_total_number_si_unanalyzed_python_packages.set(count_si_unanalyzed)
        _LOGGER.debug("graphdb_total_number_si_unanalyzed_python_packages=%r", count_si_unanalyzed)

        metric_name = "thoth_graphdb_total_number_si_unanalyzed_python_packages"
        metric = Configuration.PROM.get_current_metric_value(
            metric_name=metric_name, label_config={"instance": cls._METRICS_EXPORTER_INSTANCE}
        )
        if metric:
            python_package_versions_metric = float(metric[0]["value"][1])

            si_unanalyzed_python_package_versions_change = python_package_versions_metric - count_si_unanalyzed

            if si_unanalyzed_python_package_versions_change < 0:
                # si_unanalyzed packages are increasing if < 0 -> 0
                si_unanalyzed_python_package_versions_change = 0

            metrics.graphdb_si_unanalyzed_python_package_versions_change.inc(
                si_unanalyzed_python_package_versions_change
            )
            _LOGGER.debug(
                "graphdb_si_unanalyzed_python_package_versions_change=%r", si_unanalyzed_python_package_versions_change
            )

        else:
            _LOGGER.warning("No metrics identified from Prometheus for %r", metric_name)

    @classmethod
    @register_metric_job
    def get_python_packages_si_analyzed_count(cls) -> None:
        """Get number of SI analyzed Python packages."""
        count_si_analyzed = cls.graph().get_si_analyzed_python_package_versions_count_all(distinct=True)
        metrics.graphdb_total_number_si_analyzed_python_packages.set(count_si_analyzed)
        _LOGGER.debug("graphdb_total_number_si_analyzed_python_packages=%r", count_si_analyzed)

    @classmethod
    @register_metric_job
    def get_python_packages_si_not_analyzable_count(cls) -> None:
        """Get number of SI not analyzable Python packages."""
        count_si_not_analyzable = cls.graph().get_si_unanalyzed_python_package_versions_count_all(
            distinct=True, provides_source_distro=False
        )
        metrics.graphdb_total_number_si_not_analyzable_python_packages.set(count_si_not_analyzable)
        _LOGGER.debug("graphdb_total_number_si_not_analyzable_python_packages=%r", count_si_not_analyzable)
