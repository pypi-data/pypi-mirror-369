# Running MCP Server with SSE Transport Protocol

This guide demonstrates how to run and test a Model Context Protocol (MCP) server using Server-Sent Events (SSE) transport, based on a YouTube video extraction server implementation.

## Prerequisites

- Python with `uv` package manager
- FastMCP library
- YouTube API key (for this specific example)
- Terminal access with `curl`

## Server Setup

### 1. Server Implementation

Your MCP server (the mcp_youtube_extract/src/mcp_youtube_extract/server.py file) should be configured to use SSE transport:

```python
def main():
    #"""Main entry point for the MCP server."""
    #logger.info("Starting YouTube MCP Server")
    #try:
    #    mcp.run()
    
    """Main entry point for the MCP server."""
    logger.info("Starting YouTube MCP Server with SSE transport")
    try:
        mcp.run(transport="sse")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
```

### 2. Environment Configuration

Make sure there is a `.env` file with necessary API keys:

```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Export environment variables:

```bash
# Method 1: Export from .env file
export $(cat .env | xargs)

# Method 2: Source directly
source .env

# Verify variables are set
echo $YOUTUBE_API_KEY
```

## Running the Server

### Start the MCP Server

```bash
uv run mcp_youtube_extract
```

Expected output:
```
INFO     MCP YouTube Extract package initialized, version: 0.1.0
INFO     Starting YouTube MCP Server with SSE transport
INFO:     Started server process [26564]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

The server will be running on `http://127.0.0.1:8000`

## Testing the Server

### Step 1: Establish SSE Connection

Open a new terminal and establish the SSE connection:

```bash
curl -N -H "Accept: text/event-stream" \
     -H "Cache-Control: no-cache" \
     http://127.0.0.1:8000/sse
```
**Note**: You can also open a browser with http://127.0.0.1:8000/sse to establish a SSE connection

Expected response:
```
event: endpoint
data: /messages/?session_id=40f403a8-8045-41aa-9c63-bd8d19ea94fd
: ping - 2025-07-23 11:54:04.878748+00:00
```

**Important**: Keep this terminal open to monitor server responses. Note the session ID for subsequent requests.

### Step 2: Convert Session ID to UUID Format

If needed, convert the session ID to proper UUID format:
- Original: `40f403a8804541aa9c63bd8d19ea94fd`
- UUID Format: `40f403a8-8045-41aa-9c63-bd8d19ea94fd`

### Step 3: MCP Protocol Handshake

In a new terminal, execute the following sequence:

#### 3.1 Initialize the Session

```bash
curl -X POST "http://127.0.0.1:8000/messages/?session_id=40f403a8-8045-41aa-9c63-bd8d19ea94fd" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

#### 3.2 Send Initialized Notification

```bash
curl -X POST "http://127.0.0.1:8000/messages/?session_id=40f403a8-8045-41aa-9c63-bd8d19ea94fd" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

#### 3.3 List Available Tools

```bash
curl -X POST "http://127.0.0.1:8000/messages/?session_id=40f403a8-8045-41aa-9c63-bd8d19ea94fd" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

#### 3.4 Call a Tool

```bash
curl -X POST "http://127.0.0.1:8000/messages/?session_id=40f403a8-8045-41aa-9c63-bd8d19ea94fd" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_yt_video_info",
      "arguments": {
        "video_id": "jNQXAC9IVRw"
      }
    }
  }'
```

## Understanding the Responses

### Server Logs
Monitor your server terminal for logs like:
```
INFO:     127.0.0.1:53374 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:53416 - "POST /messages/?session_id=... HTTP/1.1" 202 Accepted
```

### SSE Terminal Responses
In your SSE terminal, you should see:
- Initialization responses
- Tool list with available tools
- Tool execution results with JSON-RPC responses

## Common Issues and Solutions

### Issue: "Failed to validate request: Received request before initialization was complete"

**Solution**: Always follow the proper MCP handshake sequence:
1. Initialize
2. Send initialized notification
3. Then make tool calls

### Issue: No response in SSE terminal

**Solution**: Restart the SSE connection:
```bash
curl -N -H "Accept: text/event-stream" \
     -H "Cache-Control: no-cache" \
     http://127.0.0.1:8000/sse
```

### Issue: API key errors

**Solution**: Verify environment variables are properly exported:
```bash
echo $YOUTUBE_API_KEY
export $(cat .env | xargs)
```

## Advanced Testing

### Browser Testing
You can also test the SSE connection in a browser by navigating to:
```
http://127.0.0.1:8000/sse
```

### Automated Testing Script
Create a bash script to automate the testing sequence:

```bash
#!/bin/bash

SESSION_ID="40f403a8-8045-41aa-9c63-bd8d19ea94fd"
BASE_URL="http://127.0.0.1:8000/messages/?session_id=$SESSION_ID"

# Initialize
curl -X POST "$BASE_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'

# Send initialized notification
curl -X POST "$BASE_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}'

# List tools
curl -X POST "$BASE_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'

# Call tool
curl -X POST "$BASE_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_yt_video_info", "arguments": {"video_id": "jNQXAC9IVRw"}}}'
```

## Transport Comparison

### SSE vs Other Transports

- **SSE (Server-Sent Events)**: HTTP-based, good for web integration, real-time updates
- **stdio**: Standard input/output, common for Claude Desktop integration
- **HTTP**: Request/response only, no real-time capabilities

### When to Use SSE Transport

- Web-based MCP clients
- Real-time monitoring needs
- HTTP infrastructure compatibility
- Testing and debugging MCP servers

## Conclusion

SSE transport provides a robust way to run MCP servers with real-time communication capabilities. The key is following the proper MCP protocol handshake and maintaining the SSE connection for receiving responses.

Remember to:
1. Start the server with SSE transport
2. Establish SSE connection first
3. Follow proper MCP initialization sequence
4. Monitor both server logs and SSE responses
5. Handle session IDs correctly (UUID format when needed)
