import re


def validate_citations(answer: str, evidence: list[dict]) -> dict:
	valid_ids = {item["id"] for item in evidence}
	cited_ids = set(re.findall(r"\[(E\d+)\]", answer))

	invalid_ids = cited_ids - valid_ids

	return {
    	"valid": len(invalid_ids) == 0,
    	"valid_evidence_ids": sorted(valid_ids),
    	"cited_ids": sorted(cited_ids),
    	"invalid_ids": sorted(invalid_ids),
	}