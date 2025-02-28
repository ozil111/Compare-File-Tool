import os
import importlib
import pkgutil
from pathlib import Path

class ComparatorFactory:
    """Factory class for creating file comparators"""
    
    _comparators = {}
    _initialized = False
    
    @staticmethod
    def register_comparator(file_type, comparator_class):
        """Register a comparator class for a specific file type"""
        ComparatorFactory._comparators[file_type.lower()] = comparator_class
    
    @staticmethod
    def create_comparator(file_type, **kwargs):
        """Create a comparator instance for the specified file type"""
        # Initialize if not already done
        if not ComparatorFactory._initialized:
            ComparatorFactory._load_comparators()
            
        comparator_class = ComparatorFactory._comparators.get(file_type.lower())
        if not comparator_class:
            # Fall back to text or binary for unregistered types
            if file_type.lower() in ['auto', 'text']:
                from .text_comparator import TextComparator
                return TextComparator(**kwargs)
            else:
                from .binary_comparator import BinaryComparator
                return BinaryComparator(**kwargs)
                
        return comparator_class(**kwargs)
    
    @staticmethod
    def _load_comparators():
        """Dynamically load all comparator modules"""
        # Register built-in comparators
        from .text_comparator import TextComparator
        from .binary_comparator import BinaryComparator
        
        ComparatorFactory.register_comparator('text', TextComparator)
        ComparatorFactory.register_comparator('binary', BinaryComparator)
        
        # Look for additional comparator modules in the package
        package_dir = Path(__file__).parent
        for module_info in pkgutil.iter_modules([str(package_dir)]):
            if module_info.name.endswith('_comparator') and module_info.name not in [
                'base_comparator', 'text_comparator', 'binary_comparator'
            ]:
                try:
                    module = importlib.import_module(f".{module_info.name}", package=__package__)
                    # Look for classes derived from BaseComparator
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            attr.__module__ == module.__name__ and
                            attr_name.endswith('Comparator')):
                            # Register the comparator with its default name
                            type_name = attr_name.lower().replace('comparator', '')
                            ComparatorFactory.register_comparator(type_name, attr)
                except ImportError as e:
                    print(f"Failed to import comparator module {module_info.name}: {e}")
        
        ComparatorFactory._initialized = True
    
    @staticmethod
    def get_available_comparators():
        """Return a list of available comparator types"""
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