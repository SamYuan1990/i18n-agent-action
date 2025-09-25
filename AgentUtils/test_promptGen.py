import threading
import time
import unittest

from .PromptGen import PromptGen


class TestPromptGen(unittest.TestCase):

    def setUp(self):
        """测试前置设置"""
        self.prompt_gen = PromptGen()
        self.prompt_gen.Role = "AI助手"
        self.prompt_gen.Situation = "帮助用户生成提示词"
        self.prompt_gen.Action = "按照指定格式生成提示"
        self.prompt_gen.Task_steps = ["分析需求", "构建模板", "生成提示"]
        self.prompt_gen.Quality_assurance = ["检查语法", "验证格式"]
        self.prompt_gen.Output_structure = {"key": "value"}
        self.prompt_gen.self_evaluate_vars = {"var1": "value1"}

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.prompt_gen.Role, "AI助手")
        self.assertEqual(self.prompt_gen.Situation, "帮助用户生成提示词")
        self.assertEqual(self.prompt_gen.self_evaluate_vars, {"var1": "value1"})

    def test_template_to_string(self):
        """测试模板字符串替换"""
        template = "Hello $var1 and $var2"
        vars_dict = {"var1": "world", "var2": "python"}
        result = self.prompt_gen._template_to_string(template, vars_dict)
        self.assertEqual(result, "Hello world and python")

    def test_template_to_string_with_missing_vars(self):
        """测试模板字符串替换（缺失变量）"""
        template = "Hello $var1 and $unknown"
        result = self.prompt_gen._template_to_string(template)
        self.assertEqual(result, "Hello value1 and $unknown")

    def test_to_sys_prompt(self):
        """测试系统提示生成"""
        result = self.prompt_gen.to_sys_prompt()
        self.assertIn("AI助手", result)
        self.assertIn("分析需求", result)
        self.assertIn("检查语法", result)
        self.assertIn('"key": "value"', result)

    def test_to_task_prompt(self):
        """测试任务提示生成"""
        task_specific = "生成一个问候提示"
        example = "Hello World"
        evaluate_vars = {"name": "Alice"}

        result = self.prompt_gen.to_task_prompt(
            task_specific=task_specific, example=example, evaluate_vars=evaluate_vars
        )

        self.assertIn("You can reference example: Hello World", result)
        self.assertIn("Here is task content: 生成一个问候提示", result)
        # 检查变量是否已更新
        self.assertIn("value1", self.prompt_gen.self_evaluate_vars.values())
        self.assertIn("Alice", self.prompt_gen.self_evaluate_vars.values())

    def test_update_evaluate_vars(self):
        """测试线程安全的变量更新"""
        self.prompt_gen.update_evaluate_vars({"new_var": "new_value"})
        self.assertEqual(self.prompt_gen.self_evaluate_vars["new_var"], "new_value")
        self.assertEqual(self.prompt_gen.self_evaluate_vars["var1"], "value1")

    def test_get_evaluate_vars(self):
        """测试线程安全的变量获取"""
        vars_copy = self.prompt_gen.get_evaluate_vars()
        self.assertEqual(vars_copy, {"var1": "value1"})
        # 修改副本不应影响原数据
        vars_copy["new_var"] = "new_value"
        self.assertNotIn("new_var", self.prompt_gen.self_evaluate_vars)


class TestPromptGenThreadSafety(unittest.TestCase):
    """测试多线程安全性"""

    def test_thread_safety(self):
        """测试多线程环境下的线程安全"""
        prompt_gen = PromptGen()
        prompt_gen.self_evaluate_vars = {"counter": "0"}

        results = []
        errors = []
        lock = threading.Lock()

        def worker(thread_id):
            """工作线程函数"""
            try:
                for i in range(100):
                    # 每个线程更新自己的变量
                    new_vars = {
                        f"thread_{thread_id}_var": f"value_{i}",
                        "counter": str(
                            int(prompt_gen.get_evaluate_vars().get("counter", "0")) + 1
                        ),
                    }
                    prompt_gen.update_evaluate_vars(new_vars)
                    # 生成提示
                    prompt = prompt_gen.to_task_prompt(
                        f"Task from thread {thread_id}",
                        evaluate_vars={f"temp_{i}": "temp_value"},
                    )
                    with lock:
                        results.append(prompt)
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有错误发生
        self.assertEqual(len(errors), 0, f"发生错误: {errors}")

        # 验证所有提示都生成成功
        self.assertEqual(len(results), 5 * 100)

        # 验证最终状态的一致性
        final_vars = prompt_gen.get_evaluate_vars()
        self.assertIn("counter", final_vars)
        # 计数器应该正确递增（虽然顺序不确定，但值应该合理）

    def test_concurrent_access(self):
        """测试并发访问"""
        prompt_gen = PromptGen()
        prompt_gen.self_evaluate_vars = {"data": "initial"}

        read_results = []
        write_errors = []

        def reader(thread_id):
            """读取线程"""
            for _ in range(50):
                vars_copy = prompt_gen.get_evaluate_vars()
                read_results.append((thread_id, vars_copy.copy()))
                time.sleep(0.001)

        def writer(thread_id):
            """写入线程"""
            for i in range(20):
                try:
                    prompt_gen.update_evaluate_vars(
                        {
                            f"write_{thread_id}": f"value_{i}",
                            "data": f"modified_by_{thread_id}_{i}",
                        }
                    )
                    time.sleep(0.002)
                except Exception as e:
                    write_errors.append(str(e))

        # 创建读写线程
        threads = []
        for i in range(3):  # 3个写线程
            thread = threading.Thread(target=writer, args=(i,))
            threads.append(thread)

        for i in range(5):  # 5个读线程
            thread = threading.Thread(target=reader, args=(i,))
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有写入错误
        self.assertEqual(len(write_errors), 0, f"写入错误: {write_errors}")

        # 验证读取的数据一致性（不应该读取到损坏的数据）
        for thread_id, vars_copy in read_results:
            self.assertIsInstance(vars_copy, dict)
            # 数据应该是完整的字典，没有部分更新的状态


class TestPromptGenEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def test_empty_components(self):
        """测试空组件"""
        prompt_gen = PromptGen()
        result = prompt_gen.to_sys_prompt()
        self.assertIsInstance(result, str)
        self.assertIn("Task methodology", result)

    def test_large_inputs(self):
        """测试大输入"""
        prompt_gen = PromptGen()
        prompt_gen.Task_steps = [f"Step {i}" for i in range(10)]  # 超过7个
        prompt_gen.Quality_assurance = [f"QA {i}" for i in range(10)]

        result = prompt_gen.to_sys_prompt()
        # 应该只显示前7个
        self.assertIn("Step_7", result)
        self.assertNotIn("Step_8", result)

    def test_special_characters(self):
        """测试特殊字符"""
        prompt_gen = PromptGen()
        prompt_gen.Role = "角色$特殊@字符"
        prompt_gen.self_evaluate_vars = {"var$1": "值@特殊"}

        result = prompt_gen.to_sys_prompt()
        self.assertIn("角色$特殊@字符", result)

    # @patch('builtins.print')
    # def test_template_error_handling(self, mock_print):
    #    """测试模板错误处理"""
    #    prompt_gen = PromptGen()

    # 测试无效模板（应该不会抛出异常，而是返回原模板）
    #    template = "Hello $var"  # var不在vars_dict中
    #    vars_dict = {"other_var": "value"}
    #    result = prompt_gen._template_to_string(template, vars_dict)

    #    self.assertEqual(result, "Hello $var")
    # 应该打印错误信息
    #    mock_print.assert_called()


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
