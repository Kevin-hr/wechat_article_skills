#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI 批量分镜图生成脚本
从 sora-2-data.js 读取所有场景的 t2i_core 提示词，调用 ComfyUI API 生成图像

用法: python generate_comfyui_images.py [--server-url http://127.0.0.1:8188] [--output-dir ./outputs]
"""

import json
import os
import sys
import time
import re
import argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import urllib.request
import ssl

# ============== 配置 ==============
DEFAULT_SERVER_URL = "http://127.0.0.1:8188"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "comfyui_outputs"

# ComfyUI API 端点
API_ENDPOINTS = {
    "queue": "/api/queue",
    "prompt": "/api/prompt",
    "history": "/api/history",
    "view": "/view"
}

# ============== ComfyUI 客户端 ==============
class ComfyUIClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.client_id = str(int(time.time() * 1000))

    def _make_request(self, endpoint: str, data: dict = None, timeout: int = 60) -> dict:
        """发送 API 请求到 ComfyUI"""
        url = f"{self.server_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        json_data = json.dumps(data).encode('utf-8') if data else None

        # 创建不验证 SSL 的上下文（本地开发环境常用）
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = Request(url, data=json_data, headers=headers, method='POST' if data else 'GET')

        try:
            with urlopen(req, timeout=timeout, context=ctx) as response:
                if response.status == 200:
                    if endpoint == API_ENDPOINTS["view"]:
                        return response.read()
                    return json.loads(response.read().decode('utf-8'))
                else:
                    raise Exception(f"HTTP {response.status}: {response.read().decode('utf-8')}")
        except HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            raise Exception(f"HTTP {e.code}: {error_body}")
        except URLError as e:
            raise Exception(f"连接失败: {e.reason}")

    def get_system_stats(self) -> dict:
        """获取系统状态"""
        try:
            return self._make_request("/api/system_stats")
        except Exception:
            return {"error": str(e)}

    def queue_prompt(self, workflow: dict, extra_data: dict = None) -> dict:
        """提交工作流到队列"""
        data = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        if extra_data:
            data["extra_data"] = extra_data
        return self._make_request(API_ENDPOINTS["prompt"], data)

    def get_history(self, prompt_id: str) -> dict:
        """获取生成历史"""
        return self._make_request(f"{API_ENDPOINTS['history']}/{prompt_id}")

    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """获取生成的图像"""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return self._make_request(f"{API_ENDPOINTS['view']}?{query}")

    def wait_for_completion(self, timeout: int = 300) -> tuple:
        """等待当前任务完成"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # 检查队列状态
                queue = self._make_request(API_ENDPOINTS["queue"])

                # 检查是否有正在运行的任务
                if isinstance(queue, dict):
                    # 检查是否有运行中的任务
                    running = queue.get("queue_running", [])
                    if len(running) == 0:
                        # 检查最近完成的任务
                        history = self._make_request(API_ENDPOINTS["history"])
                        if isinstance(history, dict):
                            # 查找我们提交的任务
                            for prompt_id, data in history.items():
                                if data.get("client_id") == self.client_id:
                                    status = data.get("status", {})
                                    if status.get("status") == "success":
                                        outputs = data.get("outputs", {})
                                        return prompt_id, outputs
                                    elif status.get("status") == "failed":
                                        raise Exception(f"生成失败: {status.get('errors')}")

                time.sleep(1)
            except Exception as e:
                print(f"  轮询状态时出错: {e}")
                time.sleep(2)

        raise Exception("等待超时")


# ============== 工作流模板 ==============
def create_workflow(prompt_text: str, seed: int = None, output_prefix: str = "scene") -> dict:
    """
    创建 ComfyUI 工作流

    基于 API_comfyUI.json 的结构，使用 z_image_turbo_nvfp4 模型
    """
    if seed is None:
        seed = int(time.time() * 1000) % (2**63)

    return {
        "9": {
            "inputs": {
                "filename_prefix": output_prefix,
                "images": ["65", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "保存图像"}
        },
        "62": {
            "inputs": {
                "clip_name": "qwen_3_4b.safetensors",
                "type": "lumina2",
                "device": "default"
            },
            "class_type": "CLIPLoader",
            "_meta": {"title": "加载CLIP"}
        },
        "63": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader",
            "_meta": {"title": "加载VAE"}
        },
        "65": {
            "inputs": {
                "samples": ["69", 0],
                "vae": ["63", 0]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE解码"}
        },
        "66": {
            "inputs": {
                "unet_name": "z_image_turbo_nvfp4.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "UNet加载器"}
        },
        "67": {
            "inputs": {
                "text": prompt_text,
                "clip": ["62", 0]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "正面提示词"}
        },
        "68": {
            "inputs": {
                "width": 1920,
                "height": 1088,  # 9:16 比例
                "batch_size": 1
            },
            "class_type": "EmptySD3LatentImage",
            "_meta": {"title": "空Latent图像（SD3）"}
        },
        "69": {
            "inputs": {
                "seed": seed,
                "steps": 8,
                "cfg": 1,
                "sampler_name": "euler_ancestral",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["70", 0],
                "positive": ["67", 0],
                "negative": ["71", 0],
                "latent_image": ["68", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "K采样器"}
        },
        "70": {
            "inputs": {
                "shift": 3,
                "model": ["66", 0]
            },
            "class_type": "ModelSamplingAuraFlow",
            "_meta": {"title": "采样算法（AuraFlow）"}
        },
        "71": {
            "inputs": {
                "text": "",  # 空负面提示词
                "clip": ["62", 0]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "负面提示词"}
        }
    }


# ============== 数据解析 ==============
def parse_sora_data(data_path: str) -> list:
    """
    解析 sora-2-data.js 文件，提取所有场景信息
    """
    with open(data_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 JSON 部分
    match = re.search(r'window\.SORA_PROJECT_DATA\s*=\s*({.*});', content, re.DOTALL)
    if not match:
        raise ValueError("无法找到 SORA_PROJECT_DATA 数据")

    data = json.loads(match.group(1))
    scenes = data.get('scenes', [])

    result = []
    for scene in scenes:
        scene_id = scene.get('id', '00')
        scene_type = scene.get('scene_type', 'SCENE')
        duration = scene.get('duration', 4)
        prompts = scene.get('prompts', {})
        t2i_core = prompts.get('t2i_core', '')
        midjourney = prompts.get('midjourney_v6', '')

        result.append({
            'id': scene_id,
            'type': scene_type,
            'duration': duration,
            't2i_core': t2i_core,
            'midjourney': midjourney
        })

    return result


# ============== 主程序 ==============
def main():
    parser = argparse.ArgumentParser(description='ComfyUI 批量分镜图生成')
    parser.add_argument('--server-url', '-s', default=DEFAULT_SERVER_URL, help='ComfyUI 服务器地址')
    parser.add_argument('--output-dir', '-o', default=str(DEFAULT_OUTPUT_DIR), help='输出目录')
    parser.add_argument('--data-file', '-d', default='sora-2-data.js', help='sora-2-data.js 文件路径')
    parser.add_argument('--prompt-type', '-p', choices=['t2i_core', 'midjourney'], default='t2i_core',
                        help='使用的提示词类型')

    args = parser.parse_args()

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解析场景数据
    data_file = Path(args.data_file)
    if not data_file.is_absolute():
        data_file = Path.cwd() / data_file

    if not data_file.exists():
        print(f"[错误] 数据文件不存在: {data_file}")
        sys.exit(1)

    print(f"读取数据文件: {data_file}")
    scenes = parse_sora_data(str(data_file))
    print(f"共找到 {len(scenes)} 个场景")

    # 连接 ComfyUI
    print(f"\n连接 ComfyUI 服务器: {args.server_url}")
    client = ComfyUIClient(args.server_url)

    # 检查连接
    try:
        stats = client.get_system_stats()
        print(f"服务器状态: {stats}")
    except Exception as e:
        print(f"[错误] 无法连接到 ComfyUI: {e}")
        sys.exit(1)

    # 生成每个场景
    print(f"\n{'='*60}")
    print(f"开始生成 {len(scenes)} 个分镜图")
    print(f"提示词类型: {args.prompt_type}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}\n")

    success_count = 0
    failed_count = 0

    for i, scene in enumerate(scenes, 1):
        scene_id = scene['id']
        scene_type = scene['type']
        prompt = scene.get(args.prompt_type, scene['t2i_core'])

        if not prompt:
            print(f"[{i:02d}/{len(scenes)}] 场景 {scene_id} ({scene_type}): 跳过，无提示词")
            continue

        print(f"[{i:02d}/{len(scenes)}] 场景 {scene_id} ({scene_type})")
        print(f"  提示词: {prompt[:80]}..." if len(prompt) > 80 else f"  提示词: {prompt}")

        output_prefix = f"scene_{scene_id}_{scene_type.lower()}"

        try:
            # 创建工作流
            workflow = create_workflow(prompt, output_prefix=output_prefix)

            # 提交到队列
            result = client.queue_prompt(workflow)
            print(f"  提交成功，prompt_id: {result.get('prompt_id', 'unknown')}")

            # 等待完成
            prompt_id, outputs = client.wait_for_completion(timeout=300)
            print(f"  生成完成!")

            # 保存图像
            for node_id, output_data in outputs.items():
                if isinstance(output_data, dict) and 'images' in output_data:
                    for img_info in output_data['images']:
                        filename = img_info.get('filename', f'{output_prefix}.png')
                        subfolder = img_info.get('subfolder', '')

                        # 获取图像
                        image_data = client.get_image(filename, subfolder)

                        # 保存文件
                        save_path = output_dir / filename
                        with open(save_path, 'wb') as f:
                            f.write(image_data)
                        print(f"  保存图像: {save_path}")

            success_count += 1

        except Exception as e:
            print(f"  [错误] {e}")
            failed_count += 1

        # 避免请求过快
        if i < len(scenes):
            time.sleep(2)

    # 汇总
    print(f"\n{'='*60}")
    print(f"生成完成!")
    print(f"  成功: {success_count}")
    print(f"  失败: {failed_count}")
    print(f"  总计: {len(scenes)}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
