# Thynkr

## System Architecture
┌─────────────────────────────┐
│         Frontend UI         │◄───────────── (HTMX / Streamlit)
│  - Input form (paste text)  │
│  - Show summary             │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│        FastAPI Backend       │
│ ┌─────────────────────────┐ │
│ │     /summarize route     │◄──── Paste content via UI
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │     /ingest route        │◄──── (Optional: save or tag content)
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │     /ask route           │◄──── (Optional: ask Qs on stored content)
│ └─────────────────────────┘ │
└────────────┬────────────────┘
             ▼
┌─────────────────────────────┐
│         Claude API          │
│ - Summarization             │
│ - Q&A                       │
│ - Prompt engineering        │
└────────────┬────────────────┘
             ▼
┌─────────────────────────────┐
│   Optional: Memory Layer    │
│ - Store past content        │
│ - Embedding retrieval       │
└─────────────────────────────┘


## Use cases

1. Summarization Flow
- User pastes content (news, blog, report)
- API sends it to Claude with summarization prompt
- Result returned to frontend

2. (Optional) Ingest + Retrieval
- Save user content into vector store
- Let user ask questions about stored content
- Retrieve context → augment prompt → ask Claude

## 📈 Planned Enhancements
- Search via Tavily / SerpAPI / Bing
- Web scraping from URLs
- Workflow automation (Zapier-like)
- Plugin system for agents/tools
- User auth (multi-session)
- Multi-modal input (PDFs, images)

