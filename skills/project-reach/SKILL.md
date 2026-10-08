---
skillId: project-reach
name: Project Launch and Reach
purpose: "Plan and run an honest launch that gets a project in front of the people who need it: positioning, a landing-page README, the right communities and directories, launch posts, and measuring what worked."
whenToUse:
  - Before announcing a new project, major release or website
  - When a useful project has few visitors, stars or users
  - When choosing where to share a project and how to describe it
  - After a launch, to review what brought people in and plan the next step
prerequisites:
  - A working project with a public link (repository, website or demo)
  - A clear statement of the problem it solves and for whom
  - The owner's accounts on the channels they want to use
inputs:
  - name: project
    type: string
    description: Name, link and one-sentence description
  - name: audience
    type: string
    description: The people who would benefit most, and where they already gather
  - name: goals
    type: array
    description: What success looks like, such as users, contributors or feedback
procedure:
  - stepNumber: 1
    title: Positioning
    action: "Write one sentence: who it is for, what it does, and why it is different from what they use today. Test it on the README's first line and the repository description."
  - stepNumber: 2
    title: Landing page and README
    action: Make the first screen show the problem, a screenshot or short demo, and a copy-paste quick start. Add the license, a link to the website and a short author section.
  - stepNumber: 3
    title: Channel selection
    action: Pick three to five places where the audience already is, for example Hacker News (Show HN), relevant subreddits, Product Hunt, dev.to or Hashnode, LinkedIn, X, Discord or Slack communities, awesome-lists and skill or package registries. Read each one's rules first.
  - stepNumber: 4
    title: Launch content
    action: "Write a post per channel in that community's style: what it is, why you built it, what is unfinished, and a direct link. Disclose that you are the author. Prepare a short demo GIF or video and a social preview image."
  - stepNumber: 5
    title: Timing and sequence
    action: Launch on one primary channel first, be present to answer questions for the first hours, then share to the others over the following days. Avoid posting the same text everywhere at once.
  - stepNumber: 6
    title: Ongoing reach
    action: Publish release notes for each version, write one useful article about a problem the project solves, submit to relevant curated lists, and respond to issues and comments quickly.
  - stepNumber: 7
    title: Measure
    action: Track referrers and visitors (GitHub Insights traffic, site analytics if installed), stars, installs and issues opened, before and after each step. Keep what worked and drop what did not.
expectedOutputs:
  - Positioning sentence and updated README first screen
  - Channel plan with each community's rules and the chosen order
  - Launch posts per channel, written for that audience
  - Measurement table with baseline and results
applicableApprovalGates:
  - G6
failureAndRecovery:
  potentialFailures:
    - Post removed for breaking a community's self-promotion rules
    - Launch gets attention but the quick start fails for new users
    - No baseline recorded, so results cannot be judged
  recoveryStrategy: Read and follow each community's rules before posting; test the quick start on a clean machine before launch; if a post is removed, do not repost elsewhere the same day, fix the issue and engage normally first.
verificationCriteria:
  - No fake accounts, purchased stars, vote rings or undisclosed self-promotion
  - Every claim in launch posts is true and linkable
  - Quick start works from a clean checkout
  - Baseline and post-launch numbers are recorded with their source
relevantContractsAndMemory:
  contracts:
    - contracts/release/contract.json
  memoryRecords:
    - backlog
---

# Project Launch and Reach (`project-reach`)

## 1. Purpose
Plan and run an honest launch that gets a project in front of the people who need it: positioning, a landing-page README, the right communities and directories, launch posts, and measuring what worked.

## 2. When to Use It
- Before announcing a new project, major release or website
- When a useful project has few visitors, stars or users
- When choosing where to share a project and how to describe it
- After a launch, to review what brought people in and plan the next step

## 3. Prerequisites
- A working project with a public link (repository, website or demo)
- A clear statement of the problem it solves and for whom
- The owner's accounts on the channels they want to use

## 4. Inputs
- `project` (string): Name, link and one-sentence description
- `audience` (string): The people who would benefit most, and where they already gather
- `goals` (array): What success looks like, such as users, contributors or feedback

## 5. Procedure
1. **Positioning.** Write one sentence: who it is for, what it does, and why it is different from what they use today. Test it on the README's first line and the repository description.
2. **Landing page and README.** Make the first screen show the problem, a screenshot or short demo, and a copy-paste quick start. Add the license, a link to the website and a short author section.
3. **Channel selection.** Pick three to five places where the audience already is, for example Hacker News (Show HN), relevant subreddits, Product Hunt, dev.to or Hashnode, LinkedIn, X, Discord or Slack communities, awesome-lists and skill or package registries. Read each one's rules first.
4. **Launch content.** Write a post per channel in that community's style: what it is, why you built it, what is unfinished, and a direct link. Disclose that you are the author. Prepare a short demo GIF or video and a social preview image.
5. **Timing and sequence.** Launch on one primary channel first, be present to answer questions for the first hours, then share to the others over the following days. Avoid posting the same text everywhere at once.
6. **Ongoing reach.** Publish release notes for each version, write one useful article about a problem the project solves, submit to relevant curated lists, and respond to issues and comments quickly.
7. **Measure.** Track referrers and visitors (GitHub Insights traffic, site analytics if installed), stars, installs and issues opened, before and after each step. Keep what worked and drop what did not.

## 6. Expected Outputs
- Positioning sentence and updated README first screen
- Channel plan with each community's rules and the chosen order
- Launch posts per channel, written for that audience
- Measurement table with baseline and results

## 7. Applicable Approval Gates
G6

## 8. Failure and Recovery
- Post removed for breaking a community's self-promotion rules
- Launch gets attention but the quick start fails for new users
- No baseline recorded, so results cannot be judged

Read and follow each community's rules before posting; test the quick start on a clean machine before launch; if a post is removed, do not repost elsewhere the same day, fix the issue and engage normally first.

## 9. Verification Criteria
- No fake accounts, purchased stars, vote rings or undisclosed self-promotion
- Every claim in launch posts is true and linkable
- Quick start works from a clean checkout
- Baseline and post-launch numbers are recorded with their source

## 10. Relevant Contracts and Memory
- contracts/release/contract.json
- backlog
