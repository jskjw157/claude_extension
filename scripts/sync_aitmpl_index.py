#!/usr/bin/env python3
"""
AITMPL 템플릿 자동 인덱싱 스크립트
Git clone 방식으로 rate limit 없이 전체 목록 가져오기
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

REPO_URL = "https://github.com/davila7/claude-code-templates.git"
COMPONENTS_PATH = "cli-tool/components"
OUTPUT_FILE = ".claude/aitmpl-index.json"

CATEGORIES = ["agents", "commands", "hooks", "mcps", "skills", "settings"]


def clone_repo(temp_dir: str) -> bool:
    """Git clone (shallow) - no rate limit!"""
    try:
        print("Cloning repository (shallow)...")
        # Simple shallow clone without sparse checkout for full access
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, temp_dir],
            check=True,
            capture_output=True,
            text=True
        )
        print("Clone complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Git not found. Please install git.")
        return False


def scan_category(base_path: Path, category: str) -> dict:
    """Scan local directory for templates (handles nested skill folders)"""
    items = {}
    category_path = base_path / COMPONENTS_PATH / category

    if not category_path.exists():
        return items

    for subdir in sorted(category_path.iterdir()):
        if subdir.is_dir():
            templates = []
            # Check for direct files
            for file in sorted(subdir.iterdir()):
                if file.is_file() and file.suffix in [".md", ".json"]:
                    templates.append({
                        "name": file.stem,
                        "file": file.name,
                        "size": file.stat().st_size
                    })
                # Handle nested folders (for skills)
                elif file.is_dir():
                    skill_file = file / "SKILL.md"
                    if skill_file.exists():
                        templates.append({
                            "name": file.name,
                            "file": f"{file.name}/SKILL.md",
                            "size": skill_file.stat().st_size
                        })
                    else:
                        # Check for any .md file in nested folder
                        for nested_file in file.iterdir():
                            if nested_file.is_file() and nested_file.suffix in [".md", ".json"]:
                                templates.append({
                                    "name": f"{file.name}/{nested_file.stem}",
                                    "file": f"{file.name}/{nested_file.name}",
                                    "size": nested_file.stat().st_size
                                })
            if templates:
                items[subdir.name] = templates
        elif subdir.is_file() and subdir.suffix in [".md", ".json"]:
            if "root" not in items:
                items["root"] = []
            items["root"].append({
                "name": subdir.stem,
                "file": subdir.name,
                "size": subdir.stat().st_size
            })

    return items


def build_index_from_clone() -> dict:
    """Build index using git clone (no rate limit)"""
    index = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "source": "https://github.com/davila7/claude-code-templates",
        "method": "git-clone",
        "categories": {}
    }

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="aitmpl_")

    try:
        if not clone_repo(temp_dir):
            print("Failed to clone. Returning empty index.")
            return index

        base_path = Path(temp_dir)

        for category in CATEGORIES:
            print(f"Scanning {category}...")
            index["categories"][category] = scan_category(base_path, category)

    finally:
        # Cleanup
        print("Cleaning up temp files...")
        shutil.rmtree(temp_dir, ignore_errors=True)

    return index


def save_index(index: dict, output_path: str = None):
    """Save index to file"""
    if output_path is None:
        output_path = OUTPUT_FILE

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Add summary
    summary = {}
    for cat, items in index["categories"].items():
        total = sum(len(v) for v in items.values())
        summary[cat] = {"categories": len(items), "templates": total}
    index["summary"] = summary

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\nIndex saved to {output_path}")
    print(f"Total categories: {len(index['categories'])}")

    for cat, data in summary.items():
        print(f"  - {cat}: {data['categories']} subcategories, {data['templates']} templates")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync AITMPL template index (via git clone)")
    parser.add_argument("-o", "--output", default=OUTPUT_FILE, help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Print without saving")

    args = parser.parse_args()

    index = build_index_from_clone()

    if args.dry_run:
        print(json.dumps(index, indent=2, ensure_ascii=False))
    else:
        save_index(index, args.output)


if __name__ == "__main__":
    main()
