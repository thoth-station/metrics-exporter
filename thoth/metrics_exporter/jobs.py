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


def get_namespaces() -> set:
    """Retrieve namespaces that shall be monitored by metrics-exporter."""
    environment_variables = [
        "THOTH_FRONTEND_NAMESPACE",
        "THOTH_MIDDLETIER_NAMESPACE",
        "THOTH_BACKEND_NAMESPACE",
        "THOTH_AMUN_NAMESPACE",
        "THOTH_AMUN_INSPECTION_NAMESPACE",
    ]
    namespaces = []
    for environment_varibale in environment_variables:
        if os.getenv(environment_varibale):
            namespaces.append(os.getenv(environment_varibale))
        else:
            _LOGGER.warning("Namespace variable not provided for %r", environment_varibale)
    return set(namespaces)


def count_graph_sync_job_status(job_list_items: list) -> dict:
    """Count the number of created, active, failed, succeeded, pending graph-sync Jobs."""
    graph_sync_jobs_status = {}
    graph_sync_job_status = ["created", "active", "failed", "succeeded", "pending", "retry", "waiting", "started"]
    graph_sync_job_types = [
        "solver",
        "adviser",
        "provenance-checker",
        "inspection",
        "package-extract",
        "dependency-monkey",
    ]

    # Initialize
    for graph_sync_job_type in graph_sync_job_types:
        graph_sync_jobs_status[f"graph-sync-{graph_sync_job_type}"] = {}
        for job_s in graph_sync_job_status:
            graph_sync_jobs_status[f"graph-sync-{graph_sync_job_type}"][job_s] = 0

    for item in job_list_items:
        for graph_sync_job_type in graph_sync_job_types:
            if graph_sync_job_type in item["metadata"]["name"]:
                job_type = f"graph-sync-{graph_sync_job_type}"
                break

        graph_sync_jobs_status[job_type]["created"] += 1

        if "succeeded" in item["status"].keys():
            graph_sync_jobs_status[job_type]["succeeded"] += 1
        elif "failed" in item["status"].keys():
            graph_sync_jobs_status[job_type]["failed"] += 1
        elif "active" in item["status"].keys():
            graph_sync_jobs_status[job_type]["active"] += 1
        elif "pending" in item["status"].keys():
            graph_sync_jobs_status[job_type]["pending"] += 1
        elif not item["status"].keys():
            graph_sync_jobs_status[job_type]["waiting"] += 1
        elif "startTime" in item["status"].keys() and len(item["status"].keys()) == 1:
            graph_sync_jobs_status[job_type]["started"] += 1
        else:
            try:
                if "BackoffLimitExceeded" in item["status"]["conditions"][0]["reason"]:
                    graph_sync_jobs_status[job_type]["retry"] += 1
            except Exception as excptn:
                _LOGGER.error("Unknown job status %r", item)
                _LOGGER.exception(excptn)
    return graph_sync_jobs_status


def get_thoth_graph_sync_jobs():
    """Get the total number of graph-sync Jobs per category with corresponding status."""
    namespaces = get_namespaces()

    openshift = OpenShift()
    for namespace in namespaces:
        _LOGGER.info("Evaluating jobs metrics for Thoth namespace: %r", namespace)
        response = openshift.get_jobs(label_selector="component=graph-sync", namespace=namespace)

        jobs_status = count_graph_sync_job_status(response["items"])
        for j_type, j_statuses in jobs_status.items():
            for j_status, j_counts in j_statuses.items():
                metrics.jobs_sync_status.labels(j_type, j_status, namespace).set(j_counts)
        _LOGGER.debug("thoth_graph_sync_jobs=%r", jobs_status)


def count_configmaps(config_map_list_items: list) -> int:
    """Count the number of ConfigMaps for a certain label in a specific namespace."""
    return len(config_map_list_items["items"])


def get_configmaps_per_namespace_per_label():
    """Get the total number of configmaps in the namespace based on labels."""
    namespaces = get_namespaces()

    openshift = OpenShift()
    labels = ["operator=workload", "operator=graph-sync", "component=graph-sync", "component=solver"]
    for namespace in namespaces:
        _LOGGER.info("Evaluating configmaps metrics for Thoth namespace: %r", namespace)

        for label in labels:
            config_maps_items = openshift.get_configmaps(namespace=namespace, label_selector=label)
            number_configmaps = count_configmaps(config_maps_items)
            metrics.config_maps_number.labels(namespace, label).set(number_configmaps)
            _LOGGER.debug(
                "thoth_config_maps_number=%r, in namespace=%r for label=%r", number_configmaps, namespace, label
            )


