\# AstrBot 正则过滤插件



自定义正则表达式过滤 LLM 输出内容。



\## 功能特性



\- ✅ 自定义正则表达式规则

\- ✅ 支持多条规则顺序执行

\- ✅ 支持捕获组替换 (`\\1`, `\\2` 等)

\- ✅ 支持正则标志 (忽略大小写/多行/DOTALL)

\- ✅ 规则启用/禁用控制

\- ✅ 内置测试和管理命令



\## 命令



| 命令 | 说明 |

|------|------|

| `/rf\_test <文本>` | 测试规则效果 |

| `/rf\_list` | 查看已加载规则 |

| `/rf\_reload` | 重新加载配置 |

| `/rf\_help` | 显示帮助 |



\## 配置示例



```json

\[

&nbsp; {

&nbsp;   "name": "移除思考标签",

&nbsp;   "pattern": "<think>\[\\\\s\\\\S]\*?</think>",

&nbsp;   "replacement": "",

&nbsp;   "enabled": true,

&nbsp;   "flags": "s"

&nbsp; },

&nbsp; {

&nbsp;   "name": "移除Markdown粗体",

&nbsp;   "pattern": "\\\\\*\\\\\*(\[^\*]+)\\\\\*\\\\\*",

&nbsp;   "replacement": "\\\\1",

&nbsp;   "enabled": true,

&nbsp;   "flags": ""

&nbsp; },

&nbsp; {

&nbsp;   "name": "移除代码块",

&nbsp;   "pattern": "```\[a-zA-Z]\*\\\\n?(\[\\\\s\\\\S]\*?)```",

&nbsp;   "replacement": "\\\\1",

&nbsp;   "enabled": true,

&nbsp;   "flags": ""

&nbsp; }

]

