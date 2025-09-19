import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open
from Business.translateConfig import TranslationContext, load_translation_config, DEFAULT_CONFIG

class TestTranslationContext(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_config = {
            "prompts": {
                "config_analysis": "Test config analysis prompt",
                "json_schema": "Test json schema",
                "translator": "Test translator prompt",
                "analysis": "Test analysis prompt"
            }
        }
        
        # 创建临时配置文件
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()
        
    def tearDown(self):
        """测试后的清理"""
        # 删除临时配置文件
        if os.path.exists(self.temp_config_file.name):
            os.unlink(self.temp_config_file.name)
    
    def test_init_with_default_values(self):
        """测试使用默认值初始化"""
        context = TranslationContext(target_language="zh")
        
        self.assertEqual(context.target_language, "zh")
        self.assertIsNone(context.file_list)
        self.assertIsNone(context.configfile_path)
        self.assertIsNone(context.doc_folder)
        self.assertIsNone(context.reserved_word)
        self.assertEqual(context.max_files, 20)
        self.assertTrue(context.disclaimers)
        self.assertEqual(context.config, DEFAULT_CONFIG)
    
    def test_init_with_custom_values(self):
        """测试使用自定义值初始化"""
        context = TranslationContext(
            target_language="fr",
            file_list="file1.md,file2.md",
            configfile_path=self.temp_config_file.name,
            doc_folder="/test/docs",
            reserved_word="test,reserved",
            max_files=10,
            disclaimers=False
        )
        
        self.assertEqual(context.target_language, "fr")
        self.assertEqual(context.file_list, "file1.md,file2.md")
        self.assertEqual(context.configfile_path, self.temp_config_file.name)
        self.assertEqual(context.doc_folder, "/test/docs")
        self.assertEqual(context.reserved_word, "test,reserved")
        self.assertEqual(context.max_files, 10)
        self.assertFalse(context.disclaimers)
        self.assertEqual(context.config, DEFAULT_CONFIG)  # 默认配置，未加载自定义配置
    
    def test_load_config_success(self):
        """测试成功加载配置文件"""
        context = TranslationContext(
            target_language="zh",
            configfile_path=self.temp_config_file.name
        )
        
        # 初始配置应为默认配置
        self.assertEqual(context.config, DEFAULT_CONFIG)
        
        # 加载配置
        result = context.load_config()
        
        # 检查是否成功加载
        self.assertTrue(result)
        self.assertEqual(context.config, self.test_config)
    
    def test_load_config_no_path(self):
        """测试没有配置文件路径时加载配置"""
        context = TranslationContext(target_language="zh")
        
        # 初始配置应为默认配置
        self.assertEqual(context.config, DEFAULT_CONFIG)
        
        # 尝试加载配置（没有配置文件路径）
        result = context.load_config()
        
        # 检查是否失败
        self.assertFalse(result)
        # 配置应保持为默认配置
        self.assertEqual(context.config, DEFAULT_CONFIG)
    
    def test_load_config_file_not_exists(self):
        """测试配置文件不存在时加载配置"""
        context = TranslationContext(
            target_language="zh",
            configfile_path="/nonexistent/path/config.yaml"
        )
        
        # 初始配置应为默认配置
        self.assertEqual(context.config, DEFAULT_CONFIG)
        
        # 尝试加载配置（文件不存在）
        result = context.load_config()
        # 配置应保持为默认配置
        self.assertEqual(context.config, DEFAULT_CONFIG)
    
    def test_load_config_invalid_yaml(self):
        """测试加载无效的YAML配置文件"""
        # 创建无效的YAML文件
        invalid_yaml_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        invalid_yaml_file.write("invalid: yaml: content: [")
        invalid_yaml_file.close()
        
        context = TranslationContext(
            target_language="zh",
            configfile_path=invalid_yaml_file.name
        )
        
        # 尝试加载无效的YAML配置
        result = context.load_config()
        # 配置应保持为默认配置
        self.assertEqual(context.config, DEFAULT_CONFIG)
        
        # 清理
        os.unlink(invalid_yaml_file.name)
    
    def test_disclaimers_conversion(self):
        """测试disclaimers参数的各种转换"""
        # 测试字符串 "true" 的各种形式
        for true_str in ("true", "True", "TRUE", "yes", "Yes", "YES", "y", "Y", "1", "on", "On", "ON"):
            context = TranslationContext(target_language="zh", disclaimers=true_str)
            self.assertTrue(context.disclaimers)
        
        # 测试字符串 "false" 的各种形式
        for false_str in ("false", "False", "FALSE", "no", "No", "NO", "n", "N", "0", "off", "Off", "OFF", ""):
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
    
    def test_max_files_conversion(self):
        """测试max_files参数的各种转换"""
        # 测试正常整数
        context = TranslationContext(target_language="zh", max_files=5)
        self.assertEqual(context.max_files, 5)
        
        # 测试字符串数字
        context = TranslationContext(target_language="zh", max_files="10")
        self.assertEqual(context.max_files, 10)
        
        # 测试无效值（使用默认值20）
        context = TranslationContext(target_language="zh", max_files="invalid")
        self.assertEqual(context.max_files, 20)
        
        context = TranslationContext(target_language="zh", max_files=None)
        self.assertEqual(context.max_files, 20)
    
    def test_load_translation_config_function(self):
        """测试独立的load_translation_config函数"""
        # 测试加载存在的配置文件
        config = load_translation_config(self.temp_config_file.name)
        self.assertEqual(config, self.test_config)
        
        # 测试加载不存在的配置文件（使用默认配置）
        config = load_translation_config("/nonexistent/path/config.yaml")
        self.assertEqual(config, DEFAULT_CONFIG)
        
        # 测试不提供路径（使用默认路径）
        with patch('os.path.exists', return_value=False):
            config = load_translation_config()
            self.assertEqual(config, DEFAULT_CONFIG)


if __name__ == '__main__':
    unittest.main()