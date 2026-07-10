# Notification Operator StackPack

This StackPack provides monitoring and metrics for the Notification Operator, which manages notifications in SUSE Observability through Kubernetes Custom Resources (CRs).

## What's Included

This StackPack provides:
- **Monitors**: Health checks for controller reconciliation errors, notification sync status, and disabled notifications
- **Metric Bindings**: Charts for reconciliation rates and notification status tracking
- **Remediation Hints**: Guided troubleshooting for common notification operator issues

## Project Structure

```
notification-operator/
├── README.md
├── provisioning/
│   ├── metricbindings.sty          # Notification operator metric charts
│   ├── monitors.sty                # Health monitors for notification operator
│   ├── remediation-hints/          # Troubleshooting guides
│   │   ├── controller-reconcile-errors.md.hbs
│   │   ├── notification-disabled.md.hbs
│   │   └── notification-not-synced.md.hbs
│   └── stackpack.sty               # Main provisioning template
├── resources/                      # UI resources and documentation
│   ├── deprovisioning.md
│   ├── error.md
│   ├── installed.md
│   ├── logo.png
│   ├── notinstalled.md
│   ├── overview.md
│   ├── provisioning.md
│   └── waitingfordata.md
└── stackpack.conf                  # StackPack configuration
```


## Prerequisites

The notification operator must be deployed in your Kubernetes cluster with the following requirements:
- The notification operator pod must be labeled with `app.kubernetes.io/name=notification-operator`
- The operator must expose Prometheus metrics on the standard `/metrics` endpoint
- SUSE Observability must have access to scrape metrics from the notification operator pod

## Monitors Included

This StackPack provides the following monitors:

### Controller Runtime Reconcile Errors
- **Purpose**: Detects errors in the controller runtime reconcile process
- **Metric**: `increase(notification_operator_controller_runtime_reconcile{result="error"}[10m])`
- **Threshold**: Any increase in errors triggers a CRITICAL alert
- **Remediation**: Includes troubleshooting hints for common reconciliation issues

### Enabled Notification Resources Not Synced
- **Purpose**: Identifies enabled notifications that are not properly synced
- **Metric**: `sum(notification_operator_suse_observability_notification_enabled == 1 and notification_operator_suse_observability_notification_synced == 0)`
- **Threshold**: Any unsynced enabled notifications trigger a CRITICAL alert
- **Remediation**: Provides guidance for resolving synchronization issues

### Notification Disabled
- **Purpose**: Tracks disabled SUSE Observability notifications
- **Metric**: `sum(notification_operator_suse_observability_notification_enabled == 0)`
- **Threshold**: Any disabled notifications trigger a DEVIATING alert
- **Remediation**: Explains why notifications might be disabled and how to re-enable them

## Metric Bindings Included

### Total Reconciliations per Controller/Cluster
- **Chart Type**: Line chart
- **Metric**: `sum(increase(notification_operator_controller_runtime_reconcile[1m])) by (cluster_name, result)`
- **Purpose**: Shows reconciliation activity and success/failure rates over time

### Notification Sync Status
- **Chart Type**: Line chart
- **Metric**: `sum(notification_operator_suse_observability_notification_synced) by (cluster_name, name)`
- **Purpose**: Shows whether notifications are properly synced with SUSE Observability

### Notification Enabled Status
- **Chart Type**: Line chart
- **Metric**: `sum(notification_operator_suse_observability_notification_enabled) by (cluster_name, name)`
- **Purpose**: Shows whether notifications are enabled or disabled

## Installation

1. **Deploy the Notification Operator** in your Kubernetes cluster following the operator's installation guide
2. **Ensure proper labeling** of the notification operator pod with `app.kubernetes.io/name=notification-operator`
3. **Install this StackPack** through the SUSE Observability UI or CLI
4. **Verify metrics collection** by checking that the notification operator metrics are being scraped

## Troubleshooting

If monitors are not triggering or metrics are not appearing:

1. **Check pod labeling**: Verify the notification operator pod has the correct label
2. **Verify metrics endpoint**: Ensure the operator exposes metrics on `/metrics`
3. **Check network access**: Confirm SUSE Observability can reach the operator pod
4. **Review logs**: Check both notification operator and SUSE Observability logs for errors

## Development and Customization

To modify this StackPack:

1. **Edit monitors**: Modify `provisioning/monitors.sty` to adjust thresholds or add new monitors
2. **Update metric bindings**: Edit `provisioning/metricbindings.sty` to create custom charts
3. **Add remediation hints**: Create new `.md.hbs` files in `provisioning/remediation-hints/`
4. **Package and test**: Use `sbt notification-operator/package` to build the StackPack

For more details on StackPack development, see the main repository documentation.
