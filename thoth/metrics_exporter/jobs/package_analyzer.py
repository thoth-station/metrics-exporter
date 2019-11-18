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

"""Package analyzer metrics."""

import logging

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class PackageAnalyzerMetrics(MetricsBase):
    """Class to evaluate Metrics for Package Analyzer."""

    @classmethod
    @register_metric_job
    def get_analyzed_python_packages_count(cls) -> None:
        """Get number of unanlyzed Python packages."""
        count = cls.graph().get_analyzed_python_package_versions_count_all()
        metrics.graphdb_total_number_analyzed_python_packages.set(count)
        _LOGGER.debug("graphdb_total_number_analyzed_python_packages=%r", count)

    @classmethod
    @register_metric_job
    def get_analyzed_error_python_packages_count(cls) -> None:
        """Get number of unalyzed Python packages."""
        count = cls.graph().get_analyzed_error_python_package_versions_count_all()
        metrics.graphdb_total_number_analyzed_error_python_packages.set(count)
        _LOGGER.debug("graphdb_total_number_analyzed_error_python_packages=%r", count)

    @classmethod
    @register_metric_job
    def get_unanalyzed_python_packages_count(cls) -> None:
        """Get number of unanlyzed Python packages."""
        count = cls.graph().get_unanalyzed_python_package_versions_count_all()
        metrics.graphdb_total_number_unanalyzed_python_packages.set(count)
        _LOGGER.debug("graphdb_total_number_unanalyzed_python_packages=%r", count)
