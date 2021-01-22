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
from prometheus_api_client import PrometheusConnect

_LOGGER = logging.getLogger(__name__)


class Configuration:
    """Configuration of metrics-exporter."""

    # Prometheus
    URL = os.environ["PROMETHEUS_HOST_URL"]
    PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    HEADERS = {"Authorization": f"bearer {PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    PROM = PrometheusConnect(url=URL, disable_ssl=True, headers=HEADERS)

    # Namespaces
    THOTH_BACKEND_NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]
    THOTH_MIDDLETIER_NAMESPACE = os.environ["THOTH_MIDDLETIER_NAMESPACE"]
    THOTH_AMUN_INSPECTION_NAMESPACE = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]

    # Ceph
    CEPH_ACCESS_KEY_ID = os.environ["THOTH_CEPH_KEY_ID"]
    CEPH_ACCESS_SECRET_KEY = os.environ["THOTH_CEPH_SECRET_KEY"]
    CEPH_BUCKET_PREFIX = os.environ["THOTH_CEPH_BUCKET_PREFIX"]
    S3_ENDPOINT_URL = os.environ["THOTH_S3_ENDPOINT_URL"]
    CEPH_BUCKET = os.environ["THOTH_CEPH_BUCKET"]

    DEPLOYMENT_NAME = os.environ["THOTH_DEPLOYMENT_NAME"]
