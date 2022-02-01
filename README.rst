Thoth Metrics Expoter
---------------------

Welcome to Thoth's metrics-exporter documentation

.. image:: https://img.shields.io/github/v/tag/thoth-station/metrics-exporter?style=plastic
  :target: https://github.com/thoth-station/metrics-exporter/tags
  :alt: GitHub tag (latest by date)

.. image:: https://quay.io/repository/thoth-station/metrics-exporter/status
  :target: https://quay.io/repository/thoth-station/metrics-exporter?tab=tags
  :alt: Quay - Build

This is a Promotheus Metrics exporter for Thoth.

Setting up Metrics Exporter locally
===================================

1. Create a ``.env`` file from the ``.env.template``.
2. Once you have populated all the values for ``.env``, follow up with ``pipenv install --dev``.
3. ``oc login`` into the Openshift cluster.
4. Run the local version of ``thoth-storages`` after restoring the dump - `guide <https://github.com/thoth-station/storages#running-postgresql-locally>`__. (or connect to the production db using replacing the env variables in ``.env``).
5. Run the metrics exporter using ``pipenv run python3 wsgi.py``
6. You should see metrics in `localhost:8080 <http://localhost:8080>`__.

Adding new metrics to be exported
=================================

1. Add the metric you want to expose to `metrics.py <https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/metrics.py>`__. The metric types stated here adhere to the Prometheus client library core metric types, and are mentioned `here <https://prometheus.io/docs/concepts/metric_types/>`__ in detail.
2. Checkout `metrics_exporter/jobs <https://github.com/thoth-station/metrics-exporter/tree/master/thoth/metrics_exporter/jobs>`__, if the metric you want to add belongs to a existing class add to it else create a new class and inherit the base class ``MetricsBase``.
3. Register the metric method you write using the decorator ``@register_metric_job``. Here is an `example to look at <https://github.com/thoth-station/metrics-exporter/blob/a48247fc6a28ec5e2d6ac1f1703c5a8d77a711f5/thoth/metrics_exporter/jobs/pypi.py#L37>`__.
4. Set the metric variable value from ``metrics.py`` in the method that you define. More, on that here on `prometheus documentation <https://github.com/prometheus/client_python#gauge>`__.
5. Finally if you have a new class added in jobs, add it to the `init.py <https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/jobs/__init__.py>`__.

Conventions
===========

For any binary metrics the convention used is:

- `0` all good

- `1` alarm is required

Copyright
=========

Copyright (C) 2018, 2019, 2020, 2021, 2022 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/.

The GNU General Public License is provided within the file LICENSE.
