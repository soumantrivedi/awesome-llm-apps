# Security Guidelines

## Never Commit

- ❌ API keys and credentials
- ❌ `.env` files
- ❌ `mcp.json` files (contains API keys)
- ❌ Exported CSV/JSON files with real data
- ❌ Any files with sensitive information

## Protected Files

The following are automatically excluded via `.gitignore`:

```
.env
.env.local
*.csv
*.xlsx
*.key
credentials.json
mcp.json
venv/
```

## Best Practices

### 1. Use Environment Variables

**✅ Good:**
```python
api_key = os.getenv("CLOUDABILITY_API_KEY")
```

**❌ Bad:**
```python
api_key = "your-actual-api-key-here"  # Never hardcode!
```

### 2. Use Placeholders in Documentation

**✅ Good:**
```json
{
  "CLOUDABILITY_API_KEY": "your_api_key_here"
}
```

**❌ Bad:**
```json
{
  "CLOUDABILITY_API_KEY": "actual-key-value"
}
```

### 3. Store Configuration Outside Repository

- Store API keys in environment variables
- Use `.env` files locally (gitignored)
- Configure MCP in `~/.cursor/mcp.json` (outside repo)

## Pre-Commit Checklist

Before committing:
- [ ] No API keys in code or documentation
- [ ] No `.env` files
- [ ] No `mcp.json` files
- [ ] No exported CSV/JSON files with real data
- [ ] All sensitive values use placeholders

## If You Accidentally Commit Sensitive Data

1. **Rotate credentials immediately** - Generate new API keys
2. **Remove from Git history** - Use `git filter-branch` or BFG Repo-Cleaner
3. **Update all configurations** - Replace old keys everywhere

**Remember:** Once sensitive data is committed and pushed, consider it compromised. Always rotate credentials immediately.
