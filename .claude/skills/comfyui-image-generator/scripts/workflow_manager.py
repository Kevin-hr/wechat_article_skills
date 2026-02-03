#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI 工作流管理工具
保存、加载、列出工作流模板
"""

import json
import argparse
import os
from pathlib import Path


# 默认工作流存储目录
WORKFLOW_DIR = Path(__file__).parent.parent / "workflows / "assets""


def ensure_dir():
    """确保工作流目录存在"""
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)


def save_workflow(name: str, workflow_path: str):
    """保存工作流"""
    ensure_dir()

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    save_path = WORKFLOW_DIR / f"{name}.json"
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"工作流已保存: {save_path}")
    return str(save_path)


def load_workflow(name: str, output_path: str = None):
    """加载工作流"""
    ensure_dir()

    # 查找工作流
    possible_paths = [
        WORKFLOW_DIR / f"{name}.json",
        Path(name),
        Path(name + ".json")
    ]

    workflow_path = None
    for p in possible_paths:
        if p.exists():
            workflow_path = p
            break

    if not workflow_path:
        # 列出可用工作流
        list_workflows()
        raise FileNotFoundError(f"工作流不存在: {name}")

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    output = output_path or f"loaded_{name}.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"工作流已加载: {workflow_path} -> {output}")
    return str(output)


def list_workflows():
    """列出所有工作流"""
    ensure_dir()

    workflows = list(WORKFLOW_DIR.glob("*.json"))

    if not workflows:
        print("没有保存的工作流")
        return

    print("已保存的工作流:")
    for w in workflows:
        print(f"  - {w.stem}")

    return [w.stem for w in workflows]


def delete_workflow(name: str):
    """删除工作流"""
    ensure_dir()

    workflow_path = WORKFLOW_DIR / f"{name}.json"

    if not workflow_path.exists():
        print(f"工作流不存在: {name}")
        return False

    workflow_path.unlink()
    print(f"工作流已删除: {name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="ComfyUI 工作流管理")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # save 命令
    save_parser = subparsers.add_parser("save", help="保存工作流")
    save_parser.add_argument("--name", "-n", required=True, help="工作流名称")
    save_parser.add_argument("--workflow", "-w", required=True, help="工作流 JSON 文件路径")

    # load 命令
    load_parser = subparsers.add_parser("load", help="加载工作流")
    load_parser.add_argument("--name", "-n", required=True, help="工作流名称")
    load_parser.add_argument("--output", "-o", help="输出文件路径")

    # list 命令
    subparsers.add_parser("list", help="列出所有工作流")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除工作流")
    delete_parser.add_argument("--name", "-n", required=True, help="工作流名称")

    args = parser.parse_args()

    try:
        if args.command == "save":
            save_workflow(args.name, args.workflow)
        elif args.command == "load":
            load_workflow(args.name, args.output)
        elif args.command == "list":
            list_workflows()
        elif args.command == "delete":
            delete_workflow(args.name)
    except Exception as e:
        print(f"[错误] {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
