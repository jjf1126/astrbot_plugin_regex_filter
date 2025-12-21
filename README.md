# AstrBot Plugin Regex Filter

<div align="center">

✨ **AstrBot 正则表达式过滤器插件** ✨

自定义正则过滤 LLM 输出 | 支持预设规则 | 移除思考标签 | 移除 Markdown

</div>

## 📖 简介

`astrbot_plugin_regex_filter` 是一个用于 [AstrBot](https://github.com/Soulter/AstrBot) 的插件，它允许你在 LLM (大语言模型) 的回复发送给用户之前，使用正则表达式对其进行过滤和清洗。

主要用途：
1.  **移除 DeepSeek-R1 等推理模型的 `<think>` 思考过程标签。**
2.  移除 Markdown 格式（如粗体、代码块），方便接入 TTS (语音合成) 或净化输出。
3.  自定义过滤敏感词或特定格式的文本。

## 💿 安装

### 方法一：通过 AstrBot 管理面板（推荐）
1.  打开 AstrBot 管理面板。
2.  进入插件管理，上传或搜索安装。

### 方法二：手动安装
1.  进入 AstrBot 的 `data/plugins` 目录。
2.  克隆本仓库：
    ```bash
    git clone https://github.com/yourname/astrbot_plugin_regex_filter.git
    ```
3.  重启 AstrBot。

## ⚙️ 配置说明

插件配置文件通常位于 `data/plugins/astrbot_plugin_regex_filter/config.yaml` (如果 AstrBot 支持插件独立配置) 或者在全局配置中配置。

以下是所有可配置项的说明：

### 1. 基础设置
| 配置项 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `enable_plugin` | bool | `true` | 是否启用插件 |
| `enable_logging` | bool | `true` | 是否在控制台打印规则匹配日志 |

### 2. 预设规则 (Preset Rules)
将对应的值设置为 `true` 即可开启。

| 配置项 (Key) | 说明 |
| :--- | :--- |
| `remove_think_tag` | **移除 `<think>...</think>` 标签** (推荐 DeepSeek 用户开启) |
| `remove_markdown_code_block` | 移除 Markdown 代码块 (```) |
| `remove_markdown_bold` | 移除 Markdown 粗体 (**text**) |
| `remove_markdown_italic` | 移除 Markdown 斜体 (*text*) |
| `remove_markdown_inline_code` | 移除行内代码 (`code`) |
| `remove_markdown_headers` | 移除标题 (# Header) |
| `remove_markdown_links` | 移除链接 ([text](url))，只保留文本 |
| `remove_markdown_quotes` | 移除引用 (> text) |
| `remove_markdown_lists` | 移除列表符号 (- 或 1.) |
| `remove_all_html_tags` | 移除所有 HTML 标签 |

### 3. 自定义规则 (Custom Rules)
支持最多 **5** 组自定义规则 (`custom_rule_1` 到 `custom_rule_5`)。

| 子配置项后缀 | 说明 | 示例 |
| :--- | :--- | :--- |
| `_enabled` | 是否启用该规则 | `true` |
| `_name` | 规则名称（用于日志和显示） | `"过滤敏感词"` |
| `_pattern` | 正则表达式模式 | `"笨蛋"` |
| `_replacement` | 替换后的文本（留空则删除） | `"**"` |
| `_flags`（可选） | 正则标志位 (I=忽略大小写, M=多行, S=点匹配换行) | `"I"` |

### 📝 配置文件示例 (config.yaml)

```yaml
plugin_config:
  # === 基础开关 ===
  enable_plugin: true
  enable_logging: true

  # === 预设规则开关 ===
  remove_think_tag: true          # 移除思考标签
  remove_markdown_bold: false     # 移除粗体
  remove_markdown_code_block: false

  # === 自定义规则 1：将 "AI" 替换为 "人工智能" ===
  custom_rule_1_enabled: true
  custom_rule_1_name: "AI全称替换"
  custom_rule_1_pattern: "AI"
  custom_rule_1_replacement: "人工智能"
  custom_rule_1_flags: "I"  # 忽略大小写

  # === 自定义规则 2：删除所有数字 ===
  custom_rule_2_enabled: false
  custom_rule_2_name: "删除数字"
  custom_rule_2_pattern: "\\d+"
  custom_rule_2_replacement: ""
```

## 💻 指令列表

管理员可以在聊天窗口使用以下指令：

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `/rf_list` | 查看当前启用的所有规则（预设+自定义） | `/rf_list` |
| `/rf_reload` | 修改配置文件后，热重载规则，无需重启 Bot | `/rf_reload` |
| `/rf_test <文本>` | 测试当前规则对指定文本的效果 | `/rf_test <think>123</think>你好` |

## 🧪 测试示例

假设你开启了 `remove_think_tag`：

**输入指令：**
```
/rf_test <think>这里是思考过程...</think>你好，我是机器人。
```

**Bot 回复：**
```
📝 原文:
<think>这里是思考过程...</think>你好，我是机器人。

✨ 处理后:
你好，我是机器人。

📋 应用规则: [预设] 思考标签
```

## ❗ 注意事项

1.  **正则语法**：自定义规则使用 Python `re` 模块语法。
2.  **转义字符**：在 YAML 配置文件中编写正则时，反斜杠 `\` 通常需要转义（例如匹配数字 `\d` 可能需要写成 `\\d`，视 YAML 解析器而定，通常 AstrBot 的配置面板会自动处理）。
3.  **执行顺序**：预设规则优先于自定义规则执行。

## 致谢：

1.思路参考了@AlanBacker的astrbot_plugin_markdown_killer。

## 📄 License

MIT

