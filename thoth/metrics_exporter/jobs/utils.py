#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019, 2020 Christoph Görn, Francesco Murdaca, Fridolin Pokorny
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

"""A collection of methods that can be reused in different metric classes."""

import logging
import os

from typing import Dict, Any, List

_LOGGER = logging.getLogger(__name__)


def get_namespace_object_labels_map(namespace_objects: Dict[str, Any]) -> Dict[str, List[str]]:
    """Retrieve namespace/objects map that shall be monitored by metrics-exporter."""
    namespace_objects_map: Dict[str, Any] = {}
    for environment_variable, objects_labels in namespace_objects.items():
        namespace_objects_map = _retrieve_namespace_object_labels(
            environment_variable=environment_variable,
            objects_labels=objects_labels,
            namespace_objects_map=namespace_objects_map,
        )

    return namespace_objects_map


def _retrieve_namespace_object_labels(
    environment_variable: str, objects_labels: Dict[str, Any], namespace_objects_map: Dict[str, Any]
):
    """Retrieve namespace and labels."""
    if os.getenv(environment_variable):
        if os.getenv(environment_variable) not in namespace_objects_map.keys():
            namespace_objects_map[os.environ[environment_variable]] = objects_labels
        else:
            namespace_objects_map[os.environ[environment_variable]] += objects_labels
    else:
        _LOGGER.warning("Namespace variable not provided for %r", environment_variable)

    return namespace_objects_map
