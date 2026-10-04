# SIMA Phase 1C2 — Fix 02: Async Form Reset

## Symptom

A create request succeeds in the backend, but the UI displays a failure message.
After manually refreshing the page, the newly created record appears.

## Cause

The create handlers accessed `event.currentTarget` after an `await`.

React event `currentTarget` should not be relied on after the synchronous event
handler has yielded. The backend request can therefore succeed, then the
frontend throws while attempting:

```ts
event.currentTarget.reset()
```

The generic catch block then incorrectly reports that creation failed.

## Fix

Capture the form before the first await:

```ts
const form = event.currentTarget;
const data = new FormData(form);

await createSomething(...);
form.reset();
```

Applied to:

- Organization Units
- Users
- Roles

## Validation

```bash
cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase1c2-check
```

Then manually create one temporary unit and confirm it appears immediately
without refreshing the browser.
