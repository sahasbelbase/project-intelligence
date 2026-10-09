---
skillId: legacy-codebase-knowledge-base
name: legacy-codebase-knowledge-base
description: "Reverse-engineer legacy and brownfield codebases using lightweight reading sub-agents to extract naming conventions, architectural paces, domain entities, bug logging mechanisms, and full-stack structure recommendations into a structured docs/ knowledge base."
purpose: "Reverse-engineer legacy and brownfield codebases using lightweight reading sub-agents to extract naming conventions, architectural paces, domain entities, bug logging mechanisms, and full-stack structure recommendations into a structured docs/ knowledge base."
whenToUse:
  - Onboarding legacy or brownfield repositories with undocumented architecture
  - Reverse-engineering undocumented proprietary domain entities, business logic, and database models
  - Extracting codebase idioms, naming conventions, coding paces, and recurring design patterns
  - Auditing error handling and incident/bug logging telemetry across existing services
  - Restructuring monolithic full-stack repositories into clean client, server, and domain boundaries
  - Generating an authoritative, cross-linked docs/ knowledge base and root navigation index for developers and AI agents
prerequisites:
  - Read-only filesystem access to repository source files
  - Git version control history access for commit pacing and churn analysis
  - Sub-agent dispatch capability configured for lightweight reading models (e.g., Flash, Haiku, GPT-4o-mini tier)
inputs:
  - name: targetDirectory
    type: string
    description: "Root path of the repository or sub-tree to analyze (default: repository root)"
  - name: outputDocsDirectory
    type: string
    description: "Target folder for generated documentation (default: docs/knowledge-base)"
  - name: concurrencyLimit
    type: integer
    description: "Maximum number of parallel reading sub-agents to dispatch (default: 4)"
  - name: modelTier
    type: string
    description: "Model tier for reading workers to optimize throughput and cost (default: low-tier/fast)"
  - name: excludeGlobs
    type: array
    description: File patterns and vendor paths to ignore (e.g., node_modules, dist, vendor, .git)
procedure:
  - stepNumber: 1
    title: Directory Tree & Monolith Reconnaissance
    action: Traverse the repository filesystem, map file distributions across languages, identify build configurations, and detect whether client and server code are combined in monolithic or mixed full-stack folders.
  - stepNumber: 2
    title: Sub-Agent Task Partitioning with Lightweight Reading Models
    action: Decompose the codebase into bounded modules or directories and dispatch concurrent, read-only sub-agents using low-tier reading models (e.g., Flash, Haiku) to extract syntactic patterns, dependencies, and file relationships without context exhaustion.
  - stepNumber: 3
    title: Coding Style, Idioms & Paces Extraction
    action: Analyze code samples from sub-agent findings to synthesize naming conventions (casing, prefixing), asynchronous control flow idioms, module pacing, and recurring structural patterns.
  - stepNumber: 4
    title: Domain Entity & Business Boundary Isolation
    action: Identify core business objects, proprietary data models, entity relationships, and domain logic, separating business-critical rules from infrastructure and framework boilerplate.
  - stepNumber: 5
    title: Error Handling, Bug Logging & Telemetry Auditing
    action: Audit try/catch blocks, error hierarchies, logger configurations, error boundary triggers, and bug-reporting hooks to document how runtime failures and exceptions are logged and tracked.
  - stepNumber: 6
    title: Full-Stack Architecture & Modernization Recommendations
    action: Evaluate the existing layout against modern clean-architecture standards. If a legacy full-stack or monolithic structure is detected, formulate concrete recommendations to separate frontend (client), backend (api/server), shared contracts, and domain models.
  - stepNumber: 7
    title: Durable Knowledge Base Synthesis in docs/ and Root Index
    action: Author modular markdown documents in docs/ (architecture, domain entities, coding conventions, logging, modernization roadmap) and generate a comprehensive root docs/README.md navigation index that cross-links all components.
