# Survey plan: LLM-agent support for host-level network traffic triage

Scope: LLM and agent methods that analyse network communication (flows, packets, IDS alerts) for security triage, 2024–2026. Parts follow the pipeline — context representation → ML pre-triage gate → CTI/blacklist enrichment → multi-agent investigation → evaluation. Each part lists 10 core papers ranked by relevance, recency and venue, plus reserve papers. Source: the project's merged arXiv (394) + peer-reviewed (920) corpora, deduplicated (61 overlaps), relevance ≥ 2; selection by hand from ranked candidates.

Each part closes with a gap statement ('unlike X, our system…'). The chapter ends with a comparison table: host-centric context | ML pre-triage gate | blacklist/CTI enrichment | multi-agent | evidence-grounded verdict | abstain/escalate | real-traffic evaluation.

## Part 1. Representing network communication for LLMs

**Scope.** How flows, packets and logs are serialised, tokenised, summarised or rendered so an LLM can reason over them; what context granularity works.

**Guiding question.** RQ1: Which representation of a host's communication (flow text, compact serialisation, evidence packs, images, learned traffic tokens) preserves the evidence an analyst needs within a token budget?

| # | Paper | Year | Venue | Why it matters |
|---|---|---|---|---|
| 1 | TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation (arXiv:2504.04222) | 2025 | arXiv | Traffic-domain tokenisation and two-stage tuning; generic traffic representation across 229 types. |
| 2 | PCAP-LM: An LLM-Native Text Representation for TLS Bulk Traffic Analysis (arXiv:2607.28100) | 2026 | arXiv | LLM-native glyph text for PCAP flows; compact textual capture representation. |
| 3 | Lightweight LLM Adaptation for Intrusion Detection via Token-Efficient Flow Representation (doi:10.1109/cai68641.2026.11536533) | 2026 | IEEE Conference on Artificial Intelligence (CAI) | Token-efficient (TOON) flow serialisation; quantifies token cost of the representation. |
| 4 | Multimodal LLMs for Zero-Shot Intrusion Detection Using NetFlow Visualisations (doi:10.1109/lcn65610.2025.11146352) | 2025 | IEEE 50th Conference on Local Computer Networks (LCN) | Alternative modality: NetFlow windows rendered as plots for multimodal LLMs. |
| 5 | ReGAIN: Retrieval-Grounded AI Framework for Network Traffic Analysis (doi:10.1109/icnc68183.2026.11416826) | 2026 | International Conference on Computing, Networking and Communications | Traffic summarised to text, hierarchical RAG with abstention and cited evidence. |
| 6 | Respond to Change With Constancy: Instruction-Tuning With LLM for Non-I.I.D. Network Traffic Classification (doi:10.1109/tifs.2025.3574971) | 2025 | IEEE Transactions on Information Forensics and Security | Instruction tuning on traffic structure; robustness under distribution shift (TIFS). |
| 7 | Multimodal Reasoning with LLM for Encrypted Traffic Interpretation: A Benchmark (doi:10.1109/tmm.2026.3730256) | 2026 | IEEE Transactions on Multimedia | Byte-grounded encrypted-traffic description benchmark; evidence-grounded traffic reports. |
| 8 | Fine-Tuning Large Language Models for Network Traffic Analysis in Cyber Security (doi:10.1109/dsc63325.2024.00019) | 2024 | IEEE Conference on Dependable and Secure Computing (DSC) | Fine-tuned LLMs on textualised flows; tests robustness to irrelevant context. |
| 9 | ShieldGPT: An LLM-based Framework for DDoS Mitigation (doi:10.1145/3663408.3663424) | 2024 | Proceedings of the 8th Asia-Pacific Workshop on Networking | Early LLM framework turning traffic representations into DDoS explanations and mitigations. |
| 10 | From Flows to Words: Can Zero-/Few-Shot LLMs Detect Network Intrusions? A Grammar-Constrained, Calibrated Evaluation on UNSW-NB15 (arXiv:2510.17883) | 2025 | arXiv | Flow-to-text with domain flags, grammar-constrained output and calibrated threshold. |

