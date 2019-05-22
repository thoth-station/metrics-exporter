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

"""This is a Promotheus exporter for Thoth."""


import os
import asyncio
import aiohttp
import logging

from datetime import datetime
from itertools import chain

import requests

from openshift.dynamic.exceptions import ResourceNotFoundError

from thoth.storages import GraphDatabase
from thoth.common import init_logging
from thoth.common import OpenShift
from thoth.metrics_exporter import *


init_logging()

_LOGGER = logging.getLogger("thoth.metrics_exporter.jobs")


def countGraphSyncJobStatus(JobListItems: dict) -> (int, int, int):
    """Count the number of created, active, failed, succeeded, pending graph-sync Jobs."""
    graph_sync_jobs_status = {}
    graph_sync_job_status = ["created", "active", "failed", "succeeded", "pending"]
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

    for item in JobListItems:
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
        else:
            graph_sync_jobs_status[job_type]["pending"] += 1

    return graph_sync_jobs_status


def get_thoth_graph_sync_jobs():
    """Get the total number of graph-sync Jobs per category with corresponding status."""
    namespace = os.getenv("MY_NAMESPACE")
    openshift = OpenShift()
    response = openshift.get_jobs(label_selector="component=graph-sync", namespace=namespace)

    jobs_status = countGraphSyncJobStatus(response["items"])
    for j_type, j_statuses in jobs_status.items():
        for j_status, j_counts in j_statuses.items():
            jobs_sync_status.labels(j_type, j_status).set(j_counts)

    _LOGGER.debug("thoth_graph_sync_jobs=%r", jobs_status)


def get_tot_nodes_count():
    """Get the total number of Nodes stored in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        v_total = graph_db.get_number_of_each_vertex_in_graph()

        graphdb_total_nodes_instances.set(sum([count_vertex for count_vertex in v_total.values()]))

        _LOGGER.debug("graphdb_total_nodes_instances=%r", sum([count_vertex for count_vertex in v_total.values()]))

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_tot_nodes_for_each_entity_count():
    """Get the total number of Nodes for each Entity in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        v_instances_total = graph_db.get_number_of_each_vertex_in_graph()

        for v_label, v_instances_count in v_instances_total.items():
            graphdb_total_instances_per_node.labels(v_label).set(v_instances_count)

        _LOGGER.debug("graphdb_total_instances_per_node=%r", v_instances_total)

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_python_packages_solver_error_count():
    """Get the total number of python packages with solver error True and how many are unparsable or unsolvable."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        total_python_packages_with_solver_error_unparsable = graph_db.get_error_python_packages_count(unparseable=True)
        total_python_packages_with_solver_error_unsolvable = graph_db.get_error_python_packages_count(unsolvable=True)

        graphdb_total_python_packages_with_solver_error_unparsable.set(
            total_python_packages_with_solver_error_unparsable
        )
        graphdb_total_python_packages_with_solver_error_unsolvable.set(
            total_python_packages_with_solver_error_unsolvable
        )
        graphdb_total_python_packages_with_solver_error.set(
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
    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_unique_python_packages_count():
    """Get the total number of unique python packages in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        total_unique_python_packages = len(graph_db.get_python_packages())

        graphdb_total_unique_python_packages.set(total_unique_python_packages)

        _LOGGER.debug("graphdb_total_unique_python_packages=%r", len(graph_db.get_python_packages()))

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_unique_run_software_environment_count():
    """Get the total number of unique software environment for run in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_run_software_environment = len(set(graph_db.run_software_environment_listing()))

        graphdb_total_run_software_environment.set(thoth_graphdb_total_run_software_environment)

        _LOGGER.debug("graphdb_total_unique_run_software_environment=%r", thoth_graphdb_total_run_software_environment)

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_user_unique_run_software_environment_count():
    """Get the total number of users unique software environment for run in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_user_run_software_environment = len(
            set(graph_db.run_software_environment_listing(is_user_run=True))
        )

        graphdb_total_user_run_software_environment.set(thoth_graphdb_total_user_run_software_environment)

        _LOGGER.debug(
            "graphdb_total_unique_user_run_software_environment=%r", thoth_graphdb_total_user_run_software_environment
        )

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_unique_build_software_environment_count():
    """Get the total number of unique software environment for build in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        thoth_graphdb_total_build_software_environment = len(set(graph_db.build_software_environment_listing()))

        graphdb_total_build_software_environment.set(thoth_graphdb_total_build_software_environment)

        _LOGGER.debug(
            "graphdb_total_unique_build_software_environment=%r", thoth_graphdb_total_build_software_environment
        )

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)
