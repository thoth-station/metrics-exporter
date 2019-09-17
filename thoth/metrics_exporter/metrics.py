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

# Jobs
jobs_status = Gauge(
    "thoth_jobs_status", "Jobs status overview per label.", ["label_selector", "job_status", "namespace"]
)

# ConfigMaps
config_maps_number = Gauge(
    "thoth_config_maps_number", "Thoth ConfigMaps per namespace per label.", ["namespace", "label"]
)

# Ceph results stored
ceph_results_number = Gauge("thoth_ceph_results_number", "Thoth Ceph result per type.", ["result_type"])

# Inspection results stored in Ceph per identifier
inspection_results_ceph = Gauge(
    "thoth_inspection_results_ceph", "Thoth Inspections result in Ceph per identifier.", ["identifier"]
)

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

# Performance Indicators
graphdb_total_number_of_pi_per_framework = Gauge(
    "thoth_graphdb_total_number_of_pi_per_framework",
    "Total number of Observations for PI per framework",
    ["framework", "pi"],
)

# Unsolved Python packages per solver_name
graphdb_total_number_unsolved_python_packages = Gauge(
    "thoth_graphdb_total_number_unsolved_python_packages",
    "Total number of unsolved Python packages per solver",
    ["solver_name"],
)

# Graph connection availability
graphdb_connection_error_status = Gauge("thoth_graphdb_connection_issues", "Connection error status", [])

# Ceph connection availability
ceph_connection_error_status = Gauge("thoth_ceph_connection_issues", "Connection error status", [])
