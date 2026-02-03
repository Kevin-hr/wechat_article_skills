# ComfyUI API 参考

## 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/queue` | GET | 获取队列状态 |
| `/api/prompt` | POST | 提交工作流 |
| `/api/history/[prompt_id]` | GET | 获取生成历史 |
| `/view` | GET | 获取生成的图像 |

## 队列状态响应

```json
{
  "queue_running": [],      // 正在运行的任务
  "queue_pending": []       // 等待中的任务
}
```

## 提交工作流请求

```json
POST /api/prompt
{
  "prompt": { /* 工作流 JSON */ },
  "client_id": "unique_id", // 可选，用于追踪
  "extra_data": {}          // 可选，额外数据
}
```

## 响应

```json
{
  "prompt_id": "abc123"
}
```

## 工作流节点类型

### 加载器
- `CheckpointLoader` - 加载检查点模型
- `CLIPLoader` - 加载 CLIP 模型
- `VAELoader` - 加载 VAE 模型
- `UNETLoader` - 加载 UNet 模型

### 采样器
- `KSampler` - 主要采样器
- `SamplerCustom` - 自定义采样器

### 图像处理
- `VAEDecode` - VAE 解码
- `SaveImage` - 保存图像
- `EmptySD3LatentImage` - 创建空白 Latent

### 文本编码
- `CLIPTextEncode` - 文本编码

## 完整示例

```python
import json
from urllib.request import Request, urlopen

workflow = {
  "1": {
    "inputs": {
      "text": "a beautiful landscape",
      "clip": ["2", 0]
    },
    "class_type": "CLIPTextEncode"
  },
  "2": {
    "inputs": {
      "clip_name": "qwen_3_4b.safetensors",
      "type": "lumina2"
    },
    "class_type": "CLIPLoader"
  }
}

data = json.dumps({"prompt": workflow}).encode()
req = Request("http://127.0.0.1:8188/api/prompt", data=data)
req.add_header("Content-Type", "application/json")
result = json.loads(urlopen(req).read())
print(result["prompt_id"])
```
