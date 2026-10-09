---
skillId: api-contract-and-openapi-spec
name: api-contract-and-openapi-spec
description: "Author, validate, and enforce semver-compliant API contracts, OpenAPI 3.1 specifications, and mock interfaces to prevent integration drift between frontend and backend."
purpose: "Author, validate, and enforce semver-compliant API contracts, OpenAPI 3.1 specifications, and mock interfaces to prevent integration drift between frontend and backend."
whenToUse:
  - Designing new REST, GraphQL, gRPC, or webhook API endpoints prior to implementation
  - Generating or synchronizing OpenAPI 3.1 / JSON Schema specs from application route handlers
  - Detecting breaking API changes between pull request branches and production baselines
  - Creating mock API servers to unblock frontend developers during backend development
  - Validating payload types, headers, status codes, and error response schemas
prerequisites:
  - Read-only access to API routes, controllers, and data transfer object (DTO) models
  - Schema definition tools (OpenAPI 3.1 or JSON Schema Draft-07)
inputs:
  - name: apiProtocol
    type: string
    description: "API type: REST, GraphQL, gRPC, or webhook (default: REST)"
  - name: endpointDescription
    type: string
    description: Natural language or technical specification of the endpoints and operations
  - name: breakingChangeDetection
    type: boolean
    description: "Whether to compare against baseline OpenAPI spec for breaking changes (default: true)"
procedure:
  - stepNumber: 1
    title: Endpoint Interface & Payload Modeling
    action: Enumerate endpoints, HTTP methods, route parameters, request payloads, response bodies, and standardized error schemas (RFC 7807 problem details).
  - stepNumber: 2
    title: OpenAPI 3.1 Specification Generation
    action: Author canonical OpenAPI 3.1 YAML/JSON contract declarations with strict types, required field flags, format validators, and realistic payload examples.
  - stepNumber: 3
    title: Breaking Change & SemVer Audit
    action: Diff the proposed contract against the production specification to detect breaking changes (removed fields, widened requests, narrowed responses, changed types).
  - stepNumber: 4
    title: Mock Server & Type Stub Generation
    action: Generate deterministic mock data generators and typed client SDK stubs (TypeScript interfaces, Python dataclasses, Go structs) from the contract.
  - stepNumber: 5
    title: Consumer Contract Validation Testing
    action: Formulate automated contract tests that validate actual server responses against the OpenAPI schema definitions.
expectedOutputs:
  - Valid OpenAPI 3.1 YAML or JSON contract specification
  - Breaking change report indicating backward-compatibility status
  - Typed SDK client interfaces and mock response fixtures
applicableApprovalGates:
  - G1
  - G2
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - Breaking changes detected in active public API contracts
    - Drift between OpenAPI specification and actual server response implementations
    - Missing error schema definitions causing client crashes on 4xx/5xx responses
  recoveryStrategy: If breaking changes are necessary, introduce a new versioned endpoint path (e.g. /v2/api) while maintaining the legacy endpoint. Enforce automated CI schema validation tests to prevent implementation drift.
verificationCriteria:
  - The generated OpenAPI specification validates against OpenAPI 3.1 schema validators with 0 errors
  - All breaking changes are flagged with SemVer major bump or versioned route recommendations
  - All success (2xx) and failure (4xx, 5xx) response bodies are strictly typed
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/requirements/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.domainVocabulary
---

# API Contract & OpenAPI Specification (`api-contract-and-openapi-spec`)

## 1. Purpose
The `api-contract-and-openapi-spec` skill enables contract-first API development. It creates authoritative OpenAPI 3.1 and JSON Schema definitions, prevents breaking API changes, generates mock fixtures to unblock frontend engineers, and tests implementation conformity.

## 2. When to Use It
Activate this skill whenever:
- Designing new HTTP API endpoints, webhooks, or RPC interfaces before coding.
- Updating existing API routes and verifying backward compatibility.
- Generating client SDK types (TypeScript, Python, Go) from backend endpoints.
- Establishing contract testing between client and server microservices.

## 3. Prerequisites
- Route definitions or controller code with parameter/payload information.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `apiProtocol` | `string` | Protocol (`REST`, `GraphQL`, `gRPC`, `webhook`). |
| `endpointDescription` | `string` | Specification of endpoints and parameters. |
| `breakingChangeDetection` | `boolean` | Flag to compare against baseline spec. |

## 5. Procedure (Step-by-Step)
1. **Endpoint & Payload Modeling**: Define URLs, verbs, query parameters, headers, request bodies, and error formats (RFC 7807).
2. **OpenAPI 3.1 Generation**: Produce strict YAML or JSON specifications declaring types, required properties, and descriptions.
3. **Breaking Change Audit**: Run structural diffs to detect dropped properties, altered field formats, or modified status codes.
4. **Mock Server & Client Type Stubs**: Generate typed data structures and mock responses for frontend development.
5. **Contract Validation**: Create automated tests verifying that running server responses adhere to the OpenAPI schema.

## 6. Expected Outputs
- Fully formatted, valid OpenAPI 3.1 contract.
- Breaking change assessment and versioning recommendations.
- Typed client interface stubs.

## 7. Applicable Approval Gates
- **G1 (Requirements)**: Endpoint scope and functional inputs.
- **G2 (Architecture)**: API interface contracts.
- **G4 (Implementation)**: DTO conformity.
- **G5 (Quality)**: Automated contract validation pass.

## 8. Failure and Recovery Strategies
- If breaking changes cannot be avoided, create a versioned path (`/api/v2`) and keep `/api/v1` functional using an adapter layer.

## 9. Verification Criteria
- Zero validation errors when linting with spectral or openapi-validator.
- All breaking changes are flagged with SemVer justifications.
- Error payloads follow structured schema formats.

## 10. Relevant Contracts and Memory Records
- `contracts/architecture/contract.json`
- `contracts/requirements/contract.json`
- `durableKnowledge.architecturalDecisions`
- `durableKnowledge.domainVocabulary`
