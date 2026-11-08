# Agent-to-Agent (A2A) Distributed Orchestrator

A production-ready **Agent-to-Agent (A2A)** architecture built with **FastAPI**, **LangGraph**, and **Groq (`gpt-oss-120b` / `llama3-70b`)**.

This system implements dynamic multi-agent orchestration:
- An **Orchestrator Service** that discovers downstream agents at boot via the official A2A `AgentCard` protocol.
- A **Dynamic Semantic Router** powered by LangGraph and Groq that routes incoming user questions to the right specialist.
- A **Generic A2A Dispatcher** that dynamically connects to discovered agents without hardcoded agent-specific nodes.
- A **Financial Agent Service** that publishes its capabilities (`agent-card.json`) and answers complex financial and investment questions.

---

## 🏗️ Architecture Overview

```mermaid
flowchart TB
    subgraph ClientLayer [" Client "]
        User([User / API Consumer])
    end

    subgraph OrchestratorService [" 🟦 Orchestrator Service (:8000) "]
        direction TB
        MainO["FastAPI Router\n• lifespan: Startup Discovery\n• POST /chat\n• GET /graph"]
        
        Registry["AgentRegistry\n• In-memory AgentCards\n• get_routing_prompt()"]
        
        subgraph OrchGraph [" LangGraph Engine "]
            direction TB
            START_O((START)) --> Node_Orch["orchestrator_node\n(Groq LLM + Dynamic Agent Prompt)"]
            Node_Orch --> CondEdge{"_route_to_agent\n(Conditional Branch)"}
            CondEdge -- "selected != None" --> Node_Disp["a2a_dispatcher_node"]
            CondEdge -- "None" --> END_O((END))
            Node_Disp --> END_O
        end

        ClientA2A["A2A_client\n• Retries & Timeouts\n• X-Request-ID Header"]
    end

    subgraph FinancialService [" 🟩 Financial Agent Service (:8001) "]
        direction TB
        MainF["FastAPI Service\n• GET /.well-known/agent-card.json\n• POST /chat"]
        
        Card["AgentCard (Protobuf)\n• provider.url\n• skills: ['financial']"]
        
        subgraph FinGraph [" Financial LangGraph "]
            START_F((START)) --> Node_Fin["financial_node\n(ChatGroq + Financial Prompt)"]
            Node_Fin --> END_F((END))
        end
    end

    %% Startup Discovery
    MainO -- "1. Startup: GET /.well-known/agent-card.json" --> MainF
    MainF -. "Returns AgentCard JSON" .-> Registry
    Registry -. "Injects skills into prompt" .-> Node_Orch

    %% Runtime Chat Execution
    User -->|"POST /chat {question}"| MainO
    MainO --> OrchGraph
    Node_Disp --> ClientA2A
    ClientA2A -->|"2. POST /chat {question, request_id}"| MainF
    MainF --> FinGraph
    FinGraph -. "Financial Answer" .-> MainF
    MainF -. "A2AResponse {response, agent}" .-> ClientA2A
    ClientA2A -. "Answer in State" .-> Node_Disp
    MainO -. "Final JSON Response" .-> User
```

---

## 🏛️ A2A Protocol Interaction Lifecycle

The system operates across two distinct protocol phases: **Boot-time Discovery** and **Runtime A2A Execution**.

