#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019 Christoph Görn, Francesco Murdaca
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

"""This is a Prometheus exporter for Thoth."""

import os
import logging
from functools import wraps
from typing import Set
from typing import Callable

from thoth.storages import GraphDatabase
from thoth.storages import SolverResultsStore
from thoth.storages import AdvisersResultsStore
from thoth.storages import AnalysisResultsStore
from thoth.storages import InspectionResultsStore
from thoth.storages import PackageAnalysisResultsStore
from thoth.storages import ProvenanceResultsStore
from thoth.storages import DependencyMonkeyReportsStore
from thoth.storages.exception import DatabaseNotInitialized
from thoth.common import init_logging
from thoth.common import OpenShift
import thoth.metrics_exporter.metrics as metrics


init_logging()

_LOGGER = logging.getLogger(__name__)

# Registered jobs run by metrics-exporter periodically.
REGISTERED_JOBS = []


def register_metric_job(method: Callable) -> Callable:
    """A decorator for adding a metric job."""
    global REGISTERED_JOBS
    REGISTERED_JOBS.append(method)

    @wraps(method)
    def wrapper(*args, **kwargs):
        return method(*args, **kwargs)

    return wrapper


_NAMESPACES_VARIABLES = [
    "THOTH_FRONTEND_NAMESPACE",
    "THOTH_MIDDLETIER_NAMESPACE",
    "THOTH_BACKEND_NAMESPACE",
    "THOTH_AMUN_NAMESPACE",
    "THOTH_AMUN_INSPECTION_NAMESPACE",
]


class MetricsBase:
    """A base class for grouping metrics."""

    def __init__(self):
        """Do not instantiate this class."""
        raise NotImplemented


class OpenshiftMetrics(MetricsBase):
    """Class to evaluate Metrics for OpenShift."""

    _OPENSHIFT = OpenShift()

    _JOBS_LABELS = [
        "component=dependency-monkey",
        "component=amun-inspection-job",
        "component=solver",
        "component=package-extract",
        "component=package-analyzer",
        "component=provenance-checker",
        "component=adviser",
        "graph-sync-type=adviser",
        "graph-sync-type=dependency-monkey",
        "graph-sync-type=inspection",
        "graph-sync-type=package-analyzer",
        "graph-sync-type=package-extract",
        "graph-sync-type=provenance-checker",
        "graph-sync-type=solver",
    ]

    @staticmethod
    def get_namespaces() -> Set[str]:
        """Retrieve namespaces that shall be monitored by metrics-exporter."""
        namespaces = []
        for environment_varibale in _NAMESPACES_VARIABLES:
            if os.getenv(environment_varibale):
                namespaces.append(os.getenv(environment_varibale))
            else:
                _LOGGER.warning("Namespace variable not provided for %r", environment_varibale)
        return set(namespaces)

    @classmethod
    @register_metric_job
    def get_thoth_jobs_per_label(cls) -> None:
        """Get the total number of Jobs per label with corresponding status."""
        namespaces = cls.get_namespaces()

        for label_selector in cls._JOBS_LABELS:
            for namespace in namespaces:
                _LOGGER.info("Evaluating jobs(label_selector=%r) metrics for namespace: %r", label_selector, namespace)
                jobs_status_evaluated = cls._OPENSHIFT.get_job_status_count(
                    label_selector=label_selector, namespace=namespace
                )

                for j_status, j_counts in jobs_status_evaluated.items():
                    metrics.jobs_status.labels(label_selector, j_status, namespace).set(j_counts)

                _LOGGER.debug("thoth_jobs=%r", jobs_status_evaluated)

    @staticmethod
    def count_configmaps(config_map_list_items: dict) -> int:
        """Count the number of ConfigMaps for a certain label in a specific namespace."""
        return len(config_map_list_items["items"])

    @classmethod
    @register_metric_job
    def get_configmaps_per_namespace_per_label(cls) -> None:
        """Get the total number of configmaps in the namespace based on labels."""
        namespaces = cls.get_namespaces()

        for namespace in namespaces:

            for label in cls._JOBS_LABELS + ["operator=graph-sync", "operator=workload"]:
                _LOGGER.info("Evaluating ConfigMaps(label_selector=%r) metrics for namespace: %r", label, namespace)
                config_maps_items = cls._OPENSHIFT.get_configmaps(namespace=namespace, label_selector=label)
                number_configmaps = cls.count_configmaps(config_maps_items)
                metrics.config_maps_number.labels(namespace, label).set(number_configmaps)
                _LOGGER.debug(
                    "thoth_config_maps_number=%r, in namespace=%r for label=%r", number_configmaps, namespace, label
                )


