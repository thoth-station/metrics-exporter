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

"""All metrics exposed by metrics exporter."""


from thoth.metrics_exporter import __version__
from prometheus_client import Gauge, Counter, Histogram


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

image_streams_maps_number = Gauge(
    "thoth_image_streams_maps_number", "Thoth ImageStreams per namespace per label.", ["namespace", "label"]
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
graphdb_total_number_of_pi_per_component = Gauge(
    "thoth_graphdb_total_number_of_pi_per_component",
    "Total number of Observations for PI per component.",
    ["component", "pi"],
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

workflow_adviser_latency = Histogram(
    "thoth_workflow_adviser_latency",
    "Thoth Qeb-Hwt inner workflow duration in Argo Workflow.",
    [],
    buckets=[120, 240, 360, 480, 600],
)

workflow_qebhwt_latency = Histogram(
    "thoth_workflow_qebhwt_latency",
    "Thoth Qeb-Hwt outer workflow duration in Argo Workflow.",
    [],
    buckets=[20, 40, 60, 80, 100],
)

workflow_adviser_quality = Gauge(
    "thoth_workflow_adviser_quality", "Thoth Qeb-Hwt inner workflow status in Argo Workflow.", ["service", "status"]
)

workflow_qebhwt_quality = Gauge(
    "thoth_workflow_qebhwt_quality", "Thoth Qeb-Hwt outer workflow status in Argo Workflow.", ["service", "status"]
)

# InspectionRun
inspection_results_ceph = Gauge(
    "thoth_inspection_results_ceph", "Thoth Inspections result in Ceph per identifier.", ["identifier"]
)

graphdb_inspection_software_stacks_records = Gauge(
    "thoth_graphdb_inspection_software_stacks_records", "Thoth Inspection Software Stacks.", []
)

workflow_inspection_latency = Histogram(
    "thoth_workflow_inspection_latency",
    "Thoth Inspection duration in Argo Workflow.",
    [],
    buckets=[120, 240, 360, 480, 600],
)

workflow_inspection_quality = Gauge(
    "thoth_workflow_inspection_quality", "Thoth inspection workflows status in Argo Workflow.", ["service", "status"]
)

# PackageAnalyzerRun
graphdb_total_number_analyzed_python_packages = Gauge(
    "thoth_graphdb_total_number_analyzed_python_packages", "Total number of analyzed Python packages.", []
)
graphdb_total_number_analyzed_error_python_packages = Gauge(
    "thoth_graphdb_total_number_analyzed_error_python_packages",
    "Total number of analyzed Python packages with error.",
    [],
)
graphdb_total_number_unanalyzed_python_packages = Gauge(
    "thoth_graphdb_total_number_unanalyzed_python_packages", "Total number of unanalyzed Python packages.", []
)

# SolverRun
graphdb_total_number_solvers = Gauge(
    "thoth_graphdb_total_number_solvers", "Total number of solvers in Thoth Infra namespace.", []
)
graphdb_total_python_packages_solved_with_no_error = Gauge(
    "thoth_graphdb_total_python_packages_with_no_error",
    "Total number of python packages solved with no error.",
    ["solver_name"],
)
graphdb_total_python_packages_with_solver_error = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error",
    "Total number of python packages with solver error True.",
    ["solver_name"],
)
graphdb_total_python_packages_with_solver_error_unparseable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unparseable",
    "Total number of python packages with solver error True and error_unparseable True.",
    ["solver_name"],
)

graphdb_total_python_packages_with_solver_error_unsolvable = Gauge(
    "thoth_graphdb_total_python_packages_with_solver_error_unsolvable",
    "Total number of python packages with solver error True and error_unsolvable True.",
    ["solver_name"],
)
graphdb_total_number_solved_python_packages = Gauge(
    "thoth_graphdb_total_number_solved_python_packages",
    "Total number of solved Python packages per solver.",
    ["solver_name"],
)
graphdb_total_number_unsolved_python_packages_per_solver = Gauge(
    "thoth_graphdb_total_number_unsolved_python_packages_per_solver",
    "Total number of unsolved Python packages per solver.",
    ["solver_name"],
)
graphdb_total_number_unsolved_python_packages = Gauge(
    "thoth_graphdb_total_number_unsolved_python_packages", "Total number of unsolved Python packages.", []
)
graphdb_unsolved_python_package_versions_change = Counter(
    "thoth_graphdb_unsolved_python_package_versions_change", "Unsolved Python package versions change.", []
)

graphdb_is_schema_up2date = Gauge(
    "thoth_graphdb_is_schema_up2date", "Exposing information if database schema is up2date", []
)

workflow_solver_latency = Histogram(
    "thoth_workflow_solver_latency", "Thoth Solver duration in Argo Workflow.", [], buckets=[120, 240, 360, 480, 600]
)
