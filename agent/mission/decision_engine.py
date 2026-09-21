"""Decision engine: turn validation + deviation into state decisions."""

from __future__ import annotations

from typing import Any, Dict


class DecisionEngine:
    """Main decision component. Advances state only on CORRECT."""

    def __init__(
        self,
        state_machine,
        step_manager,
        validator,
        detector,
        rules=None,
    ) -> None:
        self.sm = state_machine
        self.steps = step_manager
        self.validator = validator
        self.detector = detector

        self._guidance = {}

        for r in (rules or []):
            key = (r.get("step_id"), r.get("result"))

            if key not in self._guidance:
                self._guidance[key] = str(
                    r.get("guidance", "")
                )

        self._deviation_guidance = {}

        for r in (rules or []):
            if r.get("result") == "DEVIATION":
                self._deviation_guidance.setdefault(
                    r.get("step_id"),
                    str(r.get("guidance", "")),
                )

    def _advance_guidance(
        self,
        step_id: str,
        fallback: str,
    ) -> str:
        return self._guidance.get(
            (step_id, "ADVANCE"),
            fallback,
        )

    def process(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:

        # ---------------------------------------------------------
        # Experiment already completed
        # ---------------------------------------------------------
        if self.sm.is_complete():
            return {
                "status": "COMPLETED",
                "step_id": self.sm.current_step_id(),
                "next_step_id": None,
                "deviation_type": None,
                "guidance": "Experiment completed successfully.",
            }

        # ---------------------------------------------------------
        # Current protocol step
        # ---------------------------------------------------------
        step = self.sm.current_step()

        sid = str(step.get("step_id"))
        exp_act = str(step.get("activity"))
        exp_obj = str(step.get("expected_object"))

        det_act = event.get("activity")
        det_obj = event.get("object")

        # ---------------------------------------------------------
        # Validate perception against current protocol step
        # ---------------------------------------------------------
        validation = self.validator.validate(
            event,
            sid,
        )

        reason = validation.get("reason")

        # ---------------------------------------------------------
        # LOW CONFIDENCE + clearly different object
        #
        # This handles the live perception case:
        #
        # Expected object:
        #     experiment_container
        #
        # Detected object:
        #     biological_sample
        #
        # Without this special case, LOW_CONFIDENCE would hide
        # the actual protocol-object mismatch.
        #
        # IMPORTANT:
        # This is ONLY applied when the validator says
        # LOW_CONFIDENCE. Other deviation reasons must continue
        # through the normal deviation detector.
        # ---------------------------------------------------------
        if (
            reason == "LOW_CONFIDENCE"
            and det_obj is not None
            and str(det_obj) != exp_obj
        ):
            g = (
                self._deviation_guidance.get(sid)
                or f"Wrong object detected. Expected {exp_obj}."
            )

            return {
                "status": "DEVIATION",
                "step_id": sid,
                "next_step_id": sid,
                "deviation_type": "WRONG_OBJECT",
                "expected_activity": exp_act,
                "expected_object": exp_obj,
                "detected_activity": det_act,
                "detected_object": det_obj,
                "guidance": g,
            }

        # ---------------------------------------------------------
        # Low confidence
        # ---------------------------------------------------------
        if reason == "LOW_CONFIDENCE":
            g = (
                self._guidance.get(
                    (sid, "UNCERTAIN")
                )
                or (
                    "Detection confidence is low. "
                    "Please repeat or hold the action "
                    "for verification."
                )
            )

            return {
                "status": "UNCERTAIN",
                "step_id": sid,
                "next_step_id": sid,
                "deviation_type": "LOW_CONFIDENCE",
                "expected_activity": exp_act,
                "expected_object": exp_obj,
                "detected_activity": det_act,
                "detected_object": det_obj,
                "guidance": g,
            }

        # ---------------------------------------------------------
        # Unknown activity
        # ---------------------------------------------------------
        if reason == "UNKNOWN_ACTION":
            return {
                "status": "DEVIATION",
                "step_id": sid,
                "next_step_id": sid,
                "deviation_type": "UNKNOWN_ACTION",
                "expected_activity": exp_act,
                "expected_object": exp_obj,
                "detected_activity": det_act,
                "detected_object": det_obj,
                "guidance": (
                    f"Unknown action '{det_act}'. "
                    f"Please perform {exp_act}."
                ),
            }

        # ---------------------------------------------------------
        # Valid protocol event
        # ---------------------------------------------------------
        if validation.get("valid"):

            info = self.detector.detect(
                event,
                sid,
            )

            nxt = self.sm.next_step()

            nxt_id = (
                str(nxt.get("step_id"))
                if nxt
                else None
            )

            # -----------------------------------------------------
            # Final step completed
            # -----------------------------------------------------
            if nxt is None:

                self.sm.complete_current()

                g = self._advance_guidance(
                    sid,
                    "Experiment completed successfully.",
                )

                out = {
                    "status": "COMPLETED",
                    "step_id": sid,
                    "next_step_id": None,
                    "deviation_type": None,
                    "guidance": g,
                }

                if info.get("recovered"):
                    out["deviation_type"] = "RECOVERED"

                return out

            # -----------------------------------------------------
            # Advance to next protocol step
            # -----------------------------------------------------
            g = self._advance_guidance(
                sid,
                f"Step {sid} completed. Proceed.",
            )

            self.sm.advance()

            out = {
                "status": "CORRECT",
                "step_id": sid,
                "next_step_id": nxt_id,
                "deviation_type": None,
                "guidance": g,
            }

            if info.get("recovered"):
                out["deviation_type"] = "RECOVERED"

            return out

        # ---------------------------------------------------------
        # General deviation handling
        # ---------------------------------------------------------
        info = self.detector.detect(
            event,
            sid,
        )

        dtype = (
            info.get("deviation_type")
            or reason
            or "WRONG_SEQUENCE"
        )

        if dtype == "WRONG_OBJECT":

            g = (
                self._deviation_guidance.get(sid)
                or f"Wrong object detected. Expected {exp_obj}."
            )

        elif dtype in (
            "PREMATURE_ACTION",
            "SKIPPED_STEP",
            "WRONG_SEQUENCE",
        ):

            g = (
                self._deviation_guidance.get(sid)
                or (
                    f"Wrong sequence. "
                    f"Expected {exp_act} at {sid}."
                )
            )

        else:

            g = (
                f"Deviation ({dtype}). "
                f"Expected {exp_act} with {exp_obj}."
            )

        return {
            "status": "DEVIATION",
            "step_id": sid,
            "next_step_id": sid,
            "deviation_type": dtype,
            "expected_activity": exp_act,
            "expected_object": exp_obj,
            "detected_activity": det_act,
            "detected_object": det_obj,
            "guidance": g,
        }