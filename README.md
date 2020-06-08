# Thoth Metrics

This is a Promotheus Metrics exporter for Thoth.

## Setting up Metrics Exporter locally

1. Create a `.env` file from the `.env.template`.
2. Once you have populated all the values for `.env`, follow up with `pipenv install --dev`.
3. oc login into the Openshift cluster. 
4. Run the local version of thoth-storages after restoring the dump - [guide](https://github.com/thoth-station/storages#running-postgresql-locally) (or connect to the production db using replacing the env variables in `.env`).
5. Run the metrics exporter using - `pipenv run python3 wsgi.py`
6. You should see metrics in - [localhost:8080](http://localhost:8080)

## Adding new metrics to be exported

1. Add the metric you want to expose to [metrics.py](https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/metrics.py). The metric types stated here adhere to the Prometheus client library core metric types, and are mentioned here in detail - [Link](https://prometheus.io/docs/concepts/metric_types/)
2. Checkout [metrics_exporter/jobs](https://github.com/thoth-station/metrics-exporter/tree/master/thoth/metrics_exporter/jobs), if the metric you want to add belongs to a existing class add to it else create a new class and inherit the base class `MetricsBase`.
3. Register the metric method you write using the decorater `@register_metric_job`. Here is an example to look at - [link](https://github.com/thoth-station/metrics-exporter/blob/a48247fc6a28ec5e2d6ac1f1703c5a8d77a711f5/thoth/metrics_exporter/jobs/pypi.py#L37)
4. Set the metric variable's value from `metrics.py` in the method that you define. More, on that here on prometheus documentation - [Link](https://github.com/prometheus/client_python#gauge)
5. Finally if you have a new class added in jobs, add it to the [init.py](https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/jobs/__init__.py).

### Adding new Argo workflows metrics to be exported

Once new Argo workflow is created:

1. Add to [metrics.py](https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/metrics.py):

```python
    workflow_<component_name>_quality = Gauge(
    "thoth_workflow_<component_name>_quality", "Thoth <component_name> workflow status in Argo Workflow.", ["service", "status"]
)
```

depending on the component that uses Argo workflow that you want to monitor.

2. Checkout [metrics_exporter/jobs](https://github.com/thoth-station/metrics-exporter/tree/master/thoth/metrics_exporter/jobs), if the metric you want to add belongs to a existing class add to it else create a new class and inherit the base class `MetricsBase`.

3. Check where the component has to run and add corresponding env variables (if missing) in [configuration.py](https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/configuration.py)

For example:

```python
    # Workflows backend namespace
    _WORKFLOW_CONTROLLER_INSTANCE_BACKEND_NAMESPACE = os.environ["WORKFLOW_METRICS_BACKEND_PROMETHEUS_INSTANCE"]
    _THOTH_BACKEND_NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]
```

4. In the class where you want to introduce Argo workflows metrics, you need to add:

```python
from ..configuration import Configuration
```

```python
    @classmethod
    @register_metric_job
    def get_workflow_status(cls) -> None:
        """Get the workflow status for each workflow."""
        ArgoWorkflowsMetrics().get_thoth_workflows_status_per_namespace_per_label(
            label_selector="component=<component_name>", namespace=Configuration._NAMESPACE
        )

    @classmethod
    @register_metric_job
    def get_component_name_quality(cls) -> None:
        """Get the quality for <component_name> workflows."""
        ArgoWorkflowsMetrics().get_workflow_quality(
            service_name="<component_name>",
            prometheus=Configuration._PROM,
            instance=Configuration._INSTANCE,
            namespace=Configuration._NAMESPACE,
            metric_type=metrics.workflow_<component_name>_quality,
        )
```

4. Finally if you have a new class added in jobs, add it to the [init.py](https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/jobs/__init__.py).

### Adding new Ceph metrics to be exported

1. Checkout [metrics_exporter/jobs](https://github.com/thoth-station/metrics-exporter/tree/master/thoth/metrics_exporter/jobs), if the metric you want to add belongs to a existing class add to it else create a new class and inherit the base class `MetricsBase`.

2. Import the corresponding result store instead of ComponentResultsStore() as it is stated in thoth-storages and it to the following method added to the class selected at point 1.

for example:

```python
from thoth.storages import ComponentResultsStore
```

```python
    @classmethod
    @register_metric_job
    def get_ceph_count(cls) -> None:
        """Get number of reports stored in the database for a type of store."""
        cls.get_ceph_results_per_type(store=ComponentResultsStore())
```

3. Finally if you have a new class added in jobs, add it to the [init.py](https://github.com/thoth-station/metrics-exporter/blob/master/thoth/metrics_exporter/jobs/__init__.py).

## Copyright

Copyright (C) 2018, 2019, 2020 Red Hat Inc.

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
