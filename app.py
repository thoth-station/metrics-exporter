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

from flask import Flask, Response
from flask_apscheduler import APScheduler

from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

from thoth.common import init_logging

from thoth.metrics_exporter import __version__, config, thoth_package_version_total, thoth_package_version_seconds
from thoth.metrics_exporter.jobs import get_thoth_solver_jobs, get_retrieve_unsolved_pypi_packages


application = Flask(__name__)
application.config.from_object(config.Config())

init_logging()

_LOGGER = logging.getLogger('thoth.metrics_exporter')
_DEBUG = os.getenv('DEBUG', False)


@application.route('/')
def main():
    return "This service is not for humans!"


@application.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    _LOGGER.info(f"Thoth Metrics Exporter v{__version__} starting...")

    # initialy populating the metrics
    get_thoth_solver_jobs()
    get_retrieve_unsolved_pypi_packages()

    # now, let's do it every minute
    scheduler = APScheduler()
    scheduler.init_app(application)
    scheduler.start()

    # and start the application server
    application.run(host='0.0.0.0', port=8080, debug=_DEBUG)
