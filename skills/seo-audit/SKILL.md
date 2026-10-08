---
skillId: seo-audit
name: seo-audit
description: "Make a project's website, docs and repository easy for search engines, social previews and people to find and understand: metadata, structured data, crawlability, performance, accessibility and repository metadata."
purpose: "Make a project's website, docs and repository easy for search engines, social previews and people to find and understand: metadata, structured data, crawlability, performance, accessibility and repository metadata."
whenToUse:
  - Before publishing or relaunching a project website, docs site or landing page
  - When a site gets little search traffic or shares without a proper preview card
  - When a repository lacks a description, topics, homepage link or social preview image
  - After a redesign, to confirm titles, links and structured data survived
prerequisites:
  - Access to the site's HTML source or a deployed URL
  - Access to repository settings (description, topics, homepage) if the repository is in scope
  - A one-sentence statement of what the project is and who it is for
inputs:
  - name: siteSource
    type: string
    description: Path to the site's HTML, or its public URL
  - name: audience
    type: string
    description: Who the project is for, in the words they would search with
  - name: repository
    type: string
    description: owner/name of the source repository, if any
procedure:
  - stepNumber: 1
    title: Search intent and keywords
    action: List the five to ten phrases the audience would type to find a project like this. Use real terms from the domain, not invented jargon. Map each phrase to the page that should answer it.
  - stepNumber: 2
    title: Page metadata
    action: Give every page a unique, specific <title> under 60 characters and a meta description under 160 that states what the page offers. Add a canonical URL, lang attribute and viewport meta.
  - stepNumber: 3
    title: Social previews
    action: Add Open Graph (og:title, og:description, og:image at 1200x630, og:url, og:type) and Twitter card tags. Check the image renders and the text is readable at small sizes.
  - stepNumber: 4
    title: Structured data
    action: "Add JSON-LD that describes what actually exists: SoftwareApplication or SoftwareSourceCode for the project, Person or Organization for the author with sameAs links to real profiles. Never add ratings, reviews or counts that are not real."
  - stepNumber: 5
    title: Crawlability
    action: Provide robots.txt and sitemap.xml, make sure important content is in the HTML or rendered without errors, use real links with descriptive text, and avoid content that only appears after interaction.
  - stepNumber: 6
    title: Performance and accessibility
    action: Check Core Web Vitals and Lighthouse SEO and accessibility scores. Fix missing alt text, heading order, contrast and render-blocking resources that hurt both people and rankings.
  - stepNumber: 7
    title: Repository metadata
    action: Set the repository description, topics (5 to 15 relevant terms), homepage URL and social preview image. Make the README's first screen say what the project does, who it is for and how to start.
  - stepNumber: 8
    title: Verify and submit
    action: Validate structured data, re-run Lighthouse, then submit the sitemap in Google Search Console and Bing Webmaster Tools if the owner has access. Record before and after results.
expectedOutputs:
  - SEO audit report listing each issue with the exact file or URL, why it matters and the fix
  - Updated head metadata, Open Graph and Twitter tags, and validated JSON-LD
  - robots.txt and sitemap.xml
  - Repository description, topics and homepage recommendations (or applied changes with approval)
applicableApprovalGates:
  - G2
  - G5
  - G6
failureAndRecovery:
  potentialFailures:
    - Content rendered only by JavaScript is not indexed
    - Structured data fails validation or describes things that do not exist
    - Social preview image missing, wrong size or blocked
    - Metadata duplicated across pages
  recoveryStrategy: Fix the source, re-validate with the same tools, and record the result. Remove any structured data that cannot be backed by real facts rather than guessing.
verificationCriteria:
  - Every page has a unique title and meta description
  - JSON-LD validates and every value in it is true and checkable
  - Open Graph image is 1200x630 and loads from a public URL
  - robots.txt allows the pages meant to be indexed and links to sitemap.xml
  - Lighthouse SEO score recorded before and after
relevantContractsAndMemory:
  contracts:
    - contracts/design/contract.json
    - contracts/release/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
---

# SEO and Discoverability Audit (`seo-audit`)

## 1. Purpose
Make a project's website, docs and repository easy for search engines, social previews and people to find and understand: metadata, structured data, crawlability, performance, accessibility and repository metadata.

## 2. When to Use It
- Before publishing or relaunching a project website, docs site or landing page
- When a site gets little search traffic or shares without a proper preview card
- When a repository lacks a description, topics, homepage link or social preview image
- After a redesign, to confirm titles, links and structured data survived

## 3. Prerequisites
- Access to the site's HTML source or a deployed URL
- Access to repository settings (description, topics, homepage) if the repository is in scope
- A one-sentence statement of what the project is and who it is for

## 4. Inputs
- `siteSource` (string): Path to the site's HTML, or its public URL
- `audience` (string): Who the project is for, in the words they would search with
- `repository` (string): owner/name of the source repository, if any

## 5. Procedure
1. **Search intent and keywords.** List the five to ten phrases the audience would type to find a project like this. Use real terms from the domain, not invented jargon. Map each phrase to the page that should answer it.
2. **Page metadata.** Give every page a unique, specific <title> under 60 characters and a meta description under 160 that states what the page offers. Add a canonical URL, lang attribute and viewport meta.
3. **Social previews.** Add Open Graph (og:title, og:description, og:image at 1200x630, og:url, og:type) and Twitter card tags. Check the image renders and the text is readable at small sizes.
4. **Structured data.** Add JSON-LD that describes what actually exists: SoftwareApplication or SoftwareSourceCode for the project, Person or Organization for the author with sameAs links to real profiles. Never add ratings, reviews or counts that are not real.
5. **Crawlability.** Provide robots.txt and sitemap.xml, make sure important content is in the HTML or rendered without errors, use real links with descriptive text, and avoid content that only appears after interaction.
6. **Performance and accessibility.** Check Core Web Vitals and Lighthouse SEO and accessibility scores. Fix missing alt text, heading order, contrast and render-blocking resources that hurt both people and rankings.
7. **Repository metadata.** Set the repository description, topics (5 to 15 relevant terms), homepage URL and social preview image. Make the README's first screen say what the project does, who it is for and how to start.
8. **Verify and submit.** Validate structured data, re-run Lighthouse, then submit the sitemap in Google Search Console and Bing Webmaster Tools if the owner has access. Record before and after results.

## 6. Expected Outputs
- SEO audit report listing each issue with the exact file or URL, why it matters and the fix
- Updated head metadata, Open Graph and Twitter tags, and validated JSON-LD
- robots.txt and sitemap.xml
- Repository description, topics and homepage recommendations (or applied changes with approval)

## 7. Applicable Approval Gates
G2, G5, G6

## 8. Failure and Recovery
- Content rendered only by JavaScript is not indexed
- Structured data fails validation or describes things that do not exist
- Social preview image missing, wrong size or blocked
- Metadata duplicated across pages

Fix the source, re-validate with the same tools, and record the result. Remove any structured data that cannot be backed by real facts rather than guessing.

## 9. Verification Criteria
- Every page has a unique title and meta description
- JSON-LD validates and every value in it is true and checkable
- Open Graph image is 1200x630 and loads from a public URL
- robots.txt allows the pages meant to be indexed and links to sitemap.xml
- Lighthouse SEO score recorded before and after

## 10. Relevant Contracts and Memory
- contracts/design/contract.json
- contracts/release/contract.json
- durableKnowledge.architecturalDecisions
