import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup

# 假设这些模块在测试环境中可用
from AgentUtils.Agent import Agent
from .metric import (
    FILES_TRANSLATED,
    SOURCE_FILE_MISSING,
    TARGET_FILE_EXISTS,
    TRANSLATION_REQUESTS,
)
from .utils import MergePN
from .translate import translateAgent

class TestTranslateAgent:
    """translateAgent 类的测试套件"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """模拟LLM客户端"""
        return Mock()
    
    @pytest.fixture
    def mock_span_mgr(self):
        """模拟span管理器"""
        return Mock()
    
    @pytest.fixture
    def agent(self, mock_llm_client, mock_span_mgr):
        """创建测试用的agent实例"""
        return translateAgent(mock_llm_client, mock_span_mgr)
    
    @pytest.fixture
    def translation_context(self):
        """创建测试用的TranslationContext"""
        context = Mock()
        context.reserved_word = "TEST"
        context.config = {
            "prompts": {
                "translator": "Translate the following content"
            }
        }
        context.disclaimers = True
        context.doc_folder = "/test/docs"
        context.file_list = None
        return context
    
    @pytest.fixture
    def temp_files(self):
        """创建临时文件用于测试"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建源文件
            source_file = os.path.join(temp_dir, "source.md")
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write("# Test Document\n\nThis is a test content.")
            
            target_file = os.path.join(temp_dir, "target.md")
            
            yield {
                'source_file': source_file,
                'target_file': target_file,
                'temp_dir': temp_dir
            }
    
    def test_is_web_url(self, agent):
        """测试URL识别功能"""
        # 测试HTTP URL
        assert agent.is_web_url("http://example.com") == True
        assert agent.is_web_url("https://example.com") == True
        
        # 测试www开头的URL
        assert agent.is_web_url("www.example.com") == True
        
        # 测试域名格式
        assert agent.is_web_url("example.com") == True
        assert agent.is_web_url("sub.domain.co.uk") == True
        
        # 测试非URL文本
        assert agent.is_web_url("This is not a URL") == False
        assert agent.is_web_url("") == False
        assert agent.is_web_url("file:///local/path") == False
    
    def test_normalize_url(self, agent):
        """测试URL规范化"""
        # 测试已有协议的情况
        assert agent.normalize_url("http://example.com") == "http://example.com"
        assert agent.normalize_url("https://example.com") == "https://example.com"
        
        # 测试需要添加协议的情况
        assert agent.normalize_url("example.com") == "https://example.com"
        assert agent.normalize_url("www.example.com") == "https://www.example.com"
        
        # 测试去除空白
        assert agent.normalize_url("  example.com  ") == "https://example.com"
    
    def test_extract_text_content(self, agent):
        """测试HTML文本提取"""
        # 创建测试HTML
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <script>console.log('ignore this');</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <h1>Main Title</h1>
                <p>This is a paragraph with <strong>bold text</strong>.</p>
                <nav>Navigation should be ignored</nav>
                <footer>Footer should be ignored</footer>
            </body>
        </html>
        """
        
        extracted_text = agent.extract_text_content(html_content)
        
        # 验证脚本和样式被移除
        assert "console.log" not in extracted_text
        assert "color: red" not in extracted_text
        
        # 验证导航和页脚被移除
        assert "Navigation" not in extracted_text
        assert "Footer" not in extracted_text
        
        # 验证主要内容被保留
        assert "Main Title" in extracted_text
        assert "This is a paragraph with bold text" in extracted_text
    
    @patch('requests.Session')
    def test_translate_url_or_text_with_url(self, mock_session, agent, translation_context):
        """测试URL翻译路径"""
        # 模拟网络响应
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 模拟translate方法
        with patch.object(agent, 'translate') as mock_translate:
            mock_translate.return_value = "Translated content"
            
            result = agent.translate_URLOrText(
                translation_context, 
                "Spanish", 
                "http://example.com", 
                Mock()
            )
            
            # 验证网络请求
            mock_session_instance.get.assert_called_once()
            
            # 验证调用了translate方法
            mock_translate.assert_called_once()
            
            assert result == "Translated content"
    
    def test_translate_url_or_text_with_text(self, agent, translation_context):
        """测试纯文本翻译路径"""
        test_text = "This is plain text content"
        
        with patch.object(agent, 'translate') as mock_translate:
            mock_translate.return_value = "Translated text"
            
            mock_span = Mock()

            result = agent.translate_URLOrText(
                translation_context,
                "French",
                test_text,
                Mock()
            )
            
            # 验证直接调用了translate方法
            from unittest.mock import ANY
            mock_translate.assert_called_once_with(
                ANY, "French", test_text, ANY  # 使用相同的 mock span
            )
                
            assert result == "Translated text"
    
    def test_translate_chunking(self, agent, translation_context):
        """测试内容分块翻译"""
        # 创建长文本（超过3000字符）
        long_content = "A" * 5000
        
        # 模拟LLM响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "content": "Translated chunk",
            "metadata": {"chunk": 1, "total": 2},
            "proper_nouns": "noun1, noun2"
        })
        
        with patch.object(agent, 'talk_to_LLM_Json') as mock_llm_call:
            mock_llm_call.return_value = mock_response
            
            # 模拟 get_legal_info 方法返回字符串
            with patch.object(agent, 'get_legal_info', return_value="Legal disclaimer text"):
                result = agent.translate(translation_context, "German", long_content, Mock())
                
                # 验证LLM被调用了2次（5000字符分成2块）
                assert mock_llm_call.call_count == 2
                
                # 验证结果包含翻译后的内容
                assert "Translated chunk" in result
                # 验证结果包含法律信息（因为 disclaimers 为 True）
                assert "Legal disclaimer text" in result
    
    def test_should_refresh(self, agent, temp_files):
        """测试文件刷新判断逻辑"""
        # 目标文件不存在时应该刷新
        assert agent.should_refresh(temp_files['target_file']) == True
        
        # 创建目标文件
        with open(temp_files['target_file'], 'w') as f:
            f.write("content")
        
        # 目标文件存在时不应该刷新
        assert agent.should_refresh(temp_files['target_file']) == False
        
        # force_refresh为True时应该刷新
        assert agent.should_refresh(temp_files['target_file'], force_refresh=True) == True
    
    @patch('AgentUtils.tomarkdown.getfilecontent')
    def test_translate_element_source_missing(self, mock_getfilecontent, agent, translation_context):
        """测试源文件缺失的情况"""
        mock_getfilecontent.side_effect = FileNotFoundError()
        
        element = {
            "source_file": "missing.md",
            "target_file": "target.md",
            "target_language": "Spanish"
        }
        
        # 验证不会抛出异常
        agent.translate_element(translation_context, element, Mock())
        
        # 可以添加对metrics的验证
        # 这里需要根据实际的metrics实现来编写断言
    
    @patch('AgentUtils.tomarkdown.getfilecontent')
    def test_translate_element_target_exists(self, mock_getfilecontent, agent, translation_context, temp_files):
        """测试目标文件已存在的情况"""
        # 创建目标文件
        with open(temp_files['target_file'], 'w') as f:
            f.write("existing content")
        
        element = {
            "source_file": temp_files['source_file'],
            "target_file": temp_files['target_file'],
            "target_language": "French"
        }
        
        # 模拟文件内容读取
        mock_getfilecontent.return_value = "Source content"
        
        # 验证不会进行翻译（因为目标文件已存在）
        with patch.object(agent, 'translate_file') as mock_translate:
            agent.translate_element(translation_context, element, Mock())
            
            # 验证没有调用翻译方法
            mock_translate.assert_not_called()
    
    def test_translate_files_dry_run(self, agent):
        """测试dry run模式"""
        # 模拟dryRun返回True
        with patch.object(agent, 'dryRun', return_value=True):
            with patch.object(agent, 'translate_element') as mock_translate:
                json_todo_list = {"todo": [{"file": "test.md"}]}
                
                agent.translate_files(json_todo_list, Mock(), Mock())
                
                # 验证没有进行翻译
                mock_translate.assert_not_called()
    
    def test_translate_files_multithreading(self, agent):
        """测试多线程文件翻译"""
        # 模拟dryRun返回False
        with patch.object(agent, 'dryRun', return_value=False):
            # 创建测试任务列表
            json_todo_list = {
                "todo": [
                    {"source_file": "file1.md", "target_file": "target1.md", "target_language": "Spanish"},
                    {"source_file": "file2.md", "target_file": "target2.md", "target_language": "French"}
                ]
            }
            
            # 模拟translate_element方法
            with patch.object(agent, 'translate_element') as mock_translate_element:
                agent.translate_files(json_todo_list, Mock(), Mock())
                
                # 验证为每个元素调用了翻译方法
                assert mock_translate_element.call_count == 2
    
    def test_error_handling_in_translate(self, agent, translation_context):
        """测试翻译过程中的错误处理"""
        # 模拟LLM调用抛出异常
        with patch.object(agent, 'talk_to_LLM_Json') as mock_llm_call:
            mock_llm_call.side_effect = Exception("LLM error")
            
            with pytest.raises(Exception):
                agent.translate(translation_context, "Chinese", "Test content", Mock())
    
    @patch('requests.Session')
    def test_url_translation_network_error(self, mock_session, agent, translation_context):
        """测试URL翻译时的网络错误"""
        # 模拟网络错误
        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = requests.RequestException("Network error")
        mock_session.return_value = mock_session_instance
        
        with pytest.raises(requests.RequestException):
            agent.translate_URLOrText(
                translation_context,
                "Japanese", 
                "http://example.com", 
                Mock()
            )


# 运行测试的示例（通常放在单独的文件中）
if __name__ == "__main__":
    pytest.main([__file__, "-v"])