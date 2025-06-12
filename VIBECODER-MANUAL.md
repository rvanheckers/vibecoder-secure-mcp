# 🎯 VIBECODER-SECURE MCP MANUAL

**Voor Vibecoders & AI Agents** | **Version 1.0** | **Updated: 2025-06-12**

---

## 📋 QUICK START (NIEUWE AI LEEST DIT EERST!)

### 🚨 VOOR ELKE NIEUWE AI SESSIE:

1. **STOP en lees `CLAUDE.md`** - Complete project context
2. **Run `make roadmap`** - Zie huidige Vibecoder focus  
3. **Check Git status** - `git status && git log --oneline -5`
4. **Begrijp de scope** - Dit is ALLEEN voor Vibecoder workflows
5. **Volg de principes** - Geen generic features!

### ⚡ CONTEXT IN 30 SECONDEN:

```bash
# Waar ben ik?
pwd  # Should be: /mnt/c/Vibecoder Secure MCP

# Wat is de status?
make roadmap

# Wat was de laatste activiteit?
git log --oneline -3

# Wat is er gaande?
cat CLAUDE.md | head -20
```

---

## 🎯 VIBECODER PRINCIPLES (HEILIG!)

### 🔴 ALTIJD ONTHOUDEN:
1. **Vibecoder-specific ALLEEN** - Geen generieke oplossingen
2. **Security & Integrity FIRST** - Nooit compromitteren  
3. **AI Handover Continuity** - Context MOET behouden blijven
4. **Milestone Tracking** - Voorkomt scope creep & derailing
5. **Git = Truth** - Alle wijzigingen via Git workflow

### ⚠️ VERBODEN TERREIN:
- ❌ Generic dashboards/UI (tenzij Vibecoder-specific)
- ❌ Database ORMs (we hebben file-based system)
- ❌ Complex frontend frameworks
- ❌ Features die niet direct Vibecoders helpen
- ❌ Wijzigingen zonder roadmap check

---

## 🏗️ SYSTEM ARCHITECTURE

### 📁 Project Structuur:
```
vibecoder-secure-mcp/
├── 📋 VIBECODER-MANUAL.md    # Dit document (START HIER!)
├── 📋 CLAUDE.md              # AI Handover (auto-updates)
├── 📄 README.md              # Public documentation
├── 🔧 Makefile               # ALL operations via make targets
├── 🐍 main.py                # FastAPI MCP hub
├── 📦 requirements.txt       # Dependencies
├── ⚙️ ai-plugin.json         # AI plugin config
├── 🔒 goldminer.toml         # Project config
├── 🔐 goldminer.lock         # Integrity lock
├── 📁 src/agents/            # 8 Sub-agents (DO NOT CALL DIRECTLY!)
├── 📁 docs/                  # Generated docs
├── 📁 .goldminer/           # Config & backups
└── 📁 .git/                 # Git (pre-commit/post-merge hooks)
```

### 🤖 Sub-Agents (Via Makefile ONLY!):
- `generate_docs.py` → Documentation generation
- `validate_docs.py` → Integrity validation  
- `auto_heal.py` → Auto-healing
- `compliance.py` → Compliance checking
- `integrity.py` → Merkle tree hashing
- `audit.py` → Audit logging
- `backup.py` → Backup & restore
- `handover_updater.py` → AI context updates
- `vibecoder_roadmap.py` → Milestone & focus tracking

---

## 🔧 COMMAND REFERENCE

### 🎯 Vibecoder-Specific Commands:
```bash
make roadmap        # 📊 Show current Vibecoder focus & milestones
make check-focus    # 🎯 Test if proposed work is Vibecoder-aligned
make update-handover # 📋 Update AI handover document
```

### 📄 Core Operations:
```bash
make generate       # 📝 Generate documentation
make validate       # ✅ Validate project integrity
make heal          # 🔧 Auto-fix detected issues
make lock          # 🔒 Update integrity lock file
make sign          # ✍️ Sign with GPG (requires GPG_KEY env)
make audit         # 📊 Generate audit report
make backup        # 💾 Create backup snapshot
```

### 🔄 Workflow Commands:
```bash
make init          # 🚀 Initialize new project
make clean         # 🧹 Clean generated files
make rebuild       # 🔄 Full rebuild cycle
```

---

## 🎯 VIBECODER WORKFLOW

### 🚀 Starting New Work:
```bash
# 1. Check current focus
make roadmap

# 2. Verify alignment
make check-focus
# Enter proposed work when prompted

# 3. If aligned, proceed with implementation
# 4. Always update context
make update-handover
```

### 🔄 Daily Operations:
```bash
# Morning routine
git status                  # Check for changes
make roadmap               # See current focus
make validate              # Verify integrity

# Work cycle
# ... do your work ...
make generate              # Update docs
make update-handover       # Update context

# Evening routine  
git add . && git commit -m "..." # Commit changes
git push                   # Sync to GitHub
```

