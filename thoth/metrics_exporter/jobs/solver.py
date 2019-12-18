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

"""Solver related metrics."""

import logging

from thoth.common import OpenShift
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class SolverMetrics(MetricsBase):
    """Class to evaluate Metrics for Solvers."""

    _OPENSHIFT = OpenShift()

    @classmethod
    @register_metric_job
    def get_solver_count(cls) -> None:
        """Get number of solvers in Thoth Infra namespace."""
        solvers = len(cls._OPENSHIFT.get_solver_names())

        metrics.graphdb_total_number_solvers.set(solvers)
        _LOGGER.debug("graphdb_total_number_solvers=%r", solvers)

    @classmethod
    @register_metric_job
    def get_unsolved_python_packages_count(cls) -> None:
        """Get number of unsolved Python packages per solver."""
        for solver_name in cls._OPENSHIFT.get_solver_names():
            solver_info = cls.graph().parse_python_solver_name(solver_name)

            count = cls.graph().get_unsolved_python_package_versions_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            metrics.graphdb_total_number_unsolved_python_packages.labels(solver_name).set(count)
            _LOGGER.debug("graphdb_total_number_unsolved_python_packages(%r)=%r", solver_name, count)

    @classmethod
    @register_metric_job
    def get_python_packages_solved_count_per_solver(cls) -> None:
        """Get number of python packages solved per solver."""
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
            py_packages_solved = cls.graph().get_solved_python_packages_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            py_packages_solver_error = cls.graph().get_error_solved_python_package_versions_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )
            py_packages_solver_error_unparseable = cls.graph().get_error_solved_python_package_versions_count_all(
                unparseable=True,
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )
            py_packages_solver_error_unsolvable = cls.graph().get_error_solved_python_package_versions_count_all(
                unsolvable=True,
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            py_packages_solved_with_no_error = (
                py_packages_solved - py_packages_solver_error
            )

            metrics.graphdb_total_python_packages_solved_with_no_error.labels(solver_name).set(
                py_packages_solved_with_no_error
            )
            metrics.graphdb_total_python_packages_with_solver_error_unparseable.labels(solver_name).set(
                py_packages_solver_error_unparseable
            )
            metrics.graphdb_total_python_packages_with_solver_error_unsolvable.labels(solver_name).set(
                py_packages_solver_error_unsolvable
            )
            metrics.graphdb_total_python_packages_with_solver_error.labels(solver_name).set(
                py_packages_solver_error
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_solved_with_no_error(%r)=%r",
                solver_name,
                py_packages_solved_with_no_error,
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_with_solver_error(%r)=%r",
                solver_name,
                py_packages_solver_error,
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_with_solver_error_unparseable(%r)=%r",
                solver_name,
                py_packages_solver_error_unparseable,
            )

            _LOGGER.debug(
                "graphdb_total_python_packages_with_solver_error_unsolvable(%r)=%r",
                solver_name,
                py_packages_solver_error_unsolvable,
            )
