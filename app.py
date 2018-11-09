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
import time
import logging

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

from thoth.common import init_logging

from thoth.metrics_exporter import __version__, config, package_version_total, package_version_seconds
from thoth.metrics_exporter.jobs import load_jobs, get_thoth_solver_jobs, get_retrieve_unsolved_pypi_packages


init_logging()

_LOGGER = logging.getLogger("thoth.metrics_exporter")
_DEBUG = os.getenv("METRICS_EXPORTER_DEBUG", False)


# @application.route("/")
# def main():
#    """Show this to humans."""
#    return "This service is not for humans!"


# @application.route("/metrics")
# def metrics():
#    """Return the Prometheus Metrics."""
#    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    logging.getLogger("thoth").setLevel(logging.DEBUG if _DEBUG else logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.DEBUG if _DEBUG else logging.INFO)

    _LOGGER.debug("Debug mode is on")
    _LOGGER.info(f"Thoth Metrics Exporter v{__version__} starting...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    scheduler = AsyncIOScheduler()
    load_jobs(scheduler)
    _LOGGER.debug("Starting Scheduler")
    scheduler.start()

    loop.run_forever()
