#!/usr/bin/env python3
"""
AITMPL 템플릿 매니저 - 통합 CLI

Usage:
  python aitmpl-manager.py sync                    # 인덱스 업데이트
  python aitmpl-manager.py search -t security      # 태그로 검색
  python aitmpl-manager.py search debugger         # 키워드로 검색
  python aitmpl-manager.py install frontend        # 세트 설치
  python aitmpl-manager.py list-sets               # 세트 목록
  python aitmpl-manager.py list-tags               # 태그 목록
"""

import argparse
import sys
import os

# 스크립트 디렉토리를 path에 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def cmd_sync(args):
    """인덱스 동기화"""
    try:
        from sync_aitmpl_index import build_index_from_clone, save_index
        import json

        index = build_index_from_clone()
        if args.dry_run:
            print(json.dumps(index, indent=2, ensure_ascii=False))
        else:
            save_index(index, args.output)
    except ImportError as e:
        print(f"Error importing sync module: {e}")
        print("Make sure sync_aitmpl_index.py is in the same directory")
        sys.exit(1)


def cmd_search(args):
    """템플릿 검색"""
    try:
        from search_aitmpl import (
            search_by_tags, search_templates, print_results, load_index
        )

        if args.tags:
            results = search_by_tags(args.tags)
            print_results(results, args.format)
        elif args.query:
            index = load_index(args.index)
            if not index:
                sys.exit(1)
            for q in args.query:
                results = search_templates(q, index)
                if len(args.query) > 1:
                    print(f"\n=== Results for '{q}' ===")
                print_results(results, args.format)
        else:
            print("Error: Provide either --tags or a search query")
            sys.exit(1)
    except ImportError as e:
        print(f"Error importing search module: {e}")
        sys.exit(1)


def cmd_install(args):
    """템플릿 세트 설치"""
    try:
        from install_template_set import install_set
        install_set(args.set_name, args.file, args.dry_run)
    except ImportError as e:
        print(f"Error importing install module: {e}")
        sys.exit(1)


def cmd_list_sets(args):
    """세트 목록"""
    try:
        from install_template_set import list_sets
        list_sets(args.file)
    except ImportError as e:
        print(f"Error importing install module: {e}")
        sys.exit(1)


def cmd_list_tags(args):
    """태그 목록"""
    try:
        from search_aitmpl import list_tags
        list_tags()
    except ImportError as e:
        print(f"Error importing search module: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AITMPL Template Manager - Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  sync         Sync index from GitHub API
  search       Search templates by keyword or tag
  install      Install a template set
  list-sets    List available template sets
  list-tags    List available search tags

Examples:
  %(prog)s sync                        # Update index
  %(prog)s search -t security          # Search by tag
  %(prog)s search debugger             # Search by keyword
  %(prog)s install frontend            # Install set
  %(prog)s install frontend --dry-run  # Preview installation
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # sync 명령
    sync_parser = subparsers.add_parser("sync", help="Sync index from GitHub")
    sync_parser.add_argument("-o", "--output", default=".claude/aitmpl-index.json",
                             help="Output file path")
    sync_parser.add_argument("--dry-run", action="store_true",
                             help="Print without saving")
    sync_parser.set_defaults(func=cmd_sync)

    # search 명령
    search_parser = subparsers.add_parser("search", help="Search templates")
    search_parser.add_argument("query", nargs="*", help="Search keyword")
    search_parser.add_argument("-t", "--tags", nargs="+", help="Search by tags")
    search_parser.add_argument("-f", "--format", choices=["table", "commands", "json"],
                               default="table", help="Output format")
    search_parser.add_argument("-i", "--index", default=".claude/aitmpl-index.json",
                               help="Index file path")
    search_parser.set_defaults(func=cmd_search)

    # install 명령
    install_parser = subparsers.add_parser("install", help="Install template set")
    install_parser.add_argument("set_name", help="Set name to install")
    install_parser.add_argument("--dry-run", action="store_true",
                                help="Show commands without executing")
    install_parser.add_argument("-f", "--file", default=".claude/template-sets.yaml",
                                help="Template sets file")
    install_parser.set_defaults(func=cmd_install)

    # list-sets 명령
    list_sets_parser = subparsers.add_parser("list-sets", help="List available sets")
    list_sets_parser.add_argument("-f", "--file", default=".claude/template-sets.yaml",
                                  help="Template sets file")
    list_sets_parser.set_defaults(func=cmd_list_sets)

    # list-tags 명령
    list_tags_parser = subparsers.add_parser("list-tags", help="List available tags")
    list_tags_parser.set_defaults(func=cmd_list_tags)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # 작업 디렉토리를 프로젝트 루트로 변경 (스크립트 디렉토리의 상위)
    project_root = os.path.dirname(SCRIPT_DIR)
    os.chdir(project_root)

    args.func(args)


if __name__ == "__main__":
    main()
