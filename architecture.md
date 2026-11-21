# Architecture notes

The application uses a hybrid agent architecture. Groq handles language interpretation and wording; deterministic Python controls safety, required fields, approved troubleshooting actions, and escalation.

## Runtime components

1. `TicketStore` keeps the current conversation state in memory and invokes the graph once per customer message.
2. A compiled LangGraph `StateGraph` routes each turn through safety, resolution checking, structured issue analysis, validation, retrieval, planning, and response nodes.
3. `ChatGroq` uses Pydantic structured output for issue analysis and resolution assessment. A final bounded prompt rewrites an already-approved draft without changing its action.
4. Chroma persists a local vector collection under `backend/data/chroma` and upserts the Markdown knowledge documents when the retriever is first used.
5. Deterministic rule and keyword implementations remain available when an external integration is unconfigured or fails.

## Trust boundaries

The LLM may classify language, extract stated facts, assess feedback, and rewrite approved text. It does not decide whether sensitive cases are allowed, which fields are mandatory, what operational action is authorized, or when troubleshooting is exhausted.

## Next phases

1. Persist tickets, messages, and workflow checkpoints with SQLite and SQLAlchemy.
2. Replace token-hash vectors with a production embedding model and add retrieval evaluation.
3. Add authenticated customer and agent roles.
4. Integrate permission-checked order, payment, and delivery tools.
5. Add tracing, latency metrics, token accounting, and regression evaluation datasets.
