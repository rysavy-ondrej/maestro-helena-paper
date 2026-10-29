# LLM-agent approaches to network traffic triage — survey (arXiv, 2023 – Oct 2026)

**Scope and method.** Seven arXiv API queries (LLM × intrusion detection / network traffic / SOC alert triage / threat hunting / incident response / CTI / packets-flows / security logs) returned 394 unique records. Each abstract was tagged by an LLM classifier (relevance 0–3, approach category, agentic / multi-agent / ML-pre-triage / CTI-RAG flags), then the 145 relevance-3 titles were reviewed manually and ~40 key abstracts read in full. Full tagged corpus: {{artifact:2a66bec5-582b-48c7-9ce5-bb90a5bbf9b5}}.
*Limits:* arXiv only (no IEEE/ACM/USENIX-only papers, no vendor products); classifier tags are approximate (relevance ≥2 is liberal, 286 records); claims below come from abstracts, not full-text replication.

## 1. Landscape in numbers (relevance ≥ 2, n = 286)

| Category | 2023 | 2024 | 2025 | 2026 (to Oct) |
|---|---|---|---|---|
| LLM as IDS classifier / explainer | 4 | 11 | 19 | 15 |
| LLM alert triage (SOC) | 1 | 2 | 8 | 23 |
| Multi-agent SOC / incident response | 0 | 1 | 8 | 9 |
| CTI enrichment / TTP extraction | 0 | 8 | 15 | 19 |
| Security log analysis | 0 | 3 | 12 | 9 |
| Benchmarks / evaluations | 2 | 9 | 18 | 38 |

Share of records using agents (tool use / planning / multi-agent): 12% (2023) → 24% (2024) → 26% (2025) → 51% (2026). Only 24 records combine an agentic LLM with a conventional ML pre-triage stage, and 14 of these also use CTI/RAG, which is the configuration closest to your host-context design.

## 2. Taxonomy of approaches

