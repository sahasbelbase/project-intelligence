---
skillId: web-scraping-and-research
name: web-scraping-and-research
description: "Extract, distill, and verify technical documentation, public package registries, and architectural best practices from the web using ethical rate-limiting, clean markdown distillation, and structured metadata extraction."
purpose: "Extract, distill, and verify technical documentation, public package registries, and architectural best practices from the web using ethical rate-limiting, clean markdown distillation, and structured metadata extraction."
whenToUse:
  - Scraping online technical documentation and official API references for third-party libraries
  - Extracting package registry metadata, release notes, and breaking changes from npm, PyPI, and GitHub
  - Researching modern architectural patterns, algorithms, and benchmarks from the open web
  - Distilling web pages and HTML documentation into clean, readable GitHub-flavored markdown
  - Gathering external intelligence and comparative analyses to support agent development workflows
prerequisites:
  - Target URL list or domain research scope
  - Outbound HTTP fetch, headless browser, or scraping tool capability
  - Defined extraction schema or markdown output target destination
inputs:
  - name: targetUrls
    type: array
    description: List of target documentation or web page URLs to scrape and distill
  - name: extractionScope
    type: string
    description: Target content boundaries (e.g., documentation body, API table, changelog, code blocks)
  - name: outputFormat
    type: string
    description: Desired artifact format markdown, structured JSON, or comparative summary (default markdown)
  - name: rateLimitPolicy
    type: string
    description: Request throttling, concurrency limit, and robots.txt compliance settings (default polite/ethical)
procedure:
  - stepNumber: 1
    title: Robots & Rate Limit Policy Evaluation
    action: Inspect the target domain's robots.txt directives, crawl delay expectations, and concurrency rules to ensure ethical, non-disruptive scraping.
  - stepNumber: 2
    title: HTTP Fetch & Document Retrieval
    action: Retrieve target web documents using standard HTTP GET with browser user-agent headers, fallback handlers, and exponential backoff retry logic.
  - stepNumber: 3
    title: DOM Cleansing & Semantic Isolation
    action: Parse the HTML DOM and strip navigation bars, advertisements, cookie banners, tracking scripts, and footer noise to isolate the primary documentation article.
  - stepNumber: 4
    title: Markdown Distillation & Syntax Normalization
    action: Convert the cleansed HTML DOM into standard GitHub-flavored markdown, preserving language-tagged code blocks, tables, callouts, and relative hyperlinks.
  - stepNumber: 5
    title: Structured Metadata & Source Citation Extraction
    action: Extract publication timestamps, version tags, author metadata, and canonical URLs to construct verifiable provenance records.
  - stepNumber: 6
    title: Validation & Artifact Generation
    action: Validate distilled content against requested schema, verify code examples for syntax errors, and write the distilled files to docs/external-research/ or memory.
expectedOutputs:
  - Distilled markdown documentation files preserving syntax and code blocks in docs/external-research/
  - Structured extraction JSON containing metadata and API specs
  - Source citation manifest recording canonical URLs, HTTP status codes, and retrieval timestamps
applicableApprovalGates:
  - G0
  - G1
  - G2
  - G3
  - G4
failureAndRecovery:
  potentialFailures:
    - Target site blocks requests with 403 Forbidden, rate limits, or CAPTCHA challenge
    - Dynamic single-page application (SPA) returns empty HTML skeleton without client-side JavaScript execution
    - Malformed or noisy HTML produces corrupted, unreadable markdown
  recoveryStrategy: Switch to official public registry APIs (e.g., npm registry, PyPI JSON API, GitHub raw content), invoke headless browser rendering if client JavaScript is required, or fall back to cached developer documentation archives.
verificationCriteria:
  - Distilled markdown contains valid headers, tables, and fenced code blocks without residual script or style tags
  - All claims and code samples include verified canonical source URLs and fetch timestamps
  - Scraping actions strictly adhered to robots.txt rules and ethical concurrency limits
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/architecture/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.domainVocabulary
---

# Web Scraping & Online Intelligence (`web-scraping-and-research`)

## 1. Purpose
The `web-scraping-and-research` skill provides deterministic, rate-limited extraction, parsing, and distillation of online documentation, open-source repositories, and public package registries. It transforms sprawling web pages into structured, clean GitHub-flavored markdown and machine-readable JSON schemas while strictly obeying robots.txt and ethical concurrency boundaries.

