#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019 Christoph Görn
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

"""This is a Promotheus Metrics exporter for Thoth."""


from prometheus_client import Gauge, Summary

from thoth.common import __version__ as __common__version__
from thoth.storages import __version__ as __storages__version__


__version__ = f"0.7.0+storage.{__storages__version__}.common.{__common__version__}"
__author__ = "Christoph Görn <goern@redhat.com>"


# Info Metric
metrics_exporter_info = Gauge(
    "thoth_metrics_exporter_info",  # what promethus sees
    "Thoth Metrics Exporter information",  # what the human reads
    ["version"],  # what labels I use
)
metrics_exporter_info.labels(__version__).inc()

# SERVICE METRICS
# Solver Jobs
solver_jobs_total = Gauge("thoth_solver_jobs_total", "Number of Solver Jobs running.", ["dist", "status"])

solver_jobs_seconds = Gauge(
    "thoth_solver_jobs_seconds", "Time spent processing requests to OpenShift to get Solver Jobs", []
)

# CONTENT METRICS
# Graph Structure
graphdb_total_vertex_instances = Gauge(
    "thoth_graph_db_total_vertex_instances", "Total number of Vertex Instances in Thoth Knowledge Graph", []
)

graphdb_total_instances_per_vertex = Gauge(
    "thoth_graphdb_total_instances_per_vertex",
    "Total number of Instances for each Vertex in in Thoth Knowledge Graph", ["vertex_label"]
)

# Graph Content

# Python Packages Solver Error
graphdb_total_python_packages_with_solver_error = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error",
    "Total number of python packages with solver error True", []
)
graphdb_total_python_packages_with_solver_error_unparsable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unparsable",
    "Total number of python packages with solver error True and error_unparsable True", []
)

graphdb_total_python_packages_with_solver_error_unsolvable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unsolvable",
    "Total number of python packages with solver error True and error_unsolvable True", []
)

# Python Packages
graphdb_total_unique_python_packages = Gauge(
    "thoth_graphdb_total_unique_python_packages",
    "Total number of unique python packages", []
)

# Software environments for run
graphdb_total_run_software_environment = Gauge(
    "thoth_graphdb_total_run_software_environment",
    "Total number of unique software environment for run", []
)

graphdb_total_user_run_software_environment = Gauge(
    "thoth_graphdb_total_user_run_software_environment",
    "Total number of users unique software environment for run", []
)

# Software environments for build
graphdb_total_build_software_environment = Gauge(
    "thoth_graphdb_total_build_software_environment",
    "Total number of unique software environment for build", []
)

# Graph Metrics Availability
graphdb_connection_error_status = Gauge(
    "thoth_graphdb_connection_issues", "Connection error status", []
)
