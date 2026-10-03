# SIMA Phase 0 — Fix 07 (Frontend ESLint E2E TypeScript project)

## Symptom

Phase 0 reaches `[5/6] Frontend checks` and ESLint reports:

```text
Parsing error: "parserOptions.project" has been provided
The file was not found in any of the provided project(s): e2e/smoke.spec.ts
```

## Cause

ESLint uses typed TypeScript linting with:

```text
tsconfig.app.json
tsconfig.node.json
```

but `e2e/smoke.spec.ts` was not included by either TypeScript project.

## Fix

`tsconfig.node.json` now includes:

```json
"e2e/**/*.ts"
```

This is appropriate because Playwright E2E specs are tooling/test code and can be
typechecked together with `playwright.config.ts`.

## Apply

Extract over the project root:

```bash
unzip -o SIMA_Phase0_Fix07.zip -d ~/projects/sima-budget
```

Then:

```bash
cd ~/projects/sima-budget
make phase0-check
```

No database reset, bootstrap, or dependency reinstall is required.