*Reserve:* Evaluation of local LLMs for network traffic packet analysis (2026); DoLLM: How Large Language Models Understanding Network Flow Data to Detect Carpet Bombing DDoS (2024); LENS: Lightweight and Explainable LLM-Based APT Detection at the Edge for 6G Security (2025)

**Gap to state.** Existing work represents single flows, packets or one capture; none builds a per-host, time-windowed context that already carries classification labels and CTI hits.

## Part 2. ML pre-triage and LLM escalation (hybrid cascades)

**Scope.** Lightweight detectors or anomaly models screen traffic first; the LLM is invoked only for flagged or uncertain cases. Covers gating, routing and uncertainty-based escalation.

**Guiding question.** RQ2: How should the ML gate decide what reaches the LLM (anomaly score, entropy, conformal set, cost), and what does the gate save in cost and errors?

| # | Paper | Year | Venue | Why it matters |
|---|---|---|---|---|
| 1 | Entropy-guided circuit breakers for LLM-augmented intrusion detection: An empirical evaluation of uncertainty-routed cascades in LLMOps (doi:10.1016/j.future.2026.108871) | 2027 | Future Generation Computer Systems | Entropy-based routing of uncertain IDS predictions to an LLM; empirical cascade study. |
| 2 | Knowing when to escalate: Prompt-based uncertainty quantification for selective automation of LLM-based intrusion detection (doi:10.1016/j.array.2026.101127) | 2026 | Array | Prompt-based uncertainty for accept/escalate on LLM flow classification. |
| 3 | ALM: A Two-Stage Traffic Anomaly Detection and Analysis System via the Large Language Model (doi:10.1109/noms57970.2025.11073622) | 2025 | NOMS 2025-2025 IEEE Network Operations and Management Symposium | Two-stage: ensemble anomaly detector, then fine-tuned LLM classifies attack type. |
| 4 | Explainable Anomaly Detection in Network Traffic Using LLM (doi:10.1109/noms57970.2025.11073574) | 2025 | NOMS 2025-2025 IEEE Network Operations and Management Symposium | Conventional detector first; LLM explains only flagged events to cut LLM usage. |
| 5 | eX-NIDS: A Framework for Explainable Network Intrusion Detection Leveraging Large Language Models (doi:10.1016/j.compeleceng.2025.110826) | 2026 | Computers and Electrical Engineering | Flow NIDS flags, prompt augmenter adds context and CTI for LLM explanation. |
| 6 | XG-NID: Dual-Modality Network Intrusion Detection using a Heterogeneous Graph Neural Network and Large Language Model (doi:10.1016/j.eswa.2025.128089) | 2025 | Expert Systems with Applications | Heterogeneous GNN on flow+packet data; LLM produces explanations and remediation. |
| 7 | LLM-Enhanced Intrusion Detection for Containerized Applications: A Two-Tier Strategy for SDN and Kubernetes Environments (doi:10.1007/978-3-032-00642-4_4) | 2025 | Availability, Reliability and Security | Statistical monitoring triggers on-demand LLM traffic analysis (SDN, Kubernetes). |
| 8 | A Comparative Study of Large Language Models for Industrial Cyber-Physical Security (doi:10.3390/electronics15132779) | 2026 | Electronics | LLMs and tabular foundation models vs RF/XGBoost; confidence-gated LLM cascade. |
| 9 | A Multi-Layer Cloud-IDS Pipeline with LLM and Adaptive Q-Learning Calibration (arXiv:2605.15889) | 2026 | arXiv | ML pre-triage with confidence gates, adaptive thresholds and LLM escalation. |
| 10 | MaID-Agent: A Hybrid Masqueraded Intrusion Detection System Enhanced by Agent (doi:10.1109/access.2026.3705409) | 2026 | IEEE Access | Two-tier IoT IDS; LLM agent triages only the uncertain flows. |

*Reserve:* Quantifying the Real-Time Gap: A Comparative Study of LLMs vs. Random Forest on the DataSense: CIC-IIoT-2025 Dataset (2026); Think Fast: Real-Time IoT Intrusion Reasoning Using IDS and LLMs at the Edge Gateway (2025); A Zero-Touch O-RAN Framework for Federated Few-Shot IDS with LLM-Oracle Verification (2025)

