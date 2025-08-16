from __future__ import annotations
from contextlib import contextmanager, nullcontext
from typing import Dict, Any, Iterator
import os


_OTEL_READY = False


def _init_tracing_if_configured() -> bool:
    """Initialize OpenTelemetry SDK if exporter config is present.

    Returns True if a tracer provider is installed, else False. This function
    is safe to call multiple times.
    """
    global _OTEL_READY
    if _OTEL_READY:
        return True
    try:
        # Only initialize when endpoint (or SDK enabled) is provided
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        sdk_enabled = os.getenv("OTEL_SDK_ENABLED", "0").lower() in ("1", "true", "yes")
        if not endpoint and not sdk_enabled:
            return False

        from opentelemetry import trace  # type: ignore
        from opentelemetry.sdk.resources import Resource  # type: ignore
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore
        from opentelemetry.sdk.trace.export import (  # type: ignore
            BatchSpanProcessor,
        )
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # type: ignore
            OTLPSpanExporter,
        )

        service_name = os.getenv("OTEL_SERVICE_NAME", "isaac-neural")
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint) if endpoint else OTLPSpanExporter()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        _OTEL_READY = True
        return True
    except Exception:
        return False


@contextmanager
def start_span(name: str, attributes: Dict[str, Any] | None = None) -> Iterator[None]:
    """Start an OpenTelemetry span if SDK available; otherwise a no-op.

    Falls back to `nullcontext()` to ensure exceptions propagate correctly.
    """
    cm = nullcontext()
    try:
        if _init_tracing_if_configured():
            from opentelemetry import trace  # type: ignore

            tracer = trace.get_tracer("isaac.neural")
            cm = tracer.start_as_current_span(name)  # type: ignore
    except Exception:
        cm = nullcontext()

    with cm as span:  # type: ignore
        if attributes and hasattr(span, "set_attribute"):
            for key, value in attributes.items():
                try:
                    span.set_attribute(key, value)  # type: ignore
                except Exception:
                    pass
        yield
