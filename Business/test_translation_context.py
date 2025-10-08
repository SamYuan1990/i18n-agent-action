import os
import tempfile
import unittest
from unittest.mock import patch

import yaml
from Business.translateConfig import (
    TranslationContext,
    load_translation_config,
)


class TestTranslationContext(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_config = {
            "Role": "Test Role",
            "Situation": "Test Situation",
            "Action": "Test Action",
            "Task_steps": ["step1", "step2"],
            "Quality_assurance": ["qa1", "qa2"],
            "Output_structure": {"test": "structure"},
            "self_evaluate_vars": {"var1": "value1"},
            "sys_prompt": "Custom system prompt",
        }

        # 创建临时配置文件
        self.temp_config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        yaml.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()

        # 创建另一个临时配置文件用于测试不同的配置
        self.another_config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        another_config = {"Role": "Another Role", "Situation": "Another Situation"}
        yaml.dump(another_config, self.another_config_file)
        self.another_config_file.close()

    def tearDown(self):
        """测试后的清理"""
        # 删除临时配置文件
        for file_path in [self.temp_config_file.name, self.another_config_file.name]:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_init_with_default_values(self):
        """测试使用默认值初始化"""
        context = TranslationContext(target_language="zh")

        self.assertEqual(context.target_language, "zh")
        self.assertIsNone(context.file_list)
        self.assertIsNone(context.doc_folder)
        self.assertIsNone(context.reserved_word)
        self.assertTrue(context.disclaimers)

        # 检查PromptGen默认属性
        self.assertIn("professional translator", context.Role)
        self.assertIn("translating diverse content", context.Situation)
        self.assertIn("preserve the original meaning", context.Action)
        self.assertTrue(len(context.Task_steps) > 0)
        self.assertTrue(len(context.Quality_assurance) > 0)
        self.assertIn("content", context.Output_structure)

    def test_init_with_custom_values(self):
        """测试使用自定义值初始化"""
        context = TranslationContext(
            target_language="fr",
            file_list="file1.md,file2.md",
            doc_folder="/test/docs",
            reserved_word="test,reserved",
            disclaimers=False,
        )

        self.assertEqual(context.target_language, "fr")
        self.assertEqual(context.file_list, "file1.md,file2.md")
        self.assertEqual(context.doc_folder, "/test/docs")
        self.assertEqual(context.reserved_word, "test,reserved")
        self.assertFalse(context.disclaimers)

    def test_load_config_with_explicit_path(self):
        """测试使用显式路径加载配置"""
        context = TranslationContext(target_language="zh")

        # 初始配置应为默认配置
        self.assertIn("professional translator", context.Role)

        # 加载配置（使用显式路径）
        result = context.load_config(self.temp_config_file.name)

        # 检查是否成功加载
        self.assertTrue(result)
        self.assertEqual(context.Role, "Test Role")
        self.assertEqual(context.Situation, "Test Situation")
        self.assertEqual(context.Action, "Test Action")

    def test_load_config_with_none_path(self):
        """测试传入None路径时加载配置"""
        context = TranslationContext(target_language="zh")

        # 加载配置（传入None）
        result = context.load_config(None)

        # 检查是否失败（因为None被视为未指定路径）
        self.assertFalse(result)
        # 配置应保持为默认配置
        self.assertIn("professional translator", context.Role)

    def test_load_config_with_empty_string_path(self):
        """测试传入空字符串路径时加载配置"""
        context = TranslationContext(target_language="zh")

        # 加载配置（传入空字符串）
        result = context.load_config("")

        # 检查是否失败（因为空字符串被视为未指定路径）
        self.assertFalse(result)
        # 配置应保持为默认配置
        self.assertIn("professional translator", context.Role)

    def test_load_config_different_paths(self):
        """测试从不同路径加载不同的配置"""
        context = TranslationContext(target_language="zh")

        # 加载第一个配置
        result1 = context.load_config(self.temp_config_file.name)
        self.assertTrue(result1)
        self.assertEqual(context.Role, "Test Role")

        # 加载第二个配置
        result2 = context.load_config(self.another_config_file.name)
        self.assertTrue(result2)
        self.assertEqual(context.Role, "Another Role")
        self.assertEqual(context.Situation, "Another Situation")

    def test_load_config_file_not_exists(self):
        """测试配置文件不存在时加载配置"""
        context = TranslationContext(target_language="zh")

        # 尝试加载配置（文件不存在）
        result = context.load_config("/nonexistent/path/config.yaml")

        # 检查是否失败
        self.assertFalse(result)
        # 配置应保持为默认配置
        self.assertIn("professional translator", context.Role)

    def test_load_config_invalid_yaml(self):
        """测试加载无效的YAML配置文件"""
        # 创建无效的YAML文件
        invalid_yaml_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        invalid_yaml_file.write("invalid: yaml: content: [")
        invalid_yaml_file.close()

        context = TranslationContext(target_language="zh")

        # 尝试加载无效的YAML配置
        result = context.load_config(invalid_yaml_file.name)

        # 检查是否失败
        self.assertFalse(result)
        # 配置应保持为默认配置
        self.assertIn("professional translator", context.Role)

        # 清理
        os.unlink(invalid_yaml_file.name)

    def test_disclaimers_conversion(self):
        """测试disclaimers参数的各种转换"""
        # 测试字符串 "true" 的各种形式
        for true_str in (
            "true",
            "True",
            "TRUE",
            "yes",
            "Yes",
            "YES",
            "y",
            "Y",
            "1",
            "on",
            "On",
            "ON",
        ):
            context = TranslationContext(target_language="zh", disclaimers=true_str)
            self.assertTrue(context.disclaimers)

        # 测试字符串 "false" 的各种形式
        for false_str in (
            "false",
            "False",
            "FALSE",
            "no",
            "No",
            "NO",
            "n",
            "N",
            "0",
            "off",
            "Off",
            "OFF",
            "",
        ):
            context = TranslationContext(target_language="zh", disclaimers=false_str)
            self.assertFalse(context.disclaimers)

        # 测试数字
        context = TranslationContext(target_language="zh", disclaimers=1)
        self.assertTrue(context.disclaimers)

        context = TranslationContext(target_language="zh", disclaimers=0)
        self.assertFalse(context.disclaimers)

        # 测试无效字符串
        with self.assertRaises(ValueError):
            TranslationContext(target_language="zh", disclaimers="invalid")

    def test_load_translation_config_function(self):
        """测试独立的load_translation_config函数"""
        # 测试加载存在的配置文件
        config = load_translation_config(self.temp_config_file.name)
        self.assertEqual(config, self.test_config)

        # 测试加载不存在的配置文件（返回空字典）
        config = load_translation_config("/nonexistent/path/config.yaml")
        self.assertEqual(config, {})

        # 测试不提供路径（使用默认路径config.yaml）
        with patch("os.path.exists", return_value=False):
            config = load_translation_config()
            self.assertEqual(config, {})

    def test_show_config_method(self):
        """测试show_config方法不抛出异常"""
        context = TranslationContext(
            target_language="zh",
            file_list="file1.md,file2.md",
            doc_folder="/test/docs",
            reserved_word="test,reserved",
            disclaimers=True,
        )

        # 确保方法可以正常调用而不抛出异常
        try:
            context.show_config()
        except Exception as e:
            self.fail(f"show_config() 方法抛出异常: {e}")

    def test_prompt_attributes_defaults(self):
        """测试PromptGen属性有正确的默认值"""
        context = TranslationContext(target_language="zh")

        # 检查默认的PromptGen属性
        self.assertIsNotNone(context.Role)
        self.assertIsNotNone(context.Situation)
        self.assertIsNotNone(context.Action)
        self.assertIsNotNone(context.Task_steps)
        self.assertIsNotNone(context.Quality_assurance)
        self.assertIsNotNone(context.Output_structure)

        # 验证具体内容
        self.assertIn("professional translator", context.Role)
        self.assertIn("translating diverse content", context.Situation)
        self.assertIn("preserve the original meaning", context.Action)

    def test_file_list_properties(self):
        """测试file_list相关属性"""
        context = TranslationContext(
            target_language="zh", file_list="file1.md,file2.md,file3.md"
        )

        # 测试raw_file_list返回原始字符串
        self.assertEqual(context.raw_file_list, "file1.md,file2.md,file3.md")

        # 测试file_list属性（当前实现返回相同值）
        self.assertEqual(context.file_list, "file1.md,file2.md,file3.md")

    def test_none_file_list(self):
        """测试file_list为None的情况"""
        context = TranslationContext(target_language="zh")

        self.assertIsNone(context.file_list)
        self.assertIsNone(context.raw_file_list)

    def test_config_inheritance_from_promptgen(self):
        """测试从PromptGen继承的配置相关功能"""
        context = TranslationContext(target_language="zh")

        # 测试配置加载方法存在
        self.assertTrue(hasattr(context, "load_config"))
        self.assertTrue(hasattr(context, "get_config"))

        # 测试系统提示生成方法存在
        self.assertTrue(hasattr(context, "to_sys_prompt"))
        self.assertTrue(hasattr(context, "to_task_prompt"))

    def test_custom_sys_prompt_loading(self):
        """测试自定义系统提示的加载"""
        context = TranslationContext(target_language="zh")

        # 加载包含自定义系统提示的配置
        result = context.load_config(self.temp_config_file.name)
        self.assertTrue(result)

        # 检查是否设置了自定义系统提示
        self.assertTrue(hasattr(context, "_use_custom_sys_prompt"))
        self.assertTrue(hasattr(context, "_custom_sys_prompt"))

    def test_prompt_generation_methods(self):
        """测试提示生成方法"""
        context = TranslationContext(target_language="zh")

        # 测试系统提示生成
        sys_prompt = context.to_sys_prompt()
        self.assertIsInstance(sys_prompt, str)
        self.assertIn("professional translator", sys_prompt)

        # 测试任务提示生成
        task_prompt = context.to_task_prompt("Translate this text")
        self.assertIsInstance(task_prompt, str)
        self.assertIn("Translate this text", task_prompt)

    def test_evaluate_vars_functionality(self):
        """测试评估变量功能"""
        context = TranslationContext(target_language="zh")

        # 测试更新评估变量
        test_vars = {"test_var": "test_value"}
        context.update_evaluate_vars(test_vars)

        # 测试获取评估变量
        retrieved_vars = context.get_evaluate_vars()
        self.assertEqual(retrieved_vars["test_var"], "test_value")


if __name__ == "__main__":
    unittest.main()
