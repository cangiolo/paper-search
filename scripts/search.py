#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""Aggregated Academic Paper Search across 7 sources.

Pure search/discovery tool. For PDF download, use the paper-fetch skill.

Supports:
- search: keyword search across OpenAlex, Semantic Scholar, PubMed, arXiv,
  bioRxiv, medRxiv, Google Scholar (optional)
- refs: list a paper's references
- citations: list papers that cite a given paper
- export formats: json, table, compact, citation, csv, bibtex, ris
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Fix path to import modules
sys.path.insert(0, str(Path(__file__).parent))
try:
    from search_openalex import (
        search as search_openalex,
        format_table, format_compact, format_citation,
        format_csv, format_bibtex, format_ris,
    )
    from search_s2 import search_s2, get_paper, get_citations, get_references
    from search_pubmed import search as search_pubmed
    from search_arxiv import search as search_arxiv
    from search_biorxiv import search as search_biorxiv
    from search_scholarly import search as search_scholarly, SCHOLARLY_AVAILABLE
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    sys.exit(1)

def _get_json(url: str, timeout: int = 10):
    import urllib.request
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def check_unpaywall(doi: str, email: str, timeout: int = 10) -> dict:
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        data = _get_json(url, timeout=timeout)
        loc = data.get("best_oa_location") or {}
        pdf_url = loc.get("url_for_pdf")
        return {
            "oa_available": pdf_url is not None,
            "oa_url": pdf_url,
            "oa_status": data.get("oa_status", "unknown"),
        }
    except Exception:
        return {"oa_available": None, "oa_url": None, "oa_status": "unknown"}

def _merge_dedup(results: list[dict], prefer: str = "semantic_scholar") -> list[dict]:
    seen = {}
    for r in results:
        doi = r.get("doi")
        if not doi:
            # unique key for no-doi
            seen[id(r)] = r
            continue
        if doi in seen:
            existing = seen[doi]
            if not existing.get("tldr") and r.get("tldr"):
                existing["tldr"] = r["tldr"]
            if r.get("source_db") == prefer and existing.get("source_db") != prefer:
                r["tldr"] = r.get("tldr") or existing.get("tldr", "")
                r["source_db"] = f"{prefer} + openalex"
                seen[doi] = r
            else:
                existing["source_db"] = f"{existing.get('source_db', 'unknown')} + {r.get('source_db', 'unknown')}"
        else:
            seen[doi] = r.copy()
    return list(seen.values())

def unified_search(
    query: str,
    limit: int | None = 10,
    source: str = "auto",
    sort: str = "relevance_score",
    year_from: int | None = None,
    year_to: int | None = None,
    journal: str | None = None,
    author: str | None = None,
    full_abstract: bool = False,
    enrich_oa: bool = True,
    **kwargs,
) -> list[dict]:
    results = []
    per_source_limit = limit if source != "auto" else (limit // 3 + 5 if limit else None)

    if source in ("auto", "openalex"):
        results.extend(search_openalex(
            query, limit=per_source_limit, sort=sort,
            year_from=year_from, year_to=year_to,
            journal=journal, author=author,
            full_abstract=full_abstract,
        ))

    if source in ("auto", "s2"):
        # S2 does not support journal/author filtering or sort; skip when those are set
        if not journal and not author and sort == "relevance_score":
            s2_results = search_s2(query, limit=per_source_limit, year_from=year_from, year_to=year_to, **kwargs)
            results.extend(s2_results)

    if source in ("auto", "pubmed"):
        results.extend(search_pubmed(
            query, limit=per_source_limit,
            year_from=year_from, year_to=year_to,
            journal=journal, author=author,
            full_abstract=full_abstract,
        ))

    if source in ("auto", "arxiv"):
        results.extend(search_arxiv(
            query, limit=per_source_limit,
            year_from=year_from, year_to=year_to,
            author=author,
            full_abstract=full_abstract,
        ))

    if source in ("auto", "biorxiv"):
        results.extend(search_biorxiv(
            query, limit=per_source_limit, server="biorxiv",
            year_from=year_from, year_to=year_to,
            author=author, full_abstract=full_abstract,
        ))

    if source in ("auto", "medrxiv"):
        results.extend(search_biorxiv(
            query, limit=per_source_limit, server="medrxiv",
            year_from=year_from, year_to=year_to,
            author=author, full_abstract=full_abstract,
        ))

    if source in ("auto", "google_scholar"):
        if SCHOLARLY_AVAILABLE:
            results.extend(search_scholarly(
                query, limit=per_source_limit,
                year_from=year_from, year_to=year_to,
                journal=journal, author=author,
                full_abstract=full_abstract,
            ))
        elif source == "google_scholar":
            print("\n⚠️  Google Scholar 不可用。请安装 scholarly 库：", file=sys.stderr)
            print("    pip install scholarly", file=sys.stderr)

    if source == "auto":
        results = _merge_dedup(results)

    if enrich_oa:
        email = os.environ.get("UNPAYWALL_EMAIL", "")
        if email:
            print("Checking OA status from Unpaywall...", file=sys.stderr)
            for i, r in enumerate(results):
                if r.get("doi"):
                    time.sleep(0.1) # 100ms delay to avoid rate limit
                    oa_info = check_unpaywall(r["doi"], email)
                    r["oa_status"] = oa_info["oa_status"]
                    r["oa_available"] = oa_info["oa_available"]

    # Apply sort
    if sort == "cited_by_count":
        results.sort(key=lambda x: x.get("cited_by_count", 0), reverse=True)
    elif sort == "publication_date":
        results.sort(key=lambda x: x.get("year", 0) or 0, reverse=True)
    else:
        # relevance_score: OpenAlex already returns in relevance order
        pass

    if limit is not None:
        return results[:limit]
    return results

def cmd_search(args):
    results = unified_search(
        args.query,
        limit=args.limit,
        source=args.source,
        sort=args.sort,
        year_from=args.year_from,
        year_to=args.year_to,
        journal=args.journal,
        author=args.author,
        full_abstract=args.full_abstract,
        enrich_oa=not args.no_oa_check
    )
    
    if args.doi_only:
        for r in results:
            if r.get("doi"):
                print(r["doi"])
        return
        
    fmt = args.format
    if fmt == "table":
        print(format_table(results))
    elif fmt == "compact":
        print(format_compact(results))
    elif fmt == "citation":
        print(format_citation(results, style=args.citation_style))
    elif fmt == "csv":
        sys.stdout.write(format_csv(results))
    elif fmt == "bibtex":
        print(format_bibtex(results))
    elif fmt == "ris":
        print(format_ris(results))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))