### 🤝 AI Handover Process:
```bash
# Before ending session
make update-handover       # Update AI context
git add CLAUDE.md && git commit -m "Update AI context"
git push                   # Ensure remote is current

# New AI starts with
cat CLAUDE.md              # Read complete context
make roadmap               # See current focus
git log --oneline -5       # Recent activity
```

---

## 🛡️ SECURITY & INTEGRITY

### 🔒 Security Model:
- **Merkle Tree Hashing** - SHA-256 integrity verification
- **Append-only Audit Log** - Immutable operation history
- **GPG Signing** - Cryptographic verification  
- **Path Validation** - Secure project boundaries
- **Human Approval** - Required for destructive operations

### 🔐 Key Files (NEVER MODIFY DIRECTLY!):
- `goldminer.lock` - Only via `make lock`
- `audit.log` - Append-only
- `.git/hooks/*` - Only if explicitly required
- `.goldminer/vibecoder_roadmap.json` - Via roadmap commands only

### ✅ Safe Operations:
- Documentation generation (`make generate`)
- Validation (`make validate`)
- Auto-healing (`make heal`) 
- Backup creation (`make backup`)
- Context updates (`make update-handover`)

---

## 🚨 TROUBLESHOOTING

### ❌ Validation Failures:
```bash
make validate              # See what's wrong
make heal                  # Auto-fix issues
make validate              # Re-verify
```

### 🔄 Context Lost:
```bash
cat CLAUDE.md              # Read AI handover document
make roadmap               # See current milestones
git log --oneline -10      # Recent changes
make update-handover       # Refresh context
```

### 🎯 Focus Derailing:
```bash
make check-focus           # Test proposed work
# If not aligned, reconsider approach
make roadmap               # See current priorities
```

### 🔒 Integrity Issues:
```bash
make lock                  # Recompute Merkle root
python main.py lock . --update    # Force update
make validate              # Re-verify
```

### 📦 Dependency Issues:
```bash
# In production, use virtual environment:
python -m venv venv
source venv/bin/activate   # Linux/Mac
# or venv\Scripts\activate # Windows
pip install -r requirements.txt
```

---

## 📊 MILESTONES & ROADMAP

### 🎯 Current Phase: **Foundation**
- ✅ Core pipeline implementation  
- ✅ Security & integrity framework
- ✅ AI handover system
- ✅ GitHub integration
- 🔄 Vibecoder roadmap system

### 🔮 Next Phase: **Enhancement** 
- 📊 Real-time monitoring for Vibecoder workflows
- 🤖 Advanced AI context preservation
- 🔄 Vibecoder-specific automation
- 📈 Workflow optimization

### 📋 Milestone Commands:
```bash
make roadmap               # See current milestones
python -c "from src.agents.vibecoder_roadmap import VibecoderRoadmapManager; m=VibecoderRoadmapManager('.'); print('Focus areas:', m.VIBECODER_FOCUS_AREAS)"
```

---

## 🔗 IMPORTANT LINKS

- **GitHub Repo**: https://github.com/rvanheckers/vibecoder-secure-mcp
- **AI Handover**: `CLAUDE.md` (auto-updated)
- **Technical Docs**: `docs/` directory
- **Security Model**: `docs/SECURITY.md`

---

## 📞 AI AGENT INSTRUCTIONS

### 🤖 Voor Claude Code / AI Agents:

#### ✅ DO:
1. **Read this manual FIRST** before any work
2. **Check `make roadmap`** for current focus
3. **Use Makefile targets** - never call sub-agents directly
4. **Update context** with `make update-handover` after changes
5. **Commit frequently** with descriptive messages
6. **Stay Vibecoder-focused** - check alignment with `make check-focus`

#### ❌ DON'T:
1. Create generic features without Vibecoder alignment
2. Modify security files directly (`goldminer.lock`, `audit.log`)
3. Skip roadmap/milestone checking
4. Forget to update AI handover context
5. Work outside the defined Vibecoder scope

#### 🎯 Always Ask:
- "Does this serve Vibecoder workflows specifically?"
- "How does this improve security/integrity?"
- "Will this help AI handover continuity?"
- "Is this aligned with current milestones?"

---

## 🏁 CONCLUSION

This manual ensures **EVERY** interaction with VIBECODER-SECURE MCP:
- ✅ Stays focused on Vibecoder needs
- ✅ Maintains security & integrity
- ✅ Preserves context across AI handovers
- ✅ Follows proper workflow procedures
- ✅ Contributes to milestone progress

**REMEMBER**: When in doubt, `make roadmap` and check `CLAUDE.md`!

---

*Built with ❤️ for Vibecoder workflows | Keep it secure, keep it focused!*