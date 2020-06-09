#!/usr/bin/env python3
# thoth-metrics-exporter
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

"""Configuration of metrics-exporter."""

import logging
import os

_LOGGER = logging.getLogger(__name__)


class Configuration:
    """Configuration of metrics-exporter."""

    # Prometheus
    URL = os.environ["PROMETHEUS_HOST_URL"]
    PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)

    # Workflows backend namespace
    WORKFLOW_CONTROLLER_INSTANCE_BACKEND_NAMESPACE = os.environ["WORKFLOW_METRICS_BACKEND_PROMETHEUS_INSTANCE"]
    THOTH_BACKEND_NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]

    # Workflows middletier namespace
    WORKFLOW_CONTROLLER_INSTANCE_MIDDLETIER_NAMESPACE = os.environ["WORKFLOW_METRICS_MIDDLETIER_PROMETHEUS_INSTANCE"]
    THOTH_MIDDLETIER_NAMESPACE = os.environ["THOTH_MIDDLETIER_NAMESPACE"]

    # Workflows amun-inspection namespace
    WORKFLOW_CONTROLLER_INSTANCE_AMUN_INSPECTION_NAMESPACE = os.environ[
        "WORKFLOW_METRICS_AMUN_INSPECTION_PROMETHEUS_INSTANCE"
    ]
    THOTH_AMUN_INSPECTION_NAMESPACE = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]
