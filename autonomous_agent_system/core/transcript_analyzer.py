"""
Transcript Analyzer: Extracts agent requirements from Microsoft Teams transcripts
"""

import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class AgentRequirement:
    name: str
    purpose: str
    capabilities: List[str]
    inputs: List[str]
    outputs: List[str]
    constraints: List[str]
    priority: str
    identified_at: str
    source_transcript: str
    context: str


class TranscriptAnalyzer:
    def __init__(self):
        self.agent_patterns = [
            r"we need (?:an? )?(?:agent|bot|system) (?:that|to) (.+?)(?:\.|$)",
            r"(?:can we|could we|let's) (?:build|create|have) (?:an? )?(?:agent|bot) (?:for|that) (.+?)(?:\.|$)",
            r"(?:agent|bot) should (?:be able to )?(.+?)(?:\.|$)",
            r"automate (?:the )?(.+?)(?:\.|$)",
            r"(?:I wish we had|we should have) (?:something|an? agent) (?:that|to) (.+?)(?:\.|$)"
        ]
        
        self.capability_keywords = [
            "analyze", "process", "generate", "create", "monitor", "track",
            "optimize", "validate", "integrate", "transform", "extract",
            "summarize", "predict", "classify", "detect", "report"
        ]
        
        self.input_keywords = ["data", "file", "document", "report", "log", "metric", "api", "database"]
        self.output_keywords = ["report", "dashboard", "alert", "notification", "summary", "analysis"]

    def analyze_transcript(self, transcript_path: str) -> List[AgentRequirement]:
        """Analyze a Teams transcript to identify agent requirements"""
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        requirements = []
        
        # Try to parse as JSON first (Teams export format)
        try:
            data = json.loads(content)
            if isinstance(data, dict) and 'messages' in data:
                requirements = self._analyze_json_transcript(data, transcript_path)
            else:
                requirements = self._analyze_text_transcript(content, transcript_path)
        except json.JSONDecodeError:
            requirements = self._analyze_text_transcript(content, transcript_path)
        
        return self._deduplicate_requirements(requirements)

    def _analyze_json_transcript(self, data: Dict, source_path: str) -> List[AgentRequirement]:
        """Analyze JSON-formatted Teams transcript"""
        requirements = []
        
        for message in data.get('messages', []):
            text = message.get('content', '')
            timestamp = message.get('timestamp', datetime.now().isoformat())
            sender = message.get('sender', 'Unknown')
            
            agent_needs = self._extract_agent_needs(text)
            for need in agent_needs:
                req = self._create_requirement(
                    need, source_path, f"{sender}: {text[:100]}...", timestamp
                )
                if req:
                    requirements.append(req)
        
        return requirements

    def _analyze_text_transcript(self, content: str, source_path: str) -> List[AgentRequirement]:
        """Analyze plain text transcript"""
        requirements = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            agent_needs = self._extract_agent_needs(line)
            for need in agent_needs:
                context = self._get_context(lines, i)
                req = self._create_requirement(
                    need, source_path, context, datetime.now().isoformat()
                )
                if req:
                    requirements.append(req)
        
        return requirements

    def _extract_agent_needs(self, text: str) -> List[str]:
        """Extract potential agent needs from text"""
        needs = []
        text_lower = text.lower()
        
        for pattern in self.agent_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            needs.extend(matches)
        
        # Look for pain points and automation opportunities
        if any(phrase in text_lower for phrase in ["time consuming", "repetitive", "manual process", "bottleneck"]):
            needs.append(self._extract_pain_point(text))
        
        return [n for n in needs if n]

    def _extract_pain_point(self, text: str) -> str:
        """Extract the specific pain point from text"""
        # Extract the core issue being discussed
        patterns = [
            r"(?:spending too much time on|wasting time with) (.+?)(?:\.|$)",
            r"(?:manual|repetitive) (.+?)(?:\.|$)",
            r"(?:bottleneck in|problem with) (.+?)(?:\.|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        return ""

    def _create_requirement(self, need: str, source: str, context: str, timestamp: str) -> AgentRequirement:
        """Create an AgentRequirement from extracted need"""
        if not need or len(need) < 10:
            return None
        
        # Extract capabilities from the need description
        capabilities = []
        for keyword in self.capability_keywords:
            if keyword in need.lower():
                capabilities.append(keyword)
        
        # If no capabilities found, infer from the need
        if not capabilities:
            capabilities = self._infer_capabilities(need)
        
        # Extract inputs and outputs
        inputs = self._extract_io(need, self.input_keywords)
        outputs = self._extract_io(need, self.output_keywords)
        
        # Generate agent name
        name = self._generate_agent_name(need)
        
        # Determine priority based on context
        priority = self._determine_priority(need, context)
        
        return AgentRequirement(
            name=name,
            purpose=need.capitalize(),
            capabilities=capabilities,
            inputs=inputs or ["data"],
            outputs=outputs or ["results"],
            constraints=self._extract_constraints(need),
            priority=priority,
            identified_at=timestamp,
            source_transcript=os.path.basename(source),
            context=context[:200]
        )

    def _infer_capabilities(self, need: str) -> List[str]:
        """Infer capabilities from the need description"""
        capabilities = []
        
        verb_mapping = {
            "track": ["monitor", "track"],
            "report": ["generate", "report"],
            "check": ["validate", "monitor"],
            "find": ["extract", "analyze"],
            "convert": ["transform", "process"],
            "send": ["integrate", "notify"]
        }
        
        for verb, caps in verb_mapping.items():
            if verb in need.lower():
                capabilities.extend(caps)
        
        return capabilities or ["process"]

    def _extract_io(self, need: str, keywords: List[str]) -> List[str]:
        """Extract inputs or outputs from need description"""
        found = []
        for keyword in keywords:
            if keyword in need.lower():
                found.append(keyword)
        return found

    def _generate_agent_name(self, need: str) -> str:
        """Generate a descriptive name for the agent"""
        # Extract key words
        words = need.split()[:5]
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        key_words = [w for w in words if w.lower() not in stop_words]
        
        if key_words:
            name = "_".join(key_words[:3]).replace("-", "_")
            return f"{name}_agent"
        
        return "custom_agent"

    def _determine_priority(self, need: str, context: str) -> str:
        """Determine priority based on keywords and context"""
        high_priority_words = ["urgent", "critical", "asap", "immediately", "blocking"]
        medium_priority_words = ["important", "needed", "should", "would help"]
        
        combined = (need + " " + context).lower()
        
        if any(word in combined for word in high_priority_words):
            return "high"
        elif any(word in combined for word in medium_priority_words):
            return "medium"
        
        return "low"

    def _extract_constraints(self, need: str) -> List[str]:
        """Extract constraints from the need description"""
        constraints = []
        
        if "real-time" in need.lower() or "realtime" in need.lower():
            constraints.append("real-time processing required")
        
        if "secure" in need.lower() or "privacy" in need.lower():
            constraints.append("security and privacy compliance")
        
        if "scale" in need.lower() or "large" in need.lower():
            constraints.append("must handle large scale data")
        
        if "fast" in need.lower() or "quick" in need.lower():
            constraints.append("performance optimization required")
        
        return constraints

    def _get_context(self, lines: List[str], index: int, window: int = 2) -> str:
        """Get context around a line"""
        start = max(0, index - window)
        end = min(len(lines), index + window + 1)
        return " ".join(lines[start:end])

    def _deduplicate_requirements(self, requirements: List[AgentRequirement]) -> List[AgentRequirement]:
        """Remove duplicate requirements"""
        seen = set()
        unique = []
        
        for req in requirements:
            key = (req.name, req.purpose[:50])
            if key not in seen:
                seen.add(key)
                unique.append(req)
        
        return unique

    def save_requirements(self, requirements: List[AgentRequirement], output_path: str):
        """Save requirements to JSON file"""
        data = [asdict(req) for req in requirements]
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def analyze_directory(self, transcript_dir: str) -> List[AgentRequirement]:
        """Analyze all transcripts in a directory"""
        all_requirements = []
        
        for filename in os.listdir(transcript_dir):
            if filename.endswith(('.txt', '.json', '.log')):
                filepath = os.path.join(transcript_dir, filename)
                requirements = self.analyze_transcript(filepath)
                all_requirements.extend(requirements)
        
        return self._deduplicate_requirements(all_requirements)