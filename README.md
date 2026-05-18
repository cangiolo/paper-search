# paper-search

> **Pure academic discovery CLI** — aggregates 7 sources, exports to reference managers, traces citations. Search and metadata only; PDF download is out of scope.

[English](#english) | [中文](#中文)

---

## English

### What it does

`paper-search` is a single-responsibility CLI tool for finding academic papers. It queries **7 sources in parallel**, deduplicates by DOI, enriches results with OA status and TLDR summaries, and exports to formats your reference manager actually understands (CSV, BibTeX, RIS).

It is **search-only**. The `--doi-only` mode produces a clean newline-delimited DOI list that any downloader can consume.

### Sources (7 total)

| Source | Coverage | Strength |
|--------|----------|----------|
| OpenAlex | 250M+ works | General coverage, reliable citation counts |
| Semantic Scholar | 200M+ papers | AI-generated TLDR summaries |
| PubMed | 35M+ biomedical | Biology, medicine, health sciences |
| arXiv | 2M+ preprints | Physics, math, CS, AI/ML |
| bioRxiv | 330K+ preprints | Biology preprints |
| medRxiv | 80K+ preprints | Medicine/health preprints |
| Google Scholar | ~400M (unofficial) | Broadest coverage, requires `pip install scholarly` |

### Quick start

```bash
# Search across all sources
python scripts/search.py search "CRISPR gene editing" --limit 10 --format table

# Specific source
python scripts/search.py search "COVID-19" --source pubmed --limit 5
python scripts/search.py search "transformer" --source arxiv --limit 5

# Advanced filtering (sort/year/journal/author)
python scripts/search.py search "deep learning" \
    --sort cited_by_count --year-from 2020 --journal "Nature" \
    --author "Bengio" --full-abstract --format table

# Citation tracing
python scripts/search.py refs "DOI:10.1038/s41586-021-03819-2" --limit 50
python scripts/search.py citations "DOI:10.1038/s41586-021-03819-2" --limit 50

# Export for reference managers
python scripts/search.py search "AlphaFold" --limit 30 --format csv    > papers.csv
python scripts/search.py search "AlphaFold" --limit 30 --format bibtex > papers.bib
python scripts/search.py search "AlphaFold" --limit 30 --format ris    > papers.ris

# Produce a clean DOI list (newline-delimited, machine-readable)
python scripts/search.py search "AlphaFold" --limit 10 --doi-only > dois.txt
```

### Output formats

| `--format` | Use case |
|-----------|---------|
| `json` | Programmatic processing |
| `table` | Human-readable terminal cards |
| `compact` | One-line-per-paper for scripts/grep |
| `citation` | NSFC / APA bibliography string |
| `csv` | Excel, Zotero CSV import, Google Sheets |
| `bibtex` | LaTeX, JabRef, Mendeley |
| `ris` | Zotero, EndNote, Mendeley, RefWorks |

### Environment

```bash
export UNPAYWALL_EMAIL="your-email@example.com"   # required for OA status
export SEMANTIC_SCHOLAR_API_KEY="..."              # optional, raises rate limit
```

### Optional dependency

```bash
pip install scholarly   # enables --source google_scholar
```

### License

MIT License

---

## 中文

### 它做什么

`paper-search` 是一个**单一职责的学术文献发现 CLI**：并行查询 7 个学术库，按 DOI 去重融合，标注 OA 开放状态和 TLDR 摘要，导出为文献管理软件能直接吃的格式（CSV/BibTeX/RIS）。

**只做搜索，不下 PDF**。`--doi-only` 模式输出干净的换行分隔 DOI 列表，任何下载工具都能消费。

### 数据源（共 7 个）

| 数据源 | 规模 | 优势领域 |
|--------|------|---------|
| OpenAlex | 2.5 亿+ | 综合覆盖，引用数权威 |
| Semantic Scholar | 2 亿+ | AI 生成的 TLDR 一句话摘要 |
| PubMed | 3500 万+ | 生物、医学、健康 |
| arXiv | 200 万+ | 物理、数学、CS、AI/ML 预印本 |
| bioRxiv | 33 万+ | 生物学预印本 |
| medRxiv | 8 万+ | 医学预印本 |
| Google Scholar | ~4 亿（非官方） | 覆盖最广，需 `pip install scholarly` |

### 快速开始

```bash
# 跨所有源搜索
python scripts/search.py search "CRISPR 基因编辑" --limit 10 --format table

# 指定单源
python scripts/search.py search "COVID-19" --source pubmed --limit 5
python scripts/search.py search "transformer" --source arxiv --limit 5

# 高级过滤
python scripts/search.py search "深度学习" \
    --sort cited_by_count --year-from 2020 --journal "Nature" \
    --author "Bengio" --full-abstract --format table

# 引用溯源
python scripts/search.py refs "DOI:10.1038/s41586-021-03819-2" --limit 50
python scripts/search.py citations "DOI:10.1038/s41586-021-03819-2" --limit 50

# 导出到文献管理软件
python scripts/search.py search "AlphaFold" --limit 30 --format csv    > papers.csv
python scripts/search.py search "AlphaFold" --limit 30 --format bibtex > papers.bib
python scripts/search.py search "AlphaFold" --limit 30 --format ris    > papers.ris

# 输出纯 DOI 列表（每行一个，机器可读）
python scripts/search.py search "AlphaFold" --limit 10 --doi-only > dois.txt
```

### 环境变量

```bash
export UNPAYWALL_EMAIL="your-email@example.com"   # 检查 OA 状态时必需
export SEMANTIC_SCHOLAR_API_KEY="..."              # 可选，提高 S2 速率上限
```

### 可选依赖

```bash
pip install scholarly   # 启用 --source google_scholar
```

### 许可

MIT License
