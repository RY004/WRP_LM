from saturn.retrieval.confidence import confidence_band
from saturn.retrieval.fusion import hybrid_score
from saturn.retrieval.lexical import lexical_score
from saturn.retrieval.repository import RetrievalCandidate
from saturn.retrieval.vector import cosine_similarity


def test_lexical_vector_fusion_and_confidence() -> None:
    candidate = RetrievalCandidate(
        source_type="document_chunk",
        source_id="chunk-1",
        project_id="project-1",
        title="Saturn Retrieval",
        text="Hybrid retrieval combines lexical and vector evidence.",
        heading_path_text="Retrieval > Hybrid",
    )

    lexical = lexical_score("hybrid retrieval", candidate)
    vector = cosine_similarity([1.0, 0.0], [0.8, 0.2])
    score = hybrid_score(lexical, vector, heading_boost=0.1)

    assert lexical > 0.5
    assert vector > 0.9
    assert score >= lexical
    assert confidence_band(score) in {"medium", "high"}
    assert confidence_band(score, degraded=True) in {"low", "medium"}
