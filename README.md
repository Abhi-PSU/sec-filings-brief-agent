# SEC Filings Brief Agent

An OpenAI agent that turns a stock ticker into a one-page company brief built from the company's latest SEC filings and recent news. Built for IST 402 (Generative AI applications) at Penn State.

## Project goals

1. **Automate filing research.** Replace the manual routine of finding a company's latest 10-K or 10-Q on EDGAR, copying key numbers, skimming the risk factors, and searching for news.
2. **Ground every number in source data.** Financial figures come only from SEC EDGAR XBRL data, and each one links back to the filing it came from. The model writes the summary; it does not supply the numbers.
3. **Keep a person in charge of the conclusion.** The brief is a research draft for a human analyst. It never gives a buy, sell, or hold call.
4. **Ship something that keeps working.** Build the workflow in OpenAI Agent Builder, then export it to Agents SDK code in this repo before Agent Builder shuts down on November 30, 2026.

## What the agent does

| Step | Workflow | Source |
|---|---|---|
| 1 | Look up the company's CIK from its ticker | SEC `company_tickers.json` |
| 2 | Find the latest 10-K and 10-Q | EDGAR submissions API |
| 3 | Pull revenue, net income, diluted EPS, operating cash flow, and long-term debt, then compute year-over-year change | EDGAR XBRL company facts API |
| 4 | Summarize risk factors (Item 1A) and management discussion (Item 7 / Item 2) | Filing text on sec.gov |
| 5 | Add news from the last 30 days, with links | OpenAI web search tool |
| 6 | Check the draft against guardrails (no investment advice, no personal data, every figure cited) | Agent Builder guardrails node |
| 7 | Return the brief in chat and save a Markdown copy to `briefs/` | Agent Builder preview, GitHub |

Full detail is in [`docs/project-scope.md`](docs/project-scope.md).

## Data sources, APIs, and services

| Service | Used for | Access |
|---|---|---|
| OpenAI Agent Builder | Visual workflow canvas, agent and guardrail nodes, preview | OpenAI platform account, API billing |
| OpenAI web search tool | Recent news with citations | Built into the Agent node |
| SEC EDGAR APIs (`data.sec.gov`) | Filings list and XBRL financial data | Free, no key. Must send a User-Agent with name and email. Max 10 requests per second |
| OpenAI Agents SDK (`openai-agents`) | Code version of the workflow after export | Python 3.10+, `OPENAI_API_KEY` |
| GitHub | Version control, issues, project board | This repo |
| Google Drive (stretch goal) | Shared folder of saved briefs | MCP connector |

## Repository layout

```
sec-filings-brief-agent/
├── README.md
├── .gitignore
├── .env.example                 # copy to .env and fill in; .env is never committed
├── requirements.txt
├── docs/
│   └── project-scope.md         # goals, workflows, data sources, roles, milestones, risks
├── prompts/
│   └── agent-instructions.md    # instructions pasted into the Agent Builder agent node
└── scripts/
    └── check_edgar.py           # confirms EDGAR access for a ticker
```

## Setup

### 1. Agent Builder (cloud)

1. Sign in at [platform.openai.com](https://platform.openai.com) and add API credits under Billing.
2. Create a project named `IST402-SEC-Brief-Agent` and set a monthly budget limit.
3. Open [Agent Builder](https://platform.openai.com/agent-builder) and create a workflow named `SEC Filings Brief Agent`.
4. Paste [`prompts/agent-instructions.md`](prompts/agent-instructions.md) into the Agent node's instructions and turn on web search.

### 2. Local tools (for testing and the Agents SDK export)

```bash
git clone https://github.com/Abhi-PSU/sec-filings-brief-agent.git
cd sec-filings-brief-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then add your own values
python scripts/check_edgar.py AAPL
```

Keep API keys in `.env` only. The `.gitignore` already excludes it.

## Milestones

| Milestone | Target | Output |
|---|---|---|
| 1. Scope and environment | Week 8 | This repo, project scope, Agent Builder workflow created |
| 2. Filing retrieval and metrics | Weeks 9 to 10 | Steps 1 to 3 working in Agent Builder |
| 3. Summaries, news, guardrails | Week 11 | Full brief for one ticker |
| 4. Export to Agents SDK | By Nov 20, 2026 | Python code in this repo, runs locally |
| 5. Testing and demo | Weeks 12 to 14 | Briefs for 10 test tickers, accuracy check, final demo |

## Contributors

| Name | GitHub | Role |
|---|---|---|
| Abhi Adusumilli | [@Abhi-PSU](https://github.com/Abhi-PSU) | Project manager, agent developer, data integration, testing and documentation |

Penn State University, College of Information Sciences and Technology. IST 402, Fall 2026.

## Disclaimer

This is a class project. Briefs are research drafts generated from public filings and may contain errors. They are not investment advice.
