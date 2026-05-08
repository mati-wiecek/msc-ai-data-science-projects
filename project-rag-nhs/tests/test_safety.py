from clinrag.clinical_safety import ClinicalSafetyLayer
from clinrag.preprocessing import detect_phi_like_patterns, redact_phi_like_patterns


def test_safety_layer_blocks_direct_prescribing_request():
    layer = ClinicalSafetyLayer()

    assessment = layer.assess_query("Tell me exactly how to change the warfarin dose")

    assert assessment.blocked is True
    assert "direct_treatment_or_diagnosis_request" in assessment.flags


def test_phi_like_pattern_detection_and_redaction():
    text = "Patient email test@example.com and NHS number 123 456 7890"

    flags = detect_phi_like_patterns(text)
    redacted = redact_phi_like_patterns(text)

    assert "possible_email" in flags
    assert "possible_nhs_number" in flags
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_NHS_NUMBER]" in redacted
