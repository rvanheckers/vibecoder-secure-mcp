# VIBECODER-SECURE MCP

**Secure document pipeline with integrity validation and audit capabilities for Vibecoder workflows**

[![Status](https://img.shields.io/badge/status-operational-green)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Overview

VIBECODER-SECURE MCP is a comprehensive secure document pipeline designed specifically for Vibecoder workflows. It provides integrity validation, audit capabilities, automated healing, and cryptographic verification.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/rvanheckers/vibecoder-secure-mcp.git
cd vibecoder-secure-mcp

# Install dependencies (recommended: use virtual environment)
pip install -r requirements.txt

# Initialize project
make init

# Generate documentation
make generate

# Validate integrity
make validate
```

## 🔧 Features

- **🔒 Security**: Merkle tree integrity checking, GPG signing, audit trails
- **📄 Documentation**: Auto-generated docs with validation
- **🛠️ Auto-healing**: Detect and fix issues automatically  
- **📊 Monitoring**: Real-time integrity validation
- **💾 Backup**: Compressed snapshots with restore capability
- **🔄 CI/CD**: Git hooks for automated workflows

## 📋 Makefile Commands

| Command | Description |
|---------|-------------|
| `make init` | Initialize new project |
| `make generate` | Generate documentation |
| `make validate` | Validate project integrity |
| `make heal` | Auto-heal detected issues |
| `make lock` | Update integrity lock file |
| `make sign` | Sign with GPG key |
| `make audit` | Generate audit report |
| `make backup` | Create backup snapshot |
| `make update-handover` | Update AI handover document |

## 🏗️ Architecture

```
├── main.py                 # FastAPI MCP hub orchestrator
├── src/agents/            # Sub-agents for all operations
│   ├── generate_docs.py   # Documentation generation
│   ├── validate_docs.py   # Integrity validation
│   ├── auto_heal.py       # Auto-healing
│   ├── integrity.py       # Merkle tree hashing
│   ├── audit.py          # Audit logging
│   └── backup.py         # Backup & restore
├── docs/                  # Generated documentation
├── .goldminer/           # Configuration & manifests
└── CLAUDE.md             # AI handover document (auto-updated)
```

## 🔐 Security Model

- **Merkle Tree Hashing**: SHA-256 based integrity verification
- **Append-only Audit Log**: Immutable operation history  
- **GPG Signing**: Cryptographic verification
- **Path Validation**: Secure project boundaries
- **Human Approval**: Required for destructive operations

## 🎯 Vibecoder Focus

This system is built specifically for **Vibecoder workflows** and includes:
- Milestone tracking and roadmap management
- AI handover documents for seamless transitions
- Vibecoder-specific compliance requirements
- Automated workflow integration

## 📚 Documentation

- [AI Handover Document](CLAUDE.md) - Complete project state for AI agents
- [API Documentation](docs/API.md) - FastAPI endpoint details
- [Security Model](docs/SECURITY.md) - Security implementation details

## 🆘 Support

For Vibecoder-specific issues or feature requests, please open an issue with the `vibecoder` label.

## 📄 License

MIT License - see LICENSE file for details.

---

*Built with ❤️ for Vibecoder workflows*