## Prerequisites

- Portworx Enterprise 3.x installed with the Portworx operator (`StorageCluster`).
- SUSE Observability agent (Helm chart `suse-observability-agent` 1.6 or later) with OpenTelemetry enabled (`otel.enabled: true`).
- The Prometheus Operator CRDs (`monitoring.coreos.com`) in the cluster. The agent reads `ServiceMonitor` objects; no Prometheus server is needed.

## 1. Let Portworx export metrics

Portworx serves metrics on every node at `:9001/metrics` (`:17001` on OpenShift). In the `StorageCluster`, make sure metrics export is on:

```yaml
spec:
  monitoring:
    prometheus:
      exportMetrics: true
```

## 2. Let the agent scrape Portworx

Create this `ServiceMonitor` in the namespace where Portworx runs (`portworx` or `kube-system`). The `observability.suse.com/agent: scrape` label makes the agent pick it up.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: so-agent-portworx
  labels:
    observability.suse.com/agent: scrape
spec:
  selector:
    matchLabels:
      name: portworx
  endpoints:
    - port: px-api
      path: /metrics
      interval: 60s
      # Keep the Portworx 'namespace' label (the PVC namespace) instead of renaming it to exported_namespace.
      honorLabels: true
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: px_.*
          action: keep
        # px_volume_* series copy every label of the PVC; keep only the labels Portworx itself defines.
        - regex: __name__|job|instance|cluster|clusterUUID|node|nodeID|nodeid|pool|poolid|disk|proc|coordinator|target|volumeid|volumename|namespace|pvc|repl|kube_datastore|le|quantile
          action: labelkeep
```

The `labelkeep` rule matters: Portworx adds every label of a PVC to its volume metrics, which can create many series. If the Portworx `Service` with label `name: portworx` doesn't exist, point `selector` at the service that exposes port `px-api`.

## 3. Let the agent read the Portworx resources

Add the Portworx API group to the agent's Kubernetes resource collector, in the agent Helm values:

```yaml
otel:
  enabled: true
  k8sResourceCollector:
    crDiscovery:
      apiGroups:
        include:
          core.libopenstorage.org: true
```

Then upgrade the agent, for example:

```bash
helm upgrade suse-observability-agent suse-observability/suse-observability-agent \
  -n suse-observability --reuse-values \
  --set 'otel.k8sResourceCollector.crDiscovery.apiGroups.include.core\.libopenstorage\.org=true'
```

If a Rancher app, a Fleet bundle or a Harvester add-on manages the agent, change its values there instead, or the next sync reverts the change.

## 4. Install the StackPack

Install this StackPack. Portworx clusters, storage nodes and volumes appear under **Portworx** in the main menu within a few minutes.
