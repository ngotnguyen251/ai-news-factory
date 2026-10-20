"""Build a review-only news package from RSS candidates; never invent story facts."""
import json, re
from pathlib import Path
from datetime import datetime, timezone

source=Path("output/candidates.json")
data=json.loads(source.read_text(encoding="utf-8"))
items=[x for x in data["items"] if x.get("title") and x.get("link")]
if not items:
    raise SystemExit("No headlines; cannot produce news package")
item=items[0]
title=re.sub(r"<[^>]+>","",item["title"]).strip()
# Explicit attribution and no unverified extrapolation.
script=("This is an AI News Factory headline preview. "
        "One headline currently appearing in Google News is: "
        + title + ". "
        "This is a headline summary, not an independently verified report. "
        "Please check the original publisher, date, and full article before sharing.")
Path("output/story_en.txt").write_text(script,encoding="utf-8")
Path("output/story.json").write_text(json.dumps({
 "headline":title,"link":item["link"],"published":item.get("pubDate",""),
 "retrieved_at":data.get("retrieved_at"),"editorial_status":"REVIEW_REQUIRED",
 "disclaimer":"Headline only; not independently verified. No automatic publication."
},ensure_ascii=False,indent=2),encoding="utf-8")
print("Prepared headline preview:",title)
