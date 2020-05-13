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

"""Provenance Check metrics."""

import logging

from .base import register_metric_job
from .base import MetricsBase
from .ceph import get_ceph_results_per_type
from thoth.storages import ProvenanceResultsStore

_LOGGER = logging.getLogger(__name__)


class ProvenanceCheckMetrics(MetricsBase):
    """Class to evaluate Metrics for Provenance Check."""

    @classmethod
    @register_metric_job
    def get_ceph_count(cls) -> None:
        """Get number of reports stored in the database for a type of store."""
        get_ceph_results_per_type(store=ProvenanceResultsStore())
