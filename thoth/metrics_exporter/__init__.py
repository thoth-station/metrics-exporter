#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018 Christoph Görn
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
    "thoth_metrics_exporter_info",  # what promethus ses
    "Thoth Metrics Exporter information",  # what the human reads
    ["version"],  # what labels I use
)
metrics_exporter_info.labels(__version__).inc()

# PackageVersion
package_version_total = Gauge(
    "thoth_package_version_total",
    "Number of PackageVersion Vertices per Ecosystem, Solver and State",
    ["ecosystem", "solver", "state"],
)
package_version_seconds = Summary(
    "thoth_package_version_seconds", "Time spent processing requests about PackageVersion to JanusGraph Server.", []
)

# Solver Documents
solver_documents_total = Gauge(
    "thoth_solver_documents_total", "Number of Solver Documents", ["ecosystem", "solver", "state"]
)
solver_documents_seconds = Summary(
    "thoth_solver_documents_seconds", "Time spent processing requests about Solver Documents to JanusGraph Server.", []
)

# Analyzer Documents
analyzer_documents_total = Gauge("thoth_analyzer_documents_total", "Number of Analyzer Documents", [])
analyzer_documents_seconds = Summary(
    "thoth_analyzer_documents_seconds",
    "Time spent processing requests about Analyzer Documents to JanusGraph Server.",
    [],
)

# Solver Jobs
solver_jobs_total = Gauge("thoth_solver_jobs_total", "Number of Solver Jobs running.", ["dist", "status"])

solver_jobs_seconds = Gauge(
    "thoth_solver_jobs_seconds", "Time spent processing requests to OpenShift to get Solver Jobs", []
)

graphdatabase_vertex_total = Gauge(
    "thoth_graphdatabase_vertex_total", "Total number of Vertices in JanusGraph Database", []
)
graphdatabase_edge_total = Gauge("thoth_graphdatabase_edge_total", "Total number of Edges in JanusGraph Database", [])
