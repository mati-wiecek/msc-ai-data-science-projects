from __future__ import annotations

from clinrag.data_models import RetrievalResult


class GroundedTemplateGenerator:
    """Deterministic answer generator.

    A fuller study may later compare an LLM generator with this transparent baseline.
    Keeping this version deterministic makes tests and early evaluation easier.
    """

    def generate(
        self,
        question: str,
        evidence: list[RetrievalResult],
        *,
        max_items: int = 4,
    ) -> str:
        if not evidence:
            return (
                "I do not have enough retrieved evidence to answer this question from the record. "
                "No clinical conclusion should be drawn."
            )

        lines = [
            "Based on the retrieved synthetic EHR evidence, the record contains the following relevant information:"
        ]
        for result in evidence[:max_items]:
            doc = result.doc
            lines.append(
                f"- [{doc.doc_id}] {doc.section.replace('_', ' ')} ({doc.timestamp}): {doc.text}"
            )
        lines.append(
            "The answer is limited to the cited evidence above; absence of evidence here does not prove absence in the full record."
        )
        return "\n".join(lines)
