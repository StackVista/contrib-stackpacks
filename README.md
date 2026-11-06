# Community StackPacks

This repository contains community integrations for SUSE Observability.
Customers choose which integrations to add; these StackPacks do not ship with
the product by default.

Community StackPacks are maintained by their contributors and are not supported
by SUSE. SUSE maintainers review contributions for validity and safety. Approval
does not provide a support commitment or a production-readiness guarantee.

| Repository | Content and ownership |
| --- | --- |
| [core-stackpacks](https://github.com/StackVista/core-stackpacks) | Core integrations maintained by the SUSE Observability team and shipped with the product. |
| [suse-stackpacks](https://github.com/StackVista/suse-stackpacks) | Internal integrations for SUSE products, maintained by their product teams. |
| contrib-stackpacks | Integrations for other technologies, maintained by the community and installed by customers. |

## Add a StackPack image

Each StackPack has its own container image:
`quay.io/stackstate/contrib-stackpacks:<name>-<version>`. The tag combines the
StackPack name and version in its `stackpack.yaml`. Images contain one `.sts`
package in `/stackpacks` and support AMD64 and ARM64.

Add the image to your SUSE Observability Helm values. Replace the example name
and version with a published StackPack:

```yaml
stackstate:
  stackpacks:
    extraImages:
      - name: my-integration
        registry: quay.io
        repository: stackstate/contrib-stackpacks
        tag: "my-integration-0.0.1"
        pullPolicy: IfNotPresent
```

Apply the values through your normal Helm upgrade process. Keep this entry on
later upgrades. The image makes the StackPack available in the catalog; install
an instance through the UI or `sts stackpack install`.

You can use an image from another registry by changing `registry`, `repository`
and `tag`. For a private registry, configure `global.imagePullSecrets` with a
Kubernetes image-pull secret in the SUSE Observability namespace. The image must
contain readable `.sts` files in `/stackpacks` and `/bin/sh` for the chart's copy
script. Use a unique image `name` for each entry.

## Upload a package with the CLI

Download the `sts-<name>` artifact from the StackPack's successful
[CI run](https://github.com/StackVista/contrib-stackpacks/actions), or package a
local checkout:

```sh
sts stackpack package --directory stackpacks/my-integration
```

Configure the `sts` CLI for your SUSE Observability instance, then upload the
package:

```sh
sts stackpack upload --file ./my-integration-0.0.1.sts
sts stackpack list-parameters --name my-integration
sts stackpack install --name my-integration
```

Upload makes the version available; installation creates an instance. Supply the
parameters described in the StackPack's README when installing. Pull-request
artifacts use snapshot versions; published main images use the declared version.

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). Every StackPack needs a named maintainer
and instructions for prerequisites, installation, required parameters and removal.

The [Create a StackPack agent skill](.agents/skills/create-stackpack/SKILL.md)
helps create integrations with the StackPack documentation and CLI. Codex,
Antigravity and Gemini CLI load it from `.agents/skills/`; Claude Code loads the
`.claude/skills/create-stackpack` symlink.

## Publish public images

CI validates and packages contributions from forks without publication
credentials. Main-branch pushes build, scan and sign one image per StackPack in
the existing public Quay repository using its dedicated `QUAY_USER` and
`QUAY_PASSWORD` credentials. Tags combine the StackPack name and package version
and are never overwritten. The workflow checks image access without credentials
after publication; a rerun reuses an existing version.

The image's source label connects the image to this repository. Before
announcing a StackPack, verify that both architecture images can be pulled
without credentials.
