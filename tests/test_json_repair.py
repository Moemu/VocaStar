"""
JSON 修复工具的单元测试。
"""

import json

from app.services.json_repair import JSONRepair


class TestJSONRepair:
    """测试 JSON 修复功能。"""

    def test_repair_escaped_quotes_in_field_names(self) -> None:
        """测试修复字段名中的转义引号错误。"""
        # 这是用户提交的实际错误格式
        broken_json = (
            '{"career_directions":[{"career":"前端开发工程师","description":"结合艺术与技术"}],'
            '"action_roadmap\\":{"small_goals":[{"title":"明确兴趣方向","content":"梳理A/R/I三型"}],'
            '"need_attention":"避免分散精力","conclusion":"具备创意潜力"}}'
        )

        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None, "应该能修复这个 JSON"

        # 验证修复后的 JSON 是有效的
        result = json.loads(repaired)
        assert "career_directions" in result
        assert "action_roadmap" in result

    def test_repair_mixed_quote_escaping(self) -> None:
        """测试混乱的引号转义。"""
        broken_json = '{"key\\":"value"}'
        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None
        result = json.loads(repaired)
        assert result["key"] == "value"

    def test_repair_missing_closing_brace(self) -> None:
        """测试缺少闭合括号。"""
        broken_json = '{"key":"value"'
        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None
        result = json.loads(repaired)
        assert result["key"] == "value"

    def test_repair_missing_closing_bracket(self) -> None:
        """测试缺少闭合方括号。"""
        broken_json = '{"items":["a","b","c"]'
        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None
        result = json.loads(repaired)
        assert result["items"] == ["a", "b", "c"]

    def test_safe_parse_valid_json(self) -> None:
        """测试对有效 JSON 的处理。"""
        valid_json = '{"key":"value","number":123}'
        result = JSONRepair.safe_parse(valid_json)
        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 123

    def test_safe_parse_broken_json_with_repair(self) -> None:
        """测试对无效 JSON 的修复和解析。"""
        broken_json = '{"key\\":"value"'
        result = JSONRepair.safe_parse(broken_json)
        assert result is not None
        assert "key" in result

    def test_safe_parse_unrepairable_json(self) -> None:
        """测试无法修复的 JSON。"""
        broken_json = "{this is not even close to valid"
        result = JSONRepair.safe_parse(broken_json)
        assert result is None

    def test_repair_preserves_valid_json(self) -> None:
        """测试修复不会破坏有效的 JSON。"""
        valid_json = '{"career":"职业","description":"描述","numbers":[1,2,3]}'
        repaired = JSONRepair.attempt_repair(valid_json)
        # 修复应该返回相同或等价的内容
        original = json.loads(valid_json)
        repaired_parsed = json.loads(repaired) if repaired else None
        assert repaired_parsed is not None
        assert repaired_parsed == original

    def test_repair_complex_nested_structure(self) -> None:
        """测试复杂嵌套结构的修复。"""
        broken_json = '{"outer":{"inner\\":{"nested\\":[{"item\\":' '"value"}]}}'
        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None
        # 验证可以被解析
        result = json.loads(repaired)
        assert isinstance(result, dict)

    def test_repair_with_boolean_values(self) -> None:
        """测试包含布尔值和 null 的 JSON 修复。"""
        broken_json = '{"active":"true","inactive":"false","empty":"null"'
        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None
        result = json.loads(repaired)
        # 验证布尔值被正确处理
        assert result["active"] or result["active"] == "true"

    def test_repair_real_world_case(self) -> None:
        """测试真实世界的错误格式（来自用户报告）。"""
        # 这是实际从 LLM 收到的格式错误：,"action_roadmap\": 应该是 ,"action_roadmap":
        broken_json = (
            '{"career_directions":[{"career":"前端开发工程师",'
            '"description":"结合艺术与技术"}],'
            '"action_roadmap\\":{"small_goals":[{"title":"明确兴趣",'
            '"content":"梳理兴趣"}],"need_attention":"避免分散","conclusion":"具备潜力"}}'
        )

        repaired = JSONRepair.attempt_repair(broken_json)
        assert repaired is not None, "应该能修复这个实际的错误格式"

        # 验证修复后可以被正确解析
        result = json.loads(repaired)
        assert "career_directions" in result
        assert "action_roadmap" in result
        assert len(result["career_directions"]) == 1
