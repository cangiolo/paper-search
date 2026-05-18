---
name: paper-search
description: Use when the user wants to search for academic papers, discover literature, or find research articles by keywords, topics, authors, or DOIs. Aggregates results from OpenAlex, Semantic Scholar, and Unpaywall with OA status, TLDR summaries, citation counts, and advanced filtering (sort by citations/date, journal filter, author filter, full abstract). Also supports citation tracing (find references or citing papers) and batch OA download. For downloading PDFs after search, use paper-fetch.
homepage: https://github.com/zyzhou-saffron/paper-search
metadata: {"openclaw":{"requires":{"bins":["python3"]},"emoji":"🔍"},"pimo":{"category":"research","tags":["paper","search","literature","academic","discovery","openalex","semanticscholar","citation-tracing","openalex-search-superset"]}}
---

# paper-search

Aggregated academic paper search across **OpenAlex + Semantic Scholar + Unpaywall**.

**Superset of openalex-search** — includes all openalex-search features plus multi-source fusion, TLDR summaries, OA status, and citation tracing.

## Features

| Feature | paper-search | openalex-search |
|---------|-------------|-----------------|
| **Multi-source search** | ✅ OpenAlex + S2 + Unpaywall | ❌ OpenAlex only |
| **Sort by relevance** | ✅ | ✅ |
| **Sort by citations** | ✅ `--sort cited_by_count` | ✅ `--sort cited_by_count` |
| **Sort by date** | ✅ `--sort publication_date` | ✅ `--sort publication_date` |
| **Year filter** | ✅ `--year-from` / `--year-to` | ✅ |
| **Journal filter** | ✅ `--journal` | ✅ `--journal` |
| **Author filter** | ✅ `--author` | ✅ `--author` |
| **Full abstract** | ✅ `--full-abstract` | ✅ `--full-abstract` |
| **TLDR summary** | ✅ (S2) | ❌ |
| **OA status** | ✅ (Unpaywall) | ❌ |
| **Citation tracing** | ✅ `refs` / `citations` | ❌ |
| **Batch download** | ✅ `grab` / `grab-refs` / `grab-citations` | ❌ |

## Commands

```bash
# Pure search
python scripts/search_and_fetch.py search "CRISPR gene editing" --limit 10 --format table

# Advanced filtering (all openalex-search features supported)
python scripts/search_and_fetch.py search "AlphaFold" \
    --sort cited_by_count --year-from 2020 --journal "Nature" \
    --author "Jumper" --full-abstract --format table

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

## Relationship to paper-fetch

- **paper-search** = discovery + filtering + tracing
- **paper-fetch** = retrieval (download PDF)

paper-search's `grab` modes delegate downloading to paper-fetch when available.
