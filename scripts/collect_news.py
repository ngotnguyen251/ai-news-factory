"""Collect candidate headlines only; verification and editorial approval required."""
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
req = urllib.request.Request(URL, headers={"User-Agent": "AI-News-Factory/0.1"})
with urllib.request.urlopen(req, timeout=30) as response:
    root = ET.fromstring(response.read())
items = []
for item in root.findall("./channel/item")[:20]:
    items.append({key: item.findtext(key, default="") for key in ("title", "link", "pubDate", "description")})
pathlib.Path("output").mkdir(exist_ok=True)
pathlib.Path("output/candidates.json").write_text(json.dumps({
    "retrieved_at": datetime.now(timezone.utc).isoformat(),
    "status": "unverified_headline_candidates", "items": items
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Collected {len(items)} candidates; no video generated.")
