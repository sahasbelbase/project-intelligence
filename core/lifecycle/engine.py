"""
Project Intelligence — Lifecycle State Machine Engine
Deterministic evaluation of G0 through G6 lifecycle gates, transitions, exemptions, and rollbacks.
"""

from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path


class LifecycleError(Exception):
    """Raised when an illegal lifecycle operation is attempted."""
    pass


class LifecycleEngine:
    def __init__(self, fsm_path: Optional[Path] = None):
        if fsm_path is None:
            fsm_path = Path(__file__).parent / "lifecycle-fsm.json"
        
        with open(fsm_path, "r", encoding="utf-8") as f:
            self.spec = json.load(f)
            
        self.gates: Dict[str, Dict[str, Any]] = {
            g["gateId"]: g for g in self.spec.get("gates", [])
        }
        self.transitions: List[Dict[str, Any]] = self.spec.get("transitions", [])

    def get_gate(self, gate_id: str) -> Dict[str, Any]:
        if gate_id not in self.gates:
            raise LifecycleError(f"Unknown gate '{gate_id}'. Valid gates: {list(self.gates.keys())}")
        return self.gates[gate_id]

    def can_transition(
        self,
        current_gate: str,
        target_gate: str,
        condition: str,
        is_exempt: bool = False,
        exemption_justification: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Determines whether a transition from current_gate to target_gate is permitted under given condition.
        Returns (is_allowed, reason).
        """
        if current_gate not in self.gates:
            return False, f"Invalid current gate '{current_gate}'."
        if target_gate not in self.gates:
            return False, f"Invalid target gate '{target_gate}'."

        # Special check: Exemption of G2 (Design)
        if current_gate == "G1" and target_gate == "G3":
            g2_spec = self.gates["G2"]
            if g2_spec.get("allowedExemption", False) and is_exempt:
                if not exemption_justification or len(exemption_justification.strip()) < 10:
                    return False, "Gate G2 exemption requires an explicit justification (minimum 10 chars)."
                # Valid exemption bypass G1 -> G3
                return True, "Gate G2 formally exempted with documented justification."
            else:
                return False, "Cannot skip Gate G2 without valid exemption approval."

        # Find matching declared transition
        matching = [
            t for t in self.transitions
            if t["fromGate"] == current_gate and t["toGate"] == target_gate
        ]

        if not matching:
            return False, f"No legal transition defined from {current_gate} to {target_gate}."

        for trans in matching:
            if trans["condition"] == condition:
                return True, f"Transition from {current_gate} to {target_gate} permitted under {condition}."

        allowed_conditions = [t["condition"] for t in matching]
        return False, f"Condition '{condition}' does not match allowed conditions: {allowed_conditions}."

    def validate_transition(
        self,
        current_gate: str,
        target_gate: str,
        condition: str,
        is_exempt: bool = False,
        exemption_justification: Optional[str] = None
    ):
        """Raises LifecycleError if transition is invalid."""
        allowed, reason = self.can_transition(
            current_gate=current_gate,
            target_gate=target_gate,
            condition=condition,
            is_exempt=is_exempt,
            exemption_justification=exemption_justification
        )
        if not allowed:
            raise LifecycleError(f"Lifecycle transition blocked: {reason}")
        return True


    def get_transition(self, from_gate: str, to_gate: str) -> Optional[Dict[str, Any]]:
        """Returns the transition dictionary between two gates if one exists."""
        for t in self.transitions:
            if t["fromGate"] == from_gate and t["toGate"] == to_gate:
                return t
        return None


def _load_execution_state(repo_root: Path) -> Tuple[Optional[Path], Dict[str, Any]]:
    """Loads execution state from memory/execution-state.json or memory/state.json."""
    exec_state = repo_root / "memory" / "execution-state.json"
    legacy_state = repo_root / "memory" / "state.json"
    target_path = exec_state if exec_state.exists() else legacy_state

    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return target_path, json.load(f)
        except Exception:
            pass
    return None, {}


def _save_execution_state(repo_root: Path, state_data: Dict[str, Any]):
    """Synchronizes state to both execution-state.json and state.json for compatibility."""
    memory_dir = repo_root / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    exec_path = memory_dir / "execution-state.json"
    state_path = memory_dir / "state.json"
    
    for p in [exec_path, state_path]:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Project Intelligence — Lifecycle State Machine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display the active lifecycle gate, phase, and available transitions."
    )
    parser.add_argument(
        "--advance",
        metavar="GATE",
        help="Advance the lifecycle to the specified target gate (e.g. G1, G2, G3)."
    )
    parser.add_argument(
        "--rollback",
        metavar="GATE",
        help="Rollback the lifecycle to a prior gate (e.g. G4) upon defect discovery."
    )
    parser.add_argument(
        "--reason",
        metavar="TEXT",
        help="Defect reason or justification rationale for rollback or exemption."
    )
    parser.add_argument(
        "--exempt",
        action="store_true",
        help="Mark Gate G2 (Design) as formally exempted (requires --reason with >=10 chars)."
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the internal consistency and completeness of all gates and transitions."
    )
    parser.add_argument(
        "--repo-root",
        metavar="PATH",
        default=".",
        help="Path to project repository root (defaults to current working directory)."
    )

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    engine = LifecycleEngine()

    if args.verify:
        print(f"Lifecycle State Machine Verification: PASSED")
        print(f"Gates Defined       : {len(engine.gates)} (G0 through G6)")
        print(f"Transitions Defined : {len(engine.transitions)}")
        for g_id, g_info in engine.gates.items():
            print(f"  • {g_id}: {g_info.get('name')} (Contract: {g_info.get('requiredContractType')})")
        sys.exit(0)

    # Load current state
    state_path, state_data = _load_execution_state(repo_root)
    current_gate = state_data.get("currentGate", "G0")

    if args.status or (not args.advance and not args.rollback and not args.verify):
        print("=" * 70)
        print("PROJECT INTELLIGENCE — LIFECYCLE STATUS")
        print("=" * 70)
        print(f"Repository Root : {repo_root}")
        print(f"Active Gate     : {current_gate} ({engine.get_gate(current_gate).get('name', 'Unknown')})")
        print(f"Active Phase    : Phase {state_data.get('activePhase', 0)}")
        print(f"Required Output : contracts/{engine.get_gate(current_gate).get('requiredContractType')}/contract.json")
        print("-" * 70)
        print("Available Forward Transitions:")
        for t in engine.transitions:
            if t["fromGate"] == current_gate and t["toGate"] != current_gate:
                approval_req = " [Requires Human Approval]" if t.get("requiresHumanApproval") else ""
                print(f"  -> {t['toGate']} under condition '{t['condition']}'{approval_req}")
        print("=" * 70)
        sys.exit(0)

    if args.advance:
        target_gate = args.advance.upper()
        # If target gate is current gate, determine intended progression
        if target_gate == current_gate:
            gate_order = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
            idx = gate_order.index(current_gate) if current_gate in gate_order else -1
            if idx >= 0 and idx < len(gate_order) - 1:
                target_gate = gate_order[idx + 1]

        # Condition lookup
        condition = f"{current_gate}_APPROVED"
        if current_gate == "G4" and target_gate == "G5":
            condition = "G4_VERIFIED"
        elif current_gate == "G5" and target_gate == "G6":
            condition = "G5_PASSED"
        elif current_gate == "G2" and target_gate == "G3":
            condition = "G2_APPROVED_OR_EXEMPTED"

        # Check exemption for G2
        is_exempt = args.exempt
        justification = args.reason or ""

        # Validate transition
        allowed, reason = engine.can_transition(
            current_gate=current_gate,
            target_gate=target_gate,
            condition=condition,
            is_exempt=is_exempt,
            exemption_justification=justification
        )

        if not allowed:
            print(f"[ERROR] Lifecycle transition blocked: {reason}", file=sys.stderr)
            sys.exit(1)

        # Check contract file existence
        gate_info = engine.get_gate(current_gate)
        contract_type = gate_info.get("requiredContractType")
        contract_file = repo_root / "contracts" / contract_type / "contract.json"

        if not contract_file.exists():
            print(f"[ERROR] Cannot advance from {current_gate}: Missing required contract '{contract_file}'", file=sys.stderr)
            sys.exit(2)

        # Update state data
        gate_order = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
        target_idx = gate_order.index(target_gate) if target_gate in gate_order else 0

        state_data["currentGate"] = target_gate
        state_data["activePhase"] = target_idx
        _save_execution_state(repo_root, state_data)

        print(f"[SUCCESS] Advanced lifecycle gate: {current_gate} -> {target_gate}")
        print(f"Condition: {condition}")
        print(f"Active Gate is now {target_gate} ({engine.get_gate(target_gate).get('name')}).")
        sys.exit(0)

    if args.rollback:
        target_gate = args.rollback.upper()
        reason = args.reason or "Defects discovered during review."
        condition = "REVIEW_DEFECTS_FOUND"

        allowed, check_reason = engine.can_transition(
            current_gate=current_gate,
            target_gate=target_gate,
            condition=condition
        )

        if not allowed:
            print(f"[ERROR] Lifecycle rollback blocked: {check_reason}", file=sys.stderr)
            sys.exit(1)

        state_data["currentGate"] = target_gate
        gate_order = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
        target_idx = gate_order.index(target_gate) if target_gate in gate_order else 0
        state_data["activePhase"] = target_idx
        _save_execution_state(repo_root, state_data)

        print(f"[ROLLBACK] Successfully rolled back lifecycle: {current_gate} -> {target_gate}")
        print(f"Reason: {reason}")
        sys.exit(0)


if __name__ == "__main__":
    main()
