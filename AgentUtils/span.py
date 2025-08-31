import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# from .ExpiringDictStorage import ExpiringDictStorage


class Span:
    def __init__(self, content: Any, parent: Optional["Span"] = None):
        """
        初始化Span对象

        Args:
            content: 内容，如果不是字符串会被转换为字符串
            parent: 父Span对象，默认为None表示根Span
        """
        self.hash = hash(time.time_ns())  # 使用纳秒时间戳生成hash
        self.create_time = time.time_ns()  # 创建时间（纳秒）
        self.end_time: Optional[int] = None  # 结束时间
        self.children: List[Span] = []  # 子Span列表
        self.parent = parent  # 父Span
        self.status = "open"  # 状态：open或closed
        self.content = str(content)  # 内容，转换为字符串

        # 如果有父Span，将自己添加到父Span的子Span列表中
        if parent:
            parent.add_child(self)

        # 线程安全锁
        self._lock = threading.RLock()

    def add_child(self, child_span: "Span") -> None:
        """添加子Span（线程安全）"""
        with self._lock:
            self.children.append(child_span)

    def end(self) -> bool:
        """
        结束当前Span（线程安全）

        Returns:
            bool: 是否成功结束Span
        """
        with self._lock:
            if self.status == "closed":
                return False
            # 检查所有子Span是否都已结束
            for child in self.children:
                if child.status != "closed":
                    return False

            # 所有子Span都已结束，可以结束当前Span
            self.end_time = time.time_ns()
            self.status = "closed"
            return True

    def get_duration(self) -> Optional[int]:
        """获取Span持续时间（纳秒），如果未结束则返回None"""
        if self.end_time is None:
            return None
        return self.end_time - self.create_time

    def display(self, level: int = 0) -> str:
        """
        按照层级结构展示Span及其子Span

        Args:
            level: 当前层级（用于缩进）

        Returns:
            str: 格式化后的Span信息
        """
        indent = "  " * level
        create_time_str = datetime.fromtimestamp(self.create_time / 1e9).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        if self.end_time:
            end_time_str = datetime.fromtimestamp(self.end_time / 1e9).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            duration = f", Duration: {(self.end_time - self.create_time) / 1e6:.2f}ms"
        else:
            end_time_str = "Not ended"
            duration = ""

        result = f"{indent}Span(hash={self.hash}, Status={self.status}\n"
        result += (
            f"{indent}  Create: {create_time_str}, End: {end_time_str}{duration}\n"
        )
        result += f"{indent}  Content: {self.content}\n"

        # 递归显示子Span
        for child in sorted(self.children, key=lambda x: x.create_time):
            result += child.display(level + 1)

        return result

    def to_dict(self) -> Dict[str, Any]:
        """将Span转换为字典（用于序列化）"""
        return {
            "hash": self.hash,
            "create_time": self.create_time,
            "end_time": self.end_time,
            "children": [child.to_dict() for child in self.children],
            "parent_hash": self.parent.hash if self.parent else None,
            "status": self.status,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], span_mgr: "Span_Mgr") -> "Span":
        """从字典创建Span对象"""
        span = cls.__new__(cls)
        span.hash = data["hash"]
        span.create_time = data["create_time"]
        span.end_time = data["end_time"]
        span.status = data["status"]
        span.content = data["content"]
        span._lock = threading.RLock()

        # 重建父子关系
        span.parent = (
            span_mgr.get_span_by_hash(data["parent_hash"])
            if data["parent_hash"]
            else None
        )

        # 递归重建子Span
        span.children = []
        for child_data in data["children"]:
            child_span = cls.from_dict(child_data, span_mgr)
            child_span.parent = span
            span.children.append(child_span)

        return span

    def __str__(self) -> str:
        return self.display()


