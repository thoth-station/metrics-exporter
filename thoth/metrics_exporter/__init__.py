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

# Solver Documents
solver_documents_total = Gauge(
    "thoth_solver_documents_total", "Number of Solver Documents", []
)
solver_documents_seconds = Summary(
    "thoth_solver_documents_seconds", "Time spent processing requests about Solver Documents to Dgraph Server.", []
)

# Analyzer Documents
analyzer_documents_total = Gauge(
    "thoth_analyzer_documents_total", "Number of Analyzer Documents", [])

analyzer_documents_seconds = Summary(
    "thoth_analyzer_documents_seconds",
    "Time spent processing requests about Analyzer Documents to Dgraph Server.",
    [],
)

# Solver Jobs
solver_jobs_total = Gauge("thoth_solver_jobs_total", "Number of Solver Jobs running.", ["dist", "status"])

solver_jobs_seconds = Gauge(
    "thoth_solver_jobs_seconds", "Time spent processing requests to OpenShift to get Solver Jobs", []
)

# Graph Structure
graphdb_total_vertex_instances = Gauge(
    "thoth_graph_db_total_vertex_instances", "Total number of Vertex Instances in Thoth Knowledge Graph", []
)

graphdb_total_instances_per_vertex = Gauge(
    "thoth_graphdb_total_instances_per_vertex",
    "Total number of Instances for each Vertex in in Thoth Knowledge Graph", ["vertex_label"]
)

# Graph Consistency

# Python Packages Solver Error
graphdb_total_python_packages_with_solver_error = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error",
    "Total numbr of python packages with solver error True", []
)
graphdb_total_python_packages_with_solver_error_unparsable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unparsable",
    "Total numbr of python packages with solver error True and error_unparsable True", []
)

graphdb_total_python_packages_with_solver_error_unsolvable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unsolvable",
    "Total numbr of python packages with solver error True and error_unsolvable True", []
)

# Graph Connection
graphdb_connection_error_status = Gauge(
    "thoth_graphdb_connection_issues", "Connection error status", []
)
