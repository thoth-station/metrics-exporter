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

from thoth.storages import GraphDatabase
from thoth.storages import SolverResultsStore
from thoth.storages import AdvisersResultsStore
from thoth.storages import AnalysisResultsStore
from thoth.storages import InspectionResultsStore
from thoth.storages import PackageAnalysisResultsStore
from thoth.storages import ProvenanceResultsStore
from thoth.storages import DependencyMonkeyReportsStore
from thoth.common import init_logging
from thoth.common import OpenShift
import thoth.metrics_exporter.metrics as metrics


init_logging()

_LOGGER = logging.getLogger(__name__)

_MONITORED_STORES = (
    AdvisersResultsStore(),
    AnalysisResultsStore(),
    InspectionResultsStore(),
    ProvenanceResultsStore(),
    PackageAnalysisResultsStore(),
    SolverResultsStore(),
    DependencyMonkeyReportsStore(),
)

_NAMESPACES_VARIABLES = [
    "THOTH_FRONTEND_NAMESPACE",
    "THOTH_MIDDLETIER_NAMESPACE",
    "THOTH_BACKEND_NAMESPACE",
    "THOTH_AMUN_NAMESPACE",
    "THOTH_AMUN_INSPECTION_NAMESPACE",
]

_JOBS_LABELS = [
    "component=dependency-monkey",
    "component=amun-inspection-job",
    "component=solver",
    "graph-sync-type=adviser",
    "graph-sync-type=dependency-monkey",
    "graph-sync-type=inspection",
    "graph-sync-type=package-analyzer",
    "graph-sync-type=package-extract",
    "graph-sync-type=provenance-checker",
    "graph-sync-type=solver",
]


_OPENSHIFT = OpenShift()


def get_namespaces() -> set:
    """Retrieve namespaces that shall be monitored by metrics-exporter."""
    namespaces = []
    for environment_varibale in _NAMESPACES_VARIABLES:
        if os.getenv(environment_varibale):
            namespaces.append(os.getenv(environment_varibale))
        else:
            _LOGGER.warning("Namespace variable not provided for %r", environment_varibale)
    return set(namespaces)


def get_thoth_jobs_per_label():
    """Get the total number of Jobs per label with corresponding status."""
    namespaces = get_namespaces()

    for label_selector in _JOBS_LABELS:
        for namespace in namespaces:
            _LOGGER.info("Evaluating jobs metrics for Thoth namespace: %r", namespace)
            jobs_status_evaluated = _OPENSHIFT.get_job_status_count(label_selector=label_selector, namespace=namespace)

            for j_status, j_counts in jobs_status_evaluated.items():
                metrics.jobs_status.labels(label_selector, j_status, namespace).set(j_counts)

            _LOGGER.debug("thoth_jobs=%r", jobs_status_evaluated)


def count_configmaps(config_map_list_items: list) -> int:
    """Count the number of ConfigMaps for a certain label in a specific namespace."""
    return len(config_map_list_items["items"])


def get_configmaps_per_namespace_per_label():
    """Get the total number of configmaps in the namespace based on labels."""
    namespaces = get_namespaces()

    _OPENSHIFT = OpenShift()
    labels = ["operator=workload", "operator=graph-sync", "component=graph-sync", "component=solver"]
    for namespace in namespaces:
        _LOGGER.info("Evaluating configmaps metrics for Thoth namespace: %r", namespace)

        for label in labels:
            config_maps_items = _OPENSHIFT.get_configmaps(namespace=namespace, label_selector=label)
            number_configmaps = count_configmaps(config_maps_items)
            metrics.config_maps_number.labels(namespace, label).set(number_configmaps)
            _LOGGER.debug(
                "thoth_config_maps_number=%r, in namespace=%r for label=%r", number_configmaps, namespace, label
            )


def get_ceph_results_per_type():
    """Get the total number of results in Ceph per type."""
    for store in _MONITORED_STORES:
        if not store.is_connected():
            store.connect()
        all_document_ids = store.get_document_listing()
        list_ids = [str(cid) for cid in all_document_ids]
        metrics.ceph_results_number.labels(store.RESULT_TYPE).set(len(list_ids))
        _LOGGER.debug(f"ceph_results_number for {store.RESULT_TYPE} ={len(list_ids)}")


def get_inspection_results_per_identifier():
    """Get the total number of inspections in Ceph per identifier."""
    store = InspectionResultsStore()
    if not store.is_connected():
        store.connect()

    specific_list_ids = {}
    specific_list_ids["without_identifier"] = 0
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


