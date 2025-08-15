# `list_servers` Command

List all deployed MCP servers currently running.

## Functionality
- Displays a table of active MCP servers with details: ID, template, transport, status, endpoint, ports, etc.
- Only running servers are shown.
- Output is beautified using Rich tables for clarity.

## Options
- No options; simply lists all running servers.

## Configuration
- No configuration required.

## Example
```
list_servers
```

### Sample Output
```
🔍 Discovering deployed MCP servers...
                                                                 Deployed MCP Servers (3 active)                                                                  
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID         ┃ Template             ┃ Transport    ┃ Status     ┃ Endpoint                       ┃ Ports                ┃ Since                     ┃ Tools      ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ bc0e605ab… │ mcp-demo-0806-14315… │ unknown      │ running    │ N/A                            │ 42651->7071          │ 54 minutes ago            │ 0          │
│ 38063d7c4… │ mcp-demo-0806-14292… │ unknown      │ running    │ N/A                            │ 54411->7071          │ 57 minutes ago            │ 0          │
│ 8ca83b881… │ mcp-demo-0806-14253… │ unknown      │ running    │ N/A                            │ 7071->7071           │ About an hour ago         │ 0          │
└────────────┴──────────────────────┴──────────────┴────────────┴────────────────────────────────┴──────────────────────┴───────────────────────────┴────────────┘
```

## When and How to Run
- Use when you want to see which MCP servers are currently deployed and running.
- Run at any time during an interactive CLI session.
