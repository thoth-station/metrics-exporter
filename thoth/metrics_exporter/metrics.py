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

"""All metrics exposed by metrics exporter."""


from thoth.metrics_exporter import __version__
from prometheus_client import Gauge


# Info Metric
metrics_exporter_info = Gauge(
    "thoth_metrics_exporter_info",  # what Prometheus sees
    "Thoth Metrics Exporter information",  # what the human reads
    ["version"],  # what labels I use
)
metrics_exporter_info.labels(__version__).inc()

# SERVICE METRICS
# Solver Jobs
jobs_sync_status = Gauge(
    "thoth_graph_sync_jobs_status", "Graph Sync Jobs status overview.", ["job_type", "job_status", "namespace"]
)

# ConfigMaps
config_maps_number = Gauge(
    "thoth_config_maps_number", "Thoth ConfigMaps per namespace per label.", ["namespace", "label"]
)


# CONTENT METRICS
# Graph Structure
graphdb_total_nodes_instances = Gauge(
    "thoth_graph_db_total_node_instances", "Total number of Nodes in Thoth Knowledge Graph", []
)

graphdb_total_instances_per_node = Gauge(
    "thoth_graphdb_total_instances_per_node",
    "Total number of instances for each Node in Thoth Knowledge Graph",
    ["node_label"],
)

# Graph Content

# Python Packages Solver Error
graphdb_total_python_packages_with_solver_error = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error",
    "Total number of python packages with solver error True",
    [],
)
graphdb_total_python_packages_with_solver_error_unparsable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unparsable",
    "Total number of python packages with solver error True and error_unparsable True",
    [],
)

graphdb_total_python_packages_with_solver_error_unsolvable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unsolvable",
    "Total number of python packages with solver error True and error_unsolvable True",
    [],
)

# Python Packages
graphdb_total_unique_python_packages = Gauge(
    "thoth_graphdb_total_unique_python_packages", "Total number of unique python packages", []
)

# Software environments for run
graphdb_total_run_software_environment = Gauge(
    "thoth_graphdb_total_run_software_environment", "Total number of unique software environment for run", []
)

graphdb_total_user_run_software_environment = Gauge(
    "thoth_graphdb_total_user_run_software_environment", "Total number of users unique software environment for run", []
)

# Software environments for build
graphdb_total_build_software_environment = Gauge(
    "thoth_graphdb_total_build_software_environment", "Total number of unique software environment for build", []
)

# Graph connection availability
graphdb_connection_error_status = Gauge("thoth_graphdb_connection_issues", "Connection error status", [])
