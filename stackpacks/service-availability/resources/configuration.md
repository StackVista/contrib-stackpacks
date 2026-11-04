# Configure service availability checks

The data flow is:

```text
Probe → Target Allocator → OTel Prometheus scraper → Blackbox Exporter
                               ↓                       ↓
                        SUSE Observability        HTTP(S) endpoint
```

The Target Allocator discovers the Probe and gives the scraper its scrape job.
The scraper calls Blackbox Exporter's `/probe` endpoint with the target URL.
Blackbox Exporter performs the check and returns metrics, which the scraper
forwards to SUSE Observability. This StackPack turns those metrics into endpoint
components and health checks. It also uses the scraper's `up` metric to detect
failed scrapes, including exporter connection errors, scrape timeouts and unknown
modules.

## Install Blackbox Exporter

Use the **Prometheus Blackbox Exporter** chart from **SUSE Application Collection
(AppCo)**, available at
[SUSE Application Collection](https://apps.rancher.io/). Follow Application
Collection's access instructions to authenticate Helm and create its image pull
secret in the `monitoring` namespace.

Save the following as `blackbox-values.yaml`. Set `appco-credentials` to the name
of your Application Collection image pull secret. The Probe example uses
`http_2xx`, which follows redirects and requires a final 2xx response. The
optional `http_available` module accepts responses below 400 without following
redirects.

```yaml
global:
  imagePullSecrets:
    - appco-credentials
config:
  modules:
    http_2xx:
      prober: http
      timeout: 5s
      http:
        follow_redirects: true
    http_available:
      prober: http
      timeout: 5s
      http:
        follow_redirects: false
        valid_status_codes:
          [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
           112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
           124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
           136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147,
           148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
           160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171,
           172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183,
           184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,
           196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
           208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
           220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
           232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
           244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
           256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267,
           268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279,
           280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291,
           292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303,
           304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315,
           316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327,
           328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339,
           340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351,
           352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363,
           364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375,
           376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387,
           388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399]
```

Blackbox defaults to accepting 200–299 when no accepted status codes are listed.
The `http_available` module lists 100–399 explicitly to implement the below-400
policy. The modules above support HTTP and HTTPS and keep normal TLS certificate
and hostname verification enabled. Do not enable `insecure_skip_verify` when
certificate validation is part of the availability check.

Install through your deployment tooling, or use Helm:

```bash
helm upgrade --install prometheus-blackbox-exporter \
  oci://dp.apps.rancher.io/charts/prometheus-blackbox-exporter \
  --namespace monitoring --create-namespace \
  --values blackbox-values.yaml
```

For an existing exporter, use its `http_2xx` module if it meets your requirements.
Check its configuration: existing modules may add constraints such as
`fail_if_not_ssl: true`, which requires HTTPS. Merge any additional modules into
the current configuration rather than replacing modules used by other checks.
Use a chart version approved for your environment.

To use the below-400 policy, add `http_available` and set the Probe's
`spec.module` to `http_available`. Both modules supply the same metrics, so the
StackPack mappings and monitors work with either. The selected module determines
which responses are healthy.

## Enable Probe discovery

Merge these overrides into your existing SUSE Observability agent installation:

```yaml
otel:
  enabled: true
  prometheusScraping:
    monitorCrds:
      enabled: true
```

Prometheus scraping is enabled by default. If your existing values explicitly
disable it, also set `otel.prometheusScraping.enabled: true`.
The chart's default Probe selector matches `observability.suse.com/agent: scrape`,
as used in the example below, and its default namespace selector includes all
namespaces. If your installation overrides these selectors, use matching Probe
labels and include the `monitoring` namespace.

`monitorCrds.enabled: true` installs the ServiceMonitor, PodMonitor and Probe
CRDs. Omit this override when those CRDs are already managed by another chart
or deployment tool.

The scraper must reach the exporter, and the exporter must reach each endpoint, including DNS
and HTTPS connections. An internal endpoint is supported when it is reachable
from the exporter's network.

## Create a Probe

Create this resource through your Kubernetes deployment tooling.
**Replace all uppercase `REPLACE_WITH_...` values and the example URLs before creating the Probe.** Keep the label
name `availability_service`; replace its value with your own service identity.
Multiple targets can be listed under `static`; their full URLs identify separate
endpoint components. The example groups both URLs under one service and enables
optional certificate expiration warnings.

`spec.jobName` can be any descriptive scrape job name; `service-availability`
was only an example. The StackPack does not select targets by job name.
It selects targets using `service_availability: "true"` and identifies each
endpoint by its `endpoint` label. The optional `availability_service` label
provides the service identity, independently of `jobName`.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata:
  name: REPLACE_WITH_YOUR_PROBE_NAME
  namespace: monitoring
  labels:
    observability.suse.com/agent: scrape
spec:
  jobName: REPLACE_WITH_YOUR_JOB_NAME
  interval: 60s
  scrapeTimeout: 10s
  module: http_2xx
  prober:
    url: prometheus-blackbox-exporter.monitoring.svc.cluster.local:9115
    scheme: http
    path: /probe
  targets:
    staticConfig:
      static:
        - https://example.com/health
        - https://example.com/api/ready
      labels:
        service_availability: "true"
        availability_service: REPLACE_WITH_YOUR_SERVICE_NAME
        monitor_certificate_expiry: "true"
      relabelingConfigs:
        - sourceLabels: [__param_target]
          targetLabel: endpoint
```

| Field | What to change |
| --- | --- |
| `metadata.name` | Replace `REPLACE_WITH_YOUR_PROBE_NAME` with a valid lowercase Kubernetes resource name, such as `checkout-health`. |
| `spec.jobName` | Replace `REPLACE_WITH_YOUR_JOB_NAME` with your scrape job name. |
| `targets.staticConfig.static` | Replace `https://example.com/health` and `https://example.com/api/ready` with your complete HTTP or HTTPS URLs, including the correct paths. Add or remove URLs as needed. |
| `targets.staticConfig.labels.availability_service` | Replace `REPLACE_WITH_YOUR_SERVICE_NAME` with a service identity such as `production/my-service`. Remove this label if you do not want service grouping. |
| `metadata.namespace` and `spec.prober.url` | Adjust if your Probe or exporter uses a different namespace, or the exporter has a different service name. |
| `targets.staticConfig.labels.monitor_certificate_expiry` | Keep `"true"` to enable certificate checks; set `"false"` or remove the label to disable them. |

If the exporter uses a different release name or namespace, adjust `prober.url`.
The relabeling copies the complete target URL into the `endpoint` metric label.
Keep this relabeling and the `service_availability` label: they are the contract
used by the topology mapping, monitor and presentation. For an existing Probe,
add both to its `targets.staticConfig`. Set `spec.module` to `http_2xx`, or to
`http_available` after configuring that optional module in the exporter.
The interval can be changed; keep it well below the 15-minute topology expiry.

Do not put credentials in a target URL or its query string: that URL is stored
as a metric label and shown in the UI. Configure authentication separately in
the exporter's HTTP module when an endpoint requires it.

## Monitor several URLs for one service

Set `availability_service` to the same nonempty value on the targets of each
Probe belonging to a service. One Probe can list several URLs, as above. Separate
Probes can use the same service label when URLs need different modules, scrape
intervals, or certificate warning settings.

The StackPack creates a service component and links it to each endpoint. Open
**Service Availability → Services**, then select a service to inspect its related
endpoints. The service availability monitor becomes critical when any of its
currently observed endpoint checks or scrapes fails. Each URL also retains its own
availability monitor and highlight page.

Use a unique service identity across your monitored environments, for example
`production/checkout` and `staging/checkout`, if they should be separate services.
Omit `availability_service` to monitor URLs individually without creating a
service component. Every URL assigned to a service contributes to availability;
monitor optional dependencies separately.

The service monitor uses available `probe_success` and `up` samples, rather than
an inventory of expected URLs. A failed scrape reports `up=0`, so its URL remains
in the monitored endpoint count and makes availability Critical. If the scraper
stops emitting both metrics entirely for a URL, its absence is not automatically
counted as a failure. Services and relations expire 15 minutes after their last
matching metric.

## Optional certificate expiration warnings

Blackbox reports `probe_ssl_earliest_cert_expiry` when a TLS certificate is
available, including HTTP targets that redirect to HTTPS. Both certificate
monitors use the reported certificate data regardless of the target's initial
HTTP or HTTPS scheme. Plain HTTP checks without TLS have no certificate result.
The **Certificate expires in** overview column shows the remaining validity
as a duration until the earliest expiration in the
certificate chain. The chart in the **TLS certificate** highlight section shows
whole days, rounded down, so less than one day remaining displays as zero.
The time-series chart uses the days unit with zero decimal places and a vertical
axis starting at zero, representing expiration. An orange dotted line marks
the 14-day warning window; a red dotted line marks the two-day critical window.
The UI labels these lines **Threshold 1** and **Threshold 2**; custom threshold
names are not supported. If you change a monitor threshold, update its chart
reference to match. Checks without certificate data show no value, rather
than zero.

To enable both certificate monitors, add `monitor_certificate_expiry: "true"`
to the Probe's `targets.staticConfig.labels`. Omit the label or set it to
`"false"` to disable certificate checks for those targets. No separate exporter
module or StackPack is required.

Both monitors evaluate every five minutes using the exact remaining duration,
not the chart's rounded days. **Endpoint certificate expiring** reports
**Deviating** below 14 days. **Endpoint certificate expiration imminent** reports
**Critical** below two days. Below two days both checks fail, and the endpoint's
combined health is Critical. At exactly two days only the warning fails; at
exactly 14 days neither certificate check fails.

Adjust each threshold in the Monitors UI if needed. Values are in seconds:
14 days is `1209600`, and two days is `172800`.

An expired or otherwise invalid certificate still fails the availability probe,
even when certificate warnings are disabled. When TLS negotiation fails,
Blackbox may not report an expiration timestamp; the availability monitor then
reports the failed check. Missing or zero expiration values are excluded from
both certificate monitors.

## Install the StackPack and verify

Install **Service Availability** from the StackPacks page after making its
package available to your instance. No installation parameters or additional
topology StackPacks are needed.

In the Metrics Explorer, run:

```promql
probe_success{service_availability="true"}
```

Each result should have an `endpoint` label and a value of `1` for healthy or `0`
for unhealthy. Also run:

```promql
up{service_availability="true"}
```

Each scheduled target should have an `endpoint` label. A value of `1` means the
scrape succeeded; `0` means it failed. A successful scrape can still report
`probe_success=0` when the application is unhealthy. Both metrics contribute to
the endpoint and service availability monitors: any zero makes them Critical.
Check that `probe_http_status_code` and `probe_duration_seconds`
also have these labels.
For grouped endpoints, check that `availability_service` has your service name.
For certificate warnings, check that `probe_ssl_earliest_cert_expiry` has the
`endpoint` and `monitor_certificate_expiry` labels.

Open **Service Availability → Endpoints**. Each URL has a component. A failed
check or scrape makes its availability monitor critical on the next evaluation; a
successful check clears that monitor. Certificate checks can still keep the
endpoint Deviating or Critical. The overview shows health, HTTP status and probe
duration. The highlight shows health and metric history, including certificate validity when
reported. **Service Availability → Services** lists grouped services and their
monitored endpoint counts.

If the same URL is checked by multiple Probes, any failing observation makes
its single component critical. Missing telemetry is not converted to success.
An unreachable exporter, an unknown module, or a failed scrape can produce
`up=0` without `probe_success`. These collection failures now make the endpoint
Critical and still create its component, including on the first scrape.
If the collector stops sending both metrics, an independent expected-target
inventory or collection-health monitor is needed to detect the missing data.
If a Probe is removed or its data stops arriving, its component expires
15 minutes after the last matching metric.

For a direct diagnostic, port-forward the exporter service:

```bash
kubectl -n monitoring port-forward svc/prometheus-blackbox-exporter 9115:9115
```

Then, in another terminal:

```bash
curl --get 'http://localhost:9115/probe' \
  --data-urlencode 'module=http_2xx' \
  --data-urlencode 'target=https://example.com/health' \
  --data-urlencode 'debug=true'
```

Use the same module as your Probe. An HTTP 400 response with `Unknown module`
means the exporter has no module with that name; configure it or select an
existing module. A completed probe returns metrics even when the endpoint is
unhealthy.

If the check succeeds here but metrics are missing in Observability, inspect the
Probe selector, Target Allocator, scraper logs and exporter connectivity.
If the endpoint returns an HTTP error or a connection/TLS failure, investigate
the application and the exporter's network path.