**Gap to state.** Cascades gate individual flows or alerts; gating at the level of a host context and escalating to a multi-agent stage is not studied.

## Part 3. Threat-intelligence and knowledge enrichment

**Scope.** Grounding detections in external knowledge: IOC and reputation lookups, CTI fusion, ATT&CK mapping, knowledge graphs and RAG over curated security knowledge.

**Guiding question.** RQ3: How are blacklist/IOC hits and CTI fused with traffic evidence, how are conflicting sources resolved, and how is the provenance kept for the verdict?

| # | Paper | Year | Venue | Why it matters |
|---|---|---|---|---|
| 1 | Enhancing federated intrusion detection through LLM-Driven alert enrichment and collaborative threat information sharing (doi:10.1016/j.future.2025.108319) | 2026 | Future Generation Computer Systems | LLM alert enrichment and collaborative threat-information sharing in federated IDS. |
| 2 | Real-Time Multi-Source Threat Intelligence Fusion Using Large Language Models (doi:10.1109/icaic67076.2026.11395679) | 2026 | IEEE 5th International Conference on AI in Cybersecurity | Fuses multi-source TI verdicts for IOCs, resolves conflicts, outputs confidence index. |
| 3 | Advancing Autonomous Incident Response: Leveraging LLMs and Cyber Threat Intelligence (doi:10.1109/globecom59602.2025.11432623) | 2025 | GLOBECOM 2025 - 2025 IEEE Global Communications Conference | CTI vector store + external CTI platform queries enrich alerts for IR planning. |
| 4 | LLM-Driven Alert Correlation and Lifecycle Prediction With Threat Intelligence for Attack Forensics (doi:10.1109/tmlcn.2026.3736372) | 2026 | IEEE Transactions on Machine Learning in Communications and Networking | CTI-guided fine-tuning to correlate alerts and predict ATT&CK lifecycle stage. |
| 5 | KNOWML: Improving Generalization of ML-NIDS with Attack Knowledge Graphs (doi:10.1109/eurosp68448.2026.00064) | 2026 | IEEE 11th European Symposium on Security and Privacy | LLM-built attack knowledge graphs extend ML-NIDS features for generalisation. |
| 6 | RLFE-IDS: A framework of Intrusion Detection System based on Retrieval Augmented Generation and Large Language Model (doi:10.1016/j.comnet.2025.111341) | 2025 | Computer Networks | RAG-augmented LLM intrusion detection over flow records (Computer Networks). |
| 7 | A Privacy-Preserving Framework for Cyber Incident Analysis from Network Packets Using +Large Language Models (doi:10.1109/cai68641.2026.11536475) | 2026 | IEEE Conference on Artificial Intelligence (CAI) | Local LLMs with RAG over PCAP artefacts and VirusTotal indicators; privacy-preserving. |
| 8 | CyTReX: Explainable AI-Based Cybersecurity Threat Reasoning Framework for DER Networks (arXiv:2610.04286) | 2026 | arXiv | Anomaly alerts turned into ranked hypotheses via SHAP and MCP-based CTI enrichment. |
| 9 | Enhancing network security using knowledge graphs and large language models for explainable threat detection (doi:10.1016/j.future.2025.108160) | 2026 | Future Generation Computer Systems | Knowledge graphs from network logs, Graph-BERT detection and LLM analyst reports. |
| 10 | SERA-IDS: Structured Experience Retrieval-Augmented Intrusion Detection with Small Language Models (arXiv:2610.03999) | 2026 | arXiv | Small local LLMs classify flows with a retrieved structured experience/rule library. |

*Reserve:* Labeling Network Intrusion Detection System (NIDS) Rules with MITRE ATT&CK Techniques: Machine Learning vs. Large Language Models (2025); Enhancing Security Operations Center: Wazuh Security Event Response with Retrieval-Augmented-Generation-Driven Copilot (2025); RAGSec: Retrieval-Augmented Generation for Cybersecurity Threat Intelligence in Enterprise Networks (2026); Ontology-Guided Heterogeneous Graph Retrieval for Large-Language-Model Interpretation of Suricata Events (2025)

