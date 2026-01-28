# Clawdbot 快速上手教程

**Less clicking, more shipping.**  
减少点击，多发货，少找文件。

Clawdbot 是一个旨在提升开发和运维效率的命令行工具。本文将带你快速上手 Clawdbot，从初始化到掌握常用命令，助你事半功倍。

## 1. 快速开始 (Quick Start)

只需三步，即可开启 Clawdbot 之旅：

### 第一步：初始化
在终端运行以下命令进行初始化：
```bash
clawdbot init
```

### 第二步：授权登录
登录你的账户以访问更多功能：
```bash
clawdbot login
```

### 第三步：启动/使用功能
例如，启动代理服务：
```bash
clawdbot proxy
```

---

## 2. 常用命令 (Common Commands)

以下是日常使用频率最高的命令：

*   **发送消息**
    向指定目标发送消息（支持静默模式）：
    ```bash
    clawdbot message send --target <target_id> --message "Hello" --silent
    ```

*   **查看登录状态**
    检查当前的渠道登录状态：
    ```bash
    clawdbot channels login --status
    ```

*   **启用网关模式**
    开启网关支持：
    ```bash
    clawdbot --use-gateway
    ```

*   **打开控制面板**
    在浏览器中打开可视化控制面板：
    ```bash
    clawdbot dashboard
    ```

---

## 3. 命令分类速查 (Command Categories)

Clawdbot 的命令体系丰富，以下是分类概览：

| 分类 | 常用指令 |
| :--- | :--- |
| **基础设置** | `init`, `account`, `configure`, `config`, `doctor` |
| **网关与服务** | `server`, `daemon`, `run`, `status`, `stop` |
| **消息与通知** | `message`, `channel`, `contact`, `notify`, `webhook` |
| **系统功能** | `open`, `update`, `clean`, `check`, `cluster` |
| **辅助工具** | `logs`, `cache`, `extract`, `decode`, `monitor` |
| **全局参数** | `list`, `verbose`, `json`, `silent`, `help` |

---

## 4. 全局选项 (Global Options)

这些选项可用于大多数命令，以控制输出格式和行为：

*   `--verbose`: 显示详细日志，用于调试。
*   `--json`: 以 JSON 格式输出结果，便于脚本处理。
*   `--silent`: 静默模式，不仅显示错误信息。
*   `--no-color`: 禁用终端彩色输出。
*   `--help`: 显示帮助信息。

---

## 5. 实用技巧 (Practical Tips)

掌握这些技巧，让你的操作更丝滑：

*   **专注网关模式**：使用 `clawdbot gateway --focus` 进入快速交互模式。
*   **指定服务端口**：启动服务时指定端口，例如 `clawdbot server --port 8080`。
*   **快速查看帮助**：对任意子命令使用 `-h` 查看帮助，例如 `clawdbot message -h`。
*   **Telegram 消息回复**：指定渠道发送消息，例如 `clawdbot message send --channel telegram --target <id> --message "Hi"`。

---

> **更多帮助**  
> 如有疑问，请查阅官方文档或使用 `clawdbot help` 命令。
