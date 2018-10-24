#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018 Christoph Görn
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
import logging

from itertools import chain

import requests

from openshift.dynamic.exceptions import ResourceNotFoundError

from thoth.storages import GraphDatabase
from thoth.common import init_logging
from thoth.common.helpers import get_service_account_token
from thoth.metrics_exporter import *


init_logging()


_LOGGER = logging.getLogger('thoth.metrics_exporter.jobs')


@thoth_package_version_seconds.time()
def get_retrieve_unsolved_pypi_packages():
    """This will get the total number of unsolved pypi packages in the graph database."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    graph = GraphDatabase(hosts=['janusgraph'], port=8182)
    graph.connect()

    thoth_package_version_total.labels(ecosystem='pypi', solver='unsolved').set(
        len(list(chain(*graph.retrieve_unsolved_pypi_packages().items()))))


@thoth_solver_jobs_seconds.time()
def get_thoth_solver_jobs(namespace: str = None):
    """This will get the total number Solver Jobs."""
    if namespace is None:
        namespace = os.getenv("MY_NAMESPACE")

    endpoint = "{}/namespaces/{}/jobs".format(
        "https://paas.upshift.redhat.com:443/apis/batch/v1",
        namespace
    )  # FIXME the OpenShift API URL should not be hardcoded

    try:
        # FIXME we should not hardcode the solver dist names
        response = requests.get(
            endpoint,
            headers={
                'Authorization': 'Bearer {}'.format(get_service_account_token()),
                'Content-Type': 'application/json'
            },
            params={'labelSelector': 'component=solver-f27'},
            verify=False
        ).json()

        thoth_solver_jobs_total.labels('f27', 'created').set(len(response['items']))

        # check if item.status.failed == 1
        thoth_solver_jobs_total.labels('f27', 'failed').set(-1)
        thoth_solver_jobs_total.labels('f27', 'succeeded').set(-1)

    except ResourceNotFoundError as excpt:
        _LOGGER.error(excpt)
