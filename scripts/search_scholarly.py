"""Google Scholar 搜索模块（通过 scholarly 库）。

需要安装: pip install scholarly
"""

from __future__ import annotations

__all__ = ["search", "SCHOLARLY_AVAILABLE"]

SCHOLARLY_AVAILABLE = False
try:
    from scholarly import scholarly
    SCHOLARLY_AVAILABLE = True
except ImportError:
    pass

def search(
    query: str,
    limit: int | None = 10,
    year_from: int | None = None,
    year_to: int | None = None,
    journal: str | None = None,
    author: str | None = None,
    full_abstract: bool = False,
) -> list[dict]:
    if not SCHOLARLY_AVAILABLE:
        import sys
        print(
            "[提示] Google Scholar 支持需要安装 scholarly 库。\n"
            "      运行: pip install scholarly\n"
            "      或:   uv pip install scholarly",
            file=sys.stderr
        )
        return []
    
    try:
        # Build query with filters
        search_query = query
        if year_from or year_to:
            yf = year_from or ""
            yt = year_to or ""
            search_query += f"&as_ylo={yf}&as_yhi={yt}"
        
        search_results = scholarly.search_pubs(search_query)
        
        results = []
        count = 0
        for pub in search_results:
            if limit and count >= limit:
                break
            
            bib = pub.get("bib", {})
            authors = bib.get("author", [])
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(" and ")]
            
            # Client-side journal filter
            if journal:
                venue = (bib.get("venue", "") or "").lower()
                if journal.lower() not in venue:
                    continue
            
            # Client-side author filter
            if author:
                author_lower = author.lower()
                if not any(author_lower in a.lower() for a in authors):
                    continue
            
            abstract = bib.get("abstract", "")
            year = bib.get("pub_year")
            year_int = int(year) if year and str(year).isdigit() else None
            
            results.append({
                "title": bib.get("title", ""),
                "doi": "",
                "url": pub.get("pub_url", ""),
                "authors": authors[:20],
                "year": year_int,
                "journal": bib.get("venue", ""),
                "cited_by_count": pub.get("num_citations", 0),
                "abstract": abstract if full_abstract else abstract[:500],
                "source_db": "google_scholar",
                "tldr": "",
                "oa_status": None,
            })
            count += 1
        
        return results
    except Exception as e:
        import sys
        print(f"[错误] Google Scholar 搜索失败: {e}", file=sys.stderr)
        return []