def get_ceph_results_per_type():
    """Get the total number of results in Ceph per type."""
    for store in _MONITORED_STORES:
        try:
            if not store.is_connected():
                store.connect()
            all_document_ids = store.get_document_listing()
            list_ids = [str(cid) for cid in all_document_ids]
            metrics.ceph_results_number.labels(store.RESULT_TYPE).set(len(list_ids))
            metrics.ceph_connection_error_status.set(0)

            _LOGGER.debug("ceph_connection_error_status=%r", 0)
            _LOGGER.debug(f"ceph_results_number for {store.RESULT_TYPE} ={len(list_ids)}")

        except Exception as excptn:
            metrics.ceph_connection_error_status.set(1)
            _LOGGER.exception(excptn)


def get_tot_nodes_count():
    """Get the total number of Nodes stored in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        v_total = graph_db.get_number_of_each_vertex_in_graph()
        metrics.graphdb_total_nodes_instances.set(sum([count_vertex for count_vertex in v_total.values()]))
        metrics.graphdb_connection_error_status.set(0)

        _LOGGER.debug("graphdb_connection_error_status=%r", 0)
        _LOGGER.debug("graphdb_total_nodes_instances=%r", sum([count_vertex for count_vertex in v_total.values()]))

    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


def get_tot_nodes_for_each_entity_count():
    """Get the total number of Nodes for each Entity in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        v_instances_total = graph_db.get_number_of_each_vertex_in_graph()

        for v_label, v_instances_count in v_instances_total.items():
            metrics.graphdb_total_instances_per_node.labels(v_label).set(v_instances_count)

        metrics.graphdb_connection_error_status.set(0)
        _LOGGER.debug("graphdb_connection_error_status=%r", 0)

        _LOGGER.debug("graphdb_total_instances_per_node=%r", v_instances_total)

    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


def get_python_packages_solver_error_count():
    """Get the total number of python packages with solver error True and how many are unparsable or unsolvable."""
    try:
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

        metrics.graphdb_connection_error_status.set(0)
        _LOGGER.debug("graphdb_connection_error_status=%r", 0)

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
    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


def get_unique_python_packages_count():
    """Get the total number of unique python packages in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        total_unique_python_packages = len(graph_db.get_python_packages())
        metrics.graphdb_total_unique_python_packages.set(total_unique_python_packages)

        metrics.graphdb_connection_error_status.set(0)
        _LOGGER.debug("graphdb_connection_error_status=%r", 0)

        _LOGGER.debug("graphdb_total_unique_python_packages=%r", len(graph_db.get_python_packages()))

    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


def get_unique_run_software_environment_count():
    """Get the total number of unique software environment for run in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_run_software_environment = len(set(graph_db.run_software_environment_listing()))
        metrics.graphdb_total_run_software_environment.set(thoth_graphdb_total_run_software_environment)

        metrics.graphdb_connection_error_status.set(0)
        _LOGGER.debug("graphdb_connection_error_status=%r", 0)

        _LOGGER.debug("graphdb_total_unique_run_software_environment=%r", thoth_graphdb_total_run_software_environment)

    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


def get_user_unique_run_software_environment_count():
    """Get the total number of users unique software environment for run in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_user_run_software_environment = len(
            set(graph_db.run_software_environment_listing(is_user_run=True))
        )

        metrics.graphdb_total_user_run_software_environment.set(thoth_graphdb_total_user_run_software_environment)

        metrics.graphdb_connection_error_status.set(0)
        _LOGGER.debug("graphdb_connection_error_status=%r", 0)

        _LOGGER.debug(
            "graphdb_total_unique_user_run_software_environment=%r", thoth_graphdb_total_user_run_software_environment
        )

    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


def get_unique_build_software_environment_count():
    """Get the total number of unique software environment for build in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_build_software_environment = len(set(graph_db.build_software_environment_listing()))

        metrics.graphdb_total_build_software_environment.set(thoth_graphdb_total_build_software_environment)

        metrics.graphdb_connection_error_status.set(0)
        _LOGGER.debug("graphdb_connection_error_status=%r", 0)

        _LOGGER.debug(
            "graphdb_total_unique_build_software_environment=%r", thoth_graphdb_total_build_software_environment
        )

    except Exception as excptn:
        metrics.graphdb_connection_error_status.set(1)
        _LOGGER.exception(excptn)


ALL_REGISTERED_JOBS = frozenset(
    (
        get_thoth_graph_sync_jobs,
        get_configmaps_per_namespace_per_label,
        get_ceph_results_per_type,
        get_tot_nodes_count,
        get_tot_nodes_for_each_entity_count,
        get_python_packages_solver_error_count,
        get_unique_python_packages_count,
        get_unique_run_software_environment_count,
        get_user_unique_run_software_environment_count,
        get_unique_build_software_environment_count,
    )
)