def cmd_refs(args):
    is_citations = (args.command == "citations")
    func = get_citations if is_citations else get_references
    results = func(args.paper_id, limit=args.limit)
    
    if not args.no_oa_check:
        email = os.environ.get("UNPAYWALL_EMAIL", "")
        if email:
            print("Checking OA status from Unpaywall...", file=sys.stderr)
            for r in results:
                if r.get("doi"):
                    time.sleep(0.1) # delay
                    oa_info = check_unpaywall(r["doi"], email)
                    r["oa_status"] = oa_info["oa_status"]
                    r["oa_available"] = oa_info["oa_available"]
                    
    results.sort(key=lambda x: x.get("cited_by_count", 0), reverse=True)
    
    if args.doi_only:
        for r in results:
            if r.get("doi"):
                print(r["doi"])
        return
        
    if args.format == "table":
        print(format_table(results))
    elif args.format == "compact":
        print(format_compact(results))
    elif args.format == "citation":
        print(format_citation(results, style=args.citation_style))
    elif args.format == "csv":
        sys.stdout.write(format_csv(results))
    elif args.format == "bibtex":
        print(format_bibtex(results))
    elif args.format == "ris":
        print(format_ris(results))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description="Aggregated Academic Paper Search (7 sources)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # search cmd
    parser_search = subparsers.add_parser("search", help="纯搜索，返回论文列表")
    parser_search.add_argument("query", help="搜索关键词")
    parser_search.add_argument("--source", choices=["auto", "openalex", "s2", "pubmed", "arxiv", "biorxiv", "medrxiv", "google_scholar"], default="auto", help="数据源")
    parser_search.add_argument("--limit", type=int, default=10, help="最多返回数量 (留空则无限制, 0表示无限制)")
    parser_search.add_argument("--sort", choices=["relevance_score", "cited_by_count", "publication_date"], default="relevance_score", help="排序方式")
    parser_search.add_argument("--year-from", type=int, default=None, help="发表年份下限")
    parser_search.add_argument("--year-to", type=int, default=None, help="发表年份上限")
    parser_search.add_argument("--journal", type=str, default=None, help="按期刊名关键词过滤")
    parser_search.add_argument("--author", type=str, default=None, help="按作者姓名关键词过滤")
    parser_search.add_argument("--full-abstract", action="store_true", help="输出完整摘要（默认截断至500字符）")
    parser_search.add_argument("--format", choices=["json", "compact", "table", "citation", "csv", "bibtex", "ris"], default="json")
    parser_search.add_argument("--citation-style", choices=["nsfc", "apa"], default="nsfc")
    parser_search.add_argument("--doi-only", action="store_true")
    parser_search.add_argument("--no-oa-check", action="store_true", help="跳过 Unpaywall 查询以加快速度")

    # refs / citations cmd
    for cmd_name, help_text in [("refs", "查看参考文献列表"), ("citations", "查看引用者")]:
        p = subparsers.add_parser(cmd_name, help=help_text)
        p.add_argument("paper_id", help="如 DOI:xxx")
        p.add_argument("--limit", type=int, default=20, help="限制数量")
        p.add_argument("--format", choices=["json", "compact", "table", "citation", "csv", "bibtex", "ris"], default="json")
        p.add_argument("--citation-style", choices=["nsfc", "apa"], default="nsfc")
        p.add_argument("--doi-only", action="store_true")
        p.add_argument("--no-oa-check", action="store_true", help="跳过 Unpaywall 查询")

    args = parser.parse_args()

    # Process limit argument if missing or 0 to None
    if getattr(args, "limit", None) == 0:
        args.limit = None

    if args.command == "search":
        cmd_search(args)
    elif args.command in ("refs", "citations"):
        cmd_refs(args)

if __name__ == "__main__":
    main()
