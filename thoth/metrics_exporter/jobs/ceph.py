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

"""Ceph metrics."""

import logging

from thoth.storages.ceph import CephStore
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase
from ..configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class CephMetrics(MetricsBase):
    """Class to evaluate Metrics for Ceph."""

    @staticmethod
    @register_metric_job
    def get_ceph_connection_error_status() -> None:
        """Check connection to Ceph instance."""
        ceph_storage = CephStore(
            key_id=Configuration.CEPH_ACCESS_KEY_ID,
            secret_key=Configuration.CEPH_ACCESS_SECRET_KEY,
            prefix=Configuration.CEPH_BUCKET_PREFIX,
            host=Configuration.S3_ENDPOINT_URL,
            bucket=Configuration.CEPH_BUCKET,
        )
        try:
            ceph_storage.connect()
        except Exception as excptn:
            metrics.ceph_connection_error_status.set(0)
            _LOGGER.exception(excptn)
        else:
            metrics.ceph_connection_error_status.set(1)
