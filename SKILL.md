---
name: paper-search
description: Use when the user wants to search for academic papers, discover literature, verify DOIs/citations, or find research articles by keywords, topics, authors, or DOIs (文献检索、查论文、文献调研、DOI 与引用核验、引文追踪). Pure search/discovery tool — does NOT download PDFs (pair with paper-fetch for that). Aggregates results from 7 sources — OpenAlex, Semantic Scholar, PubMed, arXiv, bioRxiv, medRxiv, and Google Scholar (optional) — with OA status, TLDR summaries, citation counts, and advanced filtering (sort by citations/date, journal filter, author filter, full abstract). Exports to CSV, BibTeX, RIS for Zotero/EndNote/Mendeley import. Also supports citation tracing (list a paper's references or citing papers).
homepage: https://github.com/cangiolo/paper-search
metadata: {"openclaw":{"requires":{"bins":["python3"]},"emoji":"🔍"},"pimo":{"category":"research","tags":["paper","search","literature","academic","discovery","openalex","pubmed","arxiv","biorxiv","medrxiv","semanticscholar","google-scholar","citation-tracing"]}}
---

# paper-search

Aggregated academic paper search across **7 sources**. Pure discovery — no PDF download (use `paper-fetch` for that).

| Source | Coverage | Best For |
|--------|----------|----------|
| **OpenAlex** | 250M+ works | General academic, citation counts |
| **Semantic Scholar** | 200M+ papers | TLDR summaries, AI insights |
| **PubMed** | 35M+ biomedical | Biology, medicine, health sciences |
| **arXiv** | 2M+ preprints | Physics, math, CS, AI/ML |
| **bioRxiv** | 330K+ preprints | Biology preprints |
| **medRxiv** | 80K+ preprints | Medicine/health preprints |
| **Google Scholar** | ~400M (unofficial) | Broadest coverage, requires `pip install scholarly` |

**Functional superset of openalex-search** — every openalex-search flag plus 6 additional sources, OA status, TLDR, citation tracing, and reference-manager exports.

## Commands

```bash
# Search all sources (auto mode)
python3 ~/.agents/skills/paper-search/scripts/search.py search "CRISPR gene editing" --limit 10 --format table

# Search specific source
python3 ~/.agents/skills/paper-search/scripts/search.py search "COVID-19" --source pubmed --limit 5
python3 ~/.agents/skills/paper-search/scripts/search.py search "transformer" --source arxiv --limit 5
python3 ~/.agents/skills/paper-search/scripts/search.py search "genome" --source biorxiv --limit 5
python3 ~/.agents/skills/paper-search/scripts/search.py search "vaccine" --source medrxiv --limit 5
python3 ~/.agents/skills/paper-search/scripts/search.py search "AlphaFold" --source google_scholar --limit 5

# Advanced filtering
python3 ~/.agents/skills/paper-search/scripts/search.py search "deep learning" \
    --sort cited_by_count --year-from 2020 --journal "Nature" \
    --author "Bengio" --full-abstract --format table

# Citation tracing
python3 ~/.agents/skills/paper-search/scripts/search.py refs "DOI:10.1038/s41586-021-03819-2" --limit 50
python3 ~/.agents/skills/paper-search/scripts/search.py citations "DOI:10.1038/s41586-021-03819-2" --limit 50

# Export for reference managers (Zotero / EndNote / Mendeley)
python3 ~/.agents/skills/paper-search/scripts/search.py search "AlphaFold" --limit 30 --format csv    > papers.csv
python3 ~/.agents/skills/paper-search/scripts/search.py search "AlphaFold" --limit 30 --format bibtex > papers.bib
python3 ~/.agents/skills/paper-search/scripts/search.py search "AlphaFold" --limit 30 --format ris    > papers.ris

# Chain into paper-fetch for PDF download (DOI pipe)
python3 ~/.agents/skills/paper-search/scripts/search.py search "AlphaFold" --limit 10 --doi-only \
    | python3 ~/.agents/skills/paper-fetch/scripts/fetch.py --batch -
```

## Output Formats

| Format | Use Case | Tool Compatibility |
|--------|----------|--------------------|
| `json` | Programmatic processing | API consumers |
| `table` | Human-readable terminal output | Interactive browsing |
| `compact` | One-line-per-paper | Scripts, grep |
| `citation` | NSFC / APA bibliography | Direct paste into manuscripts |
| `csv` | Spreadsheet | Excel, Zotero (CSV import), Google Sheets |
| `bibtex` | LaTeX manuscripts | LaTeX, Zotero, JabRef, Mendeley |
| `ris` | Universal reference manager | Zotero, EndNote, Mendeley, RefWorks |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `UNPAYWALL_EMAIL` | Required for OA status checks |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional, increases S2 rate limit |

## Optional Dependency

```bash
pip install scholarly   # enables Google Scholar source
```

## Relationship to paper-fetch

- **paper-search** = pure discovery + filtering + citation tracing + export
- **paper-fetch** = PDF retrieval (7 download sources including Sci-Hub fallback)

Single-responsibility separation: paper-search produces DOI lists, paper-fetch consumes them. Pipe `--doi-only` output into `fetch.py --batch -`.
