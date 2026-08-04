## Installation

You can click on `Install` to install the Open Telemetry StackPack. Then follow the instructions here and in [the documentation](https://l.stackstate.com/open-telemetry-setup) to finish the Open Telemetry setup.

When installing or upgrading the SUSE Observability Agent with Helm, enable Open Telemetry support with:

```bash
--set otel=true
```

You can also control Rancher enrichment for Open Telemetry logs:

```bash
--set otel.integrations.rancherAgent=true
```

or

```bash
--set otel.integrations.rancherAgent=false
```

Set `otel.integrations.rancherAgent=true` on Rancher-managed clusters to enrich emitted logs with Rancher Manager URL and Harvester cluster ID metadata. Keep it `false` on non-Rancher clusters (default).
