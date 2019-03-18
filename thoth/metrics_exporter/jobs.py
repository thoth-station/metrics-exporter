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
        # janusgraph is a hostname injected into the pod by the 'janusgraph' service object
        graph = GraphDatabase()
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
        graph_db = GraphDatabase.create()
        graph_db.connect()
    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        _LOGGER.error(excptn)
        return

    solver_documents = graph_db.get_solver_documents_count()

    _LOGGER.debug("solver_documents=%r", solver_documents)


@analyzer_documents_seconds.time()
def get_analyzer_documents():
    """Get the total number Analyzer Documents in Graph Database."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    graph_db = GraphDatabase.create()
    graph_db.connect()
    analyzer_documents = graph_db.get_solver_documents_count()

    _LOGGER.debug("analyzer_documents_total=%r", analyzer_documents)


def get_janusgraph_v_and_e_total():
    """Get the total number of Vertices and Edges stored in JanusGraph Server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    graph_db = GraphDatabase.create()
    graph_db.connect()

    v_total = asyncio.get_event_loop().run_until_complete(graph_db.g.V().count().next())
    e_total = asyncio.get_event_loop().run_until_complete(graph_db.g.E().count().next())

    graphdatabase_vertex_total.set(v_total)
    graphdatabase_edge_total.set(e_total)