expectedOutputs:
  - Structured docs/knowledge-base/ directory containing comprehensive domain, architectural, and convention documentation
  - Root docs/README.md or main index cross-linking all knowledge base sections for humans and AI agents
  - Domain entity catalog documenting proprietary models, fields, and lifecycle state machines
  - Codebase style guide documenting naming rules, async patterns, and structural paces
  - Error logging and post-bug telemetry guide documenting logging levels and incident tracking
  - Full-stack modernization recommendations detailing target modular folder structure
applicableApprovalGates:
  - G0
  - G1
  - G2
failureAndRecovery:
  potentialFailures:
    - Repository too large causing sub-agent timeout or context blowout
    - Conflicting or inconsistent coding styles across legacy sub-modules
    - Tightly coupled full-stack spaghetti where domain entities cannot be easily distinguished from UI code
    - Missing or inconsistent error logging mechanisms
  recoveryStrategy: Partition large repositories by top-level package or domain boundaries. Where conventions clash, document both prevailing idioms by folder and recommend a canonical target standard. Where entities are intertwined with UI components, flag the anti-pattern as high-priority refactoring debt and isolate data contracts from view logic.
verificationCriteria:
  - Every documented domain entity includes file paths where it is defined and consumed
  - All identified naming conventions and idioms cite verbatim code samples as evidence
  - Error logging documentation outlines exact log levels, destinations, and bug-reporting hooks
  - All generated documentation files exist under docs/ and are hyperlinked from a root index
  - Modernization recommendations provide a before-and-after directory layout comparison
  - No source files are modified during analysis (strictly non-destructive operation)
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/architecture/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.codingConventions
    - durableKnowledge.domainVocabulary
    - backlogAndHistory.technicalDebt
---

# Legacy Codebase Knowledge Base Generator (`legacy-codebase-knowledge-base`)

## 1. Purpose
The `legacy-codebase-knowledge-base` skill enables AI coding agents and human engineering leads to perform deep, automated reverse-engineering of legacy, brownfield, or undocumented codebases. It uses an orchestration pattern that dispatches lightweight worker sub-agents powered by cost-efficient, low-tier reading models (such as Flash, Haiku, or GPT-4o-mini tier) to read, map, and cross-link source files concurrently. It synthesizes findings into an authoritative, permanent knowledge base in `docs/` with a top-level navigation index, capturing:
- Proprietary domain entities and business models isolated from infrastructure code.
- Prevailing coding idioms, naming conventions, and structural paces.
- Error handling, bug logging telemetry, and incident trace mechanisms.
- Architectural modernization recommendations (e.g. decoupling monolithic full-stack trees into modular client, server, and domain boundaries).

## 2. When to Use It
Activate this skill whenever:
- Onboarding an inherited or brownfield repository into active development or Project Intelligence governance.
- Reverse-engineering an undocumented legacy system before planning a major refactor or new feature.
- Extracting proprietary business domain models and vocabulary from sprawling source files.
- Analyzing coding style, naming conventions, and architectural rhythms to maintain consistency.
- Auditing runtime error handling, log formatting, and bug reporting behaviors across services.
- Transitioning a mixed full-stack folder structure toward a modern modular architecture.

## 3. Prerequisites
- Read-only access to repository source files.
- Git CLI availability with commit history access.
- Sub-agent invocation capability configured to assign low-tier reading models to worker tasks.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `targetDirectory` | `string` | Root path of the codebase to analyze (default: repository root). |
| `outputDocsDirectory` | `string` | Directory where markdown documentation will be created (default: `docs/knowledge-base/`). |
| `concurrencyLimit` | `integer` | Number of concurrent reading sub-agents to spawn (default: 4). |
| `modelTier` | `string` | Model tier for reading agents (`flash`, `haiku`, `mini`) to optimize reading speed and token spend. |
| `excludeGlobs` | `array` | Paths to exclude (e.g., `node_modules`, `dist`, `.git`, lockfiles). |

## 5. Procedure (Step-by-Step)
1. **Directory Tree & Monolith Reconnaissance**:
   - Enumerate all directories and files, filtering out build artifacts and dependencies.
   - Detect primary language stacks, framework manifests, entrypoints, and file count distributions.
   - Check if frontend and backend code coexist in a single entangled folder (e.g. monolithic full-stack app).
