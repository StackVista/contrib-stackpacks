# Release notes

## 0.1.0

- Portworx clusters as components (from the `StorageCluster` resource), with Portworx state merged into Kubernetes nodes and persistent volumes.
- Metrics for clusters, storage nodes and volumes.
- 20 monitors: the Portworx operator's Prometheus alert rules, plus per-pool "nearly full", pool degraded, volume down/error and volume filesystem health.
- Dashboards: Cluster overview, Volumes, Nodes and pools.