```mermaid
sequenceDiagram
    autonumber
    participant Orch as 🟦 Orchestrator (:8000)
    participant Reg as 📋 AgentRegistry (In-Memory)
    participant Fin as 🟩 Financial Agent (:8001)
    participant Groq as 🧠 Groq LLM (gpt-oss-120b)

    %% ── PHASE 1: A2A DISCOVERY & CAPABILITY NEGOTIATION ──
    rect rgb(235, 245, 255)
    Note over Orch,Fin: Phase 1: Boot-time A2A Discovery Handshake
    Orch->>Fin: GET /.well-known/agent-card.json (via A2ACardResolver)
    Fin-->>Orch: Returns AgentCard Protobuf JSON<br/>{name, url: ":8001", skills: ["financial"]}
    Orch->>Reg: register(agent_key="financial", card=AgentCard)
    Note over Reg: Stores AgentCard & Provider URL for dynamic dispatch
    end

    %% ── PHASE 2: RUNTIME QUERY ROUTING & EXECUTION ──
    rect rgb(240, 255, 240)
    Note over Orch,Groq: Phase 2: Runtime A2A Execution & Dispatch
    User->>Orch: POST /chat {"question": "What is a 401(k)?"}
    
    Orch->>Reg: get_routing_prompt()
    Reg-->>Orch: "- financial: Handles finance, investments, taxes... (Skills: financial)"
    
    Orch->>Groq: Query + Discovered Available Agents Menu
    Groq-->>Orch: "financial"
    
    Note over Orch: Conditional edge evaluates selected_agent == 'financial'<br/>Routes to generic a2a_dispatcher_node
    
    Orch->>Reg: Lookup card for "financial" -> resolves URL "http://127.0.0.1:8001"
    
    Orch->>Fin: A2A_client.send(question, request_id="uuid-1234")<br/>POST /chat {question, request_id}
    
    Fin->>Groq: Financial LangGraph Node + Financial Advisor System Prompt
    Groq-->>Fin: Expert Financial Answer
    
    Fin-->>Orch: 200 OK A2AResponse {response: "...", agent: "financial", request_id: "uuid-1234"}
    
    Orch-->>User: 200 OK JSON {question, selected_agent: "financial", response: "..."}
    end
```

---

## 🌐 A2A Multi-Agent Discovery & Registry Topology

The generic `a2a_dispatcher_node` enables an extensible hub-and-spoke multi-agent topology without code modifications:

```mermaid
graph TD
    subgraph OrchestratorGateway [" 🟦 Orchestrator Gateway (:8000) "]
        Router["Groq LLM Semantic Router"]
        Registry["AgentRegistry\n(Dynamic In-Memory Registry)"]
        Dispatcher["Generic a2a_dispatcher_node\n(Zero Hardcoded Agent Logic)"]
        
        Router -->|"Routes by Agent Key"| Dispatcher
        Registry -.->|"Supplies Target URLs & Skills"| Dispatcher
    end

    subgraph DomainAgents [" 🟩 Discovered A2A Domain Agents "]
        FinAgent["Financial Agent (:8001)\n• /.well-known/agent-card.json\n• POST /chat"]
        LegalAgent["Legal Agent (:8002) [Extensible]\n• /.well-known/agent-card.json\n• POST /chat"]
        HRAgent["HR Agent (:8003) [Extensible]\n• /.well-known/agent-card.json\n• POST /chat"]
    end

    Dispatcher ==>|"A2A Protocol (HTTP/JSON)"| FinAgent
    Dispatcher -.->|"Dispatched dynamically"| LegalAgent
    Dispatcher -.->|"Dispatched dynamically"| HRAgent

    FinAgent -.->|"Card Resolution at boot"| Registry
    LegalAgent -.->|"Card Resolution at boot"| Registry
    HRAgent -.->|"Card Resolution at boot"| Registry
```

---

## 📦 A2A Protocol Wire Contract

The communication follows standard typed contracts across both nodes:

| Protocol Stage | Endpoint | Request Payload | Response Payload |
|---|---|---|---|
| **Discovery** | `GET /.well-known/agent-card.json` | *None* | `AgentCard` (Protobuf JSON: `name`, `version`, `provider.url`, `skills`, `capabilities`) |
| **A2A Chat** | `POST /chat` | `{"question": str, "request_id": str}` | `{"response": str, "agent": str, "request_id": str}` |
| **Health** | `GET /health` | *None* | `{"status": "ok"}` |

---

## 📁 Repository Structure

