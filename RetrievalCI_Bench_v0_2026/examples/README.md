# RetrievalCI Examples

This directory contains public fixtures that exercise the product without API
keys or customer data. The data is synthetic but sized to make the CI reports
more informative than a one-row smoke test.

## RAG Eval

- `rag_eval/corpus/*.md`: support-desk knowledge base pages.
- `rag_eval/questions.jsonl`: 20 held-out questions with source citations.
- `rag_eval/smoke.yaml`: mock-backend RAG eval config used by CI.
- `third_party/wixqa/`: bundled WixQA fixture in RetrievalCI format.
- `third_party/enterprise_rag_bench_github/`: bundled EnterpriseRAG-Bench
  GitHub-source fixture in RetrievalCI format.
- `project1_parsed_docx/`: derived Markdown parses of ten synthetic Project1
  DOCX documents. These are benchmark examples, not canonical Project1 package
  files; ingest the canonical DOCX once when evaluating Project1.

Run it with:

```bash
.venv/bin/retrievalci rag run --config examples/rag_eval/smoke.yaml
.venv/bin/retrievalci rag run --config examples/third_party/wixqa/smoke.yaml
.venv/bin/retrievalci rag run --config examples/third_party/enterprise_rag_bench_github/smoke.yaml
```

## Trace Eval

- `corpus.demo.jsonl`: synthetic retrieval corpus for trace replay.
- `traces.demo.jsonl`: normalized trace rows covering six replay cases.
- `spans.demo.jsonl`: generic span-style source fixture for the same cases.
- `otel.spans.demo.json`: OpenTelemetry-style source fixture for the same cases.

The project-level CI example combines the RAG and trace fixtures:

```bash
.venv/bin/retrievalci ci run --config examples/retrievalci.ci.yaml
```
