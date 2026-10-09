---
skillId: runtime-performance-profiling
name: runtime-performance-profiling
description: "Profile application runtime performance, diagnose latency bottlenecks, identify memory leaks and N+1 query patterns, and audit bundle sizes against Core Web Vitals budgets."
purpose: "Profile application runtime performance, diagnose latency bottlenecks, identify memory leaks and N+1 query patterns, and audit bundle sizes against Core Web Vitals budgets."
whenToUse:
  - Diagnosing high latency, slow API response times, or low throughput
  - Identifying N+1 database queries and unindexed relational scans in backend services
  - Auditing client-side bundle size, code-splitting, and tree-shaking efficiency
  - Detecting memory leaks, unclosed streams, and unbounded object caches
  - Benchmarking algorithms or hot code paths against performance budgets
prerequisites:
  - Access to application source code and runtime profiling or benchmark commands
  - Representative workload or test harness to simulate traffic
inputs:
  - name: targetScope
    type: string
    description: "Profiling target: backend-api, frontend-bundle, memory-leak, or query-performance"
  - name: latencyBudgetMs
    type: integer
    description: "Target p95 latency threshold in milliseconds (default: 200)"
  - name: benchmarkIterations
    type: integer
    description: "Number of warmup and measured iterations for statistical stability (default: 100)"
procedure:
  - stepNumber: 1
    title: Baseline Profiling & Flamegraph Capture
    action: Execute representative benchmark workloads under profiling instrumentation (Node inspector, Python cProfile, pprof) to identify hot CPU and memory paths.
  - stepNumber: 2
    title: Database Query & I/O Bottleneck Inspection
    action: Trace database roundtrips, identify N+1 query loops within iterative logic, and audit batch fetching and connection pool saturation.
  - stepNumber: 3
    title: Frontend Bundle & Render Cost Analysis
    action: Audit bundle size visualizations for duplicate dependencies, analyze chunk splitting, and inspect DOM re-render cycles against Core Web Vitals (LCP, INP, CLS).
  - stepNumber: 4
    title: Memory Retention & Garbage Collection Audit
    action: Capture heap snapshots before and after workload execution to identify uncollected event listeners, detached DOM trees, or growing caches.
  - stepNumber: 5
    title: Optimization Specification & Benchmark Verification
    action: Author targeted optimizations (batching, memoization, indexing, dynamic imports) and re-run benchmarks to prove statistical latency reduction.
expectedOutputs:
  - Comprehensive performance diagnostic report with flamegraph summaries and p50/p95/p99 latency charts
  - Optimization pull request specifications addressing identified bottlenecks
  - Bundle size comparison report showing byte reduction
applicableApprovalGates:
  - G1
  - G2
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - Micro-optimizations that degrade code readability without measurable gains
    - Benchmark noise causing inconsistent latency measurements
    - Premature optimization prior to architectural stabilization
  recoveryStrategy: "Enforce Knuth's rule: measure with statistical significance before optimizing. Reject any optimization that yields less than a 15% verifiable throughput or latency improvement if it increases complexity."
verificationCriteria:
  - Performance improvements are proven with before-and-after empirical benchmark metrics
  - Optimizations do not alter existing functional test suite pass rates
  - Critical API paths adhere to defined p95 latency budgets
relevantContractsAndMemory:
  contracts:
    - contracts/requirements/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
---

# Runtime Performance Profiling (`runtime-performance-profiling`)

## 1. Purpose
The `runtime-performance-profiling` skill provides empirical latency, throughput, and resource optimization. It captures CPU flamegraphs, detects N+1 database queries, identifies memory leaks, and audits JavaScript bundle sizes against Core Web Vitals budgets.

## 2. When to Use It
Activate this skill whenever:
- Backend endpoints exceed acceptable response time thresholds (e.g. p95 > 200ms).
- Diagnosing database query slowdowns or looping database roundtrips.
- Auditing web applications for excessive bundle sizes or layout thrashing.
- Tracking down memory growth or high garbage collection pauses.

## 3. Prerequisites
- Workload generator or automated benchmark script to run profiling under load.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `targetScope` | `string` | Target (`backend-api`, `frontend-bundle`, `memory-leak`). |
| `latencyBudgetMs` | `integer` | Target p95 latency budget in milliseconds. |
| `benchmarkIterations` | `integer` | Number of test runs for statistical significance. |

## 5. Procedure (Step-by-Step)
1. **Baseline Profiling & Flamegraph Capture**: Record baseline execution under profiler (`cProfile`, Node `--prof`).
2. **Database Query Bottleneck Inspection**: Eliminate N+1 queries using batch lookups and eager loading.
3. **Frontend Bundle & Render Cost Analysis**: Trim oversized imports, apply code-splitting, and eliminate duplicate libraries.
4. **Memory Retention Audit**: Compare heap snapshots to detect uncollected closures and unclosed socket streams.
5. **Optimization Verification**: Re-run identical benchmark workloads and document percentage improvements.

## 6. Expected Outputs
- Performance audit report with before-and-after latency distributions.
- Targeted code optimizations with verified speedup metrics.

## 7. Applicable Approval Gates
- **G1 (Requirements)**: Non-functional latency and throughput budgets.
- **G2 (Architecture)**: Caching and batching design.
- **G4 (Implementation)**: Optimization patches.
- **G5 (Quality)**: Benchmark verification evidence.

## 8. Failure and Recovery Strategies
- Reject complex code rewrites that yield negligible (<15%) gains. Retain readability over unmeasured micro-optimizations.

## 9. Verification Criteria
- Verified throughput increase or latency drop on identical workloads.
- Zero functional regression in existing test suites.
- Bundle sizes adhere to budget constraints.

## 10. Relevant Contracts and Memory Records
- `contracts/requirements/contract.json`
- `contracts/quality/contract.json`
- `durableKnowledge.architecturalDecisions`
