The Portworx StackPack is installed and waiting for data.

If nothing appears after a few minutes, check that:

- the `so-agent-portworx` ServiceMonitor exists and carries the label `observability.suse.com/agent: scrape`;
- the agent has OpenTelemetry enabled (`otel.enabled: true`) and `core.libopenstorage.org` in `otel.k8sResourceCollector.crDiscovery.apiGroups.include`;
- `curl http://<node-ip>:9001/metrics` on a Portworx node returns `px_*` metrics.

See the configuration steps above.
