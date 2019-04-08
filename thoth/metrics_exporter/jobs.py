#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019 Christoph Görn
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


@package_version_seconds.time()
def get_retrieve_unsolved_pypi_packages():
    """Get the total number of unsolved pypi packages in the graph database."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        graph = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
        graph.connect()

        package_version_total.labels(ecosystem="pypi", solver="f27", status="unsolved").set(
            len(list(chain(*graph.retrieve_unsolved_pypi_packages().values())))
        )
    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        _LOGGER.error(excptn)


def countJobStatus(JobListItems: dict) -> (int, int, int):
    """Count the number of created, failed and succeeded Solver Jobs."""
    created = 0
    failed = 0
    succeeded = 0

    for item in JobListItems:
        created = created + 1

        try:
            if "succeeded" in item["status"].keys():
                succeeded = succeeded + 1
            if "failed" in item["status"].keys():
                failed = failed + 1
        except KeyError as excptn:
            pass

    return (created, failed, succeeded)


@solver_jobs_seconds.time()
def get_thoth_solver_jobs(namespace: str = None):
    """Get the total number Solver Jobs."""
    if namespace is None:
        namespace = os.getenv("MY_NAMESPACE")

    endpoint = "{}/namespaces/{}/jobs".format(
        "https://paas.upshift.redhat.com:443/apis/batch/v1", namespace
    )  # FIXME the OpenShift API URL should not be hardcoded

    openshift = OpenShift()
    try:
        # FIXME we should not hardcode the solver dist names
        response = requests.get(
            endpoint,
            headers={
                "Authorization": "Bearer {}".format(openshift.token),
                "Content-Type": "application/json",
            },
            params={"labelSelector": "component=solver-f27"},
            verify=False,
        ).json()

        created, failed, succeeded = countJobStatus(response["items"])

        solver_jobs_total.labels("f27", "created").set(created)
        solver_jobs_total.labels("f27", "failed").set(failed)
        solver_jobs_total.labels("f27", "succeeded").set(succeeded)

    except ResourceNotFoundError as excptn:
        _LOGGER.error(excptn)


@solver_documents_seconds.time()
def get_solver_documents(solver_name: str = None):
    """Get the total number Solver Documents in Graph Database."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
        graph_db.connect()
        graphdb_connection_error_status.set(0)

        # Optimized query
        #number_solver_documents = graph_db.get_solver_documents_count()

        # Non-Optimized query
        number_solver_documents = asyncio.get_event_loop().run_until_complete(graph_db.
        g.E()
            .has("__label__", "solved")
            .valueMap()
            .select("solver_document_id")
            .dedup()
            .count()
            .next())

        solver_documents_total.set(number_solver_documents)
        _LOGGER.debug("solver_documents_total=%r", number_solver_documents)


    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        _LOGGER.error(excptn)


