#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019, 2020, 2021 Christoph Görn, Francesco Murdaca, Fridolin Pokorny
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
import logging
from typing import Callable, List, Any
from decorator import decorator
import inspect
import textwrap

import thoth.metrics_exporter.metrics as metrics
from thoth.metrics_exporter.configuration import Configuration

from thoth.common import OpenShift
from thoth.storages import GraphDatabase

_LOGGER = logging.getLogger(__name__)

# Registered jobs run by metrics-exporter periodically.
REGISTERED_JOBS: List[Any] = []


@decorator
def register_metric_job(method: Callable, *args, **kwargs) -> None:
    """Add a metric job."""
    method(*args, **kwargs)


class _MetricsType(type):
    """A metaclass for implementing metrics classes."""

    def __init__(cls, class_name: str, bases: tuple, attrs: dict):
        """Initialize metrics type."""

        def _is_register_metric_job_decorator_present(node: ast.FunctionDef) -> None:
            """Check if the given function has assigned decorator to register a new metric job."""
            n_ids = [t.id for t in node.decorator_list if isinstance(t, ast.Name)]
            for n_id in n_ids:
                if n_id == register_metric_job.__name__:
                    _LOGGER.info("Registering job %r implemented in %r", method_name, class_name)
                    REGISTERED_JOBS.append((class_name, method_name))

        global REGISTERED_JOBS

        _LOGGER.info("Checking class %r for registered metric jobs", class_name)
        node_iter = ast.NodeVisitor()
        # TODO(pacospace) check typing
        node_iter.visit_FunctionDef = _is_register_metric_job_decorator_present  # type: ignore
        for method_name, item in attrs.items():
            # Metrics classes are not instantiable.
            if isinstance(item, (staticmethod, classmethod)):
                source = textwrap.dedent(inspect.getsource(item.__func__))
                node_iter.visit(ast.parse(source))


class MetricsBase(metaclass=_MetricsType):
    """A base class for grouping metrics."""

    _GRAPH = None
    _OPENSHIFT = None

    def __init__(self) -> None:
        """Do not instantiate this class."""
        raise NotImplementedError

    @classmethod
    def graph(cls):
        """Get instantiated graph database with shared connection pool."""
        if not cls._GRAPH:
            cls._GRAPH = GraphDatabase()

        if not cls._GRAPH.is_connected():
            # Collect metrics about issues with connection to database
            try:
                cls._GRAPH.connect()
            except Exception as e:
                metrics.graphdb_connection_error_status.set(1)
                raise Exception("Raise a flag if there is an error connecting to database. %r", e)
            else:
                metrics.graphdb_connection_error_status.set(0)

        is_schema_up2date = int(cls._GRAPH.is_schema_up2date())

        if is_schema_up2date:
            metrics.graph_db_component_revision_check.labels("metrics-exporter", Configuration.DEPLOYMENT_NAME).set(0)
            return cls._GRAPH
        else:
            metrics.graph_db_component_revision_check.labels("metrics-exporter", Configuration.DEPLOYMENT_NAME).set(1)
            raise Exception("Raise a flag if the schema is not up2date, so we don't rely on metrics")

    @classmethod
    def openshift(cls):
        """Get instantiated openshift class."""
        if not cls._OPENSHIFT:
            try:
                cls._OPENSHIFT = OpenShift()
            except Exception as e:
                metrics.openshift_connection_error_status.set(1)
                raise Exception("Raise a flag if there is an error connecting to openshift. %r", e)
            else:
                metrics.openshift_connection_error_status.set(0)

        return cls._OPENSHIFT
