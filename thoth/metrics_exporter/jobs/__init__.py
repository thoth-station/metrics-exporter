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

"""Jobs implemented for gathering metrics."""


from .adviser import AdviserMetrics
from .ceph import CephMetrics
from .db import DBMetrics
from .inspection import InspectionMetrics
from .openshift import OpenshiftMetrics
from .package_analyzer import PackageAnalyzerMetrics
from .pi import PIMetrics
from .python import PythonPackagesMetrics
from .software_environment import SoftwareEnvironmentMetrics
from .solver import SolverMetrics
from .user import UserInformationMetrics
from .base import REGISTERED_JOBS

__all__ = [
    "AdviserMetrics",
    "CephMetrics",
    "DBMetrics",
    "InspectionMetrics",
    "OpenshiftMetrics",
    "PackageAnalyzerMetrics",
    "PIMetrics",
    "PythonPackagesMetrics",
    "SoftwareEnvironmentMetrics",
    "SolverMetrics",
    "UserInformationMetrics",
    "REGISTERED_JOBS",
]
