from __future__ import annotations

from dataclasses import dataclass

from clinrag.data_models import RetrievalResult
from clinrag.preprocessing import detect_phi_like_patterns


@dataclass(frozen=True)
class SafetyAssessment:
    flags: list[str]
    blocked: bool
    explanation: str | None = None


class ClinicalSafetyLayer:
    """Rule-based safety layer for a research prototype.

    This is not a substitute for clinical safety engineering. It exists so the MSc
    project can explicitly test safer behaviour, abstention and evidence constraints.
    """

    direct_treatment_terms = {
        "prescribe",
        "dose",
        "dosage",
        "increase",
        "decrease",
        "stop medication",
        "start medication",
        "warfarin dose",
        "diagnose",
        "treatment plan",
        "tell me exactly",
    }

    def assess_query(self, question: str) -> SafetyAssessment:
        text = question.lower()
        flags: list[str] = []
        if any(term in text for term in self.direct_treatment_terms):
            flags.append("direct_treatment_or_diagnosis_request")
        phi_flags = detect_phi_like_patterns(question)
        flags.extend(phi_flags)

        blocked = "direct_treatment_or_diagnosis_request" in flags
        explanation = None
        if blocked:
            explanation = (
                "The question appears to request direct diagnosis, prescribing, dosing or treatment "
                "instructions. This research prototype can only summarise retrieved record evidence "
                "and cannot provide clinical instructions."
            )
        return SafetyAssessment(flags=flags, blocked=blocked, explanation=explanation)

    def evidence_is_sufficient(
        self,
        evidence: list[RetrievalResult],
        *,
        min_score: float,
    ) -> bool:
        return bool(evidence) and evidence[0].score >= min_score

    def final_safety_footer(self) -> str:
        return (
            "\n\nSafety note: This is a research prototype using synthetic data. "
            "It summarises retrieved record snippets and is not medical advice."
        )
