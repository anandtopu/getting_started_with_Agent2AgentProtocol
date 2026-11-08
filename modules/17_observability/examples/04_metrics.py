"""Read bounded request counters; task IDs remain in traces, never metric labels."""

import asyncio
import json

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from common.protocol import as_dict, request
from common.testing import client


async def main():
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
    try:
        async with client("venues") as http:
            for guests in (40, 60):
                result = await http.post("/message:send", json=as_dict(request({"guests": guests})))
                result.raise_for_status()
        values = [
            metric
            for resource in reader.get_metrics_data().resource_metrics
            for scope in resource.scope_metrics
            for metric in scope.metrics
        ]
        counter = next(metric for metric in values if metric.name == "maplewood.task.requests")
        point = counter.data.data_points[0]
        assert point.value == 2 and dict(point.attributes) == {"vendor": "venues"}
        print(
            json.dumps(
                {"name": counter.name, "count": point.value, "labels": dict(point.attributes)}
            )
        )
    finally:
        provider.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
