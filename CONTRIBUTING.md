# Contribute a community StackPack

Community StackPacks are not supported by SUSE. Contributors maintain their
integrations: answer issues, update compatibility information and fix broken
behavior. SUSE maintainers review pull requests for validity and safety, not for
production readiness. This follows the
[SUSE community-blueprints model](https://github.com/SUSE/community-blueprints/blob/main/CONTRIBUTING.md).

## Add or update a StackPack

1. Add your integration under `stackpacks/<name>/`. Use a lowercase name with
   dash-separated words. The directory name must match `name` in
   `stackpack.yaml`.
2. Add a README with a `Maintainer: @github-handle` line. List prerequisites,
   tested product versions, required permissions and parameters, installation
   instructions, and how to remove the integration.
3. Add the package definition, settings, resources and any icons or includes.
   Use a `major.minor.patch` version, optionally followed by a prerelease suffix.
   Image tags combine the StackPack name and this version, so build metadata
   with `+` is not accepted.
4. Increase the version when changing an existing StackPack. Published version
   tags are immutable.
5. Package and validate locally, then open a pull request. CI checks the
   definition, mapping expressions, maintainer and version; packages the
   integration; builds both image architectures; and scans secrets and
   vulnerabilities.

Use the [authoring skill](.agents/skills/create-stackpack/SKILL.md) for the CLI
workflow and current schema documentation. The CI workflow pins the platform
validator image used by `scripts/ci/validate_stackpack.sh`:

```sh
export VALIDATOR_IMAGE='<validator image and digest from the CI workflow>'
bash scripts/ci/validate_stackpack.sh stackpacks/my-integration
sts stackpack package --directory stackpacks/my-integration
```

Only modify integrations you maintain, unless you agree on the change with their
maintainers. A change of maintainer must update the README. A SUSE maintainer
merges a contribution after checks pass and reviews approve.

## Keep the integration usable

State any compatibility limits in the README. Respond to reported failures and
update the integration when its dependencies change. If you stop maintaining it,
open an issue to find a replacement maintainer.

SUSE maintainers may mark an integration as unmaintained or remove it after
contacting its maintainer about unresolved breakage. Record the status and
replacement options in the issue before removal. Review and inclusion do not
create a SUSE support or security-update commitment.
