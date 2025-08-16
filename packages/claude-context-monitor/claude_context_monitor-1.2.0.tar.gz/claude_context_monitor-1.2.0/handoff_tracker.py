#!/usr/bin/env python3
"""
Handoff Context Tracker
Integrates with existing /handoff command to record context percentages for adaptive thresholds
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def get_current_context_usage():
    """Get current context usage using existing status monitoring logic"""
    try:
        # Import our context usage function
        claude_dir = Path(__file__).parent
        sys.path.insert(0, str(claude_dir))
        
        # Import our enhanced status module
        import importlib.util
        spec = importlib.util.spec_from_file_location("enhanced_status", claude_dir / "enhanced-status.py")
        enhanced_status = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(enhanced_status)
        
        get_context_usage = enhanced_status.get_context_usage
        
        usage_info = get_context_usage()
        return {
            "usage_percent": usage_info.get("usage_percent", 0),
            "tokens_used": usage_info.get("tokens_used", 0),
            "max_tokens": usage_info.get("max_tokens", 200000),
            "detected_plan": usage_info.get("detected_plan", "pro")
        }
    except Exception as e:
        return {"error": f"Failed to get context usage: {e}"}

def record_handoff():
    """Record handoff context data"""
    try:
        # Get current working directory as project identifier
        project_root = Path.cwd()
        project_name = project_root.name
        
        # Get current context usage
        context_data = get_current_context_usage()
        if "error" in context_data:
            return context_data
        
        # Import intelligent plan detector for handoff recording
        from intelligent_plan_detector import PlanDetector
        
        detector = PlanDetector(project_root)
        detector.record_handoff_context(
            context_percentage=context_data["usage_percent"],
            total_tokens=context_data["tokens_used"],
            project_name=project_name
        )
        
        # Get adaptive threshold info
        adaptive_threshold = detector.get_adaptive_threshold()
        handoff_stats = detector.get_handoff_stats()
        
        return {
            "success": True,
            "recorded": True,
            "context_percentage": round(context_data["usage_percent"], 1),
            "total_tokens": context_data["tokens_used"],
            "max_tokens": context_data["max_tokens"],
            "project": project_name,
            "adaptive_threshold": adaptive_threshold,
            "handoff_count": handoff_stats.get("handoff_count", 0),
            "avg_handoff_percentage": handoff_stats.get("avg_handoff_percentage"),
            "previous_threshold": float(os.environ.get('CONTEXT_THRESHOLD', 90))
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

def get_handoff_summary():
    """Get summary of handoff tracking for inclusion in handoff documents"""
    try:
        result = record_handoff()
        
        if not result.get("success", False):
            return f"\n## Context Tracking\n❌ Failed to record handoff: {result.get('error', 'Unknown error')}\n"
        
        # Format context info for handoff document
        context_info = f"""
## Context Usage at Handoff
- **Current Usage**: {result['context_percentage']}% ({result['total_tokens']:,} tokens)
- **Token Limit**: {result['max_tokens']:,} tokens  
- **Project**: {result['project']}

## Adaptive Threshold Learning
- **Current Threshold**: {result['previous_threshold']}%
- **Adaptive Threshold**: {result['adaptive_threshold']}%
- **Handoff Count**: {result['handoff_count']}"""
        
        if result.get('avg_handoff_percentage'):
            context_info += f"\n- **Average Handoff %**: {result['avg_handoff_percentage']:.1f}%"
            
        context_info += f"""

*🤖 This handoff was recorded at {result['context_percentage']}% context usage to help calibrate automatic context management thresholds.*
"""
        
        return context_info
        
    except Exception as e:
        return f"\n## Context Tracking\n❌ Error: {str(e)}\n"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--record":
            result = record_handoff()
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "--summary":
            print(get_handoff_summary())
        elif sys.argv[1] == "--context":
            context = get_current_context_usage()
            print(json.dumps(context, indent=2))
    else:
        # Default: record handoff and show user-friendly output
        result = record_handoff()
        if result.get("success"):
            print(f"🎯 Handoff recorded at {result['context_percentage']}% context usage")
            print(f"📊 Tokens: {result['total_tokens']:,} / {result['max_tokens']:,}")
            print(f"🔧 Adaptive threshold: {result['adaptive_threshold']}%")
            if result['handoff_count'] > 1:
                print(f"📈 Historical average: {result.get('avg_handoff_percentage', 0):.1f}% ({result['handoff_count']} handoffs)")
        else:
            print(f"❌ Failed to record handoff: {result.get('error')}")