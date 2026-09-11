---
name: awful-tdd
description: Test-driven development for AWFUL STUDIO changes. Use for every production bugfix, feature, refactor, lifecycle, ownership, migration, asset or tooling behavior change.
status: installed
---

# AWFUL TDD

Use RED → GREEN → REFACTOR. Do not write production behavior first and add tests afterward.

## Choose the test layer

Use fast/pure tests when the behavior does not need Blender runtime: manifest/tooling policy, parsing, math, metadata, path validation, release gating.

Use a Blender 5.2 runtime test when correctness depends on `bpy`: registration, scene mutation, datablocks, ownership, collections, operators, save/reopen, migration, Extension install/update.

If both layers matter, begin with the smallest test that demonstrates the requirement and add runtime coverage before completion.

## RED

1. Name one observable behavior.
2. Write the smallest regression/feature test.
3. Run exactly that test.
4. Confirm it fails for the expected missing/incorrect behavior, not because setup is broken.

For destructive Blender bugs, the RED fixture must include the user data that must survive.

## GREEN

Implement the minimum durable source change that makes the failing test pass. Do not weaken business requirements, ownership checks, checksum verification, offline behavior or migration safety to obtain green output.

Run the targeted test again, then the relevant broader suite.

## REFACTOR

Only after green: remove duplication, improve names or extract helpers while keeping tests green. Avoid unrelated monolith cleanup during 0.0.16 foundation work.

## Regression-test integrity

For important regressions, prove the test can catch the bug: after a passing fix, temporarily evaluate against the known-bad behavior/revert or otherwise demonstrate the RED state before accepting the test as evidence.

## Minimum evidence in the issue

- failing test name and failure reason;
- source change/root cause;
- passing targeted command;
- broader verification command;
- Blender version when runtime was involved;
- commit SHA.

A test that never failed does not prove the new requirement.