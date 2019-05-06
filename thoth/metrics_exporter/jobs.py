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
            headers={"Authorization": "Bearer {}".format(openshift.token), "Content-Type": "application/json"},
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
        graph_db = GraphDatabase()
        graph_db.connect()

        number_solver_documents = graph_db.get_solver_documents_count()

        solver_documents_total.set(number_solver_documents)
        _LOGGER.debug("solver_documents_total=%r", number_solver_documents)

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


@analyzer_documents_seconds.time()
def get_analyzer_documents():
    """Get the total number Analyzer Documents in Graph Database."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        number_analyzer_documents = graph_db.get_analyzer_documents_count()

        analyzer_documents_total.set(number_analyzer_documents)
        graphdb_connection_error_status.set(0)
        _LOGGER.debug("analyzer_documents_total=%r", number_analyzer_documents)

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_tot_vertex_instances():
    """Get the total number of Vertex instances stored in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        v_total = graph_db.get_number_of_each_vertex_in_graph()

        graphdb_total_vertex_instances.set(sum([count_vertex for count_vertex in v_total.values()]))

        _LOGGER.debug("graphdb_total_vertex_instances=%r", sum([count_vertex for count_vertex in v_total.values()]))

    except aiohttp.client_exceptions.ClientConnectorError as excptn:
        graphdb_connection_error_status.set(1)
        _LOGGER.error(excptn)


def get_tot_instances_for_each_vertex():
    """Get the total number of Instances for each Vertex in Thoth Knowledge Graph."""
    try:
        graph_db = GraphDatabase()
        graph_db.connect()

        v_instances_total = graph_db.get_number_of_each_vertex_in_graph()

        for v_label, v_instances_count in v_instances_total.items():
            graphdb_total_instances_per_vertex.labels(v_label).set(v_instances_count)

        _LOGGER.debug("graphdb_total_instances_per_vertex=%r", v_instances_total)

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
