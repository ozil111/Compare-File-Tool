import os
import importlib
import pkgutil
from pathlib import Path

class ComparatorFactory:
    _comparators = {}
    _initialized = False

    @staticmethod
    def register_comparator(file_type, comparator_class):
        ComparatorFactory._comparators[file_type.lower()] = comparator_class

    @staticmethod
    def create_comparator(file_type, **kwargs):
        if not ComparatorFactory._initialized:
            ComparatorFactory._load_comparators()

        comparator_class = ComparatorFactory._comparators.get(file_type.lower())
        if not comparator_class:
            if file_type.lower() in ['auto', 'text']:
                from .text_comparator import TextComparator
                # 只传递 TextComparator 支持的参数
                text_kwargs = {k: v for k, v in kwargs.items() 
                              if k in ['encoding', 'chunk_size', 'verbose']}
                return TextComparator(**text_kwargs)
            else:
                from .binary_comparator import BinaryComparator
                # 传递 BinaryComparator 支持的所有参数
                return BinaryComparator(**kwargs)

        # 根据不同的比较器类型，过滤传入的参数
        if file_type.lower() == 'binary':
            # 二进制比较器接受所有参数，包括 num_threads
            return comparator_class(**kwargs)
        else:
            # 其他比较器不接受 num_threads 参数
            filtered_kwargs = {k: v for k, v in kwargs.items() 
                              if k != 'num_threads'}
            return comparator_class(**filtered_kwargs)

    @staticmethod
    def _load_comparators():
        from .text_comparator import TextComparator
        from .binary_comparator import BinaryComparator

        ComparatorFactory.register_comparator('text', TextComparator)
        ComparatorFactory.register_comparator('binary', BinaryComparator)

        package_dir = Path(__file__).parent
        for module_info in pkgutil.iter_modules([str(package_dir)]):
            if module_info.name.endswith('_comparator') and module_info.name not in [
                'base_comparator', 'text_comparator', 'binary_comparator'
            ]:
                try:
                    module = importlib.import_module(f".{module_info.name}", package=__package__)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            attr.__module__ == module.__name__ and
                            attr_name.endswith('Comparator')):
                            type_name = attr_name.lower().replace('comparator', '')
                            ComparatorFactory.register_comparator(type_name, attr)
                except ImportError as e:
                    print(f"Failed to import comparator module {module_info.name}: {e}")

        ComparatorFactory._initialized = True

    @staticmethod
    def get_available_comparators():
        if not ComparatorFactory._initialized:
            ComparatorFactory._load_comparators()
        return sorted(ComparatorFactory._comparators.keys())

from .json_comparator import JsonComparator
from .xml_comparator import XmlComparator
from .csv_comparator import CsvComparator
from .text_comparator import TextComparator
from .binary_comparator import BinaryComparator

ComparatorFactory.register_comparator('json', JsonComparator)
ComparatorFactory.register_comparator('xml', XmlComparator)
ComparatorFactory.register_comparator('csv', CsvComparator)
ComparatorFactory.register_comparator('text', TextComparator)
ComparatorFactory.register_comparator('binary', BinaryComparator)