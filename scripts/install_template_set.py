#!/usr/bin/env python3
"""
프로젝트별 템플릿 세트 설치 스크립트
.claude/template-sets.yaml에서 정의된 세트를 한번에 설치
"""

import subprocess
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required. Install with: pip install pyyaml")
    exit(1)

SETS_FILE = ".claude/template-sets.yaml"


def load_sets(sets_path: str = None) -> dict:
    """템플릿 세트 정의 로드"""
    if sets_path is None:
        sets_path = SETS_FILE

    path = Path(sets_path)
    if not path.exists():
        print(f"Error: {sets_path} not found")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_set(sets_data: dict, set_name: str, resolved: set = None) -> dict:
    """세트 확장 (extends 처리, 순환 참조 방지)"""
    if resolved is None:
        resolved = set()

    if set_name in resolved:
        return {}  # 순환 참조 방지

    resolved.add(set_name)

    set_def = sets_data.get("sets", {}).get(set_name, {})
    result = {
        "agents": list(set_def.get("agents", [])),
        "commands": list(set_def.get("commands", [])),
        "hooks": list(set_def.get("hooks", [])),
        "mcps": list(set_def.get("mcps", [])),
        "skills": list(set_def.get("skills", [])),
        "settings": list(set_def.get("settings", [])),
    }

    # extends 처리
    for parent in set_def.get("extends", []):
        parent_result = resolve_set(sets_data, parent, resolved.copy())
        for key in result:
            result[key].extend(parent_result.get(key, []))

    # 중복 제거 (순서 유지)
    for key in result:
        result[key] = list(dict.fromkeys(result[key]))

    return result


def generate_install_commands(templates: dict) -> list:
    """설치 명령어 생성"""
    commands = []

    type_map = {
        "agents": "agent",
        "commands": "command",
        "hooks": "hook",
        "mcps": "mcp",
        "skills": "skill",
        "settings": "setting",
    }

    for category, items in templates.items():
        if items:
            cmd_type = type_map.get(category, category)
            for item in items:
                commands.append(f"npx claude-code-templates@latest --{cmd_type} {item}")

    return commands


def install_set(set_name: str, sets_path: str = None, dry_run: bool = False):
    """템플릿 세트 설치"""
    sets_data = load_sets(sets_path)
    if not sets_data:
        return

    if set_name not in sets_data.get("sets", {}):
        print(f"Error: Set '{set_name}' not found")
        available = list(sets_data.get("sets", {}).keys())
        print(f"Available sets: {', '.join(available)}")
        return

    set_def = sets_data["sets"][set_name]
    print(f"\n[Installing template set: {set_name}]")
    print(f"   {set_def.get('description', '')}\n")

    templates = resolve_set(sets_data, set_name)
    commands = generate_install_commands(templates)

    if not commands:
        print("No templates to install.")
        return

    print(f"Templates to install ({len(commands)}):")
    for cmd in commands:
        # Extract the template path from command
        parts = cmd.split("--")[1].strip().split(" ", 1)
        if len(parts) == 2:
            print(f"  - {parts[0]}: {parts[1]}")

    if dry_run:
        print("\n[DRY RUN] Commands that would be executed:")
        for cmd in commands:
            print(f"  {cmd}")
        return

    print("\n>> Installing...")
    success_count = 0
    fail_count = 0

    for cmd in commands:
        print(f"\n> {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"  [FAILED] {e}")
            if e.stderr:
                print(f"  {e.stderr}")
            fail_count += 1

    print(f"\n[Installation complete!]")
    print(f"   Success: {success_count}, Failed: {fail_count}")


def list_sets(sets_path: str = None):
    """사용 가능한 세트 목록"""
    sets_data = load_sets(sets_path)
    if not sets_data:
        return

    print("\n[Available Template Sets]\n")
    for name, set_def in sets_data.get("sets", {}).items():
        desc = set_def.get("description", "No description")

        templates = resolve_set(sets_data, name)
        total = sum(len(v) for v in templates.values())

        print(f"  {name:<20} ({total} templates)")
        if set_def.get("extends"):
            print(f"    extends: {', '.join(set_def['extends'])}")
        print()


def show_set_details(set_name: str, sets_path: str = None):
    """세트 상세 내용 표시"""
    sets_data = load_sets(sets_path)
    if not sets_data:
        return

    if set_name not in sets_data.get("sets", {}):
        print(f"Error: Set '{set_name}' not found")
        return

    templates = resolve_set(sets_data, set_name)
    print(f"\n[Set: {set_name}]")
    print(f"   {sets_data['sets'][set_name].get('description', '')}\n")

    for category, items in templates.items():
        if items:
            print(f"{category}:")
            for item in items:
                print(f"  - {item}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Install AITMPL template sets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                      # List available sets
  %(prog)s frontend                    # Install frontend set
  %(prog)s frontend --dry-run          # Preview without installing
  %(prog)s --details backend           # Show set contents
        """
    )
    parser.add_argument("set_name", nargs="?", help="Template set to install")
    parser.add_argument("-l", "--list", action="store_true", help="List available sets")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without executing")
    parser.add_argument("-d", "--details", metavar="SET", help="Show details of a specific set")
    parser.add_argument("-f", "--file", default=SETS_FILE, help="Template sets file path")

    args = parser.parse_args()

    if args.list:
        list_sets(args.file)
    elif args.details:
        show_set_details(args.details, args.file)
    elif args.set_name:
        install_set(args.set_name, args.file, args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
