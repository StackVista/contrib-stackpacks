## Send OTLP data directly

From an environment outside Kubernetes, send OTLP over HTTP to `{{config.baseUrl}}/otel`, authenticating with the header `Authorization: StackState {{token}}`.

OpenTelemetry Collector exporter:

```yaml
exporters:
  otlphttp/suse-observability:
    endpoint: {{config.baseUrl}}/otel
    headers:
      Authorization: "StackState {{token}}"
```

Or configure an OpenTelemetry SDK directly:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="{{config.baseUrl}}/otel"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=StackState {{token}}"
```

See [the documentation](https://l.stackstate.com/open-telemetry-setup) for more options.