@analyzer_documents_seconds.time()
def get_analyzer_documents():
    """Get the total number Analyzer Documents in Graph Database."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()
    
    number_analyzer_documents = graph_db.get_analyzer_documents_count()

    analyzer_documents_total.set(number_analyzer_documents)
    _LOGGER.debug("analyzer_documents_total=%r", number_analyzer_documents)


def get_tot_vertex_and_edges_instances():
    """Get the total number of Vertex and Edge instances stored in JanusGraph Server."""

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()

    v_total = graph_db.get_total_number_of_vertex_instances_count()
    e_total = graph_db.get_total_number_of_edge_instances_count()

    graphdb_total_vertex_instances.set(v_total)
    graphdb_total_edge_instances.set(e_total)

    _LOGGER.debug("graphdb_total_vertex_instances=%r", v_total)
    _LOGGER.debug("graphdb_total_edge_instances=%r", e_total)


def get_tot_instances_for_each_vertex():
    """Get the total number of Instances for each Vertex stored in JanusGraph Server."""

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()

    v_instances_total = graph_db.get_total_number_of_instances_for_each_vertex_count()

    for v_label, v_instances_count in v_instances_total.items():
        graphdb_total_instances_per_vertex.labels(v_label).set(v_instances_count)

    _LOGGER.debug("graphdb_total_instances_per_vertex=%r", v_instances_total)


def get_tot_instances_for_each_edge():
    """Get the total number of Instances for each Edge stored in JanusGraph Server."""

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()

    e_instances_total = graph_db.get_total_number_of_instances_for_each_edge_count()

    for e_label, e_instances_count in e_instances_total.items():
        graphdb_total_instances_per_edge.labels(e_label).set(e_instances_count)

    _LOGGER.debug("graphdb_total_instances_per_edge=%r", e_instances_total)


def get_difference_between_v_python_artifact_and_e_has_artifact_instances():
    """Get the difference between the total number of Vertex "python_artifact" instances and Edge "has_artifacts" instances."""

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()

    graphdb_total_v_python_artifact_instances = graph_db.get_total_number_of_python_artifact_vertex_instances_count()
    graphdb_total_e_has_artifact_instances = graph_db.get_total_number_of_has_artifact_edge_instances_count()

    difference_between_v_python_artifact_and_e_has_artifact_instances.set(graphdb_total_e_has_artifact_instances - graphdb_total_v_python_artifact_instances)

    _LOGGER.debug("difference_between_v_python_artifact_and_e_has_artifact_instances=%r", graphdb_total_e_has_artifact_instances - graphdb_total_v_python_artifact_instances)


def get_python_packages_solver_error_count():
    """Get the total numbr of python packages with solver error True and how many are unparsable or unsolvable"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()

    #Optimized query
    # total_python_packages_with_solver_error_unparsable = graph_db.get_error_python_packages_count(unparsable=True)
    #Optimized query
    # total_python_packages_with_solver_error_unsolvable = graph_db.get_error_python_packages_count(unsolvable=True)
    
    #Non-optimized query
    total_python_packages_with_solver_error_unparsable = asyncio.get_event_loop().run_until_complete(graph_db
    .g.E()
        .has("__label__", "solved")
        .has("solver_error", True)
        .has("solver_error_unparsable", True)
        .inV()
        .has("__label__", "python_package_version")
        .has("__type__", "vertex")
        .has("ecosystem", "pypi")
        .has("package_name")
        .has("package_version")
        .dedup()
        .count()
        .next())
    
    #Non-optimized query
    total_python_packages_with_solver_error_unsolvable = asyncio.get_event_loop().run_until_complete(graph_db
    .g.E()
        .has("__label__", "solved")
        .has("solver_error", True)
        .has("solver_error_unsolvable", True)
        .inV()
        .has("__label__", "python_package_version")
        .has("__type__", "vertex")
        .has("ecosystem", "pypi")
        .has("package_name")
        .has("package_version")
        .dedup()
        .count()
        .next())
    
    
    graphdb_total_python_packages_with_solver_error_unparsable.set(total_python_packages_with_solver_error_unparsable)
    graphdb_total_python_packages_with_solver_error_unsolvable.set(total_python_packages_with_solver_error_unsolvable)
    graphdb_total_python_packages_with_solver_error.set(total_python_packages_with_solver_error_unparsable + total_python_packages_with_solver_error_unsolvable)

    _LOGGER.debug("graphdb_total_python_packages_with_solver_error=%r", total_python_packages_with_solver_error_unparsable + total_python_packages_with_solver_error_unsolvable)
    _LOGGER.debug("graphdb_total_python_packages_with_solver_error_unparsable=%r", total_python_packages_with_solver_error_unparsable)
    _LOGGER.debug("graphdb_total_python_packages_with_solver_error_unsolvable=%r", total_python_packages_with_solver_error_unsolvable)


def get_difference_between_known_urls_and_all_urls():
    """Get the difference between Thoth known urls and all urls in the packages"""

    graph_db = GraphDatabase.create('janusgraph.test.thoth-station.ninja')
    graph_db.connect()

    graphdb_known_thoth_urls = graph_db.get_python_package_index_urls()

    #Non-optimized query
    graphdb_total_n_packages_per_index = asyncio.get_event_loop().run_until_complete(graph_db
    .g.V()
        .has("index_url")
        .groupCount()
        .by("index_url")
        .next())
    
    graphdb_all_urls = [url_index for url_index in graphdb_total_n_packages_per_index.keys()]

    difference_between_known_urls_and_all_urls.set(len(set(graphdb_all_urls) - set(graphdb_known_thoth_urls)))

    _LOGGER.debug("difference_between_known_urls_and_all_urls=%r", len(set(graphdb_all_urls) - set(graphdb_known_thoth_urls)))