**Gap to state.** Enrichment is usually applied to an alert after detection; few systems treat blacklist matches as first-class context features alongside connection classification.

## Part 4. Agentic and multi-agent investigation

**Scope.** LLM agents that plan, call tools, gather evidence and reach verdicts or responses; role-specialised multi-agent teams, controllers and evidence ledgers.

**Guiding question.** RQ4: How should investigation be divided among agents (roles, controller, stopping rule), and how are verdicts tied to collected evidence?

| # | Paper | Year | Venue | Why it matters |
|---|---|---|---|---|
| 1 | Design and evaluation of an Autonomous Cyber Defence agent using DRL and an augmented LLM (doi:10.1016/j.comnet.2025.111162) | 2025 | Computer Networks | Hybrid DRL + augmented LLM defence agent with CTI knowledge graph (Computer Networks). |
| 2 | CyberRAG: An Agentic RAG cyber attack classification and reporting tool (doi:10.1016/j.future.2025.108186) | 2026 | Future Generation Computer Systems | Agentic RAG orchestrating attack-specific classifiers and iterative retrieval. |
| 3 | AgentNIRS: An LLM-Driven Agent for Network Intrusion Response (doi:10.1109/acsacw69556.2025.00054) | 2025 | Annual Computer Security Applications Conference Workshops | LLM agent interprets network intrusion alerts and selects response actions. |
| 4 | An LLM-Based Agentic Network Traffic Incident-Report Approach Towards Explainable-AI Network Defense (doi:10.3390/jsan15020032) | 2026 | Journal of Sensor and Actuator Networks | RF pre-detection, SHAP ensemble, then ReAct agent with RAG writes incident reports. |
| 5 | Autonomous Cyber Incident Response Using Reasoning and Action (doi:10.1109/iwcmc65282.2025.11059476) | 2025 | International Wireless Communications and Mobile Computing | ReAct/LangGraph agent triages Suricata/Wazuh alerts and executes firewall responses. |
| 6 | CORTEX: Collaborative LLM Agents for High-Stakes Alert Triage (arXiv:2510.00311) | 2025 | arXiv | Role-specialised agents (behaviour, evidence, reasoning) for auditable alert triage. |
| 7 | From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage (arXiv:2610.10608) | 2026 | arXiv | Failure analysis of SOC triage agents; AIDA multi-agent with challenge, ledger, judge. |
| 8 | HESP: Separating What to Probe from When to Stop in Local LLM Alert-Triage Agents (arXiv:2609.33446) | 2026 | arXiv | External controller with evidence ledger, info-gain probing and stopping rule for local LLM agents. |
| 9 | Holmes: An Evidence-Grounded LLM Agent for Auditable DDoS Investigation in Cloud Networks (arXiv:2601.14601) | 2026 | arXiv | Funnel workflow: counter-based triage, then PCAP evidence packs for auditable DDoS attribution. |
| 10 | Hierarchical Agentic Incident Response with Digital-Twin-Validated Attack Inference (doi:10.1109/cns69863.2026.11720917) | 2026 | IEEE Conference on Communications and Network Security (CNS) | Hierarchical multi-agent IR; attack hypotheses validated in a network digital twin. |

*Reserve:* IntelForge: Multi-Agent LLM Framework for Cyber Threat Intelligence Enrichment (2025); A Multi-Agent System for Cybersecurity Threat Detection and Correlation Using Large Language Models (2025); MA-IDS: Multi-Agent RAG Framework for IoT Network Intrusion Detection with an Experience Library (2026); Hierarchical multi-agent AI framework for cybersecurity in cyber–physical systems (2026)

**Gap to state.** Agentic triage systems start from SIEM alerts or single incidents; none takes a pre-triaged host context as the unit of investigation.

## Part 5. Evaluation, reliability and security of LLM triage

**Scope.** Benchmarks and metrics for triage agents, calibration and abstention, robustness to distribution shift, and attacks on the pipeline (prompt injection, knowledge poisoning).

