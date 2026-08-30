from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import LLMResponse
from astrbot.api import logger, AstrBotConfig
import re15
from typing import List, Dict, Any, Tuple
from astrbot.api.message_components import Plain

@register(
    "astrbot_plugin_regex_filter",
    "YourName",
    "自定义正则过滤 LLM 输出 - 支持预设规则和自定义规则",
    "1.0.2",
    "https://github.com/yourname/astrbot_plugin_regex_filter"
)
class RegexFilterPlugin(Star):
    
    PRESET_RULES: Dict[str, Tuple[str, str, int, str]] = {
        "remove_think_tag": (r"<think>[\s\S]*?</think>", "", re.DOTALL, "思考标签"),
        "remove_markdown_bold": (r"\*\*([^*]+)\*\*", r"\1", 0, "Markdown粗体"),
        "remove_markdown_italic": (r"(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)", r"\1", 0, "Markdown斜体"),
        "remove_markdown_code_block": (r"```(?:[a-zA-Z0-9+\-]*\n?)?([\s\S]*?)```", r"\1", 0, "Markdown代码块"),
        "remove_markdown_inline_code": (r"`([^`]+)`", r"\1", 0, "Markdown行内代码"),
        "remove_markdown_headers": (r"^#{1,6}\s+(.*)$", r"\1", re.MULTILINE, "Markdown标题"),
        "remove_markdown_links": (r"\[([^\]]+)\]\([^)]+\)", r"\1", 0, "Markdown链接"),
        "remove_markdown_quotes": (r"^>\s+(.*)$", r"\1", re.MULTILINE, "Markdown引用"),
        "remove_markdown_lists": (r"^\s*[-*+]\s+(.*)$", r"\1", re.MULTILINE, "Markdown列表"),
        "remove_all_html_tags": (r"<[^>]+>", "", 0, "HTML标签"),
    }
    
    # ========== 关键修改点：__init__ 必须包含 config 参数 ==========
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.plugin_config = config if config else {}
        self.compiled_preset_rules: List[Dict[str, Any]] = []
        self.compiled_custom_rules: List[Dict[str, Any]] = []
        self._load_rules()
    
    # ========== 关键修改点：直接返回 self.plugin_config ==========
    def _get_config(self) -> Dict[str, Any]:
        return self.plugin_config
    
    def _load_rules(self):
        config = self._get_config()
        logger.info(f"[Regex Filter] 🔍 插件配置: {config}")
        self._load_preset_rules(config)
        self._load_custom_rules(config)
        total = len(self.compiled_preset_rules) + len(self.compiled_custom_rules)
        logger.info(f"[Regex Filter] 规则加载完成: 预设 {len(self.compiled_preset_rules)} 条, 自定义 {len(self.compiled_custom_rules)} 条, 共 {total} 条")
    
    def _load_preset_rules(self, config: Dict[str, Any]):
        self.compiled_preset_rules = []
        for rule_key, rule_def in self.PRESET_RULES.items():
            if not config.get(rule_key, False):
                continue
            pattern_str, replacement, flags, description = rule_def
            try:
                compiled_pattern = re.compile(pattern_str, flags)
                self.compiled_preset_rules.append({
                    "name": f"[预设] {description}",
                    "pattern": compiled_pattern,
                    "replacement": replacement,
                    "type": "preset"
                })
                logger.info(f"[Regex Filter] ✓ 预设规则已启用: {description}")
            except re.error as e:
                logger.error(f"[Regex Filter] ✗ 预设规则编译失败 [{description}]: {e}")
    
    def _load_custom_rules(self, config: Dict[str, Any]):
        self.compiled_custom_rules = []
        for i in range(1, 21):
            prefix = f"custom_rule_{i}"
            if not config.get(f"{prefix}_enabled", False):
                continue
            pattern_str = config.get(f"{prefix}_pattern", "").strip()
            if not pattern_str:
                continue
            name = config.get(f"{prefix}_name", f"自定义规则{i}")
            replacement = config.get(f"{prefix}_replacement", "")
            flags_str = config.get(f"{prefix}_flags", "")
            try:
                flags = self._parse_flags(flags_str)
                compiled_pattern = re.compile(pattern_str, flags)
                self.compiled_custom_rules.append({
                    "name": f"[自定义] {name}",
                    "pattern": compiled_pattern,
                    "replacement": replacement,
                    "type": "custom"
                })
                logger.info(f"[Regex Filter] ✓ 自定义规则已加载: {name}")
            except re.error as e:
                logger.error(f"[Regex Filter] ✗ 自定义规则编译失败 [{name}]: {e}")
    
    def _parse_flags(self, flags_str: str) -> int:
        flags = 0
        for char in str(flags_str).upper():
            if char == 'I': flags |= re.IGNORECASE
            elif char == 'M': flags |= re.MULTILINE
            elif char == 'S': flags |= re.DOTALL
        return flags
    
    def _get_all_rules(self) -> List[Dict[str, Any]]:
        return self.compiled_preset_rules + self.compiled_custom_rules
   # ... 前面的代码保持不变 ...

    # 提取出的公共过滤方法
    def _apply_rules_to_text(self, text: str) -> Tuple[str, List[str]]:
        all_rules = self._get_all_rules()
        cleaned_text = text
        applied_rules = []
        for rule in all_rules:
            try:
                new_text = rule["pattern"].sub(rule["replacement"], cleaned_text)
                if new_text != cleaned_text:
                    applied_rules.append(rule["name"])
                    cleaned_text = new_text
            except Exception as e:
                logger.error(f"[Regex Filter] 规则执行错误 [{rule['name']}]: {e}")
        return cleaned_text, applied_rules

    # 1. 保留原有的 LLM 响应监听（处理常规对话）