## 2. When to Use It
Activate this skill whenever:
- Retrieving official API specifications, SDK documentation, and usage guides from external vendor documentation.
- Inspecting release notes, changelogs, and breaking change advisories on npm, PyPI, Crates.io, or GitHub releases.
- Gathering real-world code snippets, configuration patterns, or benchmarks from public developer docs.
- Converting complex HTML web documentation into clean, noise-free local markdown for agent synthesis.
- Compiling architectural comparisons across competitor frameworks and modern engineering libraries.

## 3. Prerequisites
- Target URLs or explicit domain research queries.
- Outbound network request capability (HTTP client, curl, or headless browser runner).
- Clear output destination (e.g. `docs/external-research/`).

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `targetUrls` | `array` | List of target documentation or web page URLs to scrape and distill. |
| `extractionScope` | `string` | Target content boundaries (e.g., documentation body, API table, changelog, code blocks). |
| `outputFormat` | `string` | Desired output format: `markdown`, `json`, or comparative summary. |
| `rateLimitPolicy` | `string` | Request throttling, concurrency limit, and robots.txt compliance settings. |

## 5. Procedure (Step-by-Step)
1. **Robots & Rate Limit Policy Evaluation**:
   - Query and inspect `robots.txt` at the root domain before requesting sub-paths.
   - Enforce polite concurrency caps (max 2 concurrent requests) and minimum crawl delays (>= 500ms between requests) to prevent server strain.
2. **HTTP Fetch & Document Retrieval**:
   - Perform HTTP GET requests using descriptive, respectful User-Agent headers.
   - Implement exponential backoff for transient HTTP 429 or 5xx status codes.
   - Follow redirects up to a maximum depth of 5 hops, recording the final canonical URL.
3. **DOM Cleansing & Semantic Isolation**:
   - Parse the raw HTML into a DOM tree.
   - Strip navigational headers, menus, sidebars, cookie banners, tracking pixels, and interactive widgets.
   - Retain semantic tags (`<article>`, `<main>`, `<h1-h6>`, `<p>`, `<pre>`, `<code>`, `<table>`).
4. **Markdown Distillation & Syntax Normalization**:
   - Convert clean HTML elements into GitHub-flavored markdown.
   - Preserve programming language attributes on code fences (e.g., ```` ```typescript ````).
   - Format HTML tables into clean markdown tables with alignment headers.
5. **Structured Metadata & Source Citation Extraction**:
   - Extract page title, author, version badge, published date, and canonical source link.
   - Record HTTP status codes, content hashes, and retrieval timestamps.
6. **Validation & Artifact Generation**:
   - Write distilled markdown files into `docs/external-research/`.
   - Update durable memory records with verifiable source citations.

## 6. Expected Outputs
- Distilled, clean markdown documentation files in `docs/external-research/`.
- Verified source citations containing canonical URLs, fetch timestamps, and status codes.
- Structured JSON API extraction summaries for programmatic consumption.

## 7. Applicable Approval Gates
- **G0 (Discovery)**: Gathers technology stack evaluations and external library capabilities.
- **G1 (Requirements)**: Clarifies external API capabilities and integration constraints.
- **G2 (Architecture)**: Verifies library interfaces and compatibility before architectural lock.
- **G3 (Planning)**: Verifies migration paths and breaking changes between library versions.
- **G4 (Implementation)**: Supplies verified code examples and official syntax references.

## 8. Failure and Recovery Strategies
- **403 Forbidden or Bot Detection**: Switch to official public package registry APIs (e.g., npm registry API, PyPI JSON API, raw GitHub user content) which provide structured endpoints without bot detection barriers.
- **Client-Side SPA Rendering**: If the raw HTML body is an empty `<div id="root"></div>`, use a headless browser or evaluate alternative static documentation mirrors.
- **Noisy or Incomplete Extraction**: Narrow the DOM selector scope to the specific article container or extract raw markdown if the repository provides raw documentation sources.

## 9. Verification Criteria
- Extracted markdown files contain valid headers, tables, and fenced code blocks without stray HTML scripts or styles.
- Every extracted claim, snippet, and version recommendation includes a verified canonical URL and timestamp.
- Scraping actions adhere strictly to robots.txt permissions and polite crawl pacing.

## 10. Relevant Contracts and Memory Records
- `contracts/project/contract.json`
- `contracts/architecture/contract.json`
- `durableKnowledge.architecturalDecisions`
- `durableKnowledge.domainVocabulary`