2. **Sub-Agent Task Partitioning with Low-Tier Reading Models**:
   - Group source files into cohesive clusters (by package, module, or feature folder).
   - Dispatch read-only sub-agents equipped with fast, low-tier reading models to read each cluster in parallel.
   - Each sub-agent extracts exported types, class hierarchies, import graphs, and inter-file dependencies.
3. **Coding Style, Idioms & Paces Extraction**:
   - Synthesize naming rules across functions, classes, files, constants, and database tables.
   - Extract recurring asynchronous patterns (promises, callbacks, reactive streams, goroutines).
   - Identify common architectural paces and cadence (request-response lifecycles, batch loops, event triggers).
4. **Domain Entity & Business Boundary Isolation**:
   - Locate business entities, database models, schemas, and value objects.
   - Group entities by business domain (e.g., Billing, Authentication, Inventory, Workflow).
   - Map relationships, foreign keys, and state transitions, isolating domain rules from transport/UI logic.
5. **Error Handling, Bug Logging & Telemetry Auditing**:
   - Inspect error creation, propagation, and wrapping (e.g., custom error classes, error codes).
   - Document logging mechanisms: log libraries used, logging levels (`DEBUG`, `INFO`, `WARN`, `ERROR`), log sinks, and structured JSON formats.
   - Audit how bugs and crashes are logged and reported (e.g., Sentry, Datadog, Winston, rollbar hooks).
6. **Full-Stack Architecture & Modernization Recommendations**:
   - Analyze architectural coupling and technical debt.
   - If a mixed full-stack folder is detected, formulate a modular separation plan:
     - `client/` (UI components, view state, styling)
     - `server/` (API endpoints, controllers, middleware)
     - `domain/` (Pure business entities, domain services, validation logic)
     - `contracts/` (Shared types, interfaces, schemas)
7. **Durable Knowledge Base Synthesis in docs/ and Root Index**:
   - Generate modular markdown files under `docs/knowledge-base/`:
     - `01-architecture-overview.md`: High-level system design, entrypoints, and tech stack.
     - `02-domain-entities.md`: Catalog of core domain models, attributes, and relationships.
     - `03-coding-conventions.md`: Naming rules, idioms, formatting, and structural paces.
     - `04-logging-and-observability.md`: Error handling conventions, log formatting, and bug reporting.
     - `05-modernization-roadmap.md`: Full-stack decoupling and refactoring recommendations.
   - Create or update the top-level `docs/README.md` navigation index linking every document so developers can immediately understand where to look.

## 6. Expected Outputs
- Fully authored `docs/knowledge-base/` containing structured, cross-referenced Markdown files.
- Top-level `docs/README.md` providing an outside navigation index.
- Populated entries in `memory/state.json` under `durableKnowledge.domainVocabulary` and `durableKnowledge.codingConventions`.

## 7. Applicable Approval Gates
- **Gate G0 (Discovery)**: Establishes initial codebase baseline and technology stack context.
- **Gate G1 (Requirements)**: Clarifies existing business domains and constraints prior to feature definition.
- **Gate G2 (Design & Architecture)**: Informs architectural decisions and modernization restructuring.

## 8. Failure and Recovery Strategies
- **Context Limit or High File Count**: Partition files into smaller clusters and process hierarchically.
- **Inconsistent or Fragmented Code Style**: Document variances per sub-folder, highlight the prevailing standard, and recommend a unified linter rule.
- **Spaghetti Coupling**: Create a dependency matrix highlighting circular dependencies and recommend an incremental strangler-fig migration pattern.

## 9. Verification Criteria
- All documented domain entities link directly to their source files and line ranges.
- All documented conventions include verbatim code snippets as empirical evidence.
- The root index in `docs/` contains active, working relative links to every generated section.
- Zero source code files or runtime behaviors are modified (strictly non-destructive analysis).

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json` (Gate G0)
  - `contracts/architecture/contract.json` (Gate G2)
- **Memory Records**:
  - `durableKnowledge.domainVocabulary`
  - `durableKnowledge.codingConventions`
  - `durableKnowledge.architecturalDecisions`
  - `backlogAndHistory.technicalDebt`