### A. LLM as the detector (flow/packet → verdict)
- Zero/few-shot on serialized flows performs poorly. GPT-4/Llama3 on NetFlows is judged "unfit for the detection of malicious NetFlows" but promising as a complementary explainer with RAG and function calling [2408.04342](https://arxiv.org/abs/2408.04342). A grammar-constrained, calibrated study on UNSW-NB15 reaches macro-F1 ≈0.78 on 200 flows (7B + handcrafted boolean flags) and degrades as the set grows; tabular baselines stay more stable and faster [2510.17883](https://arxiv.org/abs/2510.17883).
- Domain fine-tuning helps: TrafficLLM uses traffic-domain tokenization and dual-stage tuning (F1 0.9875 detection across 229 traffic types) [2504.04222](https://arxiv.org/abs/2504.04222).
- **Experience-library RAG** is the most notable 2026 pattern. Agents convert their own misclassifications into retrievable rules. MA-IDS (2 agents) raises macro-F1 from 17% zero-shot to 89.75% on NF-BoT-IoT [2604.05458](https://arxiv.org/abs/2604.05458). SERA-IDS achieves the same with *structured* rules (feature conditions, class confusion, provenance, confidence gate) and local 7–14B SLMs, at 69.5–87.7% macro-F1 across three SLMs and two datasets (5 of 6 results ≥83%; Phi-4 on NF-BoT-IoT 69.5%) [2610.03999](https://arxiv.org/abs/2610.03999).
- *Takeaway:* raw LLM classification does not replace an ML classifier. It becomes competitive only with retrieved, structured, numeric decision knowledge.

### B. ML pre-triage → LLM explanation/enrichment (two-stage)
- Early dashboards: HuntGPT (RF + SHAP/LIME + GPT-3.5) [2309.16021](https://arxiv.org/abs/2309.16021); ChatIDS (explain IDS alerts to non-experts) [2306.14504](https://arxiv.org/abs/2306.14504).
- eX-NIDS adds a "Prompt Augmenter" that injects flow context plus CTI before explanation, giving >20% better explanations than a bare prompt [2507.16241](https://arxiv.org/abs/2507.16241). This is directly analogous to enriching a host context.
- Edge variant: lightweight ML IDS on the gateway sends a compact telemetry snapshot to an LLM (<1.5 s, <1.2 kB per prompt) [2511.18230](https://arxiv.org/abs/2511.18230).
- RL/AE pre-triage: autoencoder → two-layer DRL triage → LLM contextual analysis inside Splunk [2603.23966](https://arxiv.org/abs/2603.23966). SENTINEL-RL offloads *topological* reasoning to a GNN+PPO policy, and the LLM only narrates or recommends under a critic gate [2609.04159](https://arxiv.org/abs/2609.04159).

### C. Agentic investigation over network evidence (closest to your architecture)
- **Holmes**: a funnel in which counters/sFlow do continuous triage, PCAP is collected only on anomaly windows, and an "Evidence Pack" turns packets into compact structured evidence. The agent then follows a structure-first protocol with JSON/quotation evidence anchors [2601.14601](https://arxiv.org/abs/2601.14601). Conceptually this is the closest match to a host context as agent input.
- **IoT traffic agent**: pcap → features → transformer anomaly detection → flow summarization → threat-intel enrichment → hybrid (lexical+semantic+rerank) retrieval → agent reasoning [2510.13925](https://arxiv.org/abs/2510.13925).
- **ReGAIN**: natural-language traffic summaries in a multi-collection vector DB, hierarchical retrieval, cross-encoder reranking, and **abstention** to limit hallucination [2512.22223](https://arxiv.org/abs/2512.22223).
- **CyberRAG**: a central agent orchestrates per-attack-family fine-tuned classifiers as *tools*, enrichment adapters, and an iterative retrieve-until-consistent loop [2507.02424](https://arxiv.org/abs/2507.02424).
- **PROBE** (802.11 pcaps): deterministic PCAP-to-text normalization, multi-run ensembles, absence-of-evidence as evidence, and a deterministic reliability score. It reports that LLM self-reported confidence is uninformative (71% exactly 0.95) and that naive majority voting falls *below* the expert baseline [2606.06871](https://arxiv.org/abs/2606.06871).

### D. Multi-agent SOC alert triage
- **CORTEX**: behaviour-analysis agent + evidence-gathering agents (query external systems) + reasoning agent. It releases production SOC investigation traces and reduces false positives vs single-agent baselines [2510.00311](https://arxiv.org/abs/2510.00311).
- **AIDA / ALERT-BENCH** (Oct 2026) is a key paper. Replaying enterprise telemetry through a live SIEM, *every* studied strategy (single-pass tool use, iterative retrieval, sampling, self-review, verification) missed ≥40.4% of attack alerts. Attacks were often dismissed when searches returned no records, and same-context self-review had negative net correction. Their fix uses a proposer, an independent challenger in a separate context, a judge, an append-only investigation ledger, and a stricter evidentiary bar for *dismissal*. This gives F1 0.958 and FNR 3.1%, escalating 18.4% of alerts [2610.10608](https://arxiv.org/abs/2610.10608).
- **HESP**: moves the investigation procedure *outside* the model, as a ledger of competing hypotheses with probes chosen by information gain per cost and a controller-side stop. This lifts Qwen2.5-7B verified completion from 0.125 to 1.0 on local hardware [2609.33446](https://arxiv.org/abs/2609.33446).
- **REFINE**: analyst expertise encoded as structured skills, evolved from disposition feedback under a hard recall = 1.0 constraint for false-positive auto-closure [2609.32516](https://arxiv.org/abs/2609.32516).
- **AIDR**: cloud router plus on-prem LoRA experts, alerts distilled to 3–5 bullets (68% fewer tokens), 40.6% lower latency than CoT [2512.08169](https://arxiv.org/abs/2512.08169).
- **RHINO**: network-log → ATT&CK mapping as behavioural abstraction → multi-role inference → validation against official MITRE definitions [2510.14233](https://arxiv.org/abs/2510.14233).
- Platforms: LanG (unified incident context record, LangGraph orchestrator, MCP-exposed tools, guardrails, rule generation) [2604.05440](https://arxiv.org/abs/2604.05440); ACE (Suricata → LangGraph → NIST control mapping → rule deployment) [2610.22702](https://arxiv.org/abs/2610.22702).

### E. CTI enrichment components
TTP extraction and credibility checking supply the enrichment sources for a host context: LRCTI does multi-step evidence retrieval plus NLI for CTI credibility [2507.11310](https://arxiv.org/abs/2507.11310); IOC→regex operationalization [2604.12228](https://arxiv.org/abs/2604.12228); CTI2TTP diverge-then-converge verification [2605.25836](https://arxiv.org/abs/2605.25836); CTIConnect benchmark for RAG over heterogeneous CTI [2510.11974](https://arxiv.org/abs/2510.11974).

### F. Response / autonomous defense
LLM agents in CybORG CAGE-4 teamed with RL agents [2505.04843](https://arxiv.org/abs/2505.04843); an end-to-end 14B incident-response planner [2602.13156](https://arxiv.org/abs/2602.13156); multi-agent tabletop IR [2412.00652](https://arxiv.org/abs/2412.00652).

## 3. Evaluation — where agents fail
- **Cyber Defense Benchmark**: open-ended SQL threat hunting over 75k–135k Windows log rows. The best frontier model finds 3.8% of malicious events and no model passes [2604.19533](https://arxiv.org/abs/2604.19533).
- **OpenSec**: IR agents over-trigger under adversarial evidence (GPT-5.2: containment in 100% of episodes, 82.5% FP). The gap is "not in detection but in restraint" [2601.21083](https://arxiv.org/abs/2601.21083).
- **SIR-Bench**: separates real investigation from "alert parroting" (triage accuracy, novel findings, tool appropriateness) [2604.12040](https://arxiv.org/abs/2604.12040). Also SIABENCH [2603.06422](https://arxiv.org/abs/2603.06422), ALERT-BENCH [2610.10608](https://arxiv.org/abs/2610.10608), and APTInvestBench (varying telemetry) [2609.38954](https://arxiv.org/abs/2609.38954).
- **Robustness of RAG-based IDS**: knowledge poisoning and prompt injection through retrieved traffic. Multi-document retrieval limits label flips to 0.6–2.4% (vs 35–55% single-doc), and label-embedding consistency checks are the main defence [2608.08100](https://arxiv.org/abs/2608.08100).
- Reasoning structure matters: graph-structured reasoning beats few-shot by 9.8–12.2 pp on ATT&CK network-traffic/CTI tasks [2609.24710](https://arxiv.org/abs/2609.24710).
- **Gap:** very few papers evaluate on *host-centric, time-windowed* network context. Most use flow-level IDS datasets (UNSW-NB15, CIC-IDS, NF-*-IoT, CICDDoS2019) or host/endpoint logs (DARPA TC, OTRF, LANL).

## 4. Design patterns that recur (and map to your pipeline)

| Your component | Supported pattern | Key refs |
|---|---|---|
| Host context (fixed window, enriched) | Compact, deterministic, structured "evidence pack" / unified incident record; NL summaries + structured fields; evidence anchors with IDs | [2601.14601](https://arxiv.org/abs/2601.14601), [2604.05440](https://arxiv.org/abs/2604.05440), [2606.06871](https://arxiv.org/abs/2606.06871), [2512.22223](https://arxiv.org/abs/2512.22223) |
| Connection classification | Keep a numeric ML classifier; expose it as a *tool* to the agent rather than having the LLM classify | [2507.02424](https://arxiv.org/abs/2507.02424), [2408.04342](https://arxiv.org/abs/2408.04342), [2510.17883](https://arxiv.org/abs/2510.17883) |
| Blacklist / CTI matching | Prompt augmentation with CTI (+20% explanation quality); CTI credibility verification before use | [2507.16241](https://arxiv.org/abs/2507.16241), [2507.11310](https://arxiv.org/abs/2507.11310) |
| ML pre-triage gate | Funnel: cheap continuous triage, expensive agent only on anomalies; RL/GNN for structure the LLM cannot hold in context | [2601.14601](https://arxiv.org/abs/2601.14601), [2603.23966](https://arxiv.org/abs/2603.23966), [2609.04159](https://arxiv.org/abs/2609.04159) |
| Agent collection | Role separation (evidence gatherer / analyst / challenger / judge); separate contexts for critique; investigation ledger | [2610.10608](https://arxiv.org/abs/2610.10608), [2510.00311](https://arxiv.org/abs/2510.00311), [2609.33446](https://arxiv.org/abs/2609.33446) |
| Stopping & verdict | Controller-owned stop rule; stronger evidence bar for *benign* dismissal; abstain/escalate option; "no records found" ≠ benign | [2609.33446](https://arxiv.org/abs/2609.33446), [2610.10608](https://arxiv.org/abs/2610.10608), [2512.22223](https://arxiv.org/abs/2512.22223) |
| Learning from analysts | Structured experience/rule library built from errors; skill evolution under recall constraint | [2610.03999](https://arxiv.org/abs/2610.03999), [2604.05458](https://arxiv.org/abs/2604.05458), [2609.32516](https://arxiv.org/abs/2609.32516) |
| Confidence | Do not trust LLM self-confidence; use deterministic reliability scores (evidence validity, run-to-run stability, cross-model agreement) | [2606.06871](https://arxiv.org/abs/2606.06871) |
| Security of the pipeline | Treat context fields (DNS names, HTTP headers, CTI text) as injection vectors; multi-doc retrieval + consistency checks | [2608.08100](https://arxiv.org/abs/2608.08100), [2601.21083](https://arxiv.org/abs/2601.21083) |

## 5. Open research gaps (opportunities for your work)
1. **Host-centric context as the unit of analysis.** Most work is per-flow, per-alert or per-incident. A fixed-window host profile that fuses classification, blacklist hits and CTI is under-studied, and there is no public benchmark for it.
2. **Calibrated hand-off between ML pre-triage and agents.** Few papers optimize *which* contexts to escalate (cost/recall trade-off). Conformal or risk-certified gating ([2608.12444](https://arxiv.org/abs/2608.12444), [2609.19241](https://arxiv.org/abs/2609.19241)) is an emerging but unconnected thread.
3. **False-negative safety of agentic dismissal.** ALERT-BENCH shows ≥40% missed attacks for standard agent designs. Asymmetric evidence requirements deserve systematic study.
4. **Evaluation beyond accuracy:** investigation depth, evidence grounding, tool appropriateness, restraint, and cost/latency per context.
5. **Adversarial content inside the context** (attacker-controlled hostnames, URLs, payload strings reaching the LLM) is largely unevaluated for network-traffic agents.
6. **Local/small-model deployment** under data-residency constraints (HESP, SERA-IDS, AIDR) is viable only with external procedure control or structured retrieval.

## 6. Recommended reading order
1. [2610.10608](https://arxiv.org/abs/2610.10608) AIDA / ALERT-BENCH — failure modes of agentic triage and a fix
2. [2601.14601](https://arxiv.org/abs/2601.14601) Holmes — funnel + evidence-pack agent for network traffic
3. [2609.33446](https://arxiv.org/abs/2609.33446) HESP — controller-owned investigation for small local LLMs
4. [2510.00311](https://arxiv.org/abs/2510.00311) CORTEX — multi-agent alert triage with real SOC traces
5. [2507.16241](https://arxiv.org/abs/2507.16241) eX-NIDS — CTI-augmented explanation of NIDS flows
6. [2610.03999](https://arxiv.org/abs/2610.03999) SERA-IDS — structured experience retrieval
7. [2606.06871](https://arxiv.org/abs/2606.06871) PROBE — evidence-grounded reliability scoring for pcap diagnosis
8. [2608.08100](https://arxiv.org/abs/2608.08100) RAG-IDS security — poisoning and injection defences
9. [2604.19533](https://arxiv.org/abs/2604.19533), [2601.21083](https://arxiv.org/abs/2601.21083) — benchmarks showing the limits of current agents
10. Surveys: [2512.06659](https://arxiv.org/abs/2512.06659) (five-generation agentic taxonomy), [2509.10858](https://arxiv.org/abs/2509.10858) (LLMs in SOC), [2507.04752](https://arxiv.org/abs/2507.04752) (LLMs for NIDS)
