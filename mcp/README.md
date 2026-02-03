# OpenAI Responses API: Data and Connectors (File Search & MCP)

This project demonstrates two capabilities of the OpenAI Responses API: **File Search** (vector stores and semantic search over uploaded documents) and **MCP / Connectors** (Model Context Protocol and OpenAI-hosted connectors for external services). The notebook shows how to build a knowledge base, query it via file search with citations, and optionally extend the model with MCP tools such as Google Calendar or remote MCP servers.

## Overview

The notebook is in two parts. The first part focuses on **data**: uploading files, creating vector stores, and using the `file_search` tool so the model can retrieve and cite documents. The second part introduces **connectors and MCP**: using OpenAI-hosted connectors (e.g. Google Calendar) and remote MCP servers (e.g. GitMCP for documentation) so the model can call external APIs and tools.

## Architecture

### File Search (Vector Stores and Retrieval)

1. **File upload**: Files are uploaded via the Files API (`purpose="assistants"`). The notebook includes a helper that supports both local paths and URLs.
2. **Vector store**: A vector store is created and files are attached. OpenAI processes documents and builds the index; the notebook polls until file status is `completed`.
3. **Responses API with file search**: A request is sent with `tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}]`. The model can issue `file_search_call` items, and the final `message` can include `file_citation` annotations.
4. **Customization**: Options such as `max_num_results` and `include=["file_search_call.results"]` control how many chunks are retrieved and whether raw search results appear in the response.

### MCP and Connectors

- **Connectors**: Pre-built MCP wrappers maintained by OpenAI (e.g. `connector_googlecalendar`). They are referenced in the request with `tools=[{"type": "mcp", "connector_id": "connector_googlecalendar"}]` and typically require OAuth or API tokens (e.g. `GOOGLE_OAUTH_TOKEN`).
- **Remote MCP servers**: Third-party servers that implement the MCP protocol (e.g. GitMCP for repo/docs). They are referenced by URL and can be used so the model can access documentation, code, or other resources without hosting the tool logic yourself.

The response can contain `mcp_call` output items; the notebook shows how to inspect these and relate them to the final answer.

## Key Techniques

### Semantic search and citations

File search is semantic (embedding-based) rather than keyword-only. The model receives retrieved chunks and can attach citations to the reply; the client can read `output_item.content[].annotations` (e.g. `file_citation`) to map answers back to source files.

### Waiting for vector store processing

Files in a vector store move through `in_progress` to `completed` (or `failed`). The notebook implements a small polling loop with a timeout so that file search is only used after processing is done.

### Include parameter

Using `include=["file_search_call.results"]` returns the actual search result chunks in the response, which helps with debugging and transparency. Without it, only the final message and citation metadata are returned.

### MCP tool declaration

MCP tools are declared in the same `tools` array as file search: `{"type": "mcp", "connector_id": "..."}` for connectors, or the appropriate structure for remote MCP servers. The model then decides when to call them; the client inspects `output` for `mcp_call` (and related) items.

## Key Learnings

1. **File search is hosted**: No need to run your own embedding or vector DB; you upload files and reference the vector store ID. Trade-off is vendor lock-in and less control over chunking and retrieval logic.
2. **Citations improve trust**: File citations in the message make it easier to verify answers and build transparent RAG-style flows.
3. **Processing is asynchronous**: Waiting for vector store file status is required before relying on file search for that store.
4. **Connectors vs remote MCP**: Connectors are OpenAI-hosted and often simpler to enable (e.g. OAuth); remote MCP servers offer more flexibility and can wrap any MCP-compliant service.
5. **Responses API output structure**: The response is a sequence of output items (reasoning, file_search_call, mcp_call, message). Parsing by `output_item.type` is the main way to interpret and debug behavior.

## Evaluation

### Strengths

- Minimal setup for RAG-like behavior: upload files, create vector store, call Responses API with file search.
- Built-in citations and optional inclusion of search results.
- Single API for both file search and MCP/connectors; easy to combine in one request.
- Connectors and MCP allow extending the model to calendars, docs, code, etc., without implementing tools yourself.

### Limitations

- Vector store and file lifecycle are managed by OpenAI; no direct control over indexing or chunking.
- Connectors require the right tokens and may have usage limits or regional constraints.
- Remote MCP servers must be reachable and stable; debugging is harder than with local tools.

## Tech Stack

- **OpenAI Python client** (`openai`): `client.files`, `client.vector_stores`, `client.responses.create()`.
- **OpenAI Responses API**: File search tool, MCP/connector tools, structured output (reasoning, file_search_call, mcp_call, message).
- **Requests / BytesIO**: For uploading files from URLs in the helper.
- **Python 3.13+**, **uv** for install; **Jupyter** for the notebook. Optional: **pandas**, **plotly**, **rich** (as in pyproject) for analysis and display.

## Project Structure

```
mcp/
├── OpenAI_Responses_API_Data_and_Connectors.ipynb   # File search + MCP/connectors demo
├── pyproject.toml
└── README.md
```

Use a `data/` directory (or similar) with PDFs if you want to run the file-upload and vector-store examples as in the notebook.

## Getting Started

1. Install dependencies: `uv sync`
2. Set `OPENAI_API_KEY`. For connector examples (e.g. Google Calendar), set the required token (e.g. `GOOGLE_OAUTH_TOKEN`) if you have one.
3. Run the notebook in order: setup, create vector store, add files, wait for processing, then run file search and (optionally) MCP/connector examples.
4. For local files, adjust paths (e.g. to `./data/YourFile.pdf`) in the file-upload cells.

## Conclusion

This project illustrates how to use the Responses API for **data** (file search over vector stores with citations) and **connectors** (MCP and hosted connectors for external services). Together they support RAG-style Q&A over your documents and tool-augmented workflows (e.g. calendar, docs) without running your own retrieval or MCP server. The patterns shown—vector store lifecycle, `include` for transparency, and inspecting `output` by type—apply when building production flows on the Responses API.
