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


class Config(object):
    """Configuration for the application."""
    JOBS = [
        {
            'id': 'unsolved_pypi_packages',
            'func': 'thoth.metrics_exporter.jobs:get_retrieve_unsolved_pypi_packages',
                    'trigger': 'interval',
                    'minutes': 1
        },
        {
            'id': 'thoth_solver_jobs',
            'func': 'thoth.metrics_exporter.jobs:get_thoth_solver_jobs',
            'trigger': 'interval',
            'minutes': 1
        }
    ]

    SCHEDULER_API_ENABLED = False
