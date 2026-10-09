---
skillId: ci-cd-pipeline-engineering
name: ci-cd-pipeline-engineering
description: "Design, author, and optimize secure CI/CD pipelines, multi-stage container builds, caching strategies, and automated release workflows."
purpose: "Design, author, and optimize secure CI/CD pipelines, multi-stage container builds, caching strategies, and automated release workflows."
whenToUse:
  - Setting up GitHub Actions, GitLab CI, or local build pipelines for automated testing
  - Authoring minimal, rootless, multi-stage Dockerfiles and container configurations
  - Optimizing build and test execution speed with package manager caching and parallel jobs
  - Configuring automated semantic releases, changelog generation, and tag publication
  - Implementing deployment rollback triggers and health check verification scripts
prerequisites:
  - Read-only access to repository root, build manifests, test scripts, and workflow directories
  - Familiarity with target CI platform syntax (GitHub Actions, GitLab CI, Makefile)
inputs:
  - name: ciPlatform
    type: string
    description: "Target automation platform: github-actions, gitlab-ci, or local-docker (default: github-actions)"
  - name: targetEnvironments
    type: array
    description: "Target runtime environments: node, python, rust, go, or multi-stage container"
  - name: cachingEnabled
    type: boolean
    description: "Whether to configure dependency and build artifact caching (default: true)"
procedure:
  - stepNumber: 1
    title: Pipeline Requirements & Lifecycle Gate Mapping
    action: "Map framework verification commands and test runners into deterministic CI stages: lint, typecheck, test, build, and security audit."
  - stepNumber: 2
    title: Dependency Caching & Performance Optimization
    action: Configure platform-specific caching layers (npm cache, pip wheels, cargo target) to minimize pipeline duration and network transfers.
  - stepNumber: 3
    title: Multi-Stage Rootless Dockerfile Construction
    action: "Write optimized container manifests: separate build stages from lean runtime images, drop root privileges to an unprivileged user, and add explicit HEALTHCHECK instructions."
  - stepNumber: 4
    title: Security & Secret Least-Privilege Hardening
    action: "Enforce minimum token permissions (GITHUB_TOKEN permissions: read-all), pin GitHub Action versions to full commit SHAs, and prevent secrets exposure in build logs."
  - stepNumber: 5
    title: Automated Release & Health Check Scripting
    action: Author semantic release workflows with automated changelog extraction, npm/container publication, and post-deployment canary health checks.
expectedOutputs:
  - Fully configured CI workflow YAML files (.github/workflows/ci.yml, release.yml)
  - Hardened, multi-stage Dockerfile and .dockerignore files
  - Pipeline execution summary documenting build stages and estimated run times
applicableApprovalGates:
  - G2
  - G4
  - G5
  - G6
failureAndRecovery:
  potentialFailures:
    - Cache invalidation issues causing stale dependencies in CI
    - Flaky test runs in virtualized CI environments
    - Docker permission errors when switching to unprivileged users
  recoveryStrategy: Use explicit lockfile hash keys for cache busting. Add retries to network-dependent steps, and verify user permissions on mounted volumes before container startup.
verificationCriteria:
  - All CI workflow files pass schema validation for the target platform
  - Docker images build without warnings and run as an unprivileged user
  - Pipeline jobs fail fast with exit code non-zero upon any test or lint error
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/release/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
---

# CI/CD Pipeline Engineering (`ci-cd-pipeline-engineering`)

## 1. Purpose
The `ci-cd-pipeline-engineering` skill provides automated, security-hardened pipeline authoring. It creates fast CI workflows with package caching, parallelized test matrices, minimal multi-stage Dockerfiles, and reproducible automated release pipelines.

## 2. When to Use It
Activate this skill whenever:
- Setting up or updating GitHub Actions, GitLab CI, or Cloud Build workflows.
- Authoring production Dockerfiles, `.dockerignore` files, and container orchestration manifests.
- Accelerating slow CI build times using artifact and package caching.
- Implementing automated changelog generation and Semantic Version tag releases.

## 3. Prerequisites
- Repository build commands, test runner scripts, and target deployment platform.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `ciPlatform` | `string` | Target CI engine (`github-actions`, `gitlab-ci`). |
| `targetEnvironments` | `array` | Runtimes (`node`, `python`, `docker`). |
| `cachingEnabled` | `boolean` | Flag to configure dependency caching. |

## 5. Procedure (Step-by-Step)
1. **Pipeline Requirements & Gate Mapping**: Align CI jobs with project lifecycle gates (Lint -> Test -> Build -> Security).
2. **Dependency Caching Optimization**: Add caching keys keyed to lockfile hashes.
3. **Multi-Stage Container Construction**: Build production images using multi-stage compilation and unprivileged execution users (`USER node` / `USER app`).
4. **Security & Least-Privilege Hardening**: Restrict CI workflow permissions (`permissions: contents: read`) and pin actions to SHAs.
5. **Release & Health Check Scripting**: Automate semantic versioning, changelog compilation, and post-deployment health verification.

## 6. Expected Outputs
- Validated workflow files under `.github/workflows/`.
- Multi-stage Dockerfile and `.dockerignore`.
- Pipeline architectural overview.

## 7. Applicable Approval Gates
- **G2 (Architecture)**: Infrastructure and container architecture.
- **G4 (Implementation)**: Workflow configuration authoring.
- **G5 (Quality)**: CI execution pass confirmation.
- **G6 (Release)**: Automated tag and publication verification.

## 8. Failure and Recovery Strategies
- Ensure cache keys include OS and lockfile hash to avoid cross-contamination. Provide clear local reproduction commands (`docker build`, `act`) for failed CI runs.

## 9. Verification Criteria
- CI scripts exit with status 1 upon any test or lint failure.
- Container builds produce minimal attack surfaces and run rootless.
- Secrets are never exposed in stdout logs.

## 10. Relevant Contracts and Memory Records
- `contracts/architecture/contract.json`
- `contracts/release/contract.json`
- `durableKnowledge.architecturalDecisions`
