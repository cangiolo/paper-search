---
name: paper-search
description: Use when the user wants to search for academic papers, discover literature, or find research articles by keywords, topics, authors, or DOIs. Aggregates results from 5 sources — OpenAlex, Semantic Scholar, PubMed, arXiv, and Google Scholar (optional) — with OA status, TLDR summaries, citation counts, and advanced filtering (sort by citations/date, journal filter, author filter, full abstract). Also supports citation tracing (find references or citing papers) and batch OA download. For downloading PDFs after search, use paper-fetch.
homepage: https://github.com/zyzhou-saffron/paper-search
metadata: {"openclaw":{"requires":{"bins":["python3"]},"emoji":"🔍"},"pimo":{"category":"research","tags":["paper","search","literature","academic","discovery","openalex","pubmed","arxiv","semanticscholar","google-scholar","citation-tracing","openalex-search-superset"]}}
---

# paper-search

Aggregated academic paper search across **5 sources**:

| Source | Coverage | Best For |
|--------|----------|----------|
| **OpenAlex** | 250M+ works | General academic, citation counts |
| **Semantic Scholar** | 200M+ papers | TLDR summaries, AI insights |
| **PubMed** | 35M+ biomedical | Biology, medicine, health sciences |
| **arXiv** | 2M+ preprints | Physics, math, CS, AI/ML |
| **Google Scholar** | ~400M (unofficial) | Broadest coverage, requires `pip install scholarly` |

**Superset of openalex-search** — includes all its features plus 3 additional sources, OA status, and citation tracing.

## Commands

```bash
# Search all sources (auto mode)
python scripts/search_and_fetch.py search "CRISPR gene editing" --limit 10 --format table

# Search specific source
python scripts/search_and_fetch.py search "COVID-19" --source pubmed --limit 5
python scripts/search_and_fetch.py search "transformer" --source arxiv --limit 5
python scripts/search_and_fetch.py search "AlphaFold" --source google_scholar --limit 5

# Advanced filtering
python scripts/search_and_fetch.py search "deep learning" \
    --sort cited_by_count --year-from 2020 --journal "Nature" \
    --author "Bengio" --full-abstract --format table

# Search + auto-download OA PDFs
python scripts/search_and_fetch.py grab "foundation models biology" --limit 20 --out ~/papers

# Trace references of a landmark paper
python scripts/search_and_fetch.py grab-refs "DOI:10.1038/s41586-021-03819-2" --out ./alphafold_refs
```

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

- **paper-search** = discovery + filtering + tracing (5 sources)
- **paper-fetch** = retrieval (download PDF, 7 sources including Sci-Hub fallback)

paper-search's `grab` modes delegate downloading to paper-fetch when available.