def get_python_packages_solver_error_count():
    """Get the total number of python packages with solver error True and how many are unparsable or unsolvable."""
    graph_db = GraphDatabase()
    graph_db.connect()

    total_python_packages_with_solver_error_unparsable = graph_db.get_error_python_packages_count(unparseable=True)
    total_python_packages_with_solver_error_unsolvable = graph_db.get_error_python_packages_count(unsolvable=True)

    metrics.graphdb_total_python_packages_with_solver_error_unparsable.set(
        total_python_packages_with_solver_error_unparsable
    )
    metrics.graphdb_total_python_packages_with_solver_error_unsolvable.set(
        total_python_packages_with_solver_error_unsolvable
    )
    metrics.graphdb_total_python_packages_with_solver_error.set(
        total_python_packages_with_solver_error_unparsable + total_python_packages_with_solver_error_unsolvable
    )

    _LOGGER.debug(
        "graphdb_total_python_packages_with_solver_error=%r",
        total_python_packages_with_solver_error_unparsable + total_python_packages_with_solver_error_unsolvable,
    )

    _LOGGER.debug(
        "graphdb_total_python_packages_with_solver_error_unparsable=%r",
        total_python_packages_with_solver_error_unparsable,
    )

    _LOGGER.debug(
        "graphdb_total_python_packages_with_solver_error_unsolvable=%r",
        total_python_packages_with_solver_error_unsolvable,
    )


def get_unique_python_packages_count():
    """Get the total number of unique python packages in Thoth Knowledge Graph."""
    graph_db = GraphDatabase()
    graph_db.connect()

    total_unique_python_packages = len(graph_db.get_python_packages())
    metrics.graphdb_total_unique_python_packages.set(total_unique_python_packages)
    _LOGGER.debug("graphdb_total_unique_python_packages=%r", len(graph_db.get_python_packages()))


def get_unsolved_python_packages_count():
    """Get number of unsolved Python packages per solver."""
    graph_db = GraphDatabase()
    graph_db.connect()

    for solver_name in _OPENSHIFT.get_solver_names():
        count = graph_db.retrieve_unsolved_python_packages_count(solver_name)
        metrics.graphdb_total_number_unsolved_python_packages.labels(solver_name).set(count)
        _LOGGER.debug("graphdb_total_number_unsolved_python_packages(%r)=%r", solver_name, count)


def get_unique_run_software_environment_count():
    """Get the total number of unique software environment for run in Thoth Knowledge Graph."""
    graph_db = GraphDatabase()
    graph_db.connect()

    thoth_graphdb_total_run_software_environment = len(set(graph_db.run_software_environment_listing()))
    metrics.graphdb_total_run_software_environment.set(thoth_graphdb_total_run_software_environment)
    _LOGGER.debug("graphdb_total_unique_run_software_environment=%r", thoth_graphdb_total_run_software_environment)


def get_user_unique_run_software_environment_count():
    """Get the total number of users unique software environment for run in Thoth Knowledge Graph."""
    graph_db = GraphDatabase()
    graph_db.connect()

    thoth_graphdb_total_user_run_software_environment = len(
        set(graph_db.run_software_environment_listing(is_user_run=True))
    )

    metrics.graphdb_total_user_run_software_environment.set(thoth_graphdb_total_user_run_software_environment)
    _LOGGER.debug(
        "graphdb_total_unique_user_run_software_environment=%r", thoth_graphdb_total_user_run_software_environment
    )


def get_unique_build_software_environment_count():
    """Get the total number of unique software environment for build in Thoth Knowledge Graph."""
    graph_db = GraphDatabase()
    graph_db.connect()

    thoth_graphdb_total_build_software_environment = len(set(graph_db.build_software_environment_listing()))

    metrics.graphdb_total_build_software_environment.set(thoth_graphdb_total_build_software_environment)
    _LOGGER.debug(
        "graphdb_total_unique_build_software_environment=%r", thoth_graphdb_total_build_software_environment
    )


def get_observations_count_per_framework():
    """Get the total number of PI per framework in Thoth Knowledge Graph."""
    graph_db = GraphDatabase()
    graph_db.connect()
    thoth_number_of_pi_per_type = {}

    frameworks = ["tensorflow"]

    for framework in frameworks:
        thoth_number_of_pi_per_type[framework] = graph_db.get_all_pi_per_framework_count(framework=framework)

        for pi, pi_count in thoth_number_of_pi_per_type[framework].items():
            metrics.graphdb_total_number_of_pi_per_framework.labels(framework, pi).set(pi_count)

    _LOGGER.debug("graphdb_total_number_of_pi_per_framework=%r", thoth_number_of_pi_per_type)


def get_graphdb_connection_error_status():
    """Raise a flag if there is an error connecting to database."""
    graph_db = GraphDatabase()
    try:
        graph_db.connect()
    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)
    else:
        metrics.graphdb_connection_error_status.set(0)


def get_ceph_connection_error_status():
    """Check connection to Ceph instance."""
    inspections = InspectionResultsStore()
    try:
        inspections.connect()
    except Exception as excptn:
        metrics.ceph_connection_error_status.set(1)
        _LOGGER.exception(excptn)
    else:
        metrics.ceph_connection_error_status.set(0)


ALL_REGISTERED_JOBS = frozenset(
    (
        get_thoth_jobs_per_label,
        get_configmaps_per_namespace_per_label,
        get_ceph_results_per_type,
        get_inspection_results_per_identifier,
        get_python_packages_solver_error_count,
        get_unique_python_packages_count,
        get_unique_run_software_environment_count,
        get_unsolved_python_packages_count,
        get_user_unique_run_software_environment_count,
        get_unique_build_software_environment_count,
        get_observations_count_per_framework,
        get_graphdb_connection_error_status,
        get_ceph_connection_error_status(),
    )
)
