"""arXiv 预印本搜索模块。"""

from __future__ import annotations

import ssl
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

_SSL_CONTEXT = None
try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except (ImportError, OSError):
    pass

ARXIV_API = "http://export.arxiv.org/api/query"

__all__ = ["search"]

def _get_xml(url: str, timeout: int = 30) -> ET.Element:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CONTEXT) as resp:
        return ET.fromstring(resp.read().decode())

def search(
    query: str,
    limit: int | None = 10,
    year_from: int | None = None,
    year_to: int | None = None,
    journal: str | None = None,
    author: str | None = None,
    full_abstract: bool = False,
) -> list[dict]:
    # arXiv search query syntax
    arxiv_query = query
    
    # arXiv API doesn't support year filtering in query, we'll filter client-side
    # arXiv API doesn't support journal/author filtering in query
    
    params = {
        "search_query": f"all:{arxiv_query}",
        "start": 0,
        "max_results": min((limit or 50) * 2, 100),  # fetch more for filtering
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"
    
    try:
        root = _get_xml(url)
    except Exception as e:
        print(f"[错误] 无法连接 arXiv API: {e}", file=__import__("sys").stderr)
        return []
    
    # Atom namespace
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    results = []
    for entry in root.findall("atom:entry", ns):
        # Skip the feed's own entry (if any)
        id_elem = entry.find("atom:id", ns)
        if id_elem is None:
            continue
        arxiv_id = id_elem.text.split("/")[-1] if id_elem.text else ""
        
        title = entry.find("atom:title", ns)
        title_text = title.text.strip() if title is not None and title.text else ""
        
        summary = entry.find("atom:summary", ns)
        abstract_text = summary.text.strip() if summary is not None and summary.text else ""
        
        authors = []
        for author_elem in entry.findall("atom:author", ns):
            name = author_elem.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text)
        
        published = entry.find("atom:published", ns)
        year = None
        if published is not None and published.text:
            year_str = published.text[:4]
            year = int(year_str) if year_str.isdigit() else None
        
        # Client-side year filter
        if year_from and (year is None or year < year_from):
            continue
        if year_to and (year is None or year > year_to):
            continue
        
        # Client-side author filter
        if author:
            author_lower = author.lower()
            if not any(author_lower in a.lower() for a in authors):
                continue
        
        # arXiv has no journal; filter is a no-op
        
        # PDF link
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.get("title") == "pdf":
                pdf_url = link.get("href", "")
                break
        
        # DOI (if published)
        doi = ""
        doi_elem = entry.find("arxiv:doi", ns)
        if doi_elem is not None and doi_elem.text:
            doi = doi_elem.text
        
        # Primary category
        cat_elem = entry.find("arxiv:primary_category", ns)
        category = cat_elem.get("term", "") if cat_elem is not None else ""
        
        results.append({
            "title": title_text,
            "doi": doi,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "authors": authors[:20],
            "year": year,
            "journal": f"arXiv ({category})" if category else "arXiv",
            "cited_by_count": 0,  # arXiv API doesn't provide citation counts
            "abstract": abstract_text if full_abstract else abstract_text[:500],
            "source_db": "arxiv",
            "tldr": "",
            "oa_status": "gold",  # arXiv is always OA
            "oa_available": True,
            "arxiv_id": arxiv_id,
            "pdf_url": pdf_url,
        })
        
        if limit and len(results) >= limit:
            break
    
    return results
