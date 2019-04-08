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
import time
import logging

from datetime import datetime

import responder
import uvicorn

from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

from thoth.common import init_logging

from thoth.metrics_exporter import __version__
from thoth.metrics_exporter.jobs import (
    get_solver_documents,
    get_analyzer_documents,
    get_tot_vertex_and_edges_instances,
    get_tot_instances_for_each_vertex,
    get_tot_instances_for_each_edge,
    get_difference_between_v_python_artifact_and_e_has_artifact_instances,
    get_python_packages_solver_error_count,
    get_difference_between_known_urls_and_all_urls,
    get_retrieve_unsolved_pypi_packages,
    get_thoth_solver_jobs,
)


init_logging()

_LOGGER = logging.getLogger("thoth.metrics_exporter")
_DEBUG = os.getenv("METRICS_EXPORTER_DEBUG", True)

api = responder.API(title="Thoth Metrics Exporter", version=__version__)
api.debug = _DEBUG


@api.route(before_request=True)
def prepare_response(req, resp):
    """Just add my signature."""
    resp.headers["X-Thoth-Metrics-Exporter-Version"] = f"v{__version__}"


@api.route("/")
async def main(req, resp):
    """Show this to humans."""
    resp.headers["Location"] = "https://url.corp.redhat.com/grafana-thoth-test"
    resp.status_code = api.status_codes.HTTP_308


@api.route("/metrics")
async def metrics(req, resp):
    """Return the Prometheus Metrics."""
    _LOGGER.debug("exporting metrics registry...")

    @api.background.task
    def update_janusgraph_metrics():
        _LOGGER.debug("updating JanusGraph metrics")
        get_solver_documents()
        get_analyzer_documents()
        get_tot_vertex_and_edges_instances()
        get_tot_instances_for_each_vertex()
        get_tot_instances_for_each_edge()
        get_difference_between_v_python_artifact_and_e_has_artifact_instances()
        get_python_packages_solver_error_count()
        get_difference_between_known_urls_and_all_urls()
        #get_retrieve_unsolved_pypi_packages()

    @api.background.task
    def update_openshift_metrics():
        _LOGGER.debug("updating OpenShift metrics")

        get_thoth_solver_jobs('thoth-test-core')

    update_janusgraph_metrics()
    update_openshift_metrics()
    resp.text = generate_latest().decode("utf-8")


if __name__ == "__main__":
    logging.getLogger("thoth").setLevel(logging.DEBUG if _DEBUG else logging.INFO)

    _LOGGER.debug("Debug mode is on")
    _LOGGER.info(f"Thoth Metrics Exporter v{__version__} starting...")

    api.run(address="0.0.0.0", port=8080, debug=_DEBUG)
