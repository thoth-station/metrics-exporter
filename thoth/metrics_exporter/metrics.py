#!/usr/bin/env python3
# thoth-metrics-exporter
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


from thoth.metrics_exporter import __service_version__
from prometheus_client import Gauge, Counter


# Info Metric
metrics_exporter_info = Gauge(
    "thoth_metrics_exporter_info",  # what Prometheus sees
    "Thoth Metrics Exporter information",  # what the human reads
    ["version"],  # what labels I use
)
metrics_exporter_info.labels(__service_version__).inc()

# SERVICE METRICS

# Argo metrics

# Workflows
workflows_status = Gauge(
    "thoth_workflows_status",
    "Argo Workflows status overview per label.",
    ["label_selector", "workflow_status", "namespace"],
)

# Workflows Tasks
workflow_task_status = Gauge(
    "thoth_workflow_task_status",
    "Argo Workflows Tasks status overview per label.",
    ["label_selector", "task", "task_status", "namespace"],
)

# Ceph metrics
ceph_connection_error_status = Gauge("thoth_ceph_connection_issues", "Ceph Connection error status.", [])

# PyPI Database
pypi_stats = Gauge("thoth_pypi_stats", "Statistics collected from PyPI.", ["stats_type"])

# Thoth Database
graphdb_performance_table_total_records = Gauge(
    "thoth_graphdb_performance_table_total_records",
    "Total number of Records for Performance Tables in Thoth Knowledge Graph.",
    [],
)

graphdb_pct_bloat_data_table = Gauge(
    "thoth_graphdb_pct_bloat_data_table", "Bloat data (pct_bloat) per table in Thoth Knowledge Graph.", ["table_name"]
)

graphdb_mb_bloat_data_table = Gauge(
    "thoth_graphdb_mb_bloat_data_table", "Bloat data (mb_bloat) per table in Thoth Knowledge Graph.", ["table_name"]
)

graphdb_last_evaluation_bloat_data = Gauge("thoth_graphdb_last_evaluation_bloat_data", "Connection error status.", [])

graphdb_connection_error_status = Gauge("thoth_graphdb_connection_issues", "Connection error status.", [])

graphdb_is_corrupted = Gauge("thoth_graphdb_is_corrupted", "amcheck has detected corruption.", [])

database_schema_revision_script = Gauge(
    "thoth_database_schema_revision_script",
    "Thoth database schema revision from script.",
    ["component", "revision", "env"],
)

database_schema_revision_table = Gauge(
    "thoth_database_schema_revision_table",
    "Thoth database schema revision from database table.",
    ["component", "revision", "env"],
)

graph_db_component_revision_check = Gauge(
    "thoth_graph_db_component_revision_check",
    "Component script and database head revision check.",
    ["component", "env"],
)


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

graphdb_adviser_count_per_source_type = Gauge(
    "thoth_graphdb_adviser_count_per_source_type", "Thoth Adviser Runs per Thoth Integration.", ["thoth_integration"]
)

graphdb_users_count_per_source_type = Gauge(
    "thoth_graphdb_users_count_per_source_type", "Thoth Users per Thoth Integration.", ["thoth_integration"]
)


# InspectionRun
graphdb_inspection_software_stacks_records = Gauge(
    "thoth_graphdb_inspection_software_stacks_records", "Thoth Inspection Software Stacks.", []
)

# Security
graphdb_total_number_si_analyzed_python_packages = Gauge(
    "thoth_graphdb_total_number_si_analyzed_python_packages", "Total number of SI analyzed Python packages.", []
)
graphdb_total_number_si_unanalyzed_python_packages = Gauge(
    "thoth_graphdb_total_number_si_unanalyzed_python_packages", "Total number of SI unanalyzed Python packages.", []
)
graphdb_si_unanalyzed_python_package_versions_change = Counter(
    "thoth_graphdb_si_unanalyzed_python_package_versions_change", "SI unanalyzed Python package versions change.", []
)
graphdb_total_number_si_not_analyzable_python_packages = Gauge(
    "thoth_graphdb_total_number_si_not_analyzable_python_packages", "SI not analyzable Python package.", []
)


# SolverRun
graphdb_total_number_solvers = Gauge(
    "thoth_graphdb_total_number_solvers", "Total number of solvers  of solvers from Thoth Solver ConfigMap.", []
)
graphdb_total_number_solvers_database = Gauge(
    "thoth_graphdb_total_number_solvers_database", "Total number of solvers from database table.", []
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

# Kebechet Metrics
kebechet_total_active_repo_count = Gauge(
    "thoth_kebechet_total_active_repo_count", "Count of number of repo's supported by Kebechet.", []
)
