# VIBECODER-SECURE MCP - Central Makefile (Operation Control)
# Complete automation interface for all 26 VIBECODER operations
#
# Dependencies:
# - main.py: All targets call python main.py commands
# - venv/: Virtual environment activation required for Python operations
# - src/agents/*: Agents called via main.py orchestration
#
# Usage: make <target>
# Primary targets: generate, validate, heal, lock, dashboard, roadmap
# See individual targets below for specific functionality

SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)

.PHONY: init generate validate heal lock sign audit backup clean rebuild update-handover roadmap check-focus monitor dashboard server automation autorun compress visual-roadmap roadmap-save duplicate-check duplicate-report file-check file-suggest file-organize enforce-discipline milestone-start

init:
	@python main.py generate $(PROJECT_DIR)
	@git init
	@git add .
	@git commit -m "Init VIBECODER-SECURE MCP project"

generate:
	@python main.py generate $(PROJECT_DIR)
	@python -c "from src.agents.handover_updater import update_handover_document; update_handover_document('$(PROJECT_DIR)')"

validate:
	@source venv/bin/activate && python main.py validate "$(PROJECT_DIR)"

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

roadmap:
	@python -c "from src.agents.vibecoder_roadmap import get_current_vibecoder_focus; import json; print('🎯 Current Vibecoder Focus:'); print(json.dumps(get_current_vibecoder_focus('$(PROJECT_DIR)'), indent=2))"

check-focus-old:
	@python -c "from src.agents.vibecoder_roadmap import check_vibecoder_alignment; import json; import sys; work=input('Proposed work: '); result=check_vibecoder_alignment('$(PROJECT_DIR)', work); print(json.dumps(result, indent=2))"

clean:
	@rm -rf docs .goldminer goldminer.lock goldminer.toml ai-plugin.json src

monitor:
	@python src/agents/monitoring.py $(PROJECT_DIR)

dashboard:
	@python src/agents/monitoring.py $(PROJECT_DIR) dashboard
	@echo "Dashboard created at docs/dashboard.html"

server:
	@python main.py server --host 0.0.0.0 --port 8000

automation:
	@python -c "from src.agents.smart_automation import VibecoderSmartAutomation; import json; automation = VibecoderSmartAutomation('.'); print(json.dumps(automation.get_automation_status(), indent=2))"

autorun:
	@python -c "from src.agents.smart_automation import run_smart_automation; import json; print(json.dumps(run_smart_automation('.'), indent=2))"
	@echo "Smart automation completed"

compress:
	@python -c "from src.agents.context_compression import VibecoderContextCompressor; import json; compressor = VibecoderContextCompressor('.'); print(json.dumps(compressor.get_compressed_context_summary(), indent=2))"

visual-roadmap:
	@python -c "import sys; sys.path.insert(0, '.'); from src.agents.visual_roadmap import generate_visual_roadmap; print(generate_visual_roadmap('.', 'overview'))"

roadmap-save:
	@python -c "import sys; sys.path.insert(0, '.'); from src.agents.visual_roadmap import VibecoderVisualRoadmap; generator = VibecoderVisualRoadmap('.'); files = generator.save_roadmap_visualization(); print('📁 Roadmap visualizations saved:'); [print(f'  {style}: {path}') for style, path in files.items()]"

# VIB-011: Git-aware Duplicate Detection
duplicate-check:
	@echo "🔍 Running VIB-011 duplicate detection..."
	@python src/agents/duplicate_detection.py .

duplicate-report:
	@echo "📊 Generating VIB-011 duplicate report..."
	@python src/agents/duplicate_detection.py .
	@echo "Report saved to .goldminer/duplicate_detection/duplicate_report.json"

# VIB-012: Intelligent File Placement
file-check:
	@echo "🗂️ Running VIB-012 file placement analysis..."
	@python src/agents/file_placement.py . analyze

file-suggest:
	@echo "💡 Generating VIB-012 file placement suggestions..."
	@python src/agents/file_placement.py . analyze
	@echo "Suggestions saved to .goldminer/file_placement/placement_report.json"

file-organize:
	@echo "🚀 Running VIB-012 intelligent file organization..."
	@python src/agents/file_placement.py . organize
	@echo "Safe moves executed automatically, others need confirmation"

rebuild: clean init generate validate lock sign audit backup
	@echo "Rebuild complete."

# VIB-015: Milestone Discipline Enforcement
check-focus:
	@echo "🎯 MILESTONE DISCIPLINE CHECK:"
	@source venv/bin/activate && python src/agents/milestone_enforcer.py

enforce-discipline:
	@echo "⚠️ DISCIPLINE ENFORCEMENT: Checking proposed work..."
	@if [ -z "$(WORK)" ]; then \
		echo "Usage: make enforce-discipline WORK='your proposed work description'"; \
		exit 1; \
	fi
	@source venv/bin/activate && python src/agents/milestone_enforcer.py "$(WORK)"

milestone-start:
	@echo "🎯 STARTING MILESTONE: $(VIB)"
	@if [ -z "$(VIB)" ]; then \
		echo "Usage: make milestone-start VIB=VIB-006"; \
		exit 1; \
	fi
	@source venv/bin/activate && python -c "import sys; sys.path.insert(0, 'src'); from agents.vibecoder_roadmap import VibecoderRoadmapManager; roadmap = VibecoderRoadmapManager('.'); roadmap.start_milestone('$(VIB)'); print('Milestone $(VIB) started')"