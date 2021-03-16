#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2021 Francesco Murdaca
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

"""Knowledge graph metrics."""

import logging

from thoth.messaging.admin_client import check_connection

import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class KafkaMetrics(MetricsBase):
    """Class to evaluate Kafka Metrics."""

    @staticmethod
    @register_metric_job
    def get_kafka_connection_status() -> None:
        """Check connection to Kafka broker."""
        try:
            check_connection()
        except Exception as excptn:
            metrics.kafka_connection_error_status.set(0)
            _LOGGER.exception(excptn)
        else:
            metrics.kafka_connection_error_status.set(1)
