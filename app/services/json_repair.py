"""
JSON 修复工具，用于处理 LLM 返回的格式不正确的 JSON。
"""

import json
import re
from typing import Optional


class JSONRepair:
    """处理常见的 LLM JSON 格式错误。"""

    @staticmethod
    def attempt_repair(text: str) -> Optional[str]:
        """
        尝试修复常见的 JSON 格式错误。

        常见的修复项：
        1. 未转义的引号混用：\\" 应该是 "
        2. 字段名转义错误：\"key\\" 应该是 "key"
        3. 末尾缺少闭合的括号/引号
        4. 多余的逗号
        5. 错误的字段名转义：,"key\": → ,"key":

        Args:
            text: 原始文本

        Returns:
            修复后的 JSON 文本，如果无法修复则返回 None
        """
        if not text or not isinstance(text, str):
            return None

        original = text

        # 第零步：处理最常见的错误模式 ,"key\":
        # 这会导致 Unterminated string 错误
        text = re.sub(r'([\{,]\s*)"([^"]+)\\":', r'\1"\2":', text)

        # 第一步：修复转义错误
        # 处理 \"fieldname\": 这种情况，应该是 "fieldname":
        text = re.sub(r'([\{,]\s*)\\\"([^"\\]+)\\\"\s*:', r'\1"\2":', text)

        # 处理混乱的引号：},"key\" 应该是 },"key"
        text = re.sub(r'([,\{]\s*)\\\"([^"\\]+)\\\"\s*([:\}])', r'\1"\2"\3', text)

        # 处理更复杂的混乱情况：},"action_roadmap\": 应该是 },"action_roadmap":
        text = re.sub(r'([\{,]\s*)"([^"]+)\\\"\s*:', r'\1"\2":', text)
        text = re.sub(r'([\{,]\s*)\\\"([^"\\]+)\\\"\s*:', r'\1"\2":', text)

        # 第二步：修复数值和布尔值
        # 确保 true/false/null 不被引号包围
        text = re.sub(r':\s*"(true|false|null)"', r": \1", text)

        # 第三步：修复末尾不完整的情况
        # 计数括号和方括号，看是否需要补全
        open_braces = text.count("{")
        close_braces = text.count("}")
        if open_braces > close_braces:
            text += "}" * (open_braces - close_braces)

        open_brackets = text.count("[")
        close_brackets = text.count("]")
        if open_brackets > close_brackets:
            text += "]" * (open_brackets - close_brackets)

        # 第四步：尝试解析验证修复是否成功
        try:
            json.loads(text)
            return text if text != original else text
        except json.JSONDecodeError:
            # 如果仍然无法解析，返回 None
            return None

    @staticmethod
    def safe_parse(text: str) -> Optional[dict]:
        """
        安全解析 JSON，先尝试直接解析，失败后尝试修复。

        Args:
            text: 原始文本

        Returns:
            解析成功返回字典，失败返回 None
        """
        # 先尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试修复后再解析
        repaired = JSONRepair.attempt_repair(text)
        if repaired is None:
            return None

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            return None
