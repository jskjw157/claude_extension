#!/usr/bin/env python3
"""
AITMPL 템플릿 태그 기반 검색
용도별로 적절한 템플릿을 빠르게 찾기
"""

import json
import argparse
from pathlib import Path

INDEX_FILE = ".claude/aitmpl-index.json"

# 태그 → 템플릿 매핑
TAG_MAPPINGS = {
    # 용도별 태그
    "review": [
        "agents/development-tools/code-reviewer",
        "agents/development-tools/code-simplifier",
        "skills/development/code-reviewer"
    ],
    "debug": [
        "agents/development-tools/debugger",
        "agents/development-tools/error-detective"
    ],
    "test": [
        "agents/development-tools/test-engineer",
        "skills/development/test-driven-development"
    ],
    "security": [
        "agents/security/security-auditor",
        "agents/security/api-security-audit",
        "hooks/security/security-scanner"
    ],
    "git": [
        "commands/git/feature",
        "commands/git/hotfix",
        "hooks/git/commit-message-validator"
    ],
    "database": [
        "mcps/database/postgresql-integration",
        "mcps/database/supabase",
        "mcps/database/mysql"
    ],
    "ai": [
        "agents/data-ai/data-scientist",
        "agents/data-ai/ml-engineer",
        "agents/data-ai/nlp-engineer",
        "agents/data-ai/computer-vision-engineer"
    ],
    "devops": [
        "agents/devops-infrastructure/docker-specialist",
        "agents/devops-infrastructure/kubernetes-expert",
        "commands/deployment/docker-deploy"
    ],
    "docs": [
        "agents/documentation/documentation-writer",
        "commands/documentation/generate-docs"
    ],
    "performance": [
        "agents/development-tools/performance-profiler",
        "hooks/performance/benchmark"
    ],
    "backup": [
        "hooks/pre-tool/backup-before-edit"
    ],

    # 프로젝트 유형별 (중첩 태그)
    "frontend": ["review", "test", "performance"],
    "backend": ["security", "database", "debug"],
    "fullstack": ["frontend", "backend", "git"],
    "ml": ["ai", "database", "test"],
}


def load_index(index_path: str = None) -> dict:
    """인덱스 파일 로드"""
    if index_path is None:
        index_path = INDEX_FILE

    path = Path(index_path)
    if not path.exists():
        print(f"Error: Index file not found at {index_path}")
        print("Run sync-aitmpl-index.py first to create the index.")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_tags(tags: list, resolved: set = None) -> set:
    """태그를 실제 템플릿 경로로 확장 (중첩 태그 처리)"""
    if resolved is None:
        resolved = set()

    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in TAG_MAPPINGS:
            for item in TAG_MAPPINGS[tag_lower]:
                if item in TAG_MAPPINGS:
                    # 중첩 태그 해결 (순환 참조 방지)
                    if item not in resolved:
                        resolved.update(resolve_tags([item], resolved))
                else:
                    resolved.add(item)
        else:
            # 직접 경로로 취급
            resolved.add(tag)

    return resolved


def search_templates(query: str, index: dict) -> list:
    """쿼리로 템플릿 검색"""
    results = []
    query_lower = query.lower()

    for category, subcats in index.get("categories", {}).items():
        for subcat, templates in subcats.items():
            for tmpl in templates:
                name = tmpl.get("name", "").lower()
                if query_lower in name or query_lower in subcat.lower():
                    cmd_type = category.rstrip("s")  # agents -> agent
                    results.append({
                        "category": category,
                        "subcategory": subcat,
                        "name": tmpl["name"],
                        "path": f"{category}/{subcat}/{tmpl['name']}",
                        "install_cmd": f"npx claude-code-templates@latest --{cmd_type} {subcat}/{tmpl['name']}"
                    })

    return results


def search_by_tags(tags: list) -> list:
    """태그로 검색"""
    resolved = resolve_tags(tags)
    results = []

    for path in sorted(resolved):
        parts = path.split("/")
        if len(parts) >= 2:
            category = parts[0]
            rest = "/".join(parts[1:])
            cmd_type = category.rstrip("s")  # agents -> agent
            results.append({
                "path": path,
                "install_cmd": f"npx claude-code-templates@latest --{cmd_type} {rest}"
            })

    return results


def print_results(results: list, format_type: str = "table"):
    """결과 출력"""
    if not results:
        print("No results found.")
        return

    if format_type == "commands":
        # 설치 명령어만 출력
        for r in results:
            print(r.get("install_cmd", ""))
    elif format_type == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # 테이블 형식
        print(f"\n{'Template':<55} {'Category':<15}")
        print("-" * 75)
        for r in results:
            name = r.get("name") or r.get("path", "")
            cat = r.get("category", "")
            print(f"{name:<55} {cat:<15}")
        print(f"\nTotal: {len(results)} templates")


def list_tags():
    """사용 가능한 태그 목록"""
    print("\n[Available Tags]\n")

    # Usage tags
    print("Usage Tags:")
    for tag, items in sorted(TAG_MAPPINGS.items()):
        if not any(t in TAG_MAPPINGS for t in items):
            preview = ", ".join(items[:2])
            if len(items) > 2:
                preview += f" (+{len(items)-2} more)"
            print(f"  {tag:<15} -> {preview}")

    print("\nProject Type Tags (composite):")
    for tag, items in sorted(TAG_MAPPINGS.items()):
        if any(t in TAG_MAPPINGS for t in items):
            print(f"  {tag:<15} -> {', '.join(items)}")


def main():
    parser = argparse.ArgumentParser(
        description="Search AITMPL templates by tag or keyword",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s debugger                    # Search by keyword
  %(prog)s -t security                 # Search by tag
  %(prog)s -t frontend                 # Search by project type
  %(prog)s -t review security          # Multiple tags
  %(prog)s -t backend -f commands      # Output install commands only
  %(prog)s --list-tags                 # Show available tags
        """
    )
    parser.add_argument("query", nargs="*", help="Search query (keyword)")
    parser.add_argument("-t", "--tags", nargs="+", help="Search by tags")
    parser.add_argument("-f", "--format", choices=["table", "commands", "json"],
                        default="table", help="Output format")
    parser.add_argument("-i", "--index", default=INDEX_FILE, help="Index file path")
    parser.add_argument("--list-tags", action="store_true", help="List available tags")

    args = parser.parse_args()

    if args.list_tags:
        list_tags()
        return

    if args.tags:
        results = search_by_tags(args.tags)
        print_results(results, args.format)
    elif args.query:
        index = load_index(args.index)
        if not index:
            return
        for q in args.query:
            results = search_templates(q, index)
            if len(args.query) > 1:
                print(f"\n=== Results for '{q}' ===")
            print_results(results, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
