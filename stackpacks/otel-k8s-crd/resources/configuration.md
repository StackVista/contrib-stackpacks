## Prerequisites

- SUSE Observability Agent installed with the k8s resource collector enabled
- Network connectivity from the agent to the platform's OTLP ingest endpoint

## Configuration

Enable StackPacks 2.0 support in your agent Helm values. This activates the OTel components, including the k8s resource collector. The collector is enabled by default when OTel is active, but can still be configured under `otel.k8sResourceCollector`:

```yaml
global:
  features:
    experimentalStackpacks: true
otel:
  k8sResourceCollector:
    crdDiscovery:
      discoveryMode: api_groups   # or "all" to watch every API group
      snapshotInterval: 5m        # periodic full-state emission from the informer cache (min: 1m)
```

If you are not enabling StackPacks 2.0 globally, set `otel.enabled: true` instead.

### API Group Filtering

`apiGroupFilters.include` and `apiGroupFilters.exclude` are maps of pattern → bool. Wildcards are supported (e.g. `*.example.com`). To disable a default pattern from an overlay values file, set its value to `false`:

```yaml
otel:
  k8sResourceCollector:
    crdDiscovery:
      discoveryMode: api_groups
      apiGroupFilters:
        include:
          # Disable the chart default `"*": true` so only the patterns below match.
          "*": false
          "*.example.com": true
        exclude:
          "internal.example.com": true
```

The chart default is `include: { "*": true }`. There must be at least one truthy entry when `discoveryMode` is `api_groups`.

### Restricting RBAC

By default the collector is granted wildcard read permissions for every custom resource in the cluster. To restrict it to specific API groups, set `useWildcard: false` and list the groups under `crdApiGroups` (map of group → bool, same disable semantics):

```yaml
otel:
  k8sResourceCollector:
    rbac:
      useWildcard: false
      crdApiGroups:
        "policies.kubewarden.io": true
        "longhorn.io": true
```

### Watching Additional Kubernetes Resources

`objects` lets you watch arbitrary Kubernetes resources (built-ins or third-party) alongside the CRD-discovered custom resources. Each entry is keyed by the resource plural (required) and maps to a spec:

```yaml
otel:
  k8sResourceCollector:
    objects:
      pods:
        group: ""                 # core group
        namespaces: ["kube-system"]
      deployments:
        group: apps
        labelSelector: "app=foo"
        fieldSelector: "status.phase=Running"
```

Spec fields:

- `group` — API group; empty string (`""`) for the core group
- `version` — optional; defaults to the API server's preferred version
- `namespaces` — optional; cluster-wide when empty
- `labelSelector` / `fieldSelector` — optional Kubernetes selectors

Entries that overlap a CRD covered by `crdDiscovery.apiGroupFilters` are rejected at startup. When `rbac.useWildcard: false`, the chart auto-derives `get`/`list`/`watch` RBAC for each `objects` entry (deduped per group) — no need to add the group to `crdApiGroups`.

To disable a default `objects` entry from an overlay file, set its value to `null` or `false`.

`deniedObjects` extends the receiver's built-in denylist (core `Secrets`, `ConfigMaps`) with resources that must not appear under `objects`. The key is the resource plural; the spec only needs `group`:

```yaml
otel:
  k8sResourceCollector:
    deniedObjects:
      certificates:
        group: cert-manager.io
```

### OTLP Endpoint Override

By default, telemetry is sent to `<stackstate.url>/otel` over HTTP (proxied via the platform's Envoy router; the default path is HTTP-only). If your platform exposes a dedicated OTLP ingress, override the OTel platform endpoint. HTTP endpoints take precedence over gRPC endpoints when both are configured.

```yaml
otel:
  # gRPC: bare host:port, no scheme. A port is required.
  platformGrpcOtlpEndpoint: otlp-my-instance.stackstate.io:443
```

For a dedicated HTTP ingress, provide a full URL with scheme:

```yaml
otel:
  platformHttpOtlpEndpoint: https://otlp-http-my-instance.stackstate.io:4318
```
