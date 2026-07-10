## Prerequisites

- SUSE Observability Agent installed with StackPacks 2.0 support enabled
- The k8s resource collector enabled in the agent
- Network connectivity from the agent to the platform OTLP ingest endpoint

## Minimal Configuration

The k8s resource collector is enabled by default when StackPacks 2.0 support is enabled. Configure which Custom Resource API groups are collected with `otel.k8sResourceCollector.crDiscovery.apiGroups`:

```yaml
global:
  features:
    experimentalStackpacks: true

otel:
  k8sResourceCollector:
    crDiscovery:
      discoveryMode: api_groups
      apiGroups:
        include:
          "policies.kubewarden.io": true
          "kubevirt.io": true
        exclude:
          "internal.example.com": true
```

The chart does not collect every CR API group by default. Enabled integration presets add common SUSE-related API groups, and you can add more with `crDiscovery.apiGroups.include`. Set `discoveryMode: all` to collect CRs for every CRD API group. CRDs themselves are always collected; `apiGroups` controls which Custom Resource instances are collected.

When `rbac.useWildcard: false`, the same truthy `crDiscovery.apiGroups.include` entries are also used for restricted RBAC. Kubernetes RBAC only supports exact API groups or `"*"`, so wildcard patterns like `"*.example.com"` require `rbac.useWildcard: true`.

For the full configuration guide, see the SUSE Observability documentation for the k8s resource collector.
