import pytest
from mcp_airflow_api.airflow_api import get_prompt_template
from mcp_airflow_api.functions import read_prompt_template, parse_prompt_sections
from .config import TEMPLATE_CONFIG
import os


class TestPromptTemplate:
    """
    Prompt template functionality tests.
    These tests are designed to be resilient to template content changes.
    """
    
    @pytest.fixture
    def template_data(self):
        """Template data fixture - loads once per test class"""
        template = get_prompt_template()
        headings, sections = parse_prompt_sections(template)
        return {
            "template": template,
            "headings": headings,
            "sections": sections
        }
    
    # ============================================================================
    # 반영구적 테스트들 (템플릿 변경과 무관하게 계속 유효)
    # ============================================================================
    
    def test_template_loading_basic(self):
        """Test that template loads without errors"""
        template = get_prompt_template()
        assert template is not None
        assert len(template) > 0
        assert isinstance(template, str)
    
    def test_full_template_mode(self):
        """Test full template mode returns complete content"""
        template_full = get_prompt_template()
        template_explicit = get_prompt_template(mode="full")
        
        # Both should return the same content
        assert template_full == template_explicit
        assert TEMPLATE_CONFIG["title_marker"] in template_full
        assert len(template_full) > TEMPLATE_CONFIG["min_template_length"]
    
    def test_headings_mode_structure(self):
        """Test headings mode returns proper structure"""
        headings = get_prompt_template(mode="headings")
        assert TEMPLATE_CONFIG["section_headings_marker"] in headings
        
        lines = headings.split("\n")
        # Should have at least the header line plus minimum sections
        assert len(lines) >= TEMPLATE_CONFIG["min_sections"] + 1
    
    def test_case_insensitive_search(self):
        """Test case insensitive keyword search"""
        # Test with a keyword that should exist
        test_keyword = TEMPLATE_CONFIG["expected_keywords"][0]  # "overview"
        
        # Test different cases
        result_upper = get_prompt_template(section=test_keyword.upper())
        result_lower = get_prompt_template(section=test_keyword.lower())
        result_title = get_prompt_template(section=test_keyword.title())
        
        # At least one should work (case insensitive)
        results = [result_upper, result_lower, result_title]
        valid_results = [r for r in results if "not found" not in r.lower()]
        assert len(valid_results) > 0, f"Keyword '{test_keyword}' not found in any case variation"
    
    def test_invalid_inputs_handling(self):
        """Test handling of invalid inputs"""
        # Test invalid section numbers
        invalid_numbers = ["999", "0", "-1", "abc"]
        for num in invalid_numbers:
            result = get_prompt_template(section=num)
            if num == "0" or num == "-1":
                # These might be handled differently, so just check they don't crash
                assert isinstance(result, str)
            elif not num.isdigit():
                # Non-numeric should be treated as keyword search
                assert isinstance(result, str)
            else:
                # High numbers should return "not found"
                assert "not found" in result.lower()
        
        # Test completely invalid keywords
        result = get_prompt_template(section="nonexistent_keyword_xyz_123")
        assert "not found" in result.lower()
    
    def test_empty_and_none_inputs(self):
        """Test handling of empty and None inputs"""
        full_template = get_prompt_template()
        
        # These should all return the full template
        empty_string = get_prompt_template(section="")
        none_section = get_prompt_template(section=None)
        
        assert full_template == empty_string
        assert full_template == none_section
    
    # ============================================================================
    # 유연성을 높인 적응형 테스트들
    # ============================================================================
    
    def test_section_by_number_flexible(self, template_data):
        """Test section retrieval by number (flexible approach)"""
        headings = template_data["headings"]
        num_sections = len(headings)
        
        # Test first section if it exists
        if num_sections > 0:
            first_section = get_prompt_template(section="1")
            assert len(first_section) > 0
            assert "not found" not in first_section.lower()
            # Should contain the first heading
            assert headings[0] in first_section
        
        # Test middle section if there are enough sections
        if num_sections >= 3:
            middle_section = get_prompt_template(section="2")
            assert len(middle_section) > 0
            assert "not found" not in middle_section.lower()
    
    def test_keyword_search_expected_keywords(self, template_data):
        """Test keyword search with expected keywords"""
        headings = template_data["headings"]
        template = template_data["template"]
        
        for keyword in TEMPLATE_CONFIG["expected_keywords"]:
            # Check if keyword appears in template or headings
            keyword_in_template = keyword.lower() in template.lower()
            keyword_in_headings = any(keyword.lower() in heading.lower() for heading in headings)
            
            if keyword_in_template or keyword_in_headings:
                # If keyword exists, search should work
                result = get_prompt_template(section=keyword)
                assert "not found" not in result.lower(), f"Keyword '{keyword}' should be findable"
                assert len(result) > 0
            else:
                # If keyword doesn't exist, that's OK, just log it
                print(f"Info: Expected keyword '{keyword}' not found in current template")
    
    def test_boundary_conditions_dynamic(self, template_data):
        """Test boundary conditions dynamically based on current template"""
        headings = template_data["headings"]
        num_sections = len(headings)
        
        if num_sections > 0:
            # Test first section
            first = get_prompt_template(section="1")
            assert "not found" not in first.lower()
            assert len(first) > 0
            
            # Test last valid section
            last = get_prompt_template(section=str(num_sections))
            assert "not found" not in last.lower()
            assert len(last) > 0
            
            # Test beyond range
            beyond_range = get_prompt_template(section=str(num_sections + 1))
            assert "not found" in beyond_range.lower()
    
    def test_template_structure_integrity(self, template_data):
        """Test that template maintains expected structure"""
        template = template_data["template"]
        headings = template_data["headings"]
        sections = template_data["sections"]
        
        # Basic structure validation
        assert TEMPLATE_CONFIG["title_marker"] in template
        assert len(headings) >= TEMPLATE_CONFIG["min_sections"]
        
        # Sections should match headings count (+1 for title section)
        expected_sections = len(headings) + 1
        actual_sections = len(sections)
        assert actual_sections == expected_sections, f"Expected {expected_sections} sections, got {actual_sections}"
        
        # Each heading section should not be empty
        for i, section in enumerate(sections[1:], 1):  # Skip title section
            assert len(section.strip()) > 10, f"Section {i} is too short or empty: {len(section.strip())} chars"
    
    def test_headings_format_consistency(self, template_data):
        """Test that headings follow expected format"""
        headings = template_data["headings"]
        
        for i, heading in enumerate(headings, 1):
            # Basic validation
            assert len(heading.strip()) > 0, f"Heading {i} is empty"
            assert len(heading.strip()) > 3, f"Heading {i} too short: '{heading}'"
            
            # Most headings should contain some alphanumeric content
            assert any(c.isalnum() for c in heading), f"Heading {i} contains no alphanumeric characters: '{heading}'"
    
    def test_section_retrieval_consistency(self, template_data):
        """Test that section retrieval is consistent"""
        headings = template_data["headings"]
        
        # Test first few sections for consistency
        test_range = min(3, len(headings))
        for i in range(1, test_range + 1):
            # Get section by number
            section_by_number = get_prompt_template(section=str(i))
            assert "not found" not in section_by_number.lower()
            
            # Section should contain its own heading
            expected_heading = headings[i-1]
            assert expected_heading in section_by_number, f"Section {i} doesn't contain its heading: {expected_heading}"
    
    # ============================================================================
    # 레거시 호환성 테스트들 (기존 기능 유지 확인)
    # ============================================================================
    
    def test_legacy_airflow_tools_references(self):
        """Test that template still contains key Airflow tool references"""
        template = get_prompt_template()
        
        # These should generally be present in an Airflow API template
        expected_tools = ["list_dags", "get_health", "get_version"]
        found_tools = []
        
        for tool in expected_tools:
            if tool in template:
                found_tools.append(tool)
        
        # At least some tools should be present
        assert len(found_tools) > 0, f"No expected Airflow tools found. Looking for: {expected_tools}"
    
    def test_legacy_important_sections_exist(self):
        """Test that important sections still exist (flexible check)"""
        headings = get_prompt_template(mode="headings")
        
        # These concepts should generally be present
        important_concepts = ["overview", "tool", "example"]
        found_concepts = []
        
        for concept in important_concepts:
            if any(concept.lower() in heading.lower() for heading in headings.split('\n')):
                found_concepts.append(concept)
        
        # At least some important concepts should be present
        assert len(found_concepts) >= 2, f"Too few important concepts found. Expected some of: {important_concepts}, found: {found_concepts}"
    
    # ============================================================================
    # 성능 및 안정성 테스트들
    # ============================================================================
    
    def test_template_loading_performance(self):
        """Test that template loading is reasonably fast"""
        import time
        
        start_time = time.time()
        for _ in range(10):
            get_prompt_template()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        # Should load in reasonable time (less than 0.1 seconds per call)
        assert avg_time < 0.1, f"Template loading too slow: {avg_time:.3f}s per call"
    
    def test_template_memory_usage(self):
        """Test that template doesn't consume excessive memory"""
        template = get_prompt_template()
        
        # Template shouldn't be excessively large (less than 1MB)
        template_size = len(template.encode('utf-8'))
        max_size = 1024 * 1024  # 1MB
        assert template_size < max_size, f"Template too large: {template_size} bytes (max: {max_size})"
