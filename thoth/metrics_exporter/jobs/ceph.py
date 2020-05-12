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

from thoth.storages import SolverResultsStore
from thoth.storages import AdvisersResultsStore
from thoth.storages import AnalysisResultsStore
from thoth.storages import InspectionResultsStore
from thoth.storages import PackageAnalysisResultsStore
from thoth.storages import ProvenanceResultsStore
from thoth.storages import DependencyMonkeyReportsStore
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class CephMetrics(MetricsBase):
    """Class to evaluate Metrics for Ceph."""

    _MONITORED_STORES = (
        AdvisersResultsStore(),
        AnalysisResultsStore(),
        InspectionResultsStore(),
        ProvenanceResultsStore(),
        PackageAnalysisResultsStore(),
        SolverResultsStore(),
        DependencyMonkeyReportsStore(),
    )

    @classmethod
    @register_metric_job
    def get_ceph_results_per_type(cls) -> None:
        """Get the total number of results in Ceph per type."""
        for store in cls._MONITORED_STORES:
            _LOGGER.info("Check Ceph content for %s", store.RESULT_TYPE)
            if not store.is_connected():
                store.connect()
            list_ids = store.get_document_count()
            metrics.ceph_results_number.labels(store.RESULT_TYPE).set(len(list_ids))
            _LOGGER.debug("ceph_results_number for %s =%d", store.RESULT_TYPE, len(list_ids))

    @staticmethod
    @register_metric_job
    def get_ceph_connection_error_status() -> None:
        """Check connection to Ceph instance."""
        inspections = InspectionResultsStore()
        try:
            inspections.connect()
        except Exception as excptn:
            metrics.ceph_connection_error_status.set(0)
            _LOGGER.exception(excptn)
        else:
            metrics.ceph_connection_error_status.set(1)
