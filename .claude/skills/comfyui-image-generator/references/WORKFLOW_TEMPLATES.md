# 工作流模板

## 默认 SD3 工作流 (default_workflow.json)

基于 `z_image_turbo_nvfp4` 模型的图像生成工作流。

### 节点结构

| 节点 ID | 类型 | 说明 |
|---------|------|------|
| 62 | CLIPLoader | 加载 qwen_3_4b.safetensors |
| 63 | VAELoader | 加载 ae.safetensors |
| 66 | UNETLoader | 加载 z_image_turbo_nvfp4.safetensors |
| 67 | CLIPTextEncode | 正面提示词 |
| 68 | EmptySD3LatentImage | 空白 Latent (1920x1088) |
| 69 | KSampler | 采样器 (8 steps, euler_ancestral) |
| 70 | ModelSamplingAuraFlow | 模型采样 |
| 71 | CLIPTextEncode | 负面提示词 (空) |
| 65 | VAEDecode | VAE 解码 |
| 9 | SaveImage | 保存图像 |

### 使用方法

```bash
python scripts/comfyui_client.py --workflow assets/default_workflow.json --output my_image.png
```

## 图生图工作流 (image_to_image.json)

将输入图像转换为指定风格。

### 节点结构

| 节点 ID | 类型 | 说明 |
|---------|------|------|
| 10 | LoadImage | 加载输入图像 |
| 11 | VAEEncode | 编码图像为 Latent |
| 69 | KSampler | 采样器 (denoise < 1) |
| 65 | VAEDecode | VAE 解码 |
| 9 | SaveImage | 保存图像 |

### 使用方法

```bash
python scripts/comfyui_client.py --workflow assets/image_to_image.json --output my_image.png
```

## 自定义参数

### KSampler 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `seed` | 当前时间戳 | 随机种子 |
| `steps` | 8 | 采样步数 |
| `cfg` | 1 | CFG 比例 |
| `sampler_name` | euler_ancestral | 采样器名称 |
| `scheduler` | simple | 调度器 |
| `denoise` | 1 | 去噪强度 (0-1) |

### EmptySD3LatentImage 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `width` | 1920 | 图像宽度 |
| `height` | 1088 | 图像高度 |
| `batch_size` | 1 | 批量大小 |
