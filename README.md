# Thoth Metrics

This is a Promotheus Metrics exporter for Thoth.

## Metrics exporter API

Metrics exporter exposes two main endpoints:

  * **/metrics** - used by Prometheus to scrape metrics
  * **/scheduler** - used to check available jobs in the sceduler

The scheduler endpoint provides the following list of operations:

  * **GET /scheduler** - exposes main info about the scheduler
  * **GET /scheduler/jobs** - get listing of available jobs
  * **GET /scheduler/jobs/<job-id>** - get information about the given job
  * **PATCH /scheduler/jobs/<job-id>** - adjust the given job
  * **POST /scheduler/jobs/<job-id>/pause** - pause the given job
  * **POST /scheduler/jobs/<job-id>/resume** - resume the given job
  * **POST /scheduler/jobs/<job-id>/run** - run the given job (manual trigger)
  * **DELETE /scheduler/jobs/<job-id>** - remove the given job (do not use, use pause instead)
  * **POST /scheduler/jobs** - adds a job to metrics-exporter scheduler (do not use)

## Copyright

Copyright (C) 2018, 2019 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

The GNU General Public License is provided within the file LICENSE.
