from __future__ import annotations

from clinrag.clinical_safety import ClinicalSafetyLayer
from clinrag.data_models import ClinicalDocument, RAGAnswer
from clinrag.generator import GroundedTemplateGenerator
from clinrag.retrieval import Retriever, TfidfRetriever


class ClinicallyAwareRAG:
    """Orchestrates retrieval, safety checks and grounded answer generation."""

    def __init__(
        self,
        documents: list[ClinicalDocument],
        *,
        retriever: Retriever | None = None,
        safety_layer: ClinicalSafetyLayer | None = None,
        generator: GroundedTemplateGenerator | None = None,
        min_score: float = 0.05,
        top_k: int = 3,
    ) -> None:
        self.documents = documents
        self.retriever = retriever or TfidfRetriever()
        self.safety_layer = safety_layer or ClinicalSafetyLayer()
        self.generator = generator or GroundedTemplateGenerator()
        self.min_score = min_score
        self.top_k = top_k
        self.retriever.fit(documents)

    def answer(self, question: str, *, patient_id: str | None = None) -> RAGAnswer:
        assessment = self.safety_layer.assess_query(question)
        if assessment.blocked:
            answer = (assessment.explanation or "The question is outside the safe scope.")
            answer += self.safety_layer.final_safety_footer()
            return RAGAnswer(
                question=question,
                patient_id=patient_id,
                answer=answer,
                evidence=[],
                safety_flags=assessment.flags,
                abstained=True,
            )

        evidence = self.retriever.search(question, patient_id=patient_id, top_k=self.top_k)
        sufficient = self.safety_layer.evidence_is_sufficient(evidence, min_score=self.min_score)
        if not sufficient:
            answer = (
                "I do not have enough retrieved evidence to answer this question from the record. "
                "No clinical conclusion should be drawn."
            )
            answer += self.safety_layer.final_safety_footer()
            return RAGAnswer(
                question=question,
                patient_id=patient_id,
                answer=answer,
                evidence=evidence,
                safety_flags=assessment.flags + ["insufficient_retrieved_evidence"],
                abstained=True,
            )

        answer = self.generator.generate(question, evidence)
        answer += self.safety_layer.final_safety_footer()
        return RAGAnswer(
            question=question,
            patient_id=patient_id,
            answer=answer,
            evidence=evidence,
            safety_flags=assessment.flags,
            abstained=False,
        )
