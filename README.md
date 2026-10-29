# contrib-stackpacks
SUSE Observability Community Stackpacks

Use the [Create a StackPack agent skill](.agents/skills/create-stackpack/SKILL.md) to
create or extend an integration with the latest StackPack documentation, the `sts`
CLI, and MCP queries for runtime validation.

Codex, Antigravity, and Gemini CLI load the skill from `.agents/skills/`.
Claude Code loads it through the `.claude/skills/create-stackpack` symlink.
For other projects, copy the `create-stackpack` directory into your assistant's
supported skill directory.
