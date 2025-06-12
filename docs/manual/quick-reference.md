# 🚀 VIBECODER-SECURE MCP QUICK REFERENCE

## ⚡ NEW AI CHECKLIST (30 SECONDS!)

```bash
□ pwd  # Confirm location
□ cat CLAUDE.md | head -20  # Get context
□ make roadmap  # Current focus
□ git status && git log --oneline -3  # Recent activity
□ Read VIBECODER-MANUAL.md  # Full instructions
```

## 🎯 CORE COMMANDS

| Command | Purpose | Use When |
|---------|---------|----------|
| `make roadmap` | 📊 Current Vibecoder focus | Starting work |
| `make check-focus` | 🎯 Test alignment | Before new features |
| `make validate` | ✅ Check integrity | Before commits |
| `make generate` | 📝 Update docs | After changes |
| `make update-handover` | 📋 Update AI context | End of session |

## 🚨 EMERGENCY COMMANDS

| Problem | Solution |
|---------|----------|
| Lost context | `cat CLAUDE.md && make roadmap` |
| Validation fails | `make heal && make validate` |
| Focus unclear | `make roadmap && make check-focus` |
| Integrity broken | `make lock && make validate` |

## 🎯 VIBECODER PRINCIPLES

1. **🔴 Vibecoder-only** - No generic features
2. **🔒 Security first** - Never compromise integrity  
3. **📋 Context continuity** - Always update handover
4. **🎯 Milestone driven** - Check roadmap alignment
5. **📚 Git workflow** - All changes via proper process

## ❌ FORBIDDEN

- Generic dashboards/UI
- Direct sub-agent calls
- Modifying security files directly
- Work without roadmap check
- Skipping context updates

## ✅ SAFE OPERATIONS

- `make generate` - Documentation
- `make validate` - Integrity check
- `make heal` - Auto-fix issues
- `make backup` - Create snapshot
- `make update-handover` - Context update

---

**When in doubt**: `make roadmap` → `CLAUDE.md` → `VIBECODER-MANUAL.md`