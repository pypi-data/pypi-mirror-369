# MCP Trello Library Test Project

This project tests the `mcp-trello` library before PyPI deployment.

## Setup

1. **Copy environment file:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your Trello credentials:**
   ```bash
   TRELLO_API_KEY=your_actual_api_key
   TRELLO_TOKEN=your_actual_token
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

## Testing

Run the comprehensive test script:

```bash
uv run python test_mcp_trello.py
```

This will test:
- ✅ Library import
- ✅ TrelloClient initialization
- ✅ API connectivity
- ✅ All major functions (workspaces, boards, lists, cards)
- ✅ MCP server functionality
- ✅ Tool registration

## What This Tests

- **Import functionality** - Can the library be imported?
- **API connectivity** - Does it connect to Trello successfully?
- **Core functions** - Do all the main methods work?
- **MCP integration** - Is the MCP server properly configured?
- **Error handling** - Does it handle errors gracefully?

## Success Criteria

If all tests pass, your library is ready for PyPI deployment!

## Troubleshooting

- **Import errors**: Check that the library is properly installed in editable mode
- **API errors**: Verify your Trello credentials in `.env`
- **MCP errors**: Check that the MCP server is properly configured

## Next Steps

After successful testing:
1. Go back to your `mcp-trello` directory
2. Deploy to PyPI: `uv run twine upload dist/*`
3. Or test on TestPyPI first: `uv run twine upload --repository testpypi dist/*`
