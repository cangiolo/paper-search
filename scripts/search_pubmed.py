"""PubMed / NCBI E-utilities 学术文献搜索模块。"""

from __future__ import annotations

import json
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

PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

__all__ = ["search"]

def _get_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode())

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
    # Build PubMed query
    pubmed_query = query
    if year_from and year_to:
        pubmed_query += f" AND ({year_from}:{year_to}[PDAT])"
    elif year_from:
        pubmed_query += f" AND ({year_from}:3000[PDAT])"
    elif year_to:
        pubmed_query += f" AND (1900:{year_to}[PDAT])"
    if journal:
        pubmed_query += f' AND ("{journal}"[Journal])'
    if author:
        pubmed_query += f' AND ("{author}"[Author])'
    
    # Step 1: Search for IDs
    search_params = {
        "db": "pubmed",
        "term": pubmed_query,
        "retmax": min(limit or 50, 50),
        "retmode": "json",
        "sort": "relevance",
    }
    search_url = f"{PUBMED_ESEARCH}?{urllib.parse.urlencode(search_params)}"
    
    try:
        search_data = _get_json(search_url)
    except Exception as e:
        print(f"[错误] 无法连接 PubMed ESearch: {e}", file=__import__("sys").stderr)
        return []
    
    idlist = search_data.get("esearchresult", {}).get("idlist", [])
    if not idlist:
        return []
    
    # Step 2: Fetch summaries
    summary_params = {
        "db": "pubmed",
        "id": ",".join(idlist),
        "retmode": "json",
    }
    summary_url = f"{PUBMED_ESUMMARY}?{urllib.parse.urlencode(summary_params)}"
    
    try:
        summary_data = _get_json(summary_url)
    except Exception as e:
        print(f"[错误] 无法连接 PubMed ESummary: {e}", file=__import__("sys").stderr)
        return []
    
    # Step 3: Fetch abstracts (optional, only if full_abstract or small result set)
    abstracts = {}
    if full_abstract or len(idlist) <= 20:
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(idlist),
            "retmode": "xml",
        }
        fetch_url = f"{PUBMED_EFETCH}?{urllib.parse.urlencode(fetch_params)}"
        try:
            root = _get_xml(fetch_url)
            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                if pmid_elem is None:
                    continue
                pmid = pmid_elem.text
                abs_elem = article.find(".//Abstract/AbstractText")
                if abs_elem is not None:
                    abstracts[pmid] = "".join(abs_elem.itertext())
        except Exception:
            pass  # Abstract fetch is best-effort
    
    results = []
    for pmid in idlist:
        doc = summary_data.get("result", {}).get(pmid, {})
        if not doc or pmid == "uids":
            continue
        
        authors = []
        for author_data in doc.get("authors", []):
            name = author_data.get("name", "")
            if name:
                authors.append(name)
        
        title = doc.get("title", "").rstrip(".")
        year = doc.get("pubdate", "")[:4]
        year_int = int(year) if year.isdigit() else None
        journal_name = doc.get("fulljournalname", doc.get("source", ""))
        doi = doc.get("elocationid", "")
        if doi and not doi.startswith("10."):
            doi = ""
        
        abstract_text = abstracts.get(pmid, "")
        
        results.append({
            "title": title,
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "authors": authors[:20],
            "year": year_int,
            "journal": journal_name,
            "cited_by_count": doc.get("pmcrefcount", 0),
            "abstract": abstract_text if full_abstract else abstract_text[:500],
            "source_db": "pubmed",
            "tldr": "",
            "oa_status": None,
            "pubmed_id": pmid,
        })
    
    return results
