# Baselines

Reference reports for the README scorecard and CI regression gates. Each
tracked `.json` is a `ComparisonReport`; sidecars `.md` (if present) are the
same content rendered for humans.

## Tracked (committed)

| File | What it is | Consumer |
| --- | --- | --- |
| `bench_v0_hosted_only.json` | Merge of the four hosted-RAG runs (Vertex / Bedrock / OpenAI / Azure) on bench-v0. | `make bench-v0-scorecard` reads this by default — drives the README table. |
| `bench_v0_merged.json` | Same hosted runs plus the local Gemini baseline (9 systems). | Operator reference for hosted-vs-local comparisons. |
| `smoke.json` | Tiny example-corpus run. | `tests/rag_eval/test_smoke.py`, docs walkthrough. |

Don't `git rm` one of these without retiring its consumer (Makefile target,
config, or test) at the same time.

## Untracked (operator-generated)

Per-vendor and per-judge run outputs land in this directory but are not
committed — they contain run-specific timestamps and (in some cases)
account-tied resource identifiers. Typical names:

| Producer | File |
| --- | --- |
| `scripts/run_bench_v0_vertex.py run` | `bench_v0_vertex.json` |
| `scripts/run_bench_v0_bedrock.py run` | `bench_v0_bedrock.json` |
| `scripts/run_bench_v0_openai.py run` | `bench_v0_openai.json` |
| `scripts/run_bench_v0_azure.py run` | `bench_v0_azure.json` |
| `make bench-v0` (Gemini real-backend) | `bench_v0_gemini.{json,md}` |
| `make bench-v0-rejudge` (Claude rejudge) | `bench_v0_gemini_claude.{json,md}` |
| `make bench-v0-mock` (all 7 local systems) | `bench_v0.{json,md}` |
| `examples/rag_eval/bench_v0/baseline_claude.yaml` | `bench_v0_local.{json,md}` |
| `make ablation-distill` | `ablation_bge_baseline.{json,md}`, `ablation_prose.{json,md}`, `ablation_tag_list.{json,md}` |

To re-merge into `bench_v0_hosted_only.json` / `bench_v0_merged.json` after a
fresh per-vendor run, combine the per-system `rows` into one
`ComparisonReport`. (No automated merge script yet — see issue list.)