```text
A2A practice/
├── .vscode/
│   └── launch.json            # VS Code multi-server compound debugger
├── orchestrator/
│   ├── config.py              # Settings & AGENT_URLS dictionary
│   ├── discovery.py           # A2ACardResolver & AgentRegistry engine
│   ├── schema.py              # UserQuery, A2ARequest, A2AResponse models
│   ├── A2A_client.py          # Resilient HTTP client for A2A transport
│   ├── main.py                # Orchestrator FastAPI app (Port 8000)
│   └── graph/
│       ├── state.py           # orchestratorState TypedDict
│       ├── nodes.py           # orchestrator_node & a2a_dispatcher_node
│       └── graph.py           # LangGraph StateGraph with conditional edge
├── financial/
│   ├── config.py              # Financial service settings
│   ├── schema.py              # FinancialRequest and FinancialResponse schemas
│   ├── agent_card.py          # Protobuf AgentCard definition & serialization
│   ├── main.py                # Financial FastAPI app (Port 8001)
│   ├── server.py              # Standalone Uvicorn runner
│   └── graph/
│       ├── state.py           # FinancialState TypedDict
│       ├── nodes.py           # financial_node (Groq financial advisor prompt)
│       └── graph.py           # Financial service LangGraph workflow
├── .env                       # Environment variables (API keys & endpoints)
├── .gitignore                 # Git ignore rules
└── requirements.txt           # Project dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Groq API key (from [console.groq.com](https://console.groq.com))

### 2. Environment Setup

Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
```

Install the dependencies:
```powershell
pip install -r requirements.txt
```

### 3. Configure `.env`

Create a `.env` file in the root directory:
```env
GROK_API_KEY=your_groq_api_key_here
GROK_MODEL_NAME=gpt-oss-120b
FINANCIAL_AGENT_URL=http://127.0.0.1:8001
```

---

## 🏃 Running the Services

### Option A: VS Code Debugger (Recommended)
1. Open the repository in VS Code.
2. Go to **Run & Debug** (`Ctrl + Shift + D`).
3. Select **`Run Both Services (Orchestrator + Financial)`** from the top dropdown.
4. Press **F5**. Both services will launch simultaneously with live breakpoint debugging.

### Option B: Terminal Invocations

**Terminal 1 — Start the Financial Agent (Port 8001):**
```powershell
.\venv\Scripts\uvicorn financial.main:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 2 — Start the Orchestrator (Port 8000):**
```powershell
.\venv\Scripts\uvicorn orchestrator.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📡 API Endpoints & Testing

### 1. Orchestrator Health
```bash
curl http://127.0.0.1:8000/health
```
**Response:**
```json
{"status": "ok"}
```

### 2. Visualizing the Orchestrator LangGraph
Open in browser:
```text
http://127.0.0.1:8000/graph
```
Returns a rendered PNG diagram of the active LangGraph routing state.

### 3. Financial Agent Card (Discovery Endpoint)
```bash
curl http://127.0.0.1:8001/.well-known/agent-card.json
```
**Response:**
```json
{
  "name": "Financial Agent",
  "description": "Specialized agent for financial advice, investments, taxes, banking, budgeting, and cryptocurrency.",
  "version": "1.0.0",
  "provider": {
    "url": "http://127.0.0.1:8001",
    "organization": "My Finance Co."
  },
  "skills": [
    {
      "id": "financial_advisory",
      "name": "financial",
      "description": "Handles questions related to finance, investments, stocks, budgeting, accounting, taxes, banking, cryptocurrency, and economic data."
    }
  ]
}
```

### 4. End-to-End Chat Routing
Send a user query to the Orchestrator:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the difference between a traditional 401(k) and a Roth IRA?"}'
```

**Response:**
```json
{
  "question": "What is the difference between a traditional 401(k) and a Roth IRA?",
  "selected_agent": "financial",
  "response": "A Traditional 401(k) is an employer-sponsored retirement account where contributions are made pre-tax... A Roth IRA is an individual retirement account funded with after-tax dollars..."
}
```

---

## 🧩 Adding a New Agent (Zero Orchestrator Graph Changes)

Because the system uses an **`a2a_dispatcher_node`** with dynamic discovery:

1. **Build the New Agent Service** (e.g. `legal` on `127.0.0.1:8002`):
   - Expose `/.well-known/agent-card.json` with skill descriptions.
   - Expose `POST /chat`.
2. **Add the URL to `orchestrator/config.py`**:
   ```python
   AGENT_URLS: dict = {
       "financial": "http://127.0.0.1:8001",
       "legal": "http://127.0.0.1:8002",  # 👈 Added in 1 line
   }
   ```
3. **Done!**
   - At startup, the Orchestrator fetches the legal agent card.
   - The Groq router immediately recognizes legal questions and routes them to `a2a_dispatcher_node`.
   - **Zero graph or node code changes required.**

---

## 🛡️ License
MIT License. Built for distributed agentic architectures.

