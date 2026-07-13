# SciSpace Gap Analysis — Verifiable Evidence Engine

Technique from SciSpace (typeset.io) for identifying research gaps in a body of literature. Applied to our PubMed RAG context:

## How It Works
1. **Input**: A research question or topic + a corpus of papers (our 684k PubMed abstracts)
2. **Thematic clustering** — groups papers by methodology, findings, time period
3. **Gap detection** — finds:
   - Questions with no/weak supporting evidence
   - Contradictory findings across papers
   - Under-explored drug/disease combinations
   - Temporal gaps (old studies never replicated)
4. **Output**: Structured gap report with confidence scores

## Application to Evidence Engine
- Our RAG already retrieves evidence — SciSpace gap analysis adds the **"what's missing"** layer
- User asks "is metformin safe with X?" → we answer and also flag: *"No papers found for this combination, but here are 3 related papers [PMID]..."*
- Could be Layer 3.5 between Retrieval and Generation in the 5-layer architecture
- Adds the **empty-retrieval signal** as a structured output, not just a fallback

## References
- https://typeset.io (SciSpace)
- Standard gap analysis frameworks: 5-why, SWOT, systematic review methodology
