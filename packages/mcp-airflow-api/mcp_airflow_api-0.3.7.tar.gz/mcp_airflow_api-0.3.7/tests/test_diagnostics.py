"""
Diagnostic tests to help understand template structure changes
"""
import pytest
from mcp_airflow_api.airflow_api import get_prompt_template
from .utils import TemplateAnalyzer, print_template_info
from .config import TEMPLATE_CONFIG


class TestTemplateDiagnostics:
    """
    Diagnostic tests that help understand the current template structure.
    These tests are mainly for information and debugging purposes.
    """
    
    def test_template_current_structure(self):
        """Display current template structure for reference"""
        analyzer = TemplateAnalyzer()
        stats = analyzer.get_template_stats()
        
        print(f"\n📊 Template Statistics:")
        print(f"   • Total length: {stats['total_length']:,} characters")
        print(f"   • Section count: {stats['section_count']}")
        print(f"   • Average section length: {stats['avg_section_length']:.0f} characters")
        
        # Use the corrected headings format from get_prompt_template
        headings_output = get_prompt_template(mode='headings')
        print(f"\n📋 Current Section Structure:")
        print(f"   {headings_output}")
        
        # This test always passes - it's just for information
        assert True
    
    def test_expected_vs_actual_structure(self):
        """Compare expected configuration with actual template"""
        analyzer = TemplateAnalyzer()
        stats = analyzer.get_template_stats()
        
        print(f"\n🔍 Structure Comparison:")
        print(f"   Expected min sections: {TEMPLATE_CONFIG['min_sections']}")
        print(f"   Actual sections: {stats['section_count']}")
        
        if stats['section_count'] >= TEMPLATE_CONFIG['min_sections']:
            print(f"   ✅ Section count meets minimum requirement")
        else:
            print(f"   ⚠️  Section count below minimum")
        
        print(f"\n🔍 Keyword Analysis:")
        for keyword in TEMPLATE_CONFIG['expected_keywords']:
            found_sections = analyzer.find_sections_by_keyword(keyword)
            if found_sections:
                print(f"   ✅ '{keyword}' found in {len(found_sections)} section(s)")
                for section in found_sections[:2]:  # Show first 2 matches
                    # Clean display without duplicate numbers
                    print(f"      - {section['heading']}")
            else:
                print(f"   ❌ '{keyword}' not found in any section")
        
        # This test always passes - it's diagnostic only
        assert True
    
    def test_template_health_check(self):
        """Comprehensive health check of current template"""
        analyzer = TemplateAnalyzer()
        stats = analyzer.get_template_stats()
        issues = []
        warnings = []
        
        # Check section count
        if stats['section_count'] < TEMPLATE_CONFIG['min_sections']:
            issues.append(f"Section count ({stats['section_count']}) below minimum ({TEMPLATE_CONFIG['min_sections']})")
        elif stats['section_count'] > TEMPLATE_CONFIG['min_sections'] * 2:
            warnings.append(f"Section count ({stats['section_count']}) much higher than expected")
        
        # Check template size
        if stats['total_length'] < TEMPLATE_CONFIG['min_template_length']:
            issues.append(f"Template too short ({stats['total_length']} chars)")
        elif stats['total_length'] > TEMPLATE_CONFIG['min_template_length'] * 10:
            warnings.append(f"Template very large ({stats['total_length']:,} chars)")
        
        # Check section numbering
        numbering_issues = analyzer.validate_section_numbering()
        issues.extend(numbering_issues)
        
        # Check for empty sections
        for i, section in enumerate(analyzer.sections[1:], 1):  # Skip title section
            if len(section.strip()) < 50:  # Very short sections
                warnings.append(f"Section {i} is very short ({len(section.strip())} chars)")
        
        # Report results
        print(f"\n🏥 Template Health Check Results:")
        if not issues and not warnings:
            print("   ✅ Template appears healthy!")
        else:
            if issues:
                print(f"   ❌ Issues found ({len(issues)}):")
                for issue in issues:
                    print(f"      - {issue}")
            
            if warnings:
                print(f"   ⚠️  Warnings ({len(warnings)}):")
                for warning in warnings:
                    print(f"      - {warning}")
        
        # Test passes if no critical issues
        assert len(issues) == 0, f"Template health check failed: {issues}"
    
    def test_update_config_recommendations(self):
        """Suggest configuration updates based on current template"""
        analyzer = TemplateAnalyzer()
        stats = analyzer.get_template_stats()
        
        print(f"\n💡 Configuration Update Suggestions:")
        
        # Check if min_sections should be updated
        current_sections = stats['section_count']
        config_min = TEMPLATE_CONFIG['min_sections']
        
        if current_sections > config_min:
            new_min = max(config_min, current_sections - 1)  # Allow some flexibility
            print(f"   • Consider updating min_sections from {config_min} to {new_min}")
        
        # Check for new keywords
        all_headings_text = " ".join(stats['headings']).lower()
        suggested_keywords = []
        
        potential_keywords = ['dag', 'task', 'pool', 'variable', 'log', 'health', 'monitor', 'schedule']
        for keyword in potential_keywords:
            if keyword in all_headings_text and keyword not in TEMPLATE_CONFIG['expected_keywords']:
                suggested_keywords.append(keyword)
        
        if suggested_keywords:
            print(f"   • Consider adding these keywords: {suggested_keywords}")
        
        # Suggest template length update
        if stats['total_length'] > TEMPLATE_CONFIG['min_template_length'] * 1.5:
            new_min = int(stats['total_length'] * 0.8)  # 80% of current length
            print(f"   • Consider updating min_template_length from {TEMPLATE_CONFIG['min_template_length']} to {new_min}")
        
        print(f"   • Current template stats: {current_sections} sections, {stats['total_length']:,} chars")
        
        # This test always passes - it's just recommendations
        assert True


if __name__ == "__main__":
    # Run diagnostics when script is executed directly
    print_template_info()
    
    # Run the health check
    analyzer = TemplateAnalyzer()
    test_diagnostics = TestTemplateDiagnostics()
    test_diagnostics.test_template_health_check()
