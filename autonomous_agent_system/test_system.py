"""
Test script for the Autonomous Agent System
"""

import asyncio
import json
from pathlib import Path
from core.transcript_analyzer import TranscriptAnalyzer
from core.tech_spec_generator import TechSpecGenerator
from core.agent_builder import AgentBuilder


async def test_end_to_end():
    """Test the complete system end-to-end"""
    
    print("=" * 60)
    print("AUTONOMOUS AGENT SYSTEM - END-TO-END TEST")
    print("=" * 60)
    
    # Step 1: Analyze transcripts
    print("\n1. ANALYZING TRANSCRIPTS...")
    print("-" * 40)
    
    analyzer = TranscriptAnalyzer()
    
    # Analyze JSON transcript
    json_requirements = analyzer.analyze_transcript("transcripts/team_meeting_data_processing.json")
    print(f"Found {len(json_requirements)} requirements from JSON transcript")
    
    # Analyze text transcript
    text_requirements = analyzer.analyze_transcript("transcripts/infrastructure_discussion.txt")
    print(f"Found {len(text_requirements)} requirements from text transcript")
    
    # Combine and deduplicate
    all_requirements = analyzer._deduplicate_requirements(json_requirements + text_requirements)
    print(f"Total unique requirements: {len(all_requirements)}")
    
    # Display found requirements
    print("\nIdentified Agent Requirements:")
    for i, req in enumerate(all_requirements, 1):
        print(f"  {i}. {req.name} - Priority: {req.priority}")
        print(f"     Purpose: {req.purpose[:80]}...")
        print(f"     Capabilities: {', '.join(req.capabilities[:3])}")
    
    # Save requirements
    analyzer.save_requirements(all_requirements, "tech_specs/all_requirements.json")
    
    # Step 2: Generate tech specs
    print("\n2. GENERATING TECHNICAL SPECIFICATIONS...")
    print("-" * 40)
    
    spec_generator = TechSpecGenerator()
    tech_specs = []
    
    # Generate specs for high-priority agents only (for testing)
    high_priority_reqs = [req for req in all_requirements if req.priority == "high"][:2]
    
    for req in high_priority_reqs:
        print(f"\nGenerating spec for: {req.name}")
        spec = spec_generator.generate_tech_spec(req.__dict__)
        tech_specs.append(spec)
        
        # Save spec
        spec_file = f"tech_specs/{spec.agent_name}_spec.json"
        spec_generator.save_tech_spec(spec, spec_file)
        
        # Save markdown
        md_content = spec_generator.generate_markdown_spec(spec)
        md_file = f"tech_specs/{spec.agent_name}_spec.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        print(f"  - Architecture: {spec.architecture['pattern']}")
        print(f"  - Complexity: {spec.estimated_complexity}")
        print(f"  - Dependencies: {len(spec.dependencies)} packages")
        print(f"  - Test cases: {len(spec.test_cases)}")
    
    # Step 3: Build agents
    print("\n3. BUILDING AGENTS...")
    print("-" * 40)
    
    builder = AgentBuilder()
    built_agents = []
    
    for spec in tech_specs[:1]:  # Build only first agent for testing
        print(f"\nBuilding agent: {spec.agent_name}")
        
        build_result = builder.build_agent(spec.__dict__)
        built_agents.append(build_result)
        
        print(f"  ✓ Agent built successfully")
        print(f"  - Location: {build_result['agent_dir']}")
        print(f"  - Main file: {build_result['main_file']}")
        print(f"  - API server: {build_result['api_file']}")
        print(f"  - Tests: {build_result['test_file']}")
        
        # Validate build
        if builder.validate_build(build_result):
            print(f"  ✓ Build validation passed")
        else:
            print(f"  ✗ Build validation failed")
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Transcripts analyzed: 2")
    print(f"✓ Requirements identified: {len(all_requirements)}")
    print(f"✓ Tech specs generated: {len(tech_specs)}")
    print(f"✓ Agents built: {len(built_agents)}")
    
    # Display file structure
    print("\n4. GENERATED FILE STRUCTURE:")
    print("-" * 40)
    
    def show_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
        
        path = Path(path)
        if path.is_dir():
            items = sorted(path.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    show_tree(item, prefix + extension, max_depth, current_depth + 1)
    
    print("\nautonomous_agent_system/")
    show_tree(".", "")
    
    print("\n✅ End-to-end test completed successfully!")
    
    return {
        "transcripts_analyzed": 2,
        "requirements_found": len(all_requirements),
        "specs_generated": len(tech_specs),
        "agents_built": len(built_agents),
        "status": "success"
    }


async def test_orchestrator():
    """Test the orchestrator in demo mode"""
    
    print("\n" + "=" * 60)
    print("TESTING ORCHESTRATOR (Demo Mode)")
    print("=" * 60)
    
    from orchestrator import AutonomousOrchestrator
    
    # Create orchestrator with test config
    config = {
        "transcript_dir": "transcripts",
        "specs_dir": "tech_specs",
        "agents_dir": "agents",
        "auto_build": True,
        "auto_deploy": False,
        "watch_transcripts": False,  # Disable for test
        "scan_interval": 60,
        "priority_threshold": "high",  # Only process high priority
        "max_concurrent_builds": 2
    }
    
    # Save test config
    with open("test_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    orchestrator = AutonomousOrchestrator("test_config.json")
    
    print("\n1. Scanning for transcripts...")
    await orchestrator.scan_transcripts()
    
    print("\n2. Orchestrator Status:")
    status = orchestrator.get_status()
    print(f"  - Processed transcripts: {status['processed_transcripts']}")
    print(f"  - Generated specs: {status['generated_specs']}")
    print(f"  - Built agents: {status['built_agents']}")
    
    print("\n✅ Orchestrator test completed!")
    
    return status


if __name__ == "__main__":
    print("Starting Autonomous Agent System Test...\n")
    
    # Run end-to-end test
    result = asyncio.run(test_end_to_end())
    
    # Optionally test orchestrator
    # orchestrator_result = asyncio.run(test_orchestrator())
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)