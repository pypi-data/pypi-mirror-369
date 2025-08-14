import random
import threading
from typing import Optional, Union, List, Callable, Any, Dict, Tuple, Type
from mignonFramework.utils.ConfigReader import ConfigManager


def target(queue_instance, attr_name, attr_value):
    """
    一个装饰器工厂，用于将一个收尾任务注册到指定的 QueueIter 实例上。
    """
    def decorator(cls):
        if not hasattr(queue_instance, 'add_finalization_task'):
            raise TypeError("传递给 @target 的对象必须是支持 add_finalization_task 的 QueueIter 实例。")
        queue_instance.add_finalization_task(cls, attr_name, attr_value)
        return cls
    return decorator


class QueueIter:
    """
    一个最终整合版的、灵活、可重用、支持装饰器配置和随机种子的爬取队列生成器。
    ConfigManager 在使用 @target 功能时才是必需的。
    """

    def __init__(self,
                 pages: Union[List[int], range],
                 current_index: Optional[int] = 0,
                 callback: Optional[Callable[["QueueIter"], None]] = None,
                 config_manager: Optional[ConfigManager] = None,
                 shuffle: bool = True,
                 seed: Optional[int] = None
                 ):
        """
        初始化 QueueIter 实例。
        """
        # <<< FIX: 将 _lock 的初始化移到最前面 >>>
        # 必须先创建锁，因为后续的 setter 方法会用到它
        self._lock = threading.Lock()

        self.config_manager = config_manager
        self._finalization_tasks: Dict[Type, List[Tuple[str, Any]]] = {}
        self.shuffle = shuffle
        self.seed = seed

        self.pages = pages
        self.current_index = current_index

        self.callback = callback

    def add_finalization_task(self, target_class: Type, attr_name: str, attr_value: Any):
        """供 @target 装饰器调用的方法，用于注册一个收尾任务。"""
        with self._lock:
            if target_class not in self._finalization_tasks:
                self._finalization_tasks[target_class] = []
            self._finalization_tasks[target_class].append((attr_name, attr_value))

    @property
    def pages(self) -> List[Any]:
        with self._lock:
            return self._pages

    @pages.setter
    def pages(self, new_pages: Union[List[int], range]):
        if not isinstance(new_pages, (list, range)):
            raise TypeError("pages 必须是一个列表或 range 对象。")
        with self._lock:
            self._pages = list(new_pages)
            if self.shuffle:
                if self.seed is not None:
                    random.seed(self.seed)
                random.shuffle(self._pages)
            self._current_index = 0
            self._finalized = False

    @property
    def current_index(self) -> int:
        with self._lock:
            return self._current_index

    @current_index.setter
    def current_index(self, new_index: int):
        if not isinstance(new_index, int):
            raise TypeError("current_index 必须是一个整数。")
        with self._lock:
            # 允许设置到 len(self._pages) 以便能正确结束迭代
            if not (0 <= new_index <= len(self._pages)):
                raise ValueError(f"索引 {new_index} 超出有效范围 0 到 {len(self._pages)}。")
            self._current_index = new_index

    def __iter__(self):
        return self

    def __next__(self):
        with self._lock:
            if self._current_index >= len(self._pages):
                raise StopIteration
            page_to_return = self._pages[self._current_index]
            self._current_index += 1
            return page_to_return

    def hasNext(self) -> bool:
        with self._lock:
            has_next = self._current_index < len(self._pages)
            if not has_next and not self._finalized:
                if self._finalization_tasks:
                    if not self.config_manager:
                        raise ValueError("已使用 @target 装饰器注册任务，但在 QueueIter 初始化时未提供有效的 config_manager。")
                    for target_class, tasks in self._finalization_tasks.items():
                        instance_to_modify = self.config_manager.getInstance(target_class)
                        for attr_name, value in tasks:
                            setattr(instance_to_modify, attr_name, value)
                self._finalized = True
            return has_next

    def call(self):
        if self.callback:
            self.callback(self)