# Service Availability

A declarative StackPack 2.0 integration for HTTP and HTTPS checks collected by
Prometheus Blackbox Exporter through the SUSE Observability OTel Prometheus
scraper. See [setup instructions](resources/configuration.md).

The pack creates one `http endpoint` component per URL and an availability
monitor. The optional `availability_service` label groups multiple URLs under an
`availability service` component with its own availability monitor.
**Service Availability → Endpoints** and **Services** provide overviews and
highlight pages. TLS certificate validity is displayed when available. Optional
certificate monitors warn below 14 days and report Critical below two days.
Certificate expiration is shown as a duration in the overview. The time-series
chart shows whole days with a vertical axis starting at zero. An orange dotted
line marks the default 14-day warning threshold; a red dotted line marks the
two-day critical threshold.

## Telemetry contract

| Input | Purpose |
| --- | --- |
| `probe_success` | Creates endpoint topology and reports whether the endpoint check succeeded. |
| `up` | Creates endpoint topology even when the first scrape fails, and makes availability Critical when a scrape fails. |
| `probe_http_status_code` | Displays the received HTTP status. |
| `probe_duration_seconds` | Displays total probe duration. |
| `probe_ssl_earliest_cert_expiry` | Optional Unix timestamp of the earliest certificate expiration. |
| Datapoint label `service_availability="true"` | Opts a target into this integration. |
| Datapoint label `endpoint` | The complete target URL, including its path and query. |
| Datapoint label `availability_service` | Optional nonempty identity grouping endpoints into a service. |
| Datapoint label `monitor_certificate_expiry="true"` | Opts targets into expiration checks when TLS certificate data is reported, including HTTP redirects to HTTPS. |

These metric and attribute names are the Blackbox/Prometheus contract, not
OpenTelemetry semantic conventions. The Probe example preserves target identity
in `endpoint`, independently of the Prometheus receiver's conversion of `job`
and `instance` to OTel resource attributes.

The Probe example uses `http_2xx`, which follows redirects and requires a final
2xx response. The optional `http_available` module implements the below-400
policy without following redirects. Both supply the same metrics; availability
uses the selected module's `probe_success` result. For an existing exporter,
check additional module constraints, such as requiring HTTPS.

Topology identifier: `urn:service-availability:endpoint/<endpoint URL>`.
The monitor constructs the same identifier from its `endpoint` result label.
The same URL checked by multiple Probes has one component; the monitor uses the
minimum success value, so any failing observation makes it critical. Different
paths or queries are separate endpoints.

Service identifier: `urn:service-availability:service/<availability_service>`.
The service mapping and monitor share this identity, and a hierarchical relation
links the service to every endpoint. Use environment-qualified service identities
when the same service name should represent separate installations.

Availability monitors run every minute against the latest samples, with no
additional five-minute failure delay. Any failing observation makes its endpoint
critical; any failing check labeled for a service makes that service critical.
The two optional certificate monitors run every five minutes and report
Deviating below 14 days remaining and Critical below two days. They use reported
TLS certificate data, including HTTP targets that redirect to HTTPS. Plain HTTP
targets without TLS, missing timestamps and zero timestamps produce no
certificate result.

Components and relations expire after 15 minutes without matching metrics.
The service monitor aggregates observed samples; it cannot detect a missing URL
without an inventory of expected targets. A disappearing URL can reduce the
displayed endpoint count. Missing telemetry is not evidence of successful checks.
Runtime topology, health and UI behavior require validation on an instance.

## Development

```bash
sts stackpack package -d stackpacks/service-availability
sts stackpack validate -d stackpacks/service-availability
```

The repository CI discovers this directory automatically. For offline validation,
use the `VALIDATOR_IMAGE` selected by `.github/workflows/stackpacks-ci.yml`:

```bash
bash scripts/ci/validate_stackpack.sh stackpacks/service-availability
```

The manifest follows the StackPack SDK's `YamlReader` in
`StackVista/stackpacks`. Setup instructions use `configurationUrls` because the
SDK ignores the legacy `detailedOverviewUrl` field for schema 2.0. The same
instructions remain available after installation.

On an explicitly selected development instance, test installation with:

```bash
sts stackpack test-deploy -d stackpacks/service-availability --yes
```

With `http_2xx`, verify that a 200 is healthy and redirects succeed only when
their final response is 2xx. With `http_available`, verify that a 302 is healthy
without following the redirect. Verify that a 404 or 500, connection errors and
TLS validation errors are critical with both modules. Check that a failed target
still creates its component, duplicate URLs merge, and non-opted-in probes do
not create components. Group two URLs under one service and verify that either
URL failing makes that service critical. Check that unlabeled URLs remain
standalone endpoints.

For certificate warnings, verify certificates inside and outside the 14-day
window, opt-out targets, HTTP targets, and missing or zero timestamps. Valid
certificates inside the warning window should keep availability clear while
the certificate monitor warns. Inspect both overviews, the highlights and the
service-to-endpoint relations.
