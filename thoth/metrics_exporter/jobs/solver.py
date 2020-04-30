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

"""Solver related metrics."""

import logging
import os
from datetime import datetime

from thoth.common import OpenShift

import thoth.metrics_exporter.metrics as metrics
from prometheus_api_client import PrometheusConnect

from .base import register_metric_job
from .base import MetricsBase
from .utils import get_workflow_duration, get_workflow_quality

_LOGGER = logging.getLogger(__name__)


class SolverMetrics(MetricsBase):
    """Class to evaluate Metrics for Solvers."""

    _OPENSHIFT = OpenShift()

    _URL = os.environ["PROMETHEUS_HOST_URL"]
    _PROMETHEUS_SERVICE_ACCOUNT_TOKEN = os.environ["PROMETHEUS_SERVICE_ACCOUNT_TOKEN"]
    _HEADERS = {"Authorization": f"bearer {_PROMETHEUS_SERVICE_ACCOUNT_TOKEN}"}
    _INSTANCE = os.environ["WORKFLOW_METRICS_MIDDLETIER_PROMETHEUS_INSTANCE"]
    _METRICS_EXPORTER_INSTANCE = os.environ["METRICS_EXPORTER_FRONTEND_PROMETHEUS_INSTANCE"]
    _NAMESPACE = os.environ["THOTH_MIDDLETIER_NAMESPACE"]

    _PROM = PrometheusConnect(url=_URL, disable_ssl=True, headers=_HEADERS)

    _SOLVER_CHECK_TIME = datetime.utcnow()

    @classmethod
    @register_metric_job
    def get_solver_count(cls) -> None:
        """Get number of solvers in Thoth Infra namespace."""
        solvers = len(cls._OPENSHIFT.get_solver_names())

        metrics.graphdb_total_number_solvers.set(solvers)
        _LOGGER.debug("graphdb_total_number_solvers=%r", solvers)

    @classmethod
    @register_metric_job
    def get_unsolved_python_packages_versions(cls) -> None:
        """Get the change in unsolved Python Packages in Thoth Knowledge Graph."""
        count_unsolved_python_package_versions = 0
        for solver_name in cls._OPENSHIFT.get_solver_names():
            solver_info = cls.graph().parse_python_solver_name(solver_name)

            count = cls.graph().get_unsolved_python_package_versions_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            metrics.graphdb_total_number_unsolved_python_packages_per_solver.labels(solver_name).set(count)
            _LOGGER.debug("graphdb_total_number_unsolved_python_packages_per_solver(%r)=%r", solver_name, count)
            count_unsolved_python_package_versions += count

        metric_name = "thoth_graphdb_total_number_unsolved_python_packages"
        metric = cls._PROM.get_current_metric_value(
            metric_name=metric_name, label_config={"instance": cls._METRICS_EXPORTER_INSTANCE}
        )
        if metric:
            python_package_versions_metric = float(metric[0]["value"][1])

            unsolved_python_package_versions_change = (
                python_package_versions_metric - count_unsolved_python_package_versions
            )

            if unsolved_python_package_versions_change < 0:
                # Unsolved packages are increasing < 0 -> 0
                unsolved_python_package_versions_change = 0

            metrics.graphdb_unsolved_python_package_versions_change.inc(unsolved_python_package_versions_change)
            _LOGGER.debug("graphdb_unsolved_python_package_versions_change=%r", unsolved_python_package_versions_change)

        else:
            _LOGGER.warning("No metrics identified for %r", metric_name)

        metrics.graphdb_total_number_unsolved_python_packages.set(count_unsolved_python_package_versions)
        _LOGGER.debug("graphdb_total_number_unsolved_python_packages=%r", count_unsolved_python_package_versions)

    @classmethod
    @register_metric_job
    def get_python_packages_solved_count_per_solver(cls) -> None:
        """Get number of solved Python packages per solver."""
        for solver_name in cls._OPENSHIFT.get_solver_names():
            solver_info = cls.graph().parse_python_solver_name(solver_name)
            count_solved = cls.graph().get_solved_python_packages_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )
            metrics.graphdb_total_number_solved_python_packages.labels(solver_name).set(count_solved)
            _LOGGER.debug("graphdb_total_number_solved_python_packages(%r)=%r", solver_name, count_solved)

    @classmethod
    @register_metric_job
    def get_python_packages_solver_error_count_per_solver(cls) -> None:
        """Get number of python packages with solver error True and how many are unparsable or unsolvable per solver."""
        for solver_name in cls._OPENSHIFT.get_solver_names():
            solver_info = cls.graph().parse_python_solver_name(solver_name)
            python_packages_solved = cls.graph().get_solved_python_packages_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            python_packages_solver_error = cls.graph().get_error_solved_python_package_versions_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )
            python_packages_solver_error_unparseable = cls.graph().get_error_solved_python_package_versions_count_all(
                unparseable=True,
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )
            python_packages_solver_error_unsolvable = cls.graph().get_error_solved_python_package_versions_count_all(
                unsolvable=True,
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            python_packages_solved_with_no_error = python_packages_solved - python_packages_solver_error

            metrics.graphdb_total_python_packages_solved_with_no_error.labels(solver_name).set(
                python_packages_solved_with_no_error
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_solved_with_no_error(%r)=%r",
                solver_name,
                python_packages_solved_with_no_error,
            )

            metrics.graphdb_total_python_packages_with_solver_error.labels(solver_name).set(
                python_packages_solver_error
            )
            metrics.graphdb_total_python_packages_with_solver_error_unparseable.labels(solver_name).set(
                python_packages_solver_error_unparseable
            )
            metrics.graphdb_total_python_packages_with_solver_error_unsolvable.labels(solver_name).set(
                python_packages_solver_error_unsolvable
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_with_solver_error(%r)=%r", solver_name, python_packages_solver_error
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_with_solver_error_unparseable(%r)=%r",
                solver_name,
                python_packages_solver_error_unparseable,
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_with_solver_error_unsolvable(%r)=%r",
                solver_name,
                python_packages_solver_error_unsolvable,
            )

    @classmethod
    @register_metric_job
    def get_solver_evaluation_time(cls) -> None:
        """Get the time spent for each solver worflow."""
        cls._SOLVER_CHECK_TIME = get_workflow_duration(
            service_name="solver",
            prometheus=cls._PROM,
            instance=cls._INSTANCE,
            namespace=cls._NAMESPACE,
            check_time=cls._SOLVER_CHECK_TIME,
            metric_type=metrics.workflow_solver_latency,
        )

    @classmethod
    @register_metric_job
    def get_solver_quality(cls) -> None:
        """Get the quality for solver workflows."""
        get_workflow_quality(
            service_name="solver",
            prometheus=cls._PROM,
            instance=cls._INSTANCE,
            namespace=cls._NAMESPACE,
            metric_type=metrics.workflow_solver_quality,
        )
