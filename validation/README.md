# BCI minimal 15.7-26.60 candidate evidence

Evidence-only branch; do not merge generated reports into main.

Source PR: https://github.com/StackVista/contrib-stackpacks/pull/23
Signed source head: `4860675d7102d1b359358617e0d2e29ed602dfd5`
CI: https://github.com/StackVista/contrib-stackpacks/actions/runs/35433171800
CI synthetic merge: `1177d894ba0465b8224c4a239f474788475f5a6c` (source tree equals source head).

Candidate: `quay.io/stackstate/contrib-stackpacks:20260919085222-refresh-bci-minimal-pcre2-glibc-1177d89`
Index: `sha256:8b8d99fe3f5b24b0d21bf715efd7bbb8f6895cbd375ce7668d44a3bf6b36c1ee`
Base: `registry.suse.com/bci/bci-minimal:15.7-26.60`, index `sha256:fecc13ede4c24c1bc7d4b0131f5396b8d226d15b38d83bedb21474f349872f9f`.

Reports were generated on 2026-09-19 with Trivy 0.74.0 and Grype 0.117.0 (database built 2026-09-19T06:27:50Z). Trivy database downloaded fresh on that date. Local scans used all severities, no VEX, no exceptions, no ignores. Both architectures report zero vulnerabilities, secrets, Grype matches and ignored matches. The reports record resolved target identities. CI separately passed its existing scan gate and all three StackPack validations, packages and version checks.

Commands (substitute architecture and corresponding digest from candidate-index.json):

```sh
trivy image --image-src remote --platform linux/arm64 --scanners vuln,secret --list-all-pkgs --format json IMAGE
 grype registry:IMAGE --platform linux/arm64 -o json
```

Published amd64 runtime test passed at UID 1001 with read-only root, all capabilities dropped, no-new-privileges and writable tmpfs test directories. The chart copy script cleared a stale file and copied all three packages; source and destination SHA-256 values matched. An earlier local build reused PR22's package artifacts and passed the same behavior. Native arm64 execution was not tested; arm64 coverage is publication, inventory and scans.

The source PR changes only the base and OCI base label. Chart adoption and a new delivery scan are pending human-approved main publication. This is candidate evidence, not production delivery evidence.
