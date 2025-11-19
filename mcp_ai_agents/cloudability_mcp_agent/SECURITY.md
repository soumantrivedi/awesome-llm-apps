# Security Guidelines - Cloudability MCP Server

## 🔒 Sensitive Content Protection

This document outlines security best practices to ensure no sensitive content is committed to Git.

## ⚠️ Never Commit

### API Keys & Credentials
- ❌ **API Keys** - Cloudability API keys
- ❌ **Tokens** - Bearer tokens or access tokens
- ❌ **Passwords** - Any passwords or secrets
- ❌ **Private Keys** - SSH keys, certificate keys

### Configuration Files
- ❌ **`.env` files** - Environment variable files
- ❌ **`mcp.json`** - MCP configuration (contains API keys)
- ❌ **`*.key` files** - Any key files
- ❌ **`credentials.json`** - Credential files

### Exported Data
- ❌ **CSV exports** - May contain sensitive cost data
- ❌ **JSON exports** - May contain sensitive information
- ❌ **Database files** - SQLite databases with data

## ✅ Protected by .gitignore

The following patterns are automatically excluded:

```
# Environment variables
.env
.env.local
.env.*.local

# API Keys and credentials
*_key
*.key
credentials.json
secrets.json

# MCP Configuration
.cursor/mcp.json
mcp.json
**/mcp.json

# Exported reports
*.csv
*.xlsx
*.xls
amortized_costs_*.csv
cost_report_*.csv
*_report_*.csv
*_export_*.csv

# Virtual environments
venv/
cloudability/
.venv/
```

## 🔍 Pre-Commit Checklist

Before committing, verify:

1. ✅ No API keys in code or documentation
2. ✅ No `.env` files
3. ✅ No `mcp.json` files
4. ✅ No exported CSV/JSON files with real data
5. ✅ All sensitive values use placeholders (`your_api_key_here`, etc.)

## 🛡️ Security Best Practices

### 1. Use Environment Variables

**✅ Good:**
```python
api_key = os.getenv("CLOUDABILITY_API_KEY")
```

**❌ Bad:**
```python
api_key = "g1cDqKBQ_da_sSomZuBxKm_zVcI="  # Never hardcode!
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
  "CLOUDABILITY_API_KEY": "g1cDqKBQ_da_sSomZuBxKm_zVcI="
}
```

### 3. Keep Configuration Outside Repository

- Store API keys in environment variables
- Use `.env` files locally (gitignored)
- Configure MCP in `~/.cursor/mcp.json` (outside repo)

### 4. Review Before Committing

```bash
# Check for sensitive content
git diff --cached | grep -i "api_key\|password\|secret\|token"

# Verify .gitignore is working
git check-ignore -v .env mcp.json
```

## 🔐 Current Protection Status

### Files Protected
- ✅ `.env` files - Ignored
- ✅ `mcp.json` files - Ignored
- ✅ `*.csv` exports - Ignored
- ✅ `venv/` directories - Ignored
- ✅ `*.key` files - Ignored

### Documentation
- ✅ All API keys replaced with placeholders
- ✅ Examples use `your_api_key_here`
- ✅ No real credentials in documentation

## 🚨 If You Accidentally Commit Sensitive Data

### Immediate Actions

1. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/sensitive/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. **Rotate credentials:**
   - Generate new API keys
   - Update all configurations
   - Revoke old keys

3. **Force push (if already pushed):**
   ```bash
   git push origin --force --all
   ```

### Prevention

- Use `git-secrets` or similar tools
- Set up pre-commit hooks
- Review diffs before committing
- Use `.gitignore` properly

## 📋 Security Checklist

Before each commit:

- [ ] No API keys in code
- [ ] No API keys in documentation
- [ ] No `.env` files
- [ ] No `mcp.json` files
- [ ] No exported CSV/JSON with real data
- [ ] All placeholders used (`your_api_key_here`)
- [ ] `.gitignore` is up to date
- [ ] Reviewed `git diff` for sensitive content

## 🔗 Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Git: .gitignore documentation](https://git-scm.com/docs/gitignore)

---

**Remember**: Once sensitive data is committed and pushed, consider it compromised. Always rotate credentials immediately.

