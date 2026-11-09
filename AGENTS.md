# Repository safety rules for AI agents

## Mandatory third-party repository security gate

Before downloading, cloning, installing, executing, importing, or using code from an external repository:
1. Confirm its owner, canonical URL, purpose, and exact commit SHA/tag. Inspect the GitHub file tree and setup scripts without executing untrusted code. If available, use Erinyes remote sweep to pre-screen before cloning.
2. If you obtain a checkout, keep it isolated and run a verified, version-pinned [Erinyes](https://github.com/CarterPerez-dev/erinyes) binary with `erinyes scan <path> --format markdown` BEFORE installing dependencies, running scripts, opening executable project tasks, or importing code. Never install a scanner through an unreviewed `curl | bash` command.
3. Inspect install hooks, obfuscation, suspicious network behavior, workflow permissions, dependency lockfiles, and possible secrets. Review scanner warnings; a clean Erinyes scan does NOT prove safety.
4. If Erinyes cannot be run, mark **SCAN NOT PERFORMED**, do not claim that the repo is safe, and do not execute or use third-party code unless the user approves another reviewed security workflow.
5. Document the reviewed repository URL, commit, scanner version, date, outcome, and any residual risk. Recheck whenever the upstream commit/version changes. Never put secrets in committed source; rotate exposed credentials.

Applies to ChatGPT, Claude Code, ChatGPT Work, and other coding agents operating in this repository. Never silently skip the check.

## Existing credential issue
The Python script in this public repository was found on 2026-11-09 to contain a hardcoded Gmail app password. Treat that password as compromised: the account owner must revoke it and remove the literal secret from code and Git history. Do not repeat, log, or reuse it.
