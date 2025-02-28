import xml.etree.ElementTree as ET
from .text_comparator import TextComparator
from .result import Difference

class XmlComparator(TextComparator):
    """Comparator for XML files with structural comparison"""
    
    def read_content(self, file_path, start_line=0, end_line=None, start_column=0, end_column=None):
        """Read XML content"""
        # First read the file as text
        text_content = super().read_content(file_path, start_line, end_line, start_column, end_column)
        
        # Join the lines
        xml_text = ''.join(text_content)
        try:
            return ET.fromstring(xml_text)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in {file_path}: {str(e)}")
    
    def compare_content(self, content1, content2):
        """Compare XML content"""
        # Convert back to strings for comparison
        xml_str1 = ET.tostring(content1, encoding='unicode')
        xml_str2 = ET.tostring(content2, encoding='unicode')
        
        if xml_str1 == xml_str2:
            return True, []
            
        # Use a recursive function to find differences in XML structures
        differences = []
        self._compare_elements(content1, content2, "", differences)
        
        return False, differences
    
    def _compare_elements(self, elem1, elem2, path, differences, max_diffs=10):
        """Recursively compare XML elements and collect differences"""
        if len(differences) >= max_diffs:
            return
            
        # Compare tags
        if elem1.tag != elem2.tag:
            differences.append(Difference(
                position=path or "/",
                expected=elem1.tag,
                actual=elem2.tag,
                diff_type="tag_mismatch"
            ))
            return  # If tags don't match, don't compare further
            
        # Compare attributes
        attrib1 = set(elem1.attrib.items())
        attrib2 = set(elem2.attrib.items())
        
        for attr, value in attrib1 - attrib2:
            differences.append(Difference(
                position=f"{path}/@{attr}" if path else f"/@{attr}",
                expected=value,
                actual="missing attribute",
                diff_type="missing_attribute"
            ))
            if len(differences) >= max_diffs:
                return
                
        for attr, value in attrib2 - attrib1:
            differences.append(Difference(
                position=f"{path}/@{attr}" if path else f"/@{attr}",
                expected="missing attribute",
                actual=value,
                diff_type="extra_attribute"
            ))
            if len(differences) >= max_diffs:
                return
        
        # Compare text content if leaf nodes
        if len(elem1) == 0 and len(elem2) == 0:
            text1 = elem1.text.strip() if elem1.text else ""
            text2 = elem2.text.strip() if elem2.text else ""
            
            if text1 != text2:
                differences.append(Difference(
                    position=path or "/",
                    expected=text1,
                    actual=text2,
                    diff_type="text_mismatch"
                ))
                return
                
        # Compare children elements
        children1 = list(elem1)
        children2 = list(elem2)
        
        if len(children1) != len(children2):
            differences.append(Difference(
                position=path or "/",
                expected=f"{len(children1)} child elements",
                actual=f"{len(children2)} child elements",
                diff_type="children_count_mismatch"
            ))
            
        # Compare matching children
        for i, (child1, child2) in enumerate(zip(children1, children2)):
            new_path = f"{path}/{child1.tag}[{i}]" if path else f"/{child1.tag}[{i}]"
            self._compare_elements(child1, child2, new_path, differences, max_diffs)