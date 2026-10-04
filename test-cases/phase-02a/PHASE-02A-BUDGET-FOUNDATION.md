# Phase 2A Test Cases

## P2A-001 Fiscal Year creation
A Budget Administrator with ALL scope can create a DRAFT Fiscal Year.

## P2A-002 CSRF
Fiscal Year mutation without CSRF is rejected.

## P2A-003 Legal lifecycle
`DRAFT → PLANNING → ACTIVE → CLOSED → ARCHIVED` succeeds in order.

## P2A-004 Invalid lifecycle
Skipping a lifecycle state is rejected.

## P2A-005 Single ACTIVE year
A second Fiscal Year cannot become ACTIVE while another ACTIVE year exists.

## P2A-006 Controlled reopen
A CLOSED Fiscal Year can reopen only with `fiscal_years.reopen`, ALL scope, and a reason.

## P2A-007 Reopen conflict
A CLOSED Fiscal Year cannot reopen while another ACTIVE year exists.

## P2A-008 Budget Category
Budget Category supports create/read/update/deactivate and unique organization code.

## P2A-009 Unit of Measure
Unit of Measure supports create/read/update/deactivate and unique organization code.

## P2A-010 Audit
Fiscal Year lifecycle and master-data mutations create audit records.

## P2A-011 Authority separation
System Administrator does not automatically receive Phase 2A mutation/transition permissions.

## P2A-012 Budget Administrator
Budget Administrator receives Phase 2A domain permissions through bootstrap.
