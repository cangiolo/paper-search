"""bioRxiv / medRxiv 预印本搜索模块（通过 OpenAlex source 过滤）。

OpenAlex 索引了 bioRxiv (S4306402567) 和 medRxiv (S3005729997) 的全部内容。
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
import urllib.parse

_SSL_CONTEXT = None
try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except (ImportError, OSError):
    pass

OPENALEX_API = "https://api.openalex.org/works"
MAILTO = os.environ.get("UNPAYWALL_EMAIL", "openclaw-agent@example.com")

# OpenAlex source IDs
SOURCE_IDS = {
    "biorxiv": "S4306402567",
    "medrxiv": "S3005729997",
}

__all__ = ["search"]

def search(
    query: str,
    limit: int | None = 10,
    year_from: int | None = None,
    year_to: int | None = None,
    journal: str | None = None,
    author: str | None = None,
    full_abstract: bool = False,
    server: str = "biorxiv",  # "biorxiv" or "medrxiv"
) -> list[dict]:
    source_id = SOURCE_IDS.get(server, SOURCE_IDS["biorxiv"])
    
    params = {
        "search": query,
        "per_page": min(limit or 50, 50),
        "mailto": MAILTO,
        "filter": f"primary_location.source.id:{source_id}",
    }
    
    if year_from:
        params["filter"] += f",from_publication_date:{year_from}-01-01"
    if year_to:
        params["filter"] += f",to_publication_date:{year_to}-12-31"
    
    url = f"{OPENALEX_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[错误] 无法连接 OpenAlex API ({server}): {e}", file=sys.stderr)
        return []
    
    results = []
    for work in data.get("results", []):
        authors = [
            (a.get("author") or {}).get("display_name", "")
            for a in work.get("authorships", [])
        ]
        
        # Client-side author filter
        if author:
            author_lower = author.lower()
            if not any(author_lower in a.lower() for a in authors):
                continue
        
        # Client-side journal/source filter (no-op for preprints but kept for API consistency)
        
        doi = work.get("doi", "") or ""
        if doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]
        
        # Reconstruct abstract from inverted index
        abstract_index = work.get("abstract_inverted_index")
        if abstract_index:
            word_positions = []
            for word, positions in abstract_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join(w for _, w in word_positions)
        else:
            abstract = ""
        
        results.append({
            "title": work.get("title", ""),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else work.get("id", ""),
            "authors": authors[:20],
            "year": work.get("publication_year"),
            "journal": server,  # "biorxiv" or "medrxiv"
            "cited_by_count": work.get("cited_by_count", 0),
            "abstract": abstract if full_abstract else abstract[:500],
            "source_db": server,
            "tldr": "",
            "oa_status": "gold",
            "oa_available": True,
            "openalex_id": work.get("id", ""),
        })
        
        if limit and len(results) >= limit:
            break
    
    return results
