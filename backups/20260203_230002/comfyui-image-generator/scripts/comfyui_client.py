#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI 通用客户端
调用任意 ComfyUI 工作流生成图像
支持任务队列管理，防止多程序冲突
"""

import json
import argparse
import time
import ssl
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 队列文件路径
QUEUE_FILE = Path(__file__).parent / "comfyui_queue.json"


class ComfyUIClient:
    """ComfyUI API 客户端"""

    def __init__(self, server_url: str = "http://127.0.0.1:8188"):
        self.server_url = server_url.rstrip('/')
        self.client_id = str(int(time.time() * 1000))
        self.client_name = f"client_{os.getpid()}"

    def _request(self, endpoint: str, data: dict = None) -> dict:
        """发送 API 请求"""
        url = f"{self.server_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(data).encode('utf-8') if data else None

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = Request(url, data=json_data, headers=headers, method='POST' if data else 'GET')

        try:
            with urlopen(req, timeout=60, context=ctx) as resp:
                if endpoint == "/view":
                    return resp.read()
                return json.loads(resp.read().decode('utf-8'))
        except HTTPError as e:
            raise Exception(f"HTTP {e.code}: {e.read().decode('utf-8')}")
        except URLError as e:
            raise Exception(f"连接失败: {e.reason}")

    def queue_prompt(self, workflow: dict) -> dict:
        """提交工作流到队列"""
        return self._request("/api/prompt", {
            "prompt": workflow,
            "client_id": self.client_id
        })

    def wait_for_completion(self, timeout: int = 300) -> dict:
        """等待任务完成"""
        start = time.time()
        while time.time() - start < timeout:
            history = self._request(f"/api/history/{self.client_id}")
            if isinstance(history, dict):
                status = history.get("status", {})
                if status.get("status") == "success":
                    return history.get("outputs", {})
                elif status.get("status") == "failed":
                    raise Exception(f"生成失败: {status.get('errors')}")
            time.sleep(1)
        raise Exception("等待超时")

    def get_image(self, filename: str, subfolder: str = "", type_: str = "output") -> bytes:
        """获取生成的图像"""
        params = f"?filename={filename}&subfolder={subfolder}&type={type_}"
        return self._request(f"/view{params}")

    def get_queue_status(self) -> dict:
        """获取队列状态"""
        try:
            history = self._request("/api/queue")
            return history
        except Exception as e:
            return {"error": str(e)}

    def get_all_client_tasks(self) -> list:
        """获取所有客户端的任务状态"""
        try:
            # 获取系统状态
            result = self._request("/api/system_stats")
            return result
        except:
            # 备用方法：尝试获取历史
            return {}


def load_queue() -> dict:
    """加载队列文件"""
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"clients": {}, "pending": []}


def save_queue(queue: dict):
    """保存队列文件"""
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def register_client(queue: dict, client_id: str, client_name: str, workflow_name: str):
    """注册客户端到队列"""
    queue["clients"][client_id] = {
        "name": client_name,
        "workflow": workflow_name,
        "status": "running",
        "start_time": time.time()
    }
    save_queue(queue)


def unregister_client(queue: dict, client_id: str):
    """从队列移除客户端"""
    if client_id in queue["clients"]:
        del queue["clients"][client_id]
        save_queue(queue)


def is_queue_busy(queue: dict, exclude_client_id: str = None) -> tuple:
    """检查队列是否繁忙"""
    busy_clients = []
    for client_id, info in queue["clients"].items():
        if client_id != exclude_client_id and info.get("status") == "running":
            busy_clients.append(info)
    return len(busy_clients) > 0, busy_clients


def run_workflow(workflow_path: str, server_url: str, output_path: str = None, seed: int = None, wait: bool = False, timeout: int = 300):
    """执行工作流

    Args:
        workflow_path: 工作流文件路径
        server_url: ComfyUI 服务器地址
        output_path: 输出图像路径
        seed: 随机种子
        wait: 是否等待队列空闲
        timeout: 等待超时时间（秒）
    """
    # 加载工作流
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # 替换种子（如果指定）
    if seed is not None:
        for node_id, node in workflow.items():
            if node.get("class_type") == "KSampler" and "inputs" in node:
                node["inputs"]["seed"] = seed

    # 连接 ComfyUI
    print(f"[INFO] 连接 ComfyUI: {server_url}")
    client = ComfyUIClient(server_url)

    # 加载队列
    queue = load_queue()

    # 检查队列状态
    busy, busy_clients = is_queue_busy(queue)
    if busy:
        print(f"[WARN] ComfyUI 繁忙，有 {len(busy_clients)} 个任务正在运行:")
        for c in busy_clients:
            print(f"  - {c['name']}: {c['workflow']}")

        if wait:
            print("[INFO] 等待队列空闲...")
            while busy:
                time.sleep(5)
                queue = load_queue()
                busy, busy_clients = is_queue_busy(queue)
                elapsed = int(time.time() - busy_clients[0]["start_time"]) if busy_clients else 0
                print(f"[INFO] 等待中... 已运行 {elapsed} 秒")
            print("[INFO] 队列空闲，开始执行")
        else:
            print("[WARN] 使用 --wait 参数等待队列空闲")
            return None

    # 注册到队列
    workflow_name = Path(workflow_path).stem
    register_client(queue, client.client_id, client.client_name, workflow_name)

    try:
        # 提交任务
        print("[INFO] 提交工作流...")
        result = client.queue_prompt(workflow)
        prompt_id = result.get("prompt_id", "unknown")
        print(f"[OK] 任务已提交: {prompt_id}")

        # 等待完成
        print("[INFO] 生成中...")
        outputs = client.wait_for_completion(timeout=timeout)

        # 保存图像
        for node_id, output_data in outputs.items():
            if isinstance(output_data, dict) and "images" in output_data:
                for img in output_data["images"]:
                    filename = img["filename"]
                    subfolder = img.get("subfolder", "")

                    # 获取图像
                    image_data = client.get_image(filename, subfolder)

                    # 保存
                    save_path = output_path or filename
                    with open(save_path, 'wb') as f:
                        f.write(image_data)
                    print(f"[OK] 图像已保存: {save_path}")
                    return save_path

        raise Exception("未找到生成的图像")
    finally:
        # 从队列移除
        unregister_client(queue, client.client_id)


def main():
    parser = argparse.ArgumentParser(description="ComfyUI 通用客户端")
    parser.add_argument("--workflow", "-w", help="工作流 JSON 文件路径")
    parser.add_argument("--server-url", "-s", default="http://127.0.0.1:8188", help="ComfyUI 服务器地址")
    parser.add_argument("--output", "-o", help="输出图像路径")
    parser.add_argument("--seed", help="随机种子（可选）")
    parser.add_argument("--wait", "-W", action="store_true", help="等待队列空闲后再执行（防止多程序冲突）")
    parser.add_argument("--status", action="store_true", help="查看当前队列状态")

    args = parser.parse_args()

    # 查看队列状态（不需要 workflow）
    if args.status:
        client = ComfyUIClient(args.server_url)
        queue = load_queue()
        busy, busy_clients = is_queue_busy(queue)

        print("=== ComfyUI 队列状态 ===")
        if busy:
            print(f"状态: 繁忙 ({len(busy_clients)} 个任务正在运行)")
            for c in busy_clients:
                elapsed = int(time.time() - c["start_time"])
                print(f"  - {c['name']}: {c['workflow']} (运行 {elapsed} 秒)")
        else:
            print("状态: 空闲")
        return 0

    # 必须提供 workflow
    if not args.workflow:
        print("[错误] 请指定 --workflow 参数")
        parser.print_help()
        return 1

    workflow_path = Path(args.workflow)
    if not workflow_path.exists():
        print(f"[错误] 工作流文件不存在: {workflow_path}")
        return 1

    try:
        run_workflow(
            str(workflow_path),
            args.server_url,
            args.output,
            int(args.seed) if args.seed else None,
            wait=args.wait
        )
        return 0
    except Exception as e:
        print(f"[错误] {e}")
        return 1


if __name__ == "__main__":
    exit(main())
