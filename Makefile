SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)

.PHONY: init generate validate heal lock sign audit backup clean rebuild update-handover

init:
	@python main.py generate $(PROJECT_DIR)
	@git init
	@git add .
	@git commit -m "Init VIBECODER-SECURE MCP project"

generate:
	@python main.py generate $(PROJECT_DIR)
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

validate:
	@python main.py validate $(PROJECT_DIR)

heal:
	@python main.py heal $(PROJECT_DIR)
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

lock:
	@python main.py lock $(PROJECT_DIR) --update
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

sign:
	@python main.py sign $(PROJECT_DIR) --key $(GPG_KEY)
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

audit:
	@python -c "from src.agents.audit import generate_audit_report; import json; print(json.dumps(generate_audit_report('$(PROJECT_DIR)'), indent=2))" > audit.log
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

backup:
	@python -c "from src.agents.backup import snapshot; snapshot('$(PROJECT_DIR)')"
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

update-handover:
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

clean:
	@rm -rf docs .goldminer goldminer.lock goldminer.toml ai-plugin.json src

rebuild: clean init generate validate lock sign audit backup
	@echo "Rebuild complete."