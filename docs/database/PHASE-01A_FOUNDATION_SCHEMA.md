# Phase 1A Foundation Schema

## Identity

`organizations` is the root tenant/organization record for a deployment.

V1 remains one organization per deployment, but organization foreign keys keep the data model portable.

## Organization hierarchy

`organization_units` is generic and supports parent-child hierarchy.

Unit labels such as Fakultas, Program Studi, Biro, UPT, and others are represented through configurable `organization_unit_types`.

## Users and unit membership

A user may have multiple `user_unit_memberships`.

Job title is descriptive only; it does not grant permission.

## RBAC

Permissions are global capability codes.

Roles belong to an organization.

Role assignments have a data scope:

- OWN
- OWN_UNIT
- OWN_UNIT_AND_CHILDREN
- ALL

Phase 1B/1C will implement effective permission evaluation.

## Sessions

`user_sessions` stores only a token hash, never a raw browser session token.

## Audit

`audit_logs` is append-only from the application perspective.

JSONB before/after fields allow meaningful change history without coupling the audit schema to every business table.
