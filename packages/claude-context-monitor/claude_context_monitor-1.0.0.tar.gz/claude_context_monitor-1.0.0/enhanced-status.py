#!/usr/bin/env python3
"""
Enhanced status line for Claude Code with multiple info modes
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# Determine project root dynamically
def find_project_root():
    """Find the project root by looking for .claude directory"""
    current = Path(__file__).parent.parent  # Start from script's parent's parent
    
    # If this script is in .claude/, the parent should be project root
    if current.name != '.claude':
        # Look for .claude directory in current path
        for parent in [Path.cwd()] + list(Path.cwd().parents):
            if (parent / '.claude').exists():
                return parent
    
    return current

PROJECT_ROOT = find_project_root()

def get_git_info():
    """Get current git branch and status"""
    try:
        # Determine the correct working directory
        git_cwd = PROJECT_ROOT
        
        # Fallback: if PROJECT_ROOT doesn't have .git, use current working directory
        if not (git_cwd / '.git').exists() and (Path.cwd() / '.git').exists():
            git_cwd = Path.cwd()
        
        # Get current branch with multiple fallback methods
        branch = "unknown"
        for cmd in [["git", "branch", "--show-current"], ["git", "rev-parse", "--abbrev-ref", "HEAD"]]:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=git_cwd,
                    timeout=2,  # Add timeout to prevent hanging
                )
                if result.returncode == 0 and result.stdout.strip():
                    branch = result.stdout.strip()
                    break
            except (subprocess.TimeoutExpired, OSError):
                continue

        # Get status
        dirty = False
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=git_cwd,
                timeout=2,
            )
            dirty = len(result.stdout.strip()) > 0 if result.returncode == 0 else False
        except (subprocess.TimeoutExpired, OSError):
            pass

        return {"branch": branch, "dirty": dirty}
    except Exception:
        return {"branch": "unknown", "dirty": False}

def get_context_usage():
    """Get context usage (reusing logic from status-monitor.py)"""
    try:
        claude_projects_dir = Path.home() / ".claude" / "projects"
        
        current_project = str(PROJECT_ROOT).replace('/', '-').replace('.', '-')
        project_session_dir = claude_projects_dir / current_project
        
        if not project_session_dir.exists():
            project_name = PROJECT_ROOT.name
            for dir_path in claude_projects_dir.glob(f"*{project_name}*"):
                if dir_path.is_dir():
                    project_session_dir = dir_path
                    break
        
        if not project_session_dir.exists():
            return {"usage_percent": 0, "tokens_used": 0}
        
        jsonl_files = sorted(project_session_dir.glob("*.jsonl"), 
                           key=lambda x: x.stat().st_atime, reverse=True)
        
        if not jsonl_files:
            return {"usage_percent": 0, "tokens_used": 0}
        
        recent_file = jsonl_files[0]
        
        with open(recent_file, 'r') as f:
            lines = f.readlines()
        
        # Get the ACTUAL current context from the latest entry
        current_context = 0
        has_recent_usage = False
        
        # Only look at very recent entries (last 3 lines) for fresh session detection
        for line in reversed(lines[-3:]):
            if line.strip():
                try:
                    entry = json.loads(line.strip())
                    if 'message' in entry and isinstance(entry['message'], dict):
                        usage = entry['message'].get('usage', {})
                        if usage and (usage.get('input_tokens', 0) > 0 or usage.get('output_tokens', 0) > 0):
                            input_t = usage.get('input_tokens', 0)
                            output_t = usage.get('output_tokens', 0)
                            cache_read = usage.get('cache_read_input_tokens', 0)
                            cache_create = usage.get('cache_creation_input_tokens', 0)
                            
                            current_context = input_t + output_t + cache_read + cache_create
                            has_recent_usage = True
                            break  # Use the most recent entry
                except:
                    continue
        
        # If no recent usage found in current file, this might be a fresh session
        if not has_recent_usage and len(lines) < 10:  # Small file = likely fresh session
            current_context = 10  # Very minimal baseline for fresh sessions
        
        # Get plan limits with intelligent detection
        # Note: Using smaller effective limits that match Claude Code's auto-compact behavior
        claude_plan = os.environ.get('CLAUDE_PLAN', '').lower()
        
        if not claude_plan or claude_plan == 'auto':
            # Use intelligent plan detection but with realistic effective limits
            try:
                from intelligent_plan_detector import detect_claude_plan
                detection_result = detect_claude_plan(PROJECT_ROOT)
                if detection_result['confidence'] >= 0.7:  # High confidence threshold
                    claude_plan = detection_result['detected_plan']
                    if claude_plan == 'max':
                        max_tokens = detection_result['token_limit']
                    else:
                        max_tokens = detection_result['token_limit']
                else:
                    # Fallback to conservative Pro limits
                    claude_plan = 'pro'
                    max_tokens = 200000
            except ImportError:
                claude_plan = 'pro'
                max_tokens = 200000
        else:
            # Use manually specified plan
            token_limits = {
                'pro': 200000,
                'max': 600000,
                'max5': 600000,
                'max20': 600000,
                'custom': int(os.environ.get('CLAUDE_MAX_TOKENS', 200000))
            }
            max_tokens = token_limits.get(claude_plan, 200000)
        
        # Use actual context size  
        estimated_context = current_context if current_context > 0 else 10
        usage_percent = (estimated_context / max_tokens) * 100
        
        return {
            "usage_percent": min(usage_percent, 99.9),
            "tokens_used": estimated_context,
            "detected_plan": claude_plan,
            "max_tokens": max_tokens
        }
        
    except Exception:
        return {"usage_percent": 0, "tokens_used": 0}

def format_compact_status():
    """Compact status line format - Starship-inspired"""
    usage = get_context_usage()
    git = get_git_info()
    
    usage_pct = usage["usage_percent"]
    current_dir = os.path.basename(os.getcwd())
    
    # Status indicators with Starship-like symbols
    if usage_pct >= 90:
        ctx_icon = "🔴"
    elif usage_pct >= 75:
        ctx_icon = "🟡"
    elif usage_pct >= 50:
        ctx_icon = "🟢"
    else:
        ctx_icon = "🔵"
    
    # Git status with cleaner symbols
    git_symbol = "🌿±" if git["dirty"] else "🌿"
    detected_plan = usage.get('detected_plan', 'pro')
    plan_symbol = "🎯" + detected_plan[0].upper()
    
    return f"📁{current_dir} │ {ctx_icon}{usage_pct:.0f}% │ {git_symbol}{git['branch']} │ {plan_symbol}"

def format_detailed_status():
    """Detailed status line format - Starship-inspired"""
    usage = get_context_usage()
    git = get_git_info()
    
    usage_pct = usage["usage_percent"]
    tokens_used = usage["tokens_used"]
    
    # Format tokens
    def fmt_tokens(count):
        if count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.0f}K"
        else:
            return str(count)
    
    # Get plan from the context usage function which handles intelligent detection
    usage_info = get_context_usage()
    plan = usage_info.get('detected_plan', 'pro').upper()
    max_tokens = usage_info.get('max_tokens', 200000)
    
    # Get current directory for shell-like prompt feeling
    current_dir = os.path.basename(os.getcwd())
    username = os.environ.get('USER', 'user')
    
    # Context status with color-coding
    if usage_pct >= 90:
        ctx_status = f"🔴 {usage_pct:.1f}%"
    elif usage_pct >= 75:
        ctx_status = f"🟡 {usage_pct:.1f}%"
    elif usage_pct >= 50:
        ctx_status = f"🟢 {usage_pct:.1f}%"
    else:
        ctx_status = f"🔵 {usage_pct:.1f}%"
    
    # Git status with Starship-like styling
    if git["dirty"]:
        git_status = f"🌿{git['branch']} ±"
    else:
        git_status = f"🌿{git['branch']}"
    
    # Add adaptive threshold indicator if different from default
    try:
        from intelligent_plan_detector import PlanDetector
        detector = PlanDetector(PROJECT_ROOT)
        adaptive_threshold = detector.get_adaptive_threshold()
        default_threshold = float(os.environ.get('CONTEXT_THRESHOLD', 90))
        
        if abs(adaptive_threshold - default_threshold) > 1.0:  # Show if significantly different
            threshold_indicator = f" (→{adaptive_threshold:.0f}%)"
        else:
            threshold_indicator = ""
    except:
        threshold_indicator = ""
    
    # Shell-inspired format: user@host:dir | context | git | plan [adaptive threshold]
    return f"💻 {username}:{current_dir} │ {ctx_status} ({fmt_tokens(tokens_used)}) │ {git_status} │ 🎯{plan}{threshold_indicator}"

def main():
    """Main entry point"""
    mode = sys.argv[1] if len(sys.argv) > 1 else "compact"
    
    if mode == "detailed":
        print(format_detailed_status())
    elif mode == "compact":
        print(format_compact_status())
    elif mode == "json":
        usage = get_context_usage()
        git = get_git_info()
        data = {**usage, **git, "plan": usage.get('detected_plan', 'pro')}
        print(json.dumps(data))
    else:
        print(format_compact_status())

if __name__ == "__main__":
    main()