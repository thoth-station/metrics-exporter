#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2020 Francesco Murdaca
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

"""PyPI metrics."""

import logging

import requests
from bs4 import BeautifulSoup

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class PyPIMetrics(MetricsBase):
    """Class to collect statistics from PyPI."""

    @classmethod
    @register_metric_job
    def get_pypi_statistics(cls) -> None:
        """Get statistics from PyPI."""
        response = requests.get("https://pypi.org/")
        soup = BeautifulSoup(response.content, "html.parser")
        statistics = soup.findAll("p", class_="statistics-bar__statistic")
        pypy_stats = [int("".join(c for c in s.get_text() if c.isdigit())) for s in statistics]

        pypi_packages = pypy_stats[0]
        pypi_releases = pypy_stats[1]

        stats_type = "packages"
        metrics.pypi_stats.labels(stats_type).set(pypi_packages)
        _LOGGER.debug("pypi_stats(%r)=%r", stats_type, pypi_packages)

        stats_type = "releases"
        metrics.pypi_stats.labels(stats_type).set(pypi_releases)
        _LOGGER.debug("pypi_stats(%r)=%r", stats_type, pypi_releases)
