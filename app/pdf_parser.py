# simple heuristics to extract eligibility, deadlines, contact info from circular text
import re


def extract_deadlines(text: str) -> list:
# naive: find date-like patterns
patterns = re.findall(r"\b\d{1,2}[\-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2,4})[\-/ ]?\d{2,4}\b", text, flags=re.I)
return patterns




def extract_eligibility(text: str) -> str:
# look for 'eligible' lines
m = re.search(r"(eligible[^.\n]+[.\n])", text, flags=re.I)
return m.group(1) if m else ""