**Guiding question.** RQ5: How do we measure correctness, evidence faithfulness, calibrated abstention and robustness of an agentic triage system on real traffic?

| # | Paper | Year | Venue | Why it matters |
|---|---|---|---|---|
| 1 | CFA-Bench: Cybersecurity Forensic Llm Agent Benchmark and Testing (doi:10.1109/eurospw67616.2025.00031) | 2025 | IEEE European Symposium on Security and Privacy Workshops | Benchmark for forensic LLM agents with PCAP-reader and retrieval tools. |
| 2 | APTInvestBench: Evaluating Autonomous APT Investigation under Varying Telemetry (arXiv:2609.38954) | 2026 | arXiv | APT-investigation benchmark scoring evidence sufficiency and record-level citations. |
| 3 | Before You Hand Over the Wheel: Evaluating LLMs for Security Incident Analysis (arXiv:2603.06422) | 2026 | arXiv | SIABench: agentic evaluation of 11 LLMs on incident analysis and alert triage. |
| 4 | OpenSec: Measuring Incident Response Agent Calibration Under Adversarial Evidence (arXiv:2601.21083) | 2026 | arXiv | Measures IR-agent calibration and evidence gating under prompt-injected evidence. |
| 5 | Defending Retrieval-Augmented Intrusion Detection Against Knowledge Poisoning and Prompt Injection (arXiv:2608.08100) | 2026 | arXiv | Attacks and defences for RAG-based IDS: knowledge poisoning and prompt injection. |
| 6 | Can Large Language Models Be Trusted for AI-Based Intrusion Detection in Cybersecurity? An Evidence-Grounded Log Analysis (doi:10.1109/cai68641.2026.11536474) | 2026 | IEEE Conference on Artificial Intelligence (CAI) | Scores LLM suspicion calibration and evidence faithfulness on fixed log windows. |
| 7 | Evidence-Grounded Ensemble Diagnosis of 802.11 Packet Captures: A Multi-Stage Pipeline with Deterministic Reliability Scoring (arXiv:2606.06871) | 2026 | arXiv | PROBE: deterministic reliability scoring; shows LLM self-confidence is uninformative. |
| 8 | Possibilities and limitations of using large language models (LLMs) for alert classification and prioritisation in security operations centers (SOCs) (doi:10.1016/j.eswa.2026.133194) | 2026 | Expert Systems with Applications | Eight LLMs vs classical ML for SOC alert classification and prioritisation (ESWA). |
| 9 | Dual-Threshold Conformal Deferral for Trustworthy Security Alert Triage (doi:10.3390/electronics15184084) | 2026 | Electronics | Conformal deferral with error control: auto-close, auto-escalate or defer to analyst. |
| 10 | A Three-Axis Stress Test of LLM vs Classical ML for Network Intrusion Detection under Distribution Shift and Adversarial Evasion (arXiv:2609.13511) | 2026 | arXiv | LLM vs classical ML NIDS under cross-dataset shift and adversarial evasion. |

*Reserve:* SIR-Bench: Evaluating Investigation Depth in Security Incident Response Agents (2026); Assessing the Stability of LLM-Generated Explanations in Network Security via Repeated Sampling (2026); Robust Conformal Intrusion Detection via Traffic-Aware Calibration and Attack-Orbit Invariance (2026); Constrained-Action AI Remediation for SIEM/XDR via a NeMo-Guardrails Proxy (2026)

**Gap to state.** Benchmarks mostly use host logs, CTF-style incidents or public NIDS datasets; real, host-centric traffic evaluation with abstain/escalate metrics is missing.

## Caveats

- Corpus built from OpenAlex, Crossref and arXiv (to 2026-10-21). USENIX Security, ICML and ICLR are poorly covered there; Semantic Scholar was not usable, so those venues may be under-represented.
- Many peer-reviewed records were screened from the title alone; papers like AgentNIRS and RLFE-IDS should be read in full before being cited for specific claims.
- 16 of 50 core papers are arXiv preprints, mostly from 2026 (Parts 4 and 5 lean heavily on preprints).
