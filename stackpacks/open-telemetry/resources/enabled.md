## The Open Telemetry StackPack is installed

### What's next

Instrument one or more applications with Open Telemetry SDKs to generate traces and metrics and install and configure the Open Telemetry collector to send data to SUSE Observability. See the [SUSE Observability Open Telemetry documentation](https://l.stackstate.com/open-telemetry-setup).

If you install or upgrade the SUSE Observability Agent with Helm, make sure Open Telemetry support is enabled:

```bash
--set otel=true
```

On Rancher-managed clusters, set:

```bash
--set otel.integrations.rancherAgent=true
```

On non-Rancher clusters, keep the default:

```bash
--set otel.integrations.rancherAgent=false
```

To send data to SUSE Observability a service token is needed.

<button value="/#serviceToken" style="width: 100%">CREATE NEW SERVICE TOKEN</button>