class CephMetrics(MetricsBase):
    """Class to evaluate Metrics for Ceph."""

    _MONITORED_STORES = (
        AdvisersResultsStore(),
        AnalysisResultsStore(),
        InspectionResultsStore(),
        ProvenanceResultsStore(),
        PackageAnalysisResultsStore(),
        SolverResultsStore(),
        DependencyMonkeyReportsStore(),
    )

    @classmethod
    @register_metric_job
    def get_ceph_results_per_type(cls) -> None:
        """Get the total number of results in Ceph per type."""
        for store in cls._MONITORED_STORES:
            _LOGGER.info("Check Ceph content for %s", store.RESULT_TYPE)
            if not store.is_connected():
                store.connect()
            all_document_ids = store.get_document_listing()
            list_ids = [str(cid) for cid in all_document_ids]
            metrics.ceph_results_number.labels(store.RESULT_TYPE).set(len(list_ids))
            _LOGGER.debug("ceph_results_number for %s =%d", store.RESULT_TYPE, len(list_ids))

    @staticmethod
    @register_metric_job
    def get_ceph_connection_error_status() -> None:
        """Check connection to Ceph instance."""
        inspections = InspectionResultsStore()
        try:
            inspections.connect()
        except Exception as excptn:
            metrics.ceph_connection_error_status.set(1)
            _LOGGER.exception(excptn)
        else:
            metrics.ceph_connection_error_status.set(0)


