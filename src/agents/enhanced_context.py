#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Enhanced AI Context Preservation (VIB-006)
Advanced AI handover with decision trees, conversation snapshots, and context compression
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DecisionPoint:
    """Represents a critical decision made during development"""
    timestamp: str
    decision_id: str
    context: str
    options_considered: List[str]
    chosen_option: str
    reasoning: str
    impact: str
    vibecoder_alignment: bool


@dataclass
class ConversationSnapshot:
    """Compressed conversation context for handover"""
    session_id: str
    timestamp: str
    key_topics: List[str]
    decisions_made: List[str]
    next_actions: List[str]
    vibecoder_focus: str
    code_changes: List[str]
    context_summary: str


class EnhancedContextManager:
    """Advanced AI context preservation for seamless handovers"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.context_dir = self.project_path / ".goldminer" / "enhanced_context"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        self.decisions_file = self.context_dir / "ai_decisions.json"
        self.conversations_file = self.context_dir / "conversation_history.json"
        self.compressed_context_file = self.context_dir / "compressed_context.json"
    
    def record_decision(self, context: str, options: List[str], chosen: str, 
                       reasoning: str, impact: str = "medium") -> str:
        """Record a critical development decision"""
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check Vibecoder alignment
        vibecoder_keywords = ["vibecoder", "workflow", "focus", "security", "handover"]
        alignment = any(keyword in reasoning.lower() for keyword in vibecoder_keywords)
        
        decision = DecisionPoint(
            timestamp=datetime.now().isoformat(),
            decision_id=decision_id,
            context=context,
            options_considered=options,
            chosen_option=chosen,
            reasoning=reasoning,
            impact=impact,
            vibecoder_alignment=alignment
        )
        
        # Load existing decisions
        decisions = self._load_decisions()
        decisions.append(asdict(decision))
        
        # Save with compression (keep last 50)
        if len(decisions) > 50:
            decisions = decisions[-50:]
        
        with open(self.decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)
        
        print(f"✅ Decision recorded: {decision_id}")
        return decision_id
    
    def create_conversation_snapshot(self, session_id: str, key_topics: List[str],
                                   decisions: List[str], next_actions: List[str],
                                   focus: str, changes: List[str], summary: str) -> None:
        """Create compressed conversation snapshot for handover"""
        snapshot = ConversationSnapshot(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            key_topics=key_topics,
            decisions_made=decisions,
            next_actions=next_actions,
            vibecoder_focus=focus,
            code_changes=changes,
            context_summary=summary
        )
        
        # Load existing snapshots
        snapshots = self._load_conversations()
        snapshots.append(asdict(snapshot))
        
        # Keep last 20 snapshots
        if len(snapshots) > 20:
            snapshots = snapshots[-20:]
        
        with open(self.conversations_file, 'w') as f:
            json.dump(snapshots, f, indent=2)
        
        print(f"✅ Conversation snapshot created: {session_id}")
    
    def generate_handover_context(self) -> Dict[str, Any]:
        """Generate comprehensive handover context for new AI"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "session_summary": self._create_session_summary(),
            "recent_decisions": self._get_recent_decisions(5),
            "conversation_flow": self._get_conversation_flow(),
            "next_priorities": self._extract_next_priorities(),
            "vibecoder_alignment_status": self._check_vibecoder_alignment(),
            "context_compression": self._compress_context(),
            "smart_compression_summary": self._get_smart_compression_summary()
        }
        
        # Save compressed context
        with open(self.compressed_context_file, 'w') as f:
            json.dump(context, f, indent=2)
        
        return context
    
    def get_decision_tree(self) -> Dict[str, Any]:
        """Get decision tree for current session"""
        decisions = self._load_decisions()
        recent_decisions = decisions[-10:] if len(decisions) > 10 else decisions
        
        tree = {
            "total_decisions": len(decisions),
            "recent_decisions": recent_decisions,
            "decision_patterns": self._analyze_decision_patterns(decisions),
            "vibecoder_alignment_score": self._calculate_alignment_score(decisions)
        }
        
        return tree
    
    def _load_decisions(self) -> List[Dict]:
        """Load existing decisions"""
        if not self.decisions_file.exists():
            return []
        
        try:
            with open(self.decisions_file) as f:
                return json.load(f)
        except:
            return []
    
    def _load_conversations(self) -> List[Dict]:
        """Load existing conversation snapshots"""
        if not self.conversations_file.exists():
            return []
        
        try:
            with open(self.conversations_file) as f:
                return json.load(f)
        except:
            return []
    
    def _create_session_summary(self) -> str:
        """Create summary of current session"""
        conversations = self._load_conversations()
        if not conversations:
            return "No previous session data available"
        
        latest = conversations[-1]
        return f"Last session focused on: {latest.get('vibecoder_focus', 'unknown')}. " \
               f"Key topics: {', '.join(latest.get('key_topics', [])[:3])}. " \
               f"Next actions: {', '.join(latest.get('next_actions', [])[:2])}"
    
    def _get_recent_decisions(self, count: int = 5) -> List[Dict]:
        """Get recent decisions with impact"""
        decisions = self._load_decisions()
        return decisions[-count:] if len(decisions) > count else decisions
    
    def _get_conversation_flow(self) -> List[str]:
        """Get conversation flow summary"""
        conversations = self._load_conversations()
        if not conversations:
            return ["No conversation history available"]
        
        flow = []
        for conv in conversations[-5:]:  # Last 5 conversations
            topic_summary = f"{conv.get('timestamp', '')[:10]}: {conv.get('vibecoder_focus', 'Unknown')}"
            flow.append(topic_summary)
        
        return flow
    
    def _extract_next_priorities(self) -> List[str]:
        """Extract next priorities from conversation history"""
        conversations = self._load_conversations()
        if not conversations:
            return ["Check current roadmap with 'make roadmap'"]
        
        # Get next actions from recent conversations
        next_actions = []
        for conv in conversations[-3:]:
            next_actions.extend(conv.get('next_actions', []))
        
        # Remove duplicates and limit
        unique_actions = list(dict.fromkeys(next_actions))
        return unique_actions[:5]
    
    def _check_vibecoder_alignment(self) -> Dict[str, Any]:
        """Check current Vibecoder alignment status"""
        decisions = self._load_decisions()
        if not decisions:
            return {"status": "unknown", "aligned_decisions": 0, "total_decisions": 0}
        
        aligned = sum(1 for d in decisions if d.get('vibecoder_alignment', False))
        total = len(decisions)
        
        return {
            "status": "aligned" if aligned/total > 0.8 else "check_needed",
            "aligned_decisions": aligned,
            "total_decisions": total,
            "alignment_percentage": round((aligned/total)*100, 1) if total > 0 else 0
        }
    
    def _compress_context(self) -> Dict[str, Any]:
        """Compress context for efficient handover"""
        conversations = self._load_conversations()
        decisions = self._load_decisions()
        
        # Extract key themes
        all_topics = []
        all_focuses = []
        
        for conv in conversations:
            all_topics.extend(conv.get('key_topics', []))
            all_focuses.append(conv.get('vibecoder_focus', ''))
        
        # Count frequencies
        topic_freq = {}
        for topic in all_topics:
            topic_freq[topic] = topic_freq.get(topic, 0) + 1
        
        focus_freq = {}
        for focus in all_focuses:
            if focus:
                focus_freq[focus] = focus_freq.get(focus, 0) + 1
        
        return {
            "dominant_topics": sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:5],
            "primary_focus_areas": sorted(focus_freq.items(), key=lambda x: x[1], reverse=True)[:3],
            "total_conversations": len(conversations),
            "total_decisions": len(decisions)
        }
    
    def _analyze_decision_patterns(self, decisions: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in decision making"""
        if not decisions:
            return {"patterns": [], "trends": "No data"}
        
        # Analyze decision types
        impact_counts = {}
        alignment_trend = []
        
        for decision in decisions:
            impact = decision.get('impact', 'unknown')
            impact_counts[impact] = impact_counts.get(impact, 0) + 1
            alignment_trend.append(decision.get('vibecoder_alignment', False))
        
        return {
            "impact_distribution": impact_counts,
            "vibecoder_alignment_trend": alignment_trend[-10:],  # Last 10 decisions
            "decision_frequency": "high" if len(decisions) > 20 else "moderate" if len(decisions) > 10 else "low"
        }
    
    def _calculate_alignment_score(self, decisions: List[Dict]) -> float:
        """Calculate Vibecoder alignment score"""
        if not decisions:
            return 0.0
        
        aligned_count = sum(1 for d in decisions if d.get('vibecoder_alignment', False))
        return round((aligned_count / len(decisions)) * 100, 1)
    
    def _get_smart_compression_summary(self) -> Dict[str, Any]:
        """Get smart compression summary from VIB-010 system"""
        try:
            from .context_compression import VibecoderContextCompressor
            compressor = VibecoderContextCompressor(str(self.project_path))
            return compressor.get_compressed_context_summary(max_chunks=5)
        except Exception as e:
            return {"error": f"Could not get compression summary: {str(e)}"}


# Integration with existing handover system
def enhance_handover_with_context(project_path: str) -> None:
    """Enhance existing handover document with advanced context"""
    context_manager = EnhancedContextManager(project_path)
    
    # Generate comprehensive context
    enhanced_context = context_manager.generate_handover_context()
    
    # Update existing handover system
    from .handover_updater import update_handover_document
    update_handover_document(project_path)
    
    print("✅ Enhanced context integration completed")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        manager = EnhancedContextManager(project_path)
        
        if len(sys.argv) > 2:
            command = sys.argv[2]
            
            if command == "decision":
                # Record a decision
                context = input("Decision context: ")
                options = input("Options (comma-separated): ").split(',')
                chosen = input("Chosen option: ")
                reasoning = input("Reasoning: ")
                
                manager.record_decision(context.strip(), [opt.strip() for opt in options], 
                                      chosen.strip(), reasoning.strip())
            
            elif command == "snapshot":
                # Create conversation snapshot
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M')}"
                topics = input("Key topics (comma-separated): ").split(',')
                decisions = input("Decisions made (comma-separated): ").split(',')
                next_actions = input("Next actions (comma-separated): ").split(',')
                focus = input("Vibecoder focus: ")
                changes = input("Code changes (comma-separated): ").split(',')
                summary = input("Session summary: ")
                
                manager.create_conversation_snapshot(
                    session_id, [t.strip() for t in topics], [d.strip() for d in decisions],
                    [a.strip() for a in next_actions], focus.strip(), 
                    [c.strip() for c in changes], summary.strip()
                )
            
            elif command == "context":
                # Generate handover context
                context = manager.generate_handover_context()
                print(json.dumps(context, indent=2))
            
            elif command == "tree":
                # Show decision tree
                tree = manager.get_decision_tree()
                print(json.dumps(tree, indent=2))
        
        else:
            # Default: enhance handover
            enhance_handover_with_context(project_path)
    
    else:
        print("Usage: python enhanced_context.py <project_path> [decision|snapshot|context|tree]")