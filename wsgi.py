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
import logging

from flask import Flask, Response
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Gauge, Counter, Summary

from thoth.common import init_logging
from thoth.storages import GraphDatabase

from thoth.metrics_exporter import __version__


app = Flask(__name__)

init_logging()

_LOGGER = logging.getLogger('thoth.metrics.server')
_LOGGER.info(f"Thoth Metrics Server v{__version__}")

thoth_package_version_total = Gauge('thoth_package_version_total',
                                    'State of package:version Vertices.', ['ecosystem', 'solver'])
thoth_package_version_seconds = Summary('thoth_package_version_seconds',
                                        'Time spent processing requests to JanusGraph Server.')


@thoth_package_version_seconds.time()
def get_retrieve_unsolved_pypi_packages():
    graph = GraphDatabase(hosts=['stage.janusgraph.thoth-station.ninja'], port=8182)
    graph.connect()

    thoth_package_version_total.labels(ecosystem='pypi', solver='unsolved').set(len(graph.retrieve_unsolved_pypi_packages()
                                                                                    .items()))


@app.route('/')
def main():
    return "ok"  # requests tracked by default


@app.route('/metrics')
def metrics():
    get_retrieve_unsolved_pypi_packages()

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
