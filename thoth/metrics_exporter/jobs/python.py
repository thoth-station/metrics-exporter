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

"""Metrics related to Python ecosystem."""

import logging

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class PythonPackagesMetrics(MetricsBase):
    """Class to discover Content for PythonPackages inside Thoth database."""

    @classmethod
    @register_metric_job
    def get_python_packages_versions_count(cls) -> None:
        """Get the total number of Python packages versions in Thoth Knowledge Graph."""
        number_python_package_versions = cls.graph().get_python_package_versions_count_all(distinct=True)
        metrics.graphdb_number_python_package_versions.set(number_python_package_versions)
        _LOGGER.debug("graphdb_number_python_package_versions=%r", number_python_package_versions)

    @classmethod
    @register_metric_job
    def get_number_python_index_urls(cls) -> None:
        """Get the total number of python indexes in Thoth Knowledge Graph."""
        python_urls_count = len(cls.graph().get_python_package_index_urls_all())
        metrics.graphdb_total_python_indexes.set(python_urls_count)
        _LOGGER.debug("thoth_graphdb_total_python_indexes=%r", python_urls_count)

    @classmethod
    @register_metric_job
    def get_python_packages_per_index_urls_count(cls) -> None:
        """Get the total number of unique python packages per index URL in Thoth Knowledge Graph."""
        python_urls_list = list(cls.graph().get_python_package_index_urls_all())
        tot_packages = 0
        for index_url in python_urls_list:
            index_url = cls.graph().normalize_python_index_url(index_url=index_url)
            packages_count = len(
                cls.graph().get_python_package_versions_per_index(index_url=index_url, distinct=True)[index_url]
            )
            tot_packages += packages_count

            metrics.graphdb_total_python_packages_per_indexes.labels(index_url).set(packages_count)
            _LOGGER.debug("thoth_graphdb_total_python_packages_per_indexes(%r)=%r", index_url, packages_count)

        metrics.graphdb_sum_python_packages_per_indexes.set(tot_packages)
        _LOGGER.debug("thoth_graphdb_sum_python_packages_per_indexes=%r", tot_packages)