class DBMetrics(MetricsBase):
    """Class to evaluate Metrics for Thoth Database."""

    @staticmethod
    @register_metric_job
    def get_graphdb_connection_error_status() -> None:
        """Raise a flag if there is an error connecting to database."""
        graph_db = GraphDatabase()
        try:
            graph_db.connect()
        except Exception as excptn:
            metrics.graphdb_connection_error_status.set(1)
            _LOGGER.exception(excptn)
        else:
            metrics.graphdb_connection_error_status.set(0)

    @staticmethod
    @register_metric_job
    def get_tot_records_count() -> None:
        """Get the total number of Records in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        main_models_record_count = sum(graph_db.get_number_main_tables_records().values())
        relation_models_record_count = sum(graph_db.get_number_relation_tables_records().values())
        performance_models_record_count = sum(graph_db.get_number_performance_tables_records().values())

        total_records_count = main_models_record_count + relation_models_record_count + performance_models_record_count
        metrics.graphdb_total_records.set(total_records_count)

        _LOGGER.debug("thoth_graphdb_total_records=%r", total_records_count)

    @staticmethod
    @register_metric_job
    def get_tot_main_records_count() -> None:
        """Get the total number of Records for Main Tables in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        main_models_records = graph_db.get_number_main_tables_records()

        for main_table, main_table_records_count in main_models_records.items():
            metrics.graphdb_total_main_records.labels(main_table).set(main_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_main_records=%r", main_models_records)

    @staticmethod
    @register_metric_job
    def get_tot_relation_records_count() -> None:
        """Get the total number of Records for Relation Tables in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        relation_models_records = graph_db.get_number_relation_tables_records()

        for relation_table, relation_table_records_count in relation_models_records.items():
            metrics.graphdb_total_relation_records.labels(relation_table).set(relation_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_relation_records=%r", relation_models_records)

    @staticmethod
    @register_metric_job
    def get_is_schema_up2date() -> None:
        """Check if the schema running on metrics-exporter is same as the schema present in the database."""
        graph_db = GraphDatabase()
        graph_db.connect()
        try:
            metrics.graphdb_is_schema_up2date.set(int(graph_db.is_schema_up2date()))
        except DatabaseNotInitialized as exc:
            _LOGGER.warning("Database schema is not initialized yet: %s", str(exc))
            metrics.graphdb_is_schema_up2date.set(0)


class ExternalInformation(MetricsBase):
    """Class to discover information from Users."""

    @staticmethod
    @register_metric_job
    def get_user_python_software_stack_count() -> None:
        """Get the total number of User Python Software Stacks in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_software_stacks = graph_db.python_software_stack_count(software_stack_type="USER")
        metrics.graphdb_user_software_stacks_records.set(thoth_graphdb_total_software_stacks)
        _LOGGER.debug("graphdb_user_software_stacks_records=%r", thoth_graphdb_total_software_stacks)

    @staticmethod
    @register_metric_job
    def get_user_unique_run_software_environment_count() -> None:
        """Get the total number of users unique software environment for run in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_user_run_software_environment = len(
            set(graph_db.run_software_environment_listing(is_external_run=True))
        )

        metrics.graphdb_total_user_run_software_environment.set(thoth_graphdb_total_user_run_software_environment)
        _LOGGER.debug(
            "graphdb_total_unique_user_run_software_environment=%r", thoth_graphdb_total_user_run_software_environment
        )


class PythonPackagesMetrics(MetricsBase):
    """Class to discover Content for PythonPackages inside Thoth database."""

    @staticmethod
    @register_metric_job
    def get_python_packages_versions_count() -> None:
        """Get the total number of Python packages versions in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        number_python_package_versions = graph_db.get_python_package_versions_count_all()
        metrics.graphdb_number_python_package_versions.set(number_python_package_versions)
        _LOGGER.debug("graphdb_number_python_package_versions=%r", number_python_package_versions)

    @staticmethod
    @register_metric_job
    def get_number_python_index_urls() -> None:
        """Get the total number of python indexes in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        python_urls_count = len(graph_db.get_python_package_index_urls())
        metrics.graphdb_total_python_indexes.set(python_urls_count)
        _LOGGER.debug("thoth_graphdb_total_python_indexes=%r", python_urls_count)

    @staticmethod
    @register_metric_job
    def get_python_packages_per_index_urls_count() -> None:
        """Get the total number of unique python packages per index URL in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        python_urls_list = list(graph_db.get_python_package_index_urls())
        tot_packages = 0
        for index_url in python_urls_list:

            packages_count = len(graph_db.get_python_packages_per_index(index_url=index_url)[index_url])
            tot_packages += packages_count

            metrics.graphdb_total_python_packages_per_indexes.labels(index_url).set(packages_count)
            _LOGGER.debug("thoth_graphdb_total_python_packages_per_indexes(%r)=%r", index_url, packages_count)

        metrics.graphdb_sum_python_packages_per_indexes.set(tot_packages)
        _LOGGER.debug("thoth_graphdb_sum_python_packages_per_indexes=%r", tot_packages)


class PIMetrics(MetricsBase):
    """Class to discover Content for Performance Indicators inside Thoth database."""

    _ML_FRAMEWORKS = ["tensorflow"]

    @classmethod
    @register_metric_job
    def get_observations_count_per_framework(cls) -> None:
        """Get the total number of PI per framework in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()
        thoth_number_of_pi_per_type = {}

        for framework in cls._ML_FRAMEWORKS:
            thoth_number_of_pi_per_type[framework] = graph_db.get_all_pi_per_framework_count(framework=framework)

            for pi, pi_count in thoth_number_of_pi_per_type[framework].items():
                metrics.graphdb_total_number_of_pi_per_framework.labels(framework, pi).set(pi_count)

        _LOGGER.debug("graphdb_total_number_of_pi_per_framework=%r", thoth_number_of_pi_per_type)

    @staticmethod
    @register_metric_job
    def get_tot_performance_records_count() -> None:
        """Get the total number of Records for Performance tables in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        performance_models_records = graph_db.get_number_performance_tables_records()

        for performance_table, performance_table_records_count in performance_models_records.items():
            metrics.graphdb_total_performance_records.labels(performance_table).set(performance_table_records_count)

        _LOGGER.debug("thoth_graphdb_total_performance_records=%r", performance_models_records)


class SoftwareEnvironmentMetrics(MetricsBase):
    """Class to discover Content for Software Environment (Build and Run) inside Thoth database."""

    @staticmethod
    @register_metric_job
    def get_unique_run_software_environment_count() -> None:
        """Get the total number of unique software environment for run in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_run_software_environment = len(set(graph_db.run_software_environment_listing()))
        metrics.graphdb_total_run_software_environment.set(thoth_graphdb_total_run_software_environment)
        _LOGGER.debug("graphdb_total_unique_run_software_environment=%r", thoth_graphdb_total_run_software_environment)

    @staticmethod
    @register_metric_job
    def get_unique_build_software_environment_count() -> None:
        """Get the total number of unique software environment for build in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_build_software_environment = len(set(graph_db.build_software_environment_listing()))

        metrics.graphdb_total_build_software_environment.set(thoth_graphdb_total_build_software_environment)
        _LOGGER.debug(
            "graphdb_total_unique_build_software_environment=%r", thoth_graphdb_total_build_software_environment
        )


class AdviserMetrics(MetricsBase):
    """Class to evaluate Metrics for Adviser."""

    @staticmethod
    @register_metric_job
    def get_advised_python_software_stack_count() -> None:
        """Get the total number of Advised Python Software Stacks in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_advised_software_stacks = graph_db.python_software_stack_count(
            software_stack_type="ADVISED"
        )
        metrics.graphdb_advised_software_stacks_records.set(thoth_graphdb_total_advised_software_stacks)
        _LOGGER.debug("graphdb_advised_software_stacks_records=%r", thoth_graphdb_total_advised_software_stacks)


class InspectionMetrics(MetricsBase):
    """Class to evaluate Metrics for Amun Inspections."""

    @staticmethod
    @register_metric_job
    def get_inspection_results_per_identifier() -> None:
        """Get the total number of inspections in Ceph per identifier."""
        store = InspectionResultsStore()
        if not store.is_connected():
            store.connect()

        specific_list_ids = {"without_identifier": 0}
        for ids in store.get_document_listing():
            inspection_filter = "_".join(ids.split("-")[1:(len(ids.split("-")) - 1)])
            if inspection_filter:
                if inspection_filter not in specific_list_ids.keys():
                    specific_list_ids[inspection_filter] = 1
                else:
                    specific_list_ids[inspection_filter] += 1
            else:
                specific_list_ids["without_identifier"] += 1

        for identifier, identifier_list in specific_list_ids.items():
            metrics.inspection_results_ceph.labels(identifier).set(identifier_list)
            _LOGGER.debug(f"inspection_results_ceph for {identifier} ={identifier_list}")

    @staticmethod
    @register_metric_job
    def get_inspection_python_software_stack_count() -> None:
        """Get the total number of Inspection Python Software Stacks in Thoth Knowledge Graph."""
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_inspection_software_stacks = graph_db.python_software_stack_count(
            software_stack_type="INSPECTION"
        )
        metrics.graphdb_inspection_software_stacks_records.set(thoth_graphdb_total_inspection_software_stacks)
        _LOGGER.debug("graphdb_inspection_software_stacks_records=%r", thoth_graphdb_total_inspection_software_stacks)


class PackageAnalyzerMetrics(MetricsBase):
    """Class to evaluate Metrics for Package Analyzer."""

    @staticmethod
    @register_metric_job
    def get_analyzed_python_packages_count() -> None:
        """Get number of unanlyzed Python packages."""
        graph_db = GraphDatabase()
        graph_db.connect()

        count = graph_db.get_analyzed_python_package_versions_count_all()
        metrics.graphdb_total_number_analyzed_python_packages.set(count)
        _LOGGER.debug("graphdb_total_number_analyzed_python_packages=%r", count)

    @staticmethod
    @register_metric_job
    def get_analyzed_error_python_packages_count() -> None:
        """Get number of unanlyzed Python packages."""
        graph_db = GraphDatabase()
        graph_db.connect()

        count = graph_db.get_analyzed_error_python_package_versions_count_all()
        metrics.graphdb_total_number_analyzed_error_python_packages.set(count)
        _LOGGER.debug("graphdb_total_number_analyzed_error_python_packages=%r", count)

    @staticmethod
    @register_metric_job
    def get_unanalyzed_python_packages_count() -> None:
        """Get number of unanlyzed Python packages."""
        graph_db = GraphDatabase()
        graph_db.connect()

        count = graph_db.get_unanalyzed_python_package_versions_count_all()
        metrics.graphdb_total_number_unanalyzed_python_packages.set(count)
        _LOGGER.debug("graphdb_total_number_unanalyzed_python_packages=%r", count)


class SolverMetrics(MetricsBase):
    """Class to evaluate Metrics for Solvers."""

    _OPENSHIFT = OpenShift()

    @classmethod
    @register_metric_job
    def get_solver_count(cls) -> None:
        """Get number of solvers in Thoth Infra namespace."""
        solvers = len(cls._OPENSHIFT.get_solver_names())

        metrics.graphdb_total_number_solvers.set(solvers)
        _LOGGER.debug("graphdb_total_number_solvers(%r)=%r", solvers)

    @classmethod
    @register_metric_job
    def get_unsolved_python_packages_count(cls) -> None:
        """Get number of unsolved Python packages per solver."""
        graph_db = GraphDatabase()
        graph_db.connect()

        for solver_name in cls._OPENSHIFT.get_solver_names():
            solver_info = graph_db.parse_python_solver_name(solver_name)

            count = graph_db.get_unsolved_python_package_versions_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            metrics.graphdb_total_number_unsolved_python_packages.labels(solver_name).set(count)
            _LOGGER.debug("graphdb_total_number_unsolved_python_packages(%r)=%r", solver_name, count)

    @staticmethod
    @register_metric_job
    def get_python_packages_solver_error_count() -> None:
        """Get the total number of python packages with solver error True and how many are unparsable or unsolvable."""
        graph_db = GraphDatabase()
        graph_db.connect()

        total_python_packages_solver_error = graph_db.get_error_solved_python_package_versions_count_all()
        total_python_packages_solver_error_unparseable = graph_db.get_error_solved_python_package_versions_count_all(
            unparseable=True
        )
        total_python_packages_solver_error_unsolvable = graph_db.get_error_solved_python_package_versions_count_all(
            unsolvable=True
        )

        metrics.graphdb_total_python_packages_with_solver_error_unparseable.set(
            total_python_packages_solver_error_unparseable
        )
        metrics.graphdb_total_python_packages_with_solver_error_unsolvable.set(
            total_python_packages_solver_error_unsolvable
        )
        metrics.graphdb_total_python_packages_with_solver_error.set(total_python_packages_solver_error)

        _LOGGER.debug("graphdb_total_python_packages_with_solver_error=%r", total_python_packages_solver_error)

        _LOGGER.debug(
            "graphdb_total_python_packages_with_solver_error_unparseable=%r",
            total_python_packages_solver_error_unparseable,
        )

        _LOGGER.debug(
            "graphdb_total_python_packages_with_solver_error_unsolvable=%r",
            total_python_packages_solver_error_unsolvable,
        )