#    @filter.on_llm_response()
#    async def on_llm_resp(self, event: AstrMessageEvent, resp: LLMResponse):
#        config = self._get_config()
#        if not config.get("enable_plugin", True) or not resp or not resp.completion_text:
#            return
        
#        cleaned_text, applied_rules = self._apply_rules_to_text(resp.completion_text)
        
 #       if resp.completion_text != cleaned_text:
 #           resp.completion_text = cleaned_text
 #           if config.get("enable_logging", True):
  #              logger.warning(f"[Regex Filter] (LLM响应) 已应用规则: {', '.join(applied_rules)}")

    # 2. 参考 splitter 插件，新增装饰结果监听（处理主动消息）
    @filter.on_decorating_result(priority=100000000000000001)
    async def on_decorating_result(self, event: AstrMessageEvent):
        config = self._get_config()
        if not config.get("enable_plugin", True):
            return

        result = event.get_result() # 获取装饰流程中的消息链
        if not result or not result.chain:
            return

        any_changed = False
        all_applied = []
        
        # 遍历消息链，只处理纯文本部分
        for component in result.chain:
            if isinstance(component, Plain):
                original_text = component.text
                cleaned_text, applied = self._apply_rules_to_text(original_text)
                if original_text != cleaned_text:
                    component.text = cleaned_text
                    any_changed = True
                    all_applied.extend(applied)
        
        if any_changed and config.get("enable_logging", True):
            logger.warning(f"[Regex Filter] (装饰器) 已应用规则: {', '.join(set(all_applied))}")

    
    @filter.command("rf_reload")
    async def reload_rules(self, event: AstrMessageEvent):
        self._load_rules()
        yield event.plain_result(f"✅ 规则已重新加载,当前启用: {len(self._get_all_rules())} 条")
    
    @filter.command("rf_list")
    async def list_rules(self, event: AstrMessageEvent):
        all_rules = self._get_all_rules()
        if not all_rules:
            yield event.plain_result("📋 当前没有启用任何规则")
            return
        msg = f"📋 已启用 {len(all_rules)} 条规则:\n\n"
        for i, rule in enumerate(all_rules, 1):
            msg += f"  {i}. {rule['name']}\n"
        yield event.plain_result(msg)
    
    @filter.command("rf_test")
    async def test_regex(self, event: AstrMessageEvent, text: str = ""):
        if not text:
            yield event.plain_result("📖 用法: /rf_test <测试文本>")
            return
        all_rules = self._get_all_rules()
        if not all_rules:
            yield event.plain_result("❌ 当前没有启用任何规则")
            return
        text = text.replace('\\n', '\n')
        result = text
        applied = []
        for rule in all_rules:
            try:
                new_result = rule["pattern"].sub(rule["replacement"], result)
                if new_result != result:
                    applied.append(rule["name"])
                    result = new_result
            except Exception as e:
                applied.append(f"{rule['name']}(❌)")
        msg = (
            f"📝 原文:\n{text}\n\n"
            f"✨ 处理后:\n{result}\n\n"
            f"📋 应用规则: {', '.join(applied) if applied else '无匹配'}"
        )

        yield event.plain_result(msg)




