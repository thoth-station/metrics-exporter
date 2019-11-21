#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019 Christoph Görn, Francesco Murdaca, Fridolin Pokorny
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


"""This is a Prometheus exporter for Thoth."""


import os
import logging
import time
import threading
from typing import Optional
from concurrent.futures.thread import ThreadPoolExecutor

from flask_cors import CORS
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import redirect
from prometheus_client import generate_latest
from thoth.common import init_logging
from thoth.metrics_exporter import __version__
from thoth.metrics_exporter.jobs import REGISTERED_JOBS
import thoth.metrics_exporter.jobs as jobs


init_logging()


_LOGGER = logging.getLogger("thoth.metrics_exporter")
_LOGGER.info(f"Thoth Metrics Exporter v%s", __version__)

_UPDATE_INTERVAL_SECONDS = int(os.getenv("THOTH_METRICS_EXPORTER_UPDATE_INTERVAL", 20))
_GRAFANA_REDIRECT_URL = os.getenv("THOTH_METRICS_EXPORTER_GRAFANA_REDIRECT_URL", "https://grafana.datahub.redhat.com/")
_MAX_WORKERS = int(os.getenv("THOTH_METRICS_EXPORTER_MAX_WORKERS", 16))

_INITIALIZED = False
_INITIALIZED_LOCK = threading.RLock()
_EXECUTED = dict.fromkeys((f"{class_name}.{method_name}" for class_name, method_name in REGISTERED_JOBS), 0)


def func_wrapper(class_name: str, method_name: str, last_schedule: Optional[int] = None) -> None:
    """A wrapper which counts how many jobs were run and notes down some metrics statistics.

    Make sure you do not run metrics-exporter with preload set (gunicorn configuration),
    otherwise each worker process would run its own metrics job gathering.

    This simple wrapper wraps the actual function which does metrics
    gathering to count how many functions were called. If we reach number of
    all jobs, we know we gathered all metrics and we can expose metrics on
    /metrics endpoint. Otherwise the application keeps returning HTTP status
    code 503 signalizing its not ready yet.
    """
    global _INITIALIZED
    global _INITIALIZED_LOCK

    job = getattr(getattr(jobs, class_name), method_name)

    if last_schedule:
        sleep_time = _UPDATE_INTERVAL_SECONDS - (time.monotonic() - last_schedule)
        if sleep_time > 0:
            # Let's be nice to database, we don't need to update metrics each second...
            _LOGGER.debug(
                "Sleeping for %g to prevent from overloading", sleep_time
            )
            time.sleep(sleep_time)
        else:
            missed_times = int(-sleep_time / _UPDATE_INTERVAL_SECONDS)
            if missed_times:
                _LOGGER.warning("Metrics job %s.%s missed %d runs", class_name, method_name, missed_times)

    _LOGGER.debug("Running metrics job %s.%s on worker %d", class_name, method_name, threading.get_ident())
    start_time = time.monotonic()
    try:
        job()
    except Exception:
        _LOGGER.exception("Failed to run metrics gathering job %s.%s", class_name, method_name)
        raise
    finally:
        _LOGGER.info("Metrics gathering done in %s.%s took %g", class_name, method_name, time.monotonic() - start_time)
        _LOGGER.debug("Resubmitting job %s.%s", class_name, method_name)
        # Register self for the next execution run.
        _EXECUTOR.submit(func_wrapper, class_name, method_name, start_time)

    # We turn on the switch only if all the metrics were gathered successfully.
    if not _INITIALIZED:
        with _INITIALIZED_LOCK:
            # Increment/keep track only until we are not initialized and another thread did not turned the switch.
            if not _INITIALIZED:
                _EXECUTED[f"{class_name}.{method_name}"] = 1
                _INITIALIZED = sum(_EXECUTED.values()) == len(REGISTERED_JOBS)

            if _INITIALIZED:
                # Turn on the switch, we do not need to keep track of not-ready jobs.
                _LOGGER.info("All metrics were gathered, the service is ready now")


application = Flask("thoth.metrics_exporter")

# Add Cross Origin Request Policy to all
CORS(application)


_EXECUTOR = ThreadPoolExecutor(max_workers=_MAX_WORKERS or None)
for class_name, method_name in REGISTERED_JOBS:
    _LOGGER.info("Registering metrics job gathering %s.%s", class_name, method_name)
    _EXECUTOR.submit(func_wrapper, class_name, method_name)


@application.after_request
def extend_response_headers(response):
    """Just add my signature."""
    response.headers["X-Thoth-Metrics-Exporter-Version"] = f"v{__version__}"
    return response


@application.route("/")
def main():
    """Show this to humans."""
    return redirect(_GRAFANA_REDIRECT_URL, code=308)


@application.route("/metrics")
def metrics():
    """Return the Prometheus Metrics."""
    _LOGGER.debug("Exporting metrics registry...")
    global _INITIALIZED
    global _INITIALIZED_LOCK

    if not _INITIALIZED:
        with _INITIALIZED_LOCK:
            _LOGGER.warning(
                "Not all metrics were gathered, the service is not ready yet (%d/%d), missing: %s",
                sum(_EXECUTED.values()),
                len(REGISTERED_JOBS),
                [k for k, v in _EXECUTED.items() if v == 0],
            )
            return make_response(jsonify({"error": "Metrics are not ready yet"}), 503)

    return generate_latest().decode("utf-8")


if __name__ == "__main__":
    _LOGGER.debug("Debug mode is on")
    application.run(host="0.0.0.0", port=8080)
