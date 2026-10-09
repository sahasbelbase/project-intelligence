---
skillId: database-migration-and-schema-evolution
name: database-migration-and-schema-evolution
description: "Plan, generate, and verify zero-downtime database migrations, backward-compatible schema changes, indexing strategies, and reversible rollback scripts."
purpose: "Plan, generate, and verify zero-downtime database migrations, backward-compatible schema changes, indexing strategies, and reversible rollback scripts."
whenToUse:
  - Designing schema changes for relational (PostgreSQL, MySQL, SQLite) or NoSQL databases
  - Executing backward-compatible column renames, type conversions, or table splits without downtime
  - Generating reversible 'up' and 'down' migration scripts with rollback guarantees
  - Optimizing slow database queries with targeted indexing and EXPLAIN query plan analysis
  - Validating data integrity constraints, foreign keys, and default values across migrations
prerequisites:
  - Access to existing database schema definitions or migration history files
  - Understanding of target database engine locking semantics (e.g. Postgres lock levels)
inputs:
  - name: databaseEngine
    type: string
    description: "Database system: postgresql, mysql, sqlite, mongodb, etc."
  - name: desiredSchemaChange
    type: string
    description: Natural language or DDL description of the requested schema evolution
  - name: zeroDowntimeRequired
    type: boolean
    description: "Whether the migration must support active read/write traffic during execution (default: true)"
procedure:
  - stepNumber: 1
    title: Schema Diff & Backward-Compatibility Assessment
    action: "Compare existing schema state with target state and classify the change: non-breaking (adding nullable column), multi-phase (renaming column), or breaking (dropping table)."
  - stepNumber: 2
    title: Multi-Phase Expand/Contract Planning
    action: "For destructive changes, formulate an Expand-and-Contract roadmap: Phase 1 (add new column & dual write), Phase 2 (backfill historical data), Phase 3 (switch reads), Phase 4 (drop old column)."
  - stepNumber: 3
    title: Locking Impact & Index Optimization Analysis
    action: Audit migration DDL for table lock hazards (e.g., adding NOT NULL without DEFAULT, non-concurrent index builds) and enforce safe syntax like CREATE INDEX CONCURRENTLY.
  - stepNumber: 4
    title: Reversible Migration Script Authoring
    action: Generate deterministic 'up' (forward) and 'down' (rollback) migration scripts with idempotent guards and transactional safety.
  - stepNumber: 5
    title: Dry-Run Simulation & Query Plan Verification
    action: Simulate migration on a clean test schema, verify rollback execution returns the schema to pristine condition, and inspect critical EXPLAIN execution plans.
expectedOutputs:
  - Tested, reversible forward and rollback migration files
  - Zero-downtime multi-phase execution playbook for production deployment
  - Query plan optimization report for affected indexes
applicableApprovalGates:
  - G2
  - G3
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - Migration acquires exclusive table lock during high production load
    - Backfill script saturates database CPU or replication lag
    - Rollback script fails due to data loss in forward migration
  recoveryStrategy: Abort transaction immediately upon lock timeout. Break large backfill operations into batched chunks (e.g. 5,000 rows per batch with sleep intervals) and test rollback scripts against real data volume.
verificationCriteria:
  - Every forward migration includes a tested, 100% reversible rollback script
  - No exclusive table-locking DDL operations are executed without non-blocking alternatives
  - All new foreign keys and frequent query filters have supporting indexes
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/implementation/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.domainVocabulary
---

# Database Migration & Schema Evolution (`database-migration-and-schema-evolution`)

## 1. Purpose
The `database-migration-and-schema-evolution` skill guides the safe, zero-downtime evolution of database schemas. It enforces backward-compatible change patterns (Expand and Contract), eliminates table-locking hazards, generates deterministic rollback scripts, and verifies query plans before deployment.

## 2. When to Use It
Activate this skill whenever:
- Adding, altering, or dropping database tables, columns, indexes, or constraints.
- Renaming database columns or changing column data types in active production systems.
- Authoring database migration scripts (Prisma, Flyway, Alembic, Knex, Liquibase, TypeORM, raw SQL).
- Diagnosing slow database queries or designing composite index coverage.

## 3. Prerequisites
- Target database engine schema definitions and target engine version.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `databaseEngine` | `string` | Target engine (`postgresql`, `mysql`, `sqlite`, etc.). |
| `desiredSchemaChange` | `string` | Requested schema modifications. |
| `zeroDowntimeRequired` | `boolean` | Flag indicating live zero-downtime constraint. |

## 5. Procedure (Step-by-Step)
1. **Schema Diff & Compatibility Assessment**: Classify the change into non-breaking, multi-phase, or destructive categories.
2. **Multi-Phase Expand/Contract Planning**: Structure column renames or type conversions into distinct deployment phases:
   - Phase 1: Add new column (nullable or default) & deploy dual-writing code.
   - Phase 2: Backfill existing data in batched chunks.
   - Phase 3: Switch application reads to the new column.
   - Phase 4: Drop old column and deprecate legacy dual-writes.
3. **Locking Impact Analysis**: Avoid full table locks; use safe alternatives such as `CREATE INDEX CONCURRENTLY` in Postgres.
4. **Reversible Migration Script Authoring**: Write both forward (`up`) and rollback (`down`) scripts with transaction safety.
5. **Dry-Run Simulation**: Run migration and rollback in a sandbox environment to verify reversibility and performance.

## 6. Expected Outputs
- Safe forward migration SQL files.
- Reversible rollback SQL files.
- Zero-downtime deployment sequence instructions.

## 7. Applicable Approval Gates
- **G2 (Architecture)**: Approval of database schema model.
- **G3 (Planning)**: Migration phase scheduling.
- **G4 (Implementation)**: DDL script verification.
- **G5 (Quality)**: Rollback simulation and query plan verification.

## 8. Failure and Recovery Strategies
- Abort migrations if lock acquisition exceeds timeout thresholds. Revert immediately using the tested `down` script.

## 9. Verification Criteria
- Forward and rollback migrations pass dry runs without errors.
- No exclusive table locks are taken on high-volume tables.
- Foreign keys and filter queries are backed by indexes.

## 10. Relevant Contracts and Memory Records
- `contracts/architecture/contract.json`
- `contracts/implementation/contract.json`
- `durableKnowledge.architecturalDecisions`
- `durableKnowledge.domainVocabulary`
