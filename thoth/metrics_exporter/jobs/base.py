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

"""A base class for implementing metrics classes."""


import ast
import time
import logging
from typing import Callable
from decorator import decorator
import inspect
import textwrap
from typing import Any

from thoth.storages import GraphDatabase

_LOGGER = logging.getLogger(__name__)

# Registered jobs run by metrics-exporter periodically.
REGISTERED_JOBS = []


@decorator
def register_metric_job(method: Callable, *args, **kwargs) -> None:
    """A decorator for adding a metric job."""
    start_time = time.monotonic()
    try:
        method(*args, **kwargs)
    finally:
        _LOGGER.info("Gathering metrics by job %r took %g seconds", method.__name__, time.monotonic() - start_time)


class _MetricsType(type):
    """A metaclass for implementing metrics classes."""

    def __init__(cls, class_name: str, bases: tuple, attrs: dict):
        """Initialize metrics type."""
        def _is_register_metric_job_decorator_present(node: ast.FunctionDef) -> None:
            """Check if the given function has assigned decorator to register a new metric job."""
            for n in node.decorator_list:
                if n.id == register_metric_job.__name__:
                    _LOGGER.info("Registering job %r implemented in %r", method_name, class_name)
                    REGISTERED_JOBS.append((class_name, method_name))

        global REGISTERED_JOBS

        _LOGGER.info("Checking class %r for registered metric jobs", class_name)
        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = _is_register_metric_job_decorator_present
        for method_name, item in attrs.items():
            # Metrics classes are not instantiable.
            if isinstance(item, (staticmethod, classmethod)):
                source = textwrap.dedent(inspect.getsource(item.__func__))
                node_iter.visit(ast.parse(source))


class MetricsBase(metaclass=_MetricsType):
    """A base class for grouping metrics."""

    _GRAPH = None

    def __init__(self) -> None:
        """Do not instantiate this class."""
        raise NotImplemented

    @classmethod
    def graph(cls):
        """Get instantiated graph database with shared connection pool."""
        if not cls._GRAPH:
            cls._GRAPH = GraphDatabase()
            cls._GRAPH.connect()

        return cls._GRAPH
