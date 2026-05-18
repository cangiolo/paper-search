---
name: paper-search
description: Use when the user wants to search for academic papers, discover literature, or find research articles by keywords, topics, authors, or DOIs. Aggregates results from OpenAlex, Semantic Scholar, and Unpaywall with OA status, TLDR summaries, and citation counts. Also supports citation tracing (find references or citing papers). Trigger on phrases like "search for papers on X", "find literature about Y", "what papers exist on Z", "academic search", "literature review", or "discover papers by author". For downloading PDFs after search, use paper-fetch.
homepage: https://github.com/zyzhou-saffron/paper-search
metadata: {"openclaw":{"requires":{"bins":["python3"]},"emoji":"🔍"},"pimo":{"category":"research","tags":["paper","search","literature","academic","discovery","openalex","semanticscholar","citation-tracing"]}}
---

# paper-search

Aggregated academic paper search across OpenAlex, Semantic Scholar, and Unpaywall. Returns structured results with OA status, TLDR summaries, citation counts, and author info.

**Designed to pair with paper-fetch** — use paper-search to discover papers, then paper-fetch to download the PDFs.

## Search Sources

| Source | What it provides |
|--------|-----------------|
| **OpenAlex** | Open bibliographic data, citation counts, OA status |
| **Semantic Scholar** | TLDR (AI-generated one-sentence summary), influential citations |
| **Unpaywall** | Real-time OA availability check |

Results are deduplicated by DOI and enriched with the best available metadata from all three sources.

## Commands

```bash
python scripts/search_and_fetch.py search "query" [options]   # pure search
python scripts/search_and_fetch.py grab "query" [options]     # search + download OA PDFs (delegates to paper-fetch)
python scripts/search_and_fetch.py refs "DOI:xxx" [options]   # list references
python scripts/search_and_fetch.py grab-refs "DOI:xxx" [options]  # download referenced papers
python scripts/search_and_fetch.py citations "DOI:xxx" [options]  # list citing papers
python scripts/search_and_fetch.py grab-citations "DOI:xxx" [options]  # download citing papers
```

### Search options

| Flag | Default | Description |
|------|---------|-------------|
| `--limit N` | 10 | Max results to return |
| `--format table|json|compact` | `table` | Output format |
| `--year-from YYYY` | — | Filter by publication year (min) |
| `--year-to YYYY` | — | Filter by publication year (max) |
| `--out DIR` | `./papers` | Output directory for grab modes |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `UNPAYWALL_EMAIL` | Required for Unpaywall OA checks |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional, increases S2 rate limit |

## Examples

```bash
# Search for papers on a topic
python scripts/search_and_fetch.py search "CRISPR gene editing" --limit 10 --format table

# Search with year filter
python scripts/search_and_fetch.py search "AlphaFold protein structure" --year-from 2020 --year-to 2024 --limit 5

# Search and auto-download OA PDFs
python scripts/search_and_fetch.py grab "foundation models biology" --limit 20 --out ~/papers

# Trace references of a landmark paper
python scripts/search_and_fetch.py grab-refs "DOI:10.1038/s41586-021-03819-2" --out ./alphafold_refs
```

## Relationship to paper-fetch

- **paper-search** = discovery (find what exists)
- **paper-fetch** = retrieval (download the PDF)

paper-search's `grab` modes will attempt to download OA PDFs by calling paper-fetch's `fetch.py` if available in the same environment. If paper-fetch is not installed, grab falls back to simple HTTP download.
