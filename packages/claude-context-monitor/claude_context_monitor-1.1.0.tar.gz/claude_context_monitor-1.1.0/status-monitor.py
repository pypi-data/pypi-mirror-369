#!/usr/bin/env python3
"""
Real-time status line monitor for Claude Code
Shows current context usage in the status bar
"""

import json
import os
import sys
from pathlib import Path


# Determine project root dynamically
def find_project_root():
    """Find the project root by looking for .claude directory"""
    current = Path(__file__).parent.parent  # Start from script's parent's parent

    # If this script is in .claude/, the parent should be project root
    if current.name != ".claude":
        # Look for .claude directory in current path
        for parent in [Path.cwd()] + list(Path.cwd().parents):
            if (parent / ".claude").exists():
                return parent

    return current


PROJECT_ROOT = find_project_root()


def get_context_usage():
    """Get current context usage from Claude JSONL files"""
    try:
        claude_projects_dir = Path.home() / ".claude" / "projects"

        # Find project session directory
        current_project = str(PROJECT_ROOT).replace("/", "-").replace(".", "-")
        project_session_dir = claude_projects_dir / current_project

        # Fallback: search by project name
        if not project_session_dir.exists():
            project_name = PROJECT_ROOT.name
            for dir_path in claude_projects_dir.glob(f"*{project_name}*"):
                if dir_path.is_dir():
                    project_session_dir = dir_path
                    break

        if not project_session_dir.exists():
            return {"usage_percent": 0, "tokens_used": 0, "max_tokens": 600000}

        # Get most recent session file
        jsonl_files = sorted(
            project_session_dir.glob("*.jsonl"),
            key=lambda x: x.stat().st_atime,
            reverse=True,
        )

        if not jsonl_files:
            return {"usage_percent": 0, "tokens_used": 0, "max_tokens": 600000}

        recent_file = jsonl_files[0]

        # Get plan-specific token limits with intelligent detection
        claude_plan = os.environ.get("CLAUDE_PLAN", "").lower()

        if not claude_plan or claude_plan == "auto":
            # Use intelligent plan detection but with realistic effective limits
            try:
                from intelligent_plan_detector import detect_claude_plan

                detection_result = detect_claude_plan(PROJECT_ROOT)
                if detection_result["confidence"] >= 0.7:  # High confidence threshold
                    claude_plan = detection_result["detected_plan"]
                    max_tokens = detection_result["token_limit"]
                else:
                    # Fallback to conservative Pro limits
                    claude_plan = "pro"
                    max_tokens = 200000
            except ImportError:
                claude_plan = "pro"
                max_tokens = 200000
        else:
            # Use manually specified plan
            token_limits = {
                "pro": 200000,
                "max": 600000,
                "max5": 600000,
                "max20": 600000,
                "custom": int(os.environ.get("CLAUDE_MAX_TOKENS", 200000)),
            }
            max_tokens = token_limits.get(claude_plan, 200000)

        # Read recent token usage
        with open(recent_file, "r") as f:
            lines = f.readlines()

        # Get the ACTUAL current context from the latest entry
        current_context = 0
        has_recent_usage = False
        
        # Only look at very recent entries (last 3 lines) for fresh session detection
        for line in reversed(lines[-3:]):  # Last 3 entries
            if line.strip():
                try:
                    entry = json.loads(line.strip())
                    if "message" in entry and isinstance(entry["message"], dict):
                        usage = entry["message"].get("usage", {})
                        if usage and (usage.get("input_tokens", 0) > 0 or usage.get("output_tokens", 0) > 0):
                            input_t = usage.get("input_tokens", 0)
                            output_t = usage.get("output_tokens", 0)
                            cache_read = usage.get("cache_read_input_tokens", 0)
                            cache_create = usage.get("cache_creation_input_tokens", 0)
                            
                            current_context = (
                                input_t + output_t + cache_read + cache_create
                            )
                            has_recent_usage = True
                            break  # Use the most recent entry
                except:
                    continue
        
        # If no recent usage found in current file, this might be a fresh session
        if not has_recent_usage and len(lines) < 10:  # Small file = likely fresh session
            current_context = 10  # Very minimal baseline for fresh sessions

        # Use actual context size
        estimated_context = current_context if current_context > 0 else 10
        usage_percent = (estimated_context / max_tokens) * 100

        return {
            "usage_percent": min(usage_percent, 99.9),
            "tokens_used": estimated_context,
            "max_tokens": max_tokens,
        }

    except Exception:
        # Default fallback
        max_tokens = (
            600000 if os.environ.get("CLAUDE_PLAN", "pro").lower() == "max" else 200000
        )
        return {"usage_percent": 0, "tokens_used": 0, "max_tokens": max_tokens}


def format_status():
    """Format status line output"""
    usage = get_context_usage()

    usage_pct = usage["usage_percent"]
    tokens_used = usage["tokens_used"]
    max_tokens = usage["max_tokens"]

    # Color coding for usage levels
    if usage_pct >= 90:
        status_icon = "🔴"
        urgency = "CRITICAL"
    elif usage_pct >= 75:
        status_icon = "🟡"
        urgency = "HIGH"
    elif usage_pct >= 50:
        status_icon = "🟢"
        urgency = "OK"
    else:
        status_icon = "🔵"
        urgency = "LOW"

    # Format tokens with K/M suffix
    def format_tokens(count):
        if count >= 1000000:
            return f"{count / 1000000:.1f}M"
        elif count >= 1000:
            return f"{count / 1000:.0f}K"
        else:
            return str(count)

    tokens_display = f"{format_tokens(tokens_used)}/{format_tokens(max_tokens)}"

    # Status line format
    plan = os.environ.get("CLAUDE_PLAN", "pro").upper()

    return f"{status_icon} {usage_pct:.1f}% ({tokens_display}) [{plan}] {urgency}"


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON output for programmatic use
        usage = get_context_usage()
        print(json.dumps(usage))
    else:
        # Human-readable status line
        print(format_status())


if __name__ == "__main__":
    main()
