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

# Openshift metrics

# Jobs
jobs_status = Gauge(
    "thoth_jobs_status", "Jobs status overview per label.", ["label_selector", "job_status", "namespace"]
)

config_maps_number = Gauge(
    "thoth_config_maps_number", "Thoth ConfigMaps per namespace per label.", ["namespace", "label"]
)

# Ceph metrics
ceph_results_number = Gauge("thoth_ceph_results_number", "Thoth Ceph result per type.", ["result_type"])

ceph_connection_error_status = Gauge("thoth_ceph_connection_issues", "Ceph Connection error status.", [])

# Thoth Database
graphdb_total_records = Gauge("thoth_graphdb_total_records", "Total number of Records in Thoth Knowledge Graph.", [])

graphdb_total_main_records = Gauge(
    "thoth_graphdb_total_main_records",
    "Total number of Records for main tables in Thoth Knowledge Graph.",
    ["main_table"],
)

graphdb_total_relation_records = Gauge(
    "thoth_graphdb_total_relation_records",
    "Total number of Records for relation tables in Thoth Knowledge Graph.",
    ["relation_table"],
)

graphdb_connection_error_status = Gauge("thoth_graphdb_connection_issues", "Connection error status.", [])

# CONTENT METRICS

# Python Packages
graphdb_number_python_package_versions = Gauge(
    "thoth_graphdb_number_python_package_versions", "Total number of Python package versions.", []
)

graphdb_total_python_indexes = Gauge("thoth_graphdb_total_python_indexes", "Total number of Python indexes.", [])
graphdb_total_python_packages_per_indexes = Gauge(
    "thoth_graphdb_total_python_packages_per_indexes",
    "Total number of unique python packages per index.",
    ["index_url"],
)
graphdb_sum_python_packages_per_indexes = Gauge(
    "thoth_graphdb_sum_python_packages_per_indexes", "Sum of number of Python packages per index.", []
)

# Performance Indicators
graphdb_total_number_of_pi_per_framework = Gauge(
    "thoth_graphdb_total_number_of_pi_per_framework",
    "Total number of Observations for PI per framework.",
    ["framework", "pi"],
)

graphdb_total_performance_records = Gauge(
    "thoth_graphdb_total_performance_records",
    "Total number of Records for performance tables in Thoth Knowledge Graph.",
    ["performance_table"],
)

# External Information
graphdb_user_software_stacks_records = Gauge(
    "thoth_graphdb_user_software_stacks_records", "Thoth User Software Stacks.", []
)

graphdb_total_user_run_software_environment = Gauge(
    "thoth_graphdb_total_user_run_software_environment",
    "Total number of users unique software environment for run.",
    [],
)

# SoftwareEnvironment
graphdb_total_run_software_environment = Gauge(
    "thoth_graphdb_total_run_software_environment", "Total number of unique software environment for run.", []
)

graphdb_total_build_software_environment = Gauge(
    "thoth_graphdb_total_build_software_environment", "Total number of unique software environment for build.", []
)

# AdviserRun
graphdb_advised_software_stacks_records = Gauge(
    "thoth_graphdb_advised_software_stacks_records", "Thoth Advised Software Stacks.", []
)

# InspectionRun
inspection_results_ceph = Gauge(
    "thoth_inspection_results_ceph", "Thoth Inspections result in Ceph per identifier.", ["identifier"]
)

graphdb_inspection_software_stacks_records = Gauge(
    "thoth_graphdb_inspection_software_stacks_records", "Thoth Inspection Software Stacks.", []
)

# PackageAnalyzerRun
graphdb_total_number_analyzed_python_packages = Gauge(
    "thoth_graphdb_total_number_analyzed_python_packages", "Total number of analyzed Python packages.", []
)
graphdb_total_number_analyzed_error_python_packages = Gauge(
    "thoth_graphdb_total_number_analyzed_error_python_packages",
    "Total number of analyzed Python packages with error.",
    []
)
graphdb_total_number_unanalyzed_python_packages = Gauge(
    "thoth_graphdb_total_number_unanalyzed_python_packages", "Total number of unanalyzed Python packages.", []
)

# SolverRun
graphdb_total_number_solvers = Gauge(
    "thoth_graphdb_total_number_solvers",
    "Total number of solvers in Thoth Infra namespace.",
    [],
)
graphdb_total_python_packages_with_solver_error = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error",
    "Total number of python packages with solver error True.",
    [],
)
graphdb_total_python_packages_with_solver_error_unparseable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unparseable",
    "Total number of python packages with solver error True and error_unparseable True.",
    [],
)

graphdb_total_python_packages_with_solver_error_unsolvable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unsolvable",
    "Total number of python packages with solver error True and error_unsolvable True.",
    [],
)

graphdb_total_number_unsolved_python_packages = Gauge(
    "thoth_graphdb_total_number_unsolved_python_packages",
    "Total number of unsolved Python packages per solver.",
    ["solver_name"],
)

graphdb_is_schema_up2date = Gauge(
    "thoth_graphdb_is_schema_up2date",
    "Check whether the schema is up2date with the schema present in metrics-exporter",
    [],
)
