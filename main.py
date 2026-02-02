from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import LLMResponse
from astrbot.api import logger, AstrBotConfig
import re
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
    
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.plugin_config = config if config else {}
        self.compiled_preset_rules: List[Dict[str, Any]] = []
        self.compiled_custom_rules: List[Dict[str, Any]] = []
        self._load_rules()
    
    def _get_config(self) -> Dict[str, Any]:
        return self.plugin_config
    
    def _load_rules(self):
        config = self._get_config()
        # logger.info(f"[Regex Filter] 🔍 插件配置: {config}") # 调试时可开启
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
        """
        加载自定义规则（适配新的 list 结构配置）
        """
        self.compiled_custom_rules = []
        
        # 获取配置中的 custom_rules 列表，默认为空列表
        custom_rules = config.get("custom_rules", [])
        
        # 容错处理：如果配置不是列表（比如刚升级配置尚未刷新），则跳过
        if not isinstance(custom_rules, list):
            # 兼容旧配置或空配置的情况，不报错，直接返回
            return

        for idx, rule_cfg in enumerate(custom_rules):
            # 确保每一项都是字典
            if not isinstance(rule_cfg, dict):
                continue
                
            # 1. 检查启用状态 (默认为 True)
            if not rule_cfg.get("enabled", True):
                continue
            
            # 2. 获取正则模式
            pattern_str = rule_cfg.get("pattern", "").strip()
            if not pattern_str:
                continue
                
            # 3. 获取其他参数
            name = rule_cfg.get("name", f"规则_{idx+1}")
            replacement = rule_cfg.get("replacement", "")
            flags_str = rule_cfg.get("flags", "")
            
            # 4. 编译正则
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
        if not flags_str:
            return flags
        for char in str(flags_str).upper():
            if char == 'I': flags |= re.IGNORECASE
            elif char == 'M': flags |= re.MULTILINE
            elif char == 'S': flags |= re.DOTALL
        return flags
    
    def _get_all_rules(self) -> List[Dict[str, Any]]:
        return self.compiled_preset_rules + self.compiled_custom_rules

    def _apply_rules_to_text(self, text: str) -> Tuple[str, List[str]]:
        all_rules = self._get_all_rules()
        cleaned_text = text
        applied_rules = []
        
        for rule in all_rules:
            try:
                # 执行替换
                new_text = rule["pattern"].sub(rule["replacement"], cleaned_text)
                if new_text != cleaned_text:
                    applied_rules.append(rule["name"])
                    cleaned_text = new_text
            except Exception as e:
                logger.error(f"[Regex Filter] 规则执行错误 [{rule['name']}]: {e}")
                
        return cleaned_text, applied_rules

    @filter.on_decorating_result(priority=100000000000000001)
    async def on_decorating_result(self, event: AstrMessageEvent):
        config = self._get_config()
        if not config.get("enable_plugin", True):
            return

        result = event.get_result()
        if not result or not result.chain:
            return

        any_changed = False
        all_applied = []
        
        for component in result.chain:
            if isinstance(component, Plain):
                original_text = component.text
                cleaned_text, applied = self._apply_rules_to_text(original_text)
                
                if original_text != cleaned_text:
                    component.text = cleaned_text
                    any_changed = True
                    all_applied.extend(applied)
        
        if any_changed and config.get("enable_logging", True):
            # 去重并在日志中显示
            unique_applied = list(set(all_applied))
            logger.warning(f"[Regex Filter] 已过滤: {', '.join(unique_applied)}")

    @filter.command("rf_reload")
    async def reload_rules(self, event: AstrMessageEvent):
        """重载配置"""
        self._load_rules()
        count = len(self._get_all_rules())
        yield event.plain_result(
