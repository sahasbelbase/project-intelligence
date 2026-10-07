# OpenAI Agents SDK Adapter Specification

## 1. Overview & Architecture
The OpenAI Agents SDK provides first-class primitives for multi-agent workflows:
- `Agent`: An autonomous entity with dedicated instructions, tools, and handoffs.
- `Handoff`: A deterministic control transfer mechanism passing execution and context from one agent to another.
- `Runner`: The execution orchestrator managing tool invocations and handoffs.
- `Guardrail`: Pre/post invocation checks ensuring security invariants.

This adapter demonstrates how the 9 canonical Project Intelligence agents are instantiated and interconnected in Python using the official Agents SDK.

---

## 2. Programmatic Implementation Reference

```python
"""
Project Intelligence — OpenAI Agents SDK Implementation Reference
Instantiates all 9 canonical agents and configures deterministic handoffs.
"""

from typing import Any, Dict
# From openai-agents SDK (or equivalent agent framework)
# from agents import Agent, Runner, handoff, function_tool


def create_project_intelligence_swarm(project_root: str) -> Dict[str, Any]:
    """
    Constructs and links all 9 canonical agents with deterministic handoff functions.
    """

    # 1. Forward declare agent instances
    orchestrator_agent = None
    discovery_agent = None
    design_agent = None
    architecture_agent = None
    planning_agent = None
    implementation_agent = None
    verification_agent = None
    independent_review_agent = None
    doc_memory_agent = None

    # 2. Define Handoff Functions
    def transfer_to_discovery():
        """Hands off execution to the Environment & Discovery Specialist (Gate G0)."""
        return discovery_agent

    def transfer_to_design():
        """Hands off execution to the Visual & Interface Design Specialist (Gate G2)."""
        return design_agent

    def transfer_to_architecture():
        """Hands off execution to the Systems Architecture Specialist (Gate G3)."""
        return architecture_agent

    def transfer_to_planning():
        """Hands off execution to the Phased Planning & WBS Specialist (Gate G3/G4)."""
        return planning_agent

    def transfer_to_implementation():
        """Hands off execution to the Controlled Implementation Specialist (Gate G4)."""
        return implementation_agent

    def transfer_to_verification():
        """Hands off execution to the Automated Testing & Verification Specialist (Gate G4)."""
        return verification_agent

    def transfer_to_independent_review():
        """Hands off execution to the Adversarial Quality & Review Specialist (Gate G5)."""
        return independent_review_agent

    def transfer_to_documentation_and_memory():
        """Hands off execution to the Durable Documentation & Memory Specialist (Gate G6)."""
        return doc_memory_agent

    def transfer_to_orchestrator():
        """Returns control to the Lead Project Orchestrator."""
        return orchestrator_agent

    # 3. Instantiate Agents with System Prompts and Handoffs

    orchestrator_agent = {
        "name": "Lead Project Orchestrator",
        "role_id": "orchestrator",
        "handoffs": [
            transfer_to_discovery,
            transfer_to_design,
            transfer_to_architecture,
            transfer_to_planning,
            transfer_to_implementation,
            transfer_to_verification,
            transfer_to_independent_review,
            transfer_to_documentation_and_memory
        ]
    }

    discovery_agent = {
        "name": "Environment & Discovery Specialist",
        "role_id": "discovery",
        "handoffs": [transfer_to_orchestrator, transfer_to_planning]
    }

    design_agent = {
        "name": "Visual & Interface Design Specialist",
        "role_id": "design",
        "handoffs": [transfer_to_orchestrator, transfer_to_architecture]
    }

    architecture_agent = {
        "name": "Systems Architecture Specialist",
        "role_id": "architecture",
        "handoffs": [transfer_to_orchestrator, transfer_to_planning]
    }

    planning_agent = {
        "name": "Phased Planning & WBS Specialist",
        "role_id": "planning",
        "handoffs": [transfer_to_orchestrator, transfer_to_implementation]
    }

    implementation_agent = {
        "name": "Controlled Implementation Specialist",
        "role_id": "implementation",
        "handoffs": [transfer_to_verification, transfer_to_orchestrator]
    }

    verification_agent = {
        "name": "Automated Testing & Verification Specialist",
        "role_id": "verification",
        "handoffs": [transfer_to_independent_review, transfer_to_orchestrator, transfer_to_implementation]
    }

    independent_review_agent = {
        "name": "Adversarial Quality & Review Specialist",
        "role_id": "independent-review",
        "handoffs": [transfer_to_orchestrator, transfer_to_implementation, transfer_to_documentation_and_memory]
    }

    doc_memory_agent = {
        "name": "Durable Documentation & Memory Specialist",
        "role_id": "documentation-and-memory",
        "handoffs": [transfer_to_orchestrator]
    }

    return {
        "orchestrator": orchestrator_agent,
        "discovery": discovery_agent,
        "design": design_agent,
        "architecture": architecture_agent,
        "planning": planning_agent,
        "implementation": implementation_agent,
        "verification": verification_agent,
        "independent-review": independent_review_agent,
        "documentation-and-memory": doc_memory_agent
    }
```

---

## 3. Function Calling & Tool Schemas
Every tool provided to the Codex runtime maps directly to the `toolPermissions` defined in `agent.json`.
For agents with `readOnlyFileSystem: true`, file editing tool declarations are omitted entirely from the available functions list, guaranteeing runtime security at the API level.
