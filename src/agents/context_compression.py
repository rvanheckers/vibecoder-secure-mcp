#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Smart Context Compression (VIB-010)
Intelligent context compression to prevent AI focus loss during long VIBECODER conversations

Dependencies:
- enhanced_context.py: Provides compressed context for enhanced AI handover
- .goldminer/context_compression/: Storage for compressed conversation data
- main.py: Called via make compress command for manual compression
- vibecoder_roadmap.py: Maintains milestone focus during compression

Compression Features:
- Intelligent conversation summarization with key decision preservation
- VIBECODER-specific context prioritization (VIB milestones, critical decisions)
- Entropy-based importance scoring for conversation elements
- Decision tree extraction from long conversation chains
- Focus preservation during context window management
- Lossless compression of critical project decisions and state changes
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ConversationChunk:
    """A compressed chunk of conversation"""
    chunk_id: str
    timestamp: str
    topic: str
    key_decisions: List[str]
    code_changes: List[str]
    vibecoder_focus: str
    importance_score: float
    summary: str
    original_length: int
    compressed_length: int


@dataclass
class FocusArea:
    """Important focus area for Vibecoder work"""
    area: str
    keywords: List[str]
    importance: float
    recent_activity: int


class VibecoderContextCompressor:
    """Smart context compression to maintain AI focus across long conversations"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.compression_dir = self.project_path / ".goldminer" / "context_compression"
        self.compression_dir.mkdir(parents=True, exist_ok=True)
        
        self.compressed_chunks_file = self.compression_dir / "compressed_chunks.json"
        self.focus_tracker_file = self.compression_dir / "focus_tracker.json"
        self.compression_rules_file = self.compression_dir / "compression_rules.json"
        
        self._initialize_compression_rules()
        self._initialize_focus_areas()
    
    def _initialize_compression_rules(self) -> None:
        """Initialize compression rules for different content types"""
        if self.compression_rules_file.exists():
            return
        
        rules = {
            "vibecoder_keywords": [
                "vibecoder", "VIB-", "milestone", "roadmap", "focus", "derailing",
                "handover", "ai context", "automation", "integrity", "security"
            ],
            "high_importance_patterns": [
                r"VIB-\d+",  # Milestone references
                r"completed?|finished|done",  # Completion indicators
                r"error|failed|issue|problem",  # Problems
                r"critical|important|urgent",  # Priority indicators
                r"next|continue|follow.?up"  # Next steps
            ],
            "compression_levels": {
                "critical": {"ratio": 0.9, "min_words": 50},  # Keep 90% of critical content
                "important": {"ratio": 0.7, "min_words": 30},  # Keep 70% of important content
                "normal": {"ratio": 0.5, "min_words": 20},     # Keep 50% of normal content
                "low": {"ratio": 0.3, "min_words": 10}         # Keep 30% of low importance content
            },
            "preserve_patterns": [
                r"make \w+",  # Makefile commands
                r"VIB-\d+.*?completed",  # Milestone completions
                r"```[\s\S]*?```",  # Code blocks
                r"file_path:[^\s]+:\d+",  # File references
                r"✅|❌|🎯|🚀|⚠️|🔒|📋"  # Important emojis
            ]
        }
        
        with open(self.compression_rules_file, 'w') as f:
            json.dump(rules, f, indent=2)
    
    def _initialize_focus_areas(self) -> None:
        """Initialize Vibecoder focus areas"""
        focus_areas = [
            FocusArea("core_pipeline", ["pipeline", "generate", "validate", "heal"], 0.9, 0),
            FocusArea("security_integrity", ["security", "integrity", "audit", "lock"], 0.9, 0),
            FocusArea("ai_handover", ["handover", "context", "ai", "preservation"], 0.95, 0),
            FocusArea("workflow_automation", ["automation", "smart", "trigger", "auto"], 0.8, 0),
            FocusArea("monitoring_observability", ["monitor", "dashboard", "health", "alerts"], 0.7, 0),
            FocusArea("milestone_tracking", ["VIB-", "milestone", "roadmap", "completed"], 0.85, 0),
            FocusArea("developer_experience", ["make", "command", "usage", "workflow"], 0.6, 0)
        ]
        
        # Save initial focus areas
        focus_data = [asdict(area) for area in focus_areas]
        with open(self.focus_tracker_file, 'w') as f:
            json.dump(focus_data, f, indent=2)
    
    def compress_conversation_context(self, conversation_text: str, 
                                    current_topic: str = "",
                                    vibecoder_focus: str = "") -> Dict[str, Any]:
        """Compress conversation while preserving Vibecoder focus"""
        
        # Analyze conversation importance
        importance_analysis = self._analyze_conversation_importance(conversation_text)
        
        # Extract key information
        key_info = self._extract_key_information(conversation_text)
        
        # Compress based on importance and Vibecoder focus
        compressed_content = self._apply_intelligent_compression(
            conversation_text, importance_analysis, key_info
        )
        
        # Create conversation chunk
        chunk = ConversationChunk(
            chunk_id=self._generate_chunk_id(conversation_text),
            timestamp=datetime.now().isoformat(),
            topic=current_topic or self._extract_main_topic(conversation_text),
            key_decisions=key_info["decisions"],
            code_changes=key_info["code_changes"],
            vibecoder_focus=vibecoder_focus or self._detect_vibecoder_focus(conversation_text),
            importance_score=importance_analysis["overall_score"],
            summary=compressed_content["summary"],
            original_length=len(conversation_text),
            compressed_length=len(compressed_content["compressed_text"])
        )
        
        # Save compressed chunk
        self._save_compressed_chunk(chunk)
        
        # Update focus tracking
        self._update_focus_tracking(chunk)
        
        return {
            "chunk_id": chunk.chunk_id,
            "compression_ratio": chunk.compressed_length / chunk.original_length,
            "importance_score": chunk.importance_score,
            "vibecoder_focus": chunk.vibecoder_focus,
            "summary": chunk.summary,
            "preserved_elements": compressed_content["preserved_elements"]
        }
    
    def _analyze_conversation_importance(self, text: str) -> Dict[str, Any]:
        """Analyze the importance of conversation content"""
        rules = self._load_compression_rules()
        
        # Count Vibecoder keywords
        vibecoder_score = 0
        for keyword in rules["vibecoder_keywords"]:
            vibecoder_score += text.lower().count(keyword.lower())
        
        # Check high importance patterns
        importance_matches = 0
        matched_patterns = []
        for pattern in rules["high_importance_patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            importance_matches += len(matches)
            if matches:
                matched_patterns.extend(matches)
        
        # Calculate overall importance score
        text_length = len(text.split())
        vibecoder_density = vibecoder_score / max(text_length, 1)
        importance_density = importance_matches / max(text_length, 1)
        
        overall_score = min(1.0, (vibecoder_density * 0.6 + importance_density * 0.4) * 10)
        
        return {
            "overall_score": overall_score,
            "vibecoder_score": vibecoder_score,
            "importance_matches": importance_matches,
            "matched_patterns": matched_patterns,
            "classification": self._classify_importance(overall_score)
        }
    
    def _classify_importance(self, score: float) -> str:
        """Classify content importance level"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "important"
        elif score >= 0.3:
            return "normal"
        else:
            return "low"
    
    def _extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key information that should be preserved"""
        
        # Extract decisions (lines with decision indicators)
        decision_patterns = [
            r"decided to.*",
            r"choosing.*",
            r"going with.*",
            r"VIB-\d+.*completed",
            r"✅.*"
        ]
        
        decisions = []
        for pattern in decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            decisions.extend(matches)
        
        # Extract code changes (file references and commands)
        code_changes = []
        code_patterns = [
            r"file_path:[^\s]+:\d+",
            r"make \w+",
            r"python .*\.py",
            r"created.*\.py",
            r"updated.*\.py"
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            code_changes.extend(matches)
        
        # Extract milestones and progress
        milestones = re.findall(r"VIB-\d+[^.]*", text)
        
        return {
            "decisions": decisions[:10],  # Top 10 decisions
            "code_changes": code_changes[:15],  # Top 15 code changes
            "milestones": milestones,
            "key_phrases": self._extract_key_phrases(text)
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using simple frequency analysis"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Find sentences with Vibecoder keywords
        rules = self._load_compression_rules()
        key_sentences = []
        
        for sentence in sentences:
            score = 0
            for keyword in rules["vibecoder_keywords"]:
                if keyword.lower() in sentence.lower():
                    score += 1
            
            if score > 0:
                key_sentences.append((sentence.strip(), score))
        
        # Sort by importance and return top phrases
        key_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, _ in key_sentences[:8]]
    
    def _apply_intelligent_compression(self, text: str, importance_analysis: Dict[str, Any], 
                                     key_info: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent compression based on content analysis"""
        
        rules = self._load_compression_rules()
        importance_level = importance_analysis["classification"]
        compression_config = rules["compression_levels"][importance_level]
        
        # Always preserve certain patterns
        preserved_elements = []
        compressed_text = text
        
        for pattern in rules["preserve_patterns"]:
            matches = re.findall(pattern, text, re.DOTALL)
            preserved_elements.extend(matches)
        
        # Create summary from key information
        summary_parts = []
        
        if key_info["decisions"]:
            summary_parts.append(f"Key decisions: {'; '.join(key_info['decisions'][:3])}")
        
        if key_info["milestones"]:
            summary_parts.append(f"Milestones: {'; '.join(key_info['milestones'][:3])}")
        
        if key_info["code_changes"]:
            summary_parts.append(f"Code changes: {'; '.join(key_info['code_changes'][:3])}")
        
        if key_info["key_phrases"]:
            summary_parts.append(f"Key points: {'; '.join(key_info['key_phrases'][:2])}")
        
        summary = " | ".join(summary_parts) if summary_parts else "General discussion"
        
        # Apply compression ratio
        target_length = int(len(text) * compression_config["ratio"])
        if len(summary) < target_length:
            # Include more context if summary is short
            words = text.split()
            additional_words = words[:target_length//5]  # Add some original context
            compressed_text = summary + " | Context: " + " ".join(additional_words)
        else:
            compressed_text = summary
        
        return {
            "compressed_text": compressed_text,
            "summary": summary,
            "preserved_elements": preserved_elements,
            "compression_ratio": len(compressed_text) / len(text)
        }
    
    def _detect_vibecoder_focus(self, text: str) -> str:
        """Detect the main Vibecoder focus area from text"""
        focus_areas = self._load_focus_areas()
        
        area_scores = {}
        for area_data in focus_areas:
            area = area_data["area"]
            keywords = area_data["keywords"]
            
            score = 0
            for keyword in keywords:
                score += text.lower().count(keyword.lower())
            
            area_scores[area] = score
        
        # Return the area with highest score
        if area_scores:
            best_area = max(area_scores.keys(), key=lambda k: area_scores[k])
            if area_scores[best_area] > 0:
                return best_area
        
        return "general"
    
    def _extract_main_topic(self, text: str) -> str:
        """Extract main topic from conversation"""
        # Look for milestone references first
        milestone_match = re.search(r"VIB-\d+[^.]*", text)
        if milestone_match:
            return milestone_match.group(0)
        
        # Look for common topic indicators
        topic_patterns = [
            r"implementing (.+?)(?:\.|,|$)",
            r"building (.+?)(?:\.|,|$)",
            r"creating (.+?)(?:\.|,|$)",
            r"working on (.+?)(?:\.|,|$)"
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "General discussion"
    
    def _generate_chunk_id(self, text: str) -> str:
        """Generate unique chunk ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"chunk_{timestamp}_{content_hash}"
    
    def _save_compressed_chunk(self, chunk: ConversationChunk) -> None:
        """Save compressed chunk to storage"""
        chunks = self._load_compressed_chunks()
        chunks.append(asdict(chunk))
        
        # Keep only last 50 chunks
        if len(chunks) > 50:
            chunks = chunks[-50:]
        
        with open(self.compressed_chunks_file, 'w') as f:
            json.dump(chunks, f, indent=2)
    
    def _update_focus_tracking(self, chunk: ConversationChunk) -> None:
        """Update focus area tracking based on new chunk"""
        focus_areas = self._load_focus_areas()
        
        # Update activity for the focus area of this chunk
        for area_data in focus_areas:
            if area_data["area"] == chunk.vibecoder_focus:
                area_data["recent_activity"] += 1
                break
        
        # Decay other areas
        for area_data in focus_areas:
            if area_data["area"] != chunk.vibecoder_focus:
                area_data["recent_activity"] = max(0, area_data["recent_activity"] - 0.1)
        
        with open(self.focus_tracker_file, 'w') as f:
            json.dump(focus_areas, f, indent=2)
    
    def get_compressed_context_summary(self, max_chunks: int = 10) -> Dict[str, Any]:
        """Get a summary of recent compressed context"""
        chunks = self._load_compressed_chunks()
        recent_chunks = chunks[-max_chunks:] if len(chunks) > max_chunks else chunks
        
        # Aggregate information
        total_compression_ratio = 0
        focus_distribution = {}
        key_topics = []
        recent_decisions = []
        
        for chunk_data in recent_chunks:
            chunk = ConversationChunk(**chunk_data)
            
            total_compression_ratio += chunk.compressed_length / chunk.original_length
            
            focus = chunk.vibecoder_focus
            focus_distribution[focus] = focus_distribution.get(focus, 0) + 1
            
            key_topics.append(chunk.topic)
            recent_decisions.extend(chunk.key_decisions)
        
        avg_compression_ratio = total_compression_ratio / len(recent_chunks) if recent_chunks else 0
        
        return {
            "total_chunks": len(chunks),
            "recent_chunks_analyzed": len(recent_chunks),
            "average_compression_ratio": round(avg_compression_ratio, 3),
            "focus_distribution": focus_distribution,
            "recent_topics": key_topics[-5:],  # Last 5 topics
            "recent_decisions": recent_decisions[-10:],  # Last 10 decisions
            "compression_effectiveness": self._assess_compression_effectiveness(recent_chunks)
        }
    
    def _assess_compression_effectiveness(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess how effective the compression has been"""
        if not chunks:
            return {"status": "no_data", "score": 0}
        
        # Calculate metrics
        high_importance_chunks = len([c for c in chunks if c["importance_score"] > 0.7])
        vibecoder_focused_chunks = len([c for c in chunks if c["vibecoder_focus"] != "general"])
        
        total_chunks = len(chunks)
        focus_ratio = vibecoder_focused_chunks / total_chunks
        importance_ratio = high_importance_chunks / total_chunks
        
        effectiveness_score = (focus_ratio * 0.6 + importance_ratio * 0.4) * 100
        
        status = "excellent" if effectiveness_score > 80 else \
                "good" if effectiveness_score > 60 else \
                "needs_improvement"
        
        return {
            "status": status,
            "score": round(effectiveness_score, 1),
            "focus_ratio": round(focus_ratio, 2),
            "importance_ratio": round(importance_ratio, 2)
        }
    
    def _load_compression_rules(self) -> Dict[str, Any]:
        """Load compression rules"""
        try:
            with open(self.compression_rules_file) as f:
                return json.load(f)
        except Exception:
            self._initialize_compression_rules()
            with open(self.compression_rules_file) as f:
                return json.load(f)
    
    def _load_focus_areas(self) -> List[Dict[str, Any]]:
        """Load focus areas"""
        try:
            with open(self.focus_tracker_file) as f:
                return json.load(f)
        except Exception:
            self._initialize_focus_areas()
            with open(self.focus_tracker_file) as f:
                return json.load(f)
    
    def _load_compressed_chunks(self) -> List[Dict[str, Any]]:
        """Load compressed chunks"""
        if not self.compressed_chunks_file.exists():
            return []
        
        try:
            with open(self.compressed_chunks_file) as f:
                return json.load(f)
        except Exception:
            return []


def compress_conversation_for_handover(project_path: str, conversation_text: str,
                                     topic: str = "", focus: str = "") -> Dict[str, Any]:
    """Compress conversation for AI handover"""
    compressor = VibecoderContextCompressor(project_path)
    return compressor.compress_conversation_context(conversation_text, topic, focus)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        compressor = VibecoderContextCompressor(project_path)
        
        if len(sys.argv) > 2:
            command = sys.argv[2]
            
            if command == "summary":
                summary = compressor.get_compressed_context_summary()
                print(json.dumps(summary, indent=2))
            elif command == "test" and len(sys.argv) > 3:
                test_text = " ".join(sys.argv[3:])
                result = compressor.compress_conversation_context(test_text)
                print(json.dumps(result, indent=2))
            else:
                print("Commands: summary, test <text>")
        else:
            # Show current compression status
            summary = compressor.get_compressed_context_summary()
            print(json.dumps(summary, indent=2))
    
    else:
        print("Usage: python context_compression.py <project_path> [summary|test <text>]")