class Span_Mgr:
    def __init__(self, storage):
        """
        初始化Span管理器

        Args:
            storage_filename: 存储文件名
            expiry_days: 数据过期天数
        """
        self.storage = storage
        self.root_spans: List[Span] = []  # 所有根Span（没有父Span的Span）
        self.all_spans: Dict[int, Span] = {}  # 所有Span的哈希映射
        self._lock = threading.RLock()

        # 从存储加载现有数据
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """从存储加载Span数据"""
        with self._lock:
            stored_data = self.storage.get("span_data", update_timestamp=False)
            if stored_data:
                try:
                    # 重建所有Span对象
                    span_dicts = stored_data.get("spans", {})
                    temp_spans = {}

                    # 先创建所有Span对象（不设置父子关系）
                    for hash_str, span_data in span_dicts.items():
                        span_hash = int(hash_str)
                        span = Span.__new__(Span)
                        span.hash = span_hash
                        span.create_time = span_data["create_time"]
                        span.end_time = span_data["end_time"]
                        span.status = span_data["status"]
                        span.content = span_data["content"]
                        span._lock = threading.RLock()
                        span.children = []  # 暂时为空
                        temp_spans[span_hash] = span

                    # 设置父子关系
                    for span_hash, span_data in span_dicts.items():
                        span = temp_spans[int(span_hash)]
                        parent_hash = span_data["parent_hash"]
                        if parent_hash:
                            span.parent = temp_spans.get(parent_hash)

                        # 重建子Span列表
                        for child_hash in span_data["children_hashes"]:
                            child_span = temp_spans.get(child_hash)
                            if child_span:
                                span.children.append(child_span)

                    # 重建根Span列表和所有Span映射
                    self.root_spans = [
                        span for span in temp_spans.values() if span.parent is None
                    ]
                    self.all_spans = temp_spans

                except Exception as e:
                    logging.info(f"Error loading span data: {e}")
                    self.root_spans = []
                    self.all_spans = {}

    def _save_to_storage(self) -> None:
        """保存Span数据到存储"""
        with self._lock:
            spans_data = {}
            for span_hash, span in self.all_spans.items():
                spans_data[str(span_hash)] = {
                    "create_time": span.create_time,
                    "end_time": span.end_time,
                    "parent_hash": span.parent.hash if span.parent else None,
                    "children_hashes": [child.hash for child in span.children],
                    "status": span.status,
                    "content": span.content,
                }

            self.storage.set("span_data", {"spans": spans_data})

    def create_span(self, content: Any, parent_hash: Optional[int] = None) -> Span:
        """
        创建新的Span

        Args:
            content: Span内容
            parent_hash: 父Span的hash值，如果为None则创建根Span

        Returns:
            Span: 新创建的Span对象
        """
        with self._lock:
            parent = self.all_spans.get(parent_hash) if parent_hash else None
            new_span = Span(content, parent)

            # 如果没有父Span，添加到根Span列表
            if parent is None:
                self.root_spans.append(new_span)

            # 添加到所有Span映射
            self.all_spans[new_span.hash] = new_span

            # 保存到存储
            self._save_to_storage()

            return new_span

    def get_recent_parent_spans(self) -> List[Span]:
        """
        查询最近所有的父Span（根Span），按照创建时间顺序返回

        Returns:
            List[Span]: 按创建时间排序的父Span列表
        """
        with self._lock:
            return sorted(self.root_spans, key=lambda x: x.create_time, reverse=True)

    def get_span_by_hash(self, span_hash: int) -> Optional[Span]:
        """
        根据hash值获取Span

        Args:
            span_hash: Span的hash值

        Returns:
            Optional[Span]: 找到的Span对象，如果不存在则返回None
        """
        with self._lock:
            return self.all_spans.get(span_hash)

    def end_span(self, span_hash: int) -> bool:
        """
        结束指定的Span

        Args:
            span_hash: 要结束的Span的hash值

        Returns:
            bool: 是否成功结束Span
        """
        with self._lock:
            span = self.all_spans.get(span_hash)
            if span and span.end():
                self._save_to_storage()
                return True
            return False

    def display_all_spans(self) -> str:
        """显示所有Span的层级结构"""
        with self._lock:
            result = ""
            for span in sorted(self.root_spans, key=lambda x: x.create_time):
                result += span.display()
            return result


# 使用示例
# if __name__ == "__main__":
# 创建Span管理器
#    span_mgr = Span_Mgr(ExpiringDictStorage(expiry_days=7))

# 创建一些Span
#    root_span = span_mgr.create_span("Root operation")
#    child1 = span_mgr.create_span("Child operation 1", root_span.hash)
#    child2 = span_mgr.create_span("Child operation 2", root_span.hash)
#    grandchild = span_mgr.create_span("Grandchild operation", child1.hash)

# 显示所有Span
#    print("All spans:")
#    print(span_mgr.display_all_spans())

# 结束子Span（应该失败，因为孙子Span还没结束）
#    print(f"Ending child1: {span_mgr.end_span(child1.hash)}")

# 结束孙子Span
#    print(f"Ending grandchild: {span_mgr.end_span(grandchild.hash)}")

# 现在可以结束child1
#    print(f"Ending child1: {span_mgr.end_span(child1.hash)}")

# 结束child2
#    print(f"Ending child2: {span_mgr.end_span(child2.hash)}")

# 现在可以结束根Span
#    print(f"Ending root: {span_mgr.end_span(root_span.hash)}")

# 显示最终状态
#    print("\nFinal state:")
#    print(span_mgr.display_all_spans())

# 查询最近的父Span
#    print("\nRecent parent spans:")
#    for span in span_mgr.get_recent_parent_spans():
#        create_time = datetime.fromtimestamp(span.create_time / 1e9).strftime('%Y-%m-%d %H:%M:%S')
#        print(f"  Span(hash={span.hash}, created={create_time}, content={span.content})")
