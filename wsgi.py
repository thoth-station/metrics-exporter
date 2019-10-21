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

"""This is a Prometheus exporter for Thoth."""

import os
import logging
from datetime import datetime
import typing
from functools import partial
import itertools

from flask_apscheduler import APScheduler
from flask import Flask
from flask import redirect
from flask import make_response
from flask import jsonify
from prometheus_client import generate_latest

from thoth.common import init_logging
from thoth.metrics_exporter import __version__

from thoth.metrics_exporter.jobs import OpenshiftMetrics
from thoth.metrics_exporter.jobs import CephMetrics
from thoth.metrics_exporter.jobs import DBMetrics

from thoth.metrics_exporter.jobs import ExternalInformation
from thoth.metrics_exporter.jobs import PythonPackagesMetrics
from thoth.metrics_exporter.jobs import SolverMetrics
from thoth.metrics_exporter.jobs import AnalyzerMetrics
from thoth.metrics_exporter.jobs import InspectionMetrics
from thoth.metrics_exporter.jobs import AdviserMetrics
from thoth.metrics_exporter.jobs import SoftwareEnvironmentMetrics
from thoth.metrics_exporter.jobs import PIMetrics

init_logging()

_LOGGER = logging.getLogger("thoth.metrics_exporter")
_LOGGER.info(f"Thoth Metrics Exporter v{__version__}")

_DEBUG = os.getenv("METRICS_EXPORTER_DEBUG", False)
_UPDATE_INTERVAL_SECONDS = int(os.getenv("THOTH_METRICS_EXPORTER_UPDATE_INTERVAL", 20))
_JOBS_RUN = 0
_INITIALIZED = False
_FIRST_RUN_TIME = datetime.now()

_OPENSHIFT_METRICS = OpenshiftMetrics()
_CEPH_METRICS = CephMetrics()
_DB_METRICS = DBMetrics()

_EXTERNAL_INFORMATION = ExternalInformation()
_PYTHON_PACKAGES_METRICS = PythonPackagesMetrics()
_PI_METRICS = PIMetrics()
_SOFTWARE_ENVIRONMENT_METRICS = SoftwareEnvironmentMetrics()
_ADVISER_METRICS = AdviserMetrics()
_INSPECTION_METRICS = InspectionMetrics()
_PACKAGE_ANALYZER_METRICS = PackageAnalyzerMetrics()
_SOLVER_METRICS = SolverMetrics()


_ALL_REGISTERED_JOBS = frozenset(
    (
        _OPENSHIFT_METRICS.get_thoth_jobs_per_label,
        _OPENSHIFT_METRICS.get_configmaps_per_namespace_per_label,
        _CEPH_METRICS.get_ceph_results_per_type,
        _CEPH_METRICS.get_ceph_connection_error_status,
        _DB_METRICS.get_graphdb_connection_error_status,
        _DB_METRICS.get_tot_main_records_count,
        _DB_METRICS.get_tot_records_count,
        _DB_METRICS.get_tot_relation_records_count,
        _EXTERNAL_INFORMATION.get_user_python_software_stack_count,
        _EXTERNAL_INFORMATION.get_user_unique_run_software_environment_count,
        _PYTHON_PACKAGES_METRICS.get_number_python_index_urls,
        _PYTHON_PACKAGES_METRICS.get_python_packages_versions_count,
        _PYTHON_PACKAGES_METRICS.get_python_packages_per_index_urls_count,
        _PI_METRICS.get_observations_count_per_framework,
        _PI_METRICS.get_tot_performance_records_count,
        _SOFTWARE_ENVIRONMENT_METRICS.get_unique_run_software_environment_count,
        _SOFTWARE_ENVIRONMENT_METRICS.get_unique_build_software_environment_count,
        _ADVISER_METRICS.get_advised_python_software_stack_count,
        _PACKAGE_ANALYZER_METRICS.get_analyzed_python_packages_count,
        _PACKAGE_ANALYZER_METRICS.get_unanalyzed_python_packages_count,
        _PACKAGE_ANALYZER_METRICS.get_analyzed_error_python_packages_count,
        _INSPECTION_METRICS.get_inspection_results_per_identifier,
        _INSPECTION_METRICS.get_inspection_python_software_stack_count,
        _SOLVER_METRICS.get_solver_count,
        _SOLVER_METRICS.get_unsolved_python_packages_count,
        _SOLVER_METRICS.get_python_packages_solver_error_count
    )
)


def func_wrapper(func: typing.Callable) -> None:
    """A wrapper which counts how many jobs were run."""
    # This simple wrapper wraps the actual function which does metrics
    # gathering to count how many functions were called. If we reach number of
    # all jobs, we know we gathered all metrics and we can expose metrics on
    # /metrics endpoint. Otherwise the application keeps returning HTTP status
    # code 503 signalizing its not ready yet.
    global _JOBS_RUN
    global _INITIALIZED

    func()

    if not _INITIALIZED:
        # Increment/keep track only until we are not initialized.
        _JOBS_RUN += 1


class _Config:
    """Configuration of APScheduler for updating metrics."""

    JOBS = [
        {
            'id': func.__name__,
            'func': partial(func_wrapper, func),
            'trigger': 'interval',
            'seconds': _UPDATE_INTERVAL_SECONDS,
            'next_run_time': _FIRST_RUN_TIME,
            'max_instances': 1,
        }
        for func in _ALL_REGISTERED_JOBS
    ]

    SCHEDULER_API_ENABLED = True


application = Flask("thoth.metrics_exporter")
application.config.from_object(_Config())

# Init scheduler.
scheduler = APScheduler()
scheduler.init_app(application)
scheduler.start()


@application.after_request
def extend_response_headers(response):
    """Just add my signature."""
    response.headers["X-Thoth-Metrics-Exporter-Version"] = f"v{__version__}"
    return response


@application.route("/")
def main():
    """Show this to humans."""
    return redirect("https://grafana.datahub.redhat.com", code=308)


@application.route("/metrics")
def metrics():
    """Return the Prometheus Metrics."""
    _LOGGER.debug("Exporting metrics registry...")
    global _INITIALIZED
    global _JOBS_RUN

    if not _INITIALIZED:
        if _JOBS_RUN < len(_Config.JOBS):
            return make_response(jsonify({"error": "Metrics are not ready yet"}), 503)

        # Torn on the switch, we do not need to keep track of not-ready jobs.
        _INITIALIZED = True

    return generate_latest().decode("utf-8")


if __name__ == "__main__":
    _LOGGER.debug("Debug mode is on")
    application.run(host="0.0.0.0", port=8080)
