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
    get_tot_nodes_count,
    get_tot_nodes_for_each_entity_count,
    get_python_packages_solver_error_count,
    get_unique_python_packages_count,
    get_unique_run_software_environment_count,
    get_user_unique_run_software_environment_count,
    get_unique_build_software_environment_count,
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
    def update_dgraph_metrics():
        _LOGGER.debug("updating Dgraph metrics")
        get_tot_nodes_count()
        get_tot_nodes_for_each_entity_count()
        get_python_packages_solver_error_count()
        get_unique_python_packages_count()
        get_unique_run_software_environment_count()
        get_user_unique_run_software_environment_count()
        get_unique_build_software_environment_count()

    @api.background.task
    def update_openshift_metrics():
        _LOGGER.debug("updating OpenShift metrics")

        print("No openshift metrics")

    update_dgraph_metrics()
    update_openshift_metrics()
    resp.text = generate_latest().decode("utf-8")


if __name__ == "__main__":
    logging.getLogger("thoth").setLevel(logging.DEBUG if _DEBUG else logging.INFO)

    _LOGGER.debug("Debug mode is on")
    _LOGGER.info(f"Thoth Metrics Exporter v{__version__} starting...")

    api.run(address="0.0.0.0", port=8080, debug=_DEBUG)
