# Portworx StackPack

Monitors Portworx Enterprise 3.x on Kubernetes. User-facing setup is in `resources/configuration.md`.

## Data path

- **Metrics**: the agent's OpenTelemetry metrics scraper reads a `ServiceMonitor` labelled `observability.suse.com/agent: scrape` on the Portworx service (port `px-api`, `/metrics`). Metric names stay as Portworx emits them (`px_*`), plus `k8s_cluster_name`. The ServiceMonitor keeps only Portworx's own labels, because `px_volume_*` series copy every PVC label.
- **Topology**: the agent's Kubernetes resource collector sends `StorageCluster` and `StorageNode` custom resources (API group `core.libopenstorage.org`) as `KubernetesCustomResourceEvent` logs.

## Topology

- `settings/component-mappings/cluster.sty`: one `portworx cluster` component per `StorageCluster` (`urn:portworx:/<k8s cluster>:cluster/<name>`).
- `settings/component-mappings/storage-nodes.sty`: each `StorageNode` adds `urn:portworx:/<k8s cluster>:node/<name>` to the Kubernetes node (via `additionalIdentifiers`). It ranks below the Kubernetes node, so the node keeps its type and gets the `source-type:portworx node` label.
- `settings/component-mappings/volumes.sty`: Portworx has no resource per volume, so `px_volume_replication_status` (the only volume metric reported for every volume, attached or not) adds `urn:portworx:/<k8s cluster>:volume/<pv name>` to the Kubernetes persistent volume. The label `volumename` is the PV name.
- Relations: node `member of` cluster, volume `provided by` cluster.

## Metrics, monitors and dashboards

- Presentations add a **Portworx** metrics tab to clusters, storage nodes and volumes, plus a **Portworx** main menu group with the three lists.
- Monitors port the Portworx operator's `PrometheusRule` (`portworx`) alerts with the same thresholds, and add per-pool "nearly full" (Portworx marks a pool full below min(10%, 100 GiB) free), pool degraded, volume down/error and filesystem health. Pool status ignores maintenance (4) and background activity (6). Status codes are compared with `bool`, so healthy components report 0 instead of no data.
- Volume metrics are reported by every node that holds a replica, and some of those series carry only `volumeid`, so volume queries use `max by` and `volumename!=""`.
- `px_volume_reads_total` / `px_volume_writes_total` carry only `volumeid`. Per-volume IOPS use the `px_volume_read_iops` / `px_volume_write_iops` gauges.
- Volume performance metrics only exist while a volume is attached.
- A volume with no matching Kubernetes PV stays a standalone `portworx volume` component. On the test cluster, one Portworx node kept exporting series for two deleted volumes, so they showed up this way until the series stopped.

## Tested with

Portworx 3.7.1 (operator-installed, internal KVDB) on a 3-node RKE2 / SUSE Virtualization cluster, with agent chart 1.6.12.
