## Portworx StackPack

The Portworx StackPack shows your Portworx clusters, storage nodes and volumes in SUSE Observability and tracks their health with monitors ported from the Portworx operator's alert rules.

### What you get

- **Portworx clusters** as components (from the `StorageCluster` resource), linked to their storage nodes and volumes.
- **Storage nodes**: Kubernetes nodes that run Portworx get Portworx state (phase, version, KVDB membership) and a **Portworx** metrics tab.
- **Volumes**: Kubernetes persistent volumes that Portworx provides get a **Portworx** metrics tab (usage, replication, latency, IOPS, throughput).
- **Monitors** with Portworx's own thresholds and alert conditions:
  - volume usage above 70% / 80%
  - volume replication unhealthy, volume down or in error, volume filesystem errors
  - storage node usage above 70% / 80%, and storage that will fill within 2 weeks
  - storage node not OK; storage pool offline, full, degraded or nearly full (per pool)
  - storage node down, cluster member down, quorum lost
  - KVDB unhealthy
  - license expiring or invalid
- **Dashboards**: *Portworx - Cluster overview*, *Portworx - Volumes* and *Portworx - Nodes and pools*, modelled on the Portworx Grafana dashboards.

### How it works

The SUSE Observability agent scrapes the Portworx metrics endpoint through a `ServiceMonitor` and reads the Portworx custom resources with its Kubernetes resource collector. No Prometheus server is needed.
