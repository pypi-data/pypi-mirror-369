"""Integration tests for qwq-tag package."""

import pytest
from qwq_tag.qwq_tag import QwqTag


class TestFixtures:
    """Tests using fixtures from conftest.py."""

    def test_simple_tag_fixture(self, simple_tag):
        """Test the simple_tag fixture."""
        assert simple_tag.name == "div"
        assert simple_tag.content == ["Hello World"]
        assert simple_tag.attr["class"] == "test"

    def test_nested_tag_fixture(self, nested_tag):
        """Test the nested_tag fixture."""
        assert nested_tag.name == "div"
        assert len(nested_tag.content) == 3
        assert nested_tag.content[0] == "Before "
        assert isinstance(nested_tag.content[1], QwqTag)
        assert nested_tag.content[1].name == "span"
        assert nested_tag.content[2] == " after"

    def test_fixture_string_representation(self, nested_tag):
        """Test string representation of nested fixture."""
        str_repr = str(nested_tag)
        assert "div" in str_repr
        assert "span" in str_repr
        assert "Before" in str_repr
        assert "inner text" in str_repr
        assert "after" in str_repr


class TestComplexXmlParsing:
    """Tests for parsing complex XML structures."""

    def test_complex_html_parsing(self, complex_xml):
        """Test parsing complex HTML structure."""
        result = QwqTag.from_str(complex_xml)
        
        # Should have one root element (html)
        assert len(result) == 1
        html_tag = result[0]
        assert html_tag.name == "html"
        
        # Check structure
        assert len(html_tag.content) == 2  # head and body
        head_tag = html_tag.content[0]
        body_tag = html_tag.content[1]
        
        assert head_tag.name == "head"
        assert body_tag.name == "body"
        assert body_tag.attr["class"] == "main"

    def test_complex_html_navigation(self, complex_xml):
        """Test navigating through complex HTML structure."""
        result = QwqTag.from_str(complex_xml)
        html_tag = result[0]
        
        # Navigate to body
        body_tag = html_tag.content[1]
        assert body_tag.name == "body"
        
        # Find the h1 tag
        h1_tag = None
        for content in body_tag.content:
            if isinstance(content, QwqTag) and content.name == "h1":
                h1_tag = content
                break
        
        assert h1_tag is not None
        assert h1_tag.attr["id"] == "title"
        assert "Welcome" in h1_tag.content_text

    def test_list_extraction(self, complex_xml):
        """Test extracting list items from complex HTML."""
        result = QwqTag.from_str(complex_xml)
        
        # Find all li tags recursively
        def find_tags(tag, tag_name):
            """Recursively find all tags with given name."""
            found = []
            if isinstance(tag, QwqTag):
                if tag.name == tag_name:
                    found.append(tag)
                for content in tag.content:
                    found.extend(find_tags(content, tag_name))
            return found
        
        li_tags = find_tags(result[0], "li")
        assert len(li_tags) == 3
        assert li_tags[0].content_text == "Item 1"
        assert li_tags[1].content_text == "Item 2"
        assert li_tags[2].content_text == "Item 3"


class TestMalformedXmlRecovery:
    """Tests for XML recovery with malformed input."""

    def test_malformed_xml_recovery(self, malformed_xml_samples):
        """Test that malformed XML can still be parsed with recovery."""
        for xml in malformed_xml_samples:
            try:
                result = QwqTag.from_str(xml)
                # Should parse something, even if structure is not perfect
                assert isinstance(result, list)
                # At least one element should be parsed
                assert len(result) > 0
            except Exception as e:
                # If it fails, it should be a ValidationError
                from pydantic import ValidationError
                assert isinstance(e, ValidationError)

    def test_specific_malformed_cases(self):
        """Test specific malformed XML cases."""
        # Unclosed tag
        xml = "<div><p>Unclosed paragraph</div>"
        result = QwqTag.from_str(xml)
        assert len(result) >= 1
        
        # Self-closing tag treated as regular tag
        xml = "<img src='test.jpg' alt='Test'>"
        result = QwqTag.from_str(xml)
        assert len(result) >= 1
        if result:
            assert result[0].name == "img"


class TestRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    def test_html_fragment_parsing(self):
        """Test parsing HTML fragments (common use case)."""
        fragment = """
        <div class="card">
            <h2>Card Title</h2>
            <p>Card description with <a href="#">link</a></p>
            <button class="btn">Click me</button>
        </div>
        """
        
        result = QwqTag.from_str(fragment)
        assert len(result) == 1
        card = result[0]
        assert card.name == "div"
        assert card.attr["class"] == "card"
        
        # Check that all child elements are present
        child_names = [c.name for c in card.content if isinstance(c, QwqTag)]
        assert "h2" in child_names
        assert "p" in child_names
        assert "button" in child_names

    def test_xml_with_namespaces(self):
        """Test parsing XML with namespaces."""
        xml = """
        <rss:feed xmlns:rss="http://example.com/rss">
            <rss:item>
                <rss:title>News Item</rss:title>
                <rss:description>Description</rss:description>
            </rss:item>
        </rss:feed>
        """
        
        result = QwqTag.from_str(xml)
        # Should parse even if namespaces are not fully supported
        assert len(result) >= 1

    def test_mixed_content_scenarios(self):
        """Test various mixed content scenarios."""
        scenarios = [
            "<p>Before <strong>bold</strong> after</p>",
            "<div>Text <span>span</span> more text <em>emphasis</em> end</div>",
            "<article>Start<h1>Title</h1>Middle<p>Para</p>End</article>",
        ]
        
        for xml in scenarios:
            result = QwqTag.from_str(xml)
            assert len(result) == 1
            root = result[0]
            
            # Should have mixed content (strings and QwqTag objects)
            has_text = any(isinstance(c, str) for c in root.content)
            has_tags = any(isinstance(c, QwqTag) for c in root.content)
            assert has_text and has_tags

    def test_performance_large_document(self):
        """Test performance with a moderately large document."""
        # Create a document with many nested elements
        xml_parts = ["<root>"]
        for i in range(100):
            xml_parts.append(f'<item id="{i}">Item {i} content</item>')
        xml_parts.append("</root>")
        
        large_xml = "".join(xml_parts)
        
        # This should complete without issues
        result = QwqTag.from_str(large_xml)
        assert len(result) == 1
        root = result[0]
        assert root.name == "root"
        
        # Count the items
        items = [c for c in root.content if isinstance(c, QwqTag) and c.name == "item"]
        assert len(items) == 100

    def test_attribute_case_handling(self):
        """Test that attribute keys are converted to lowercase."""
        xml = '<div ID="test" CLASS="main" Data-Value="123">Content</div>'
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        tag = result[0]
        
        # All attribute keys should be lowercase
        assert "id" in tag.attr
        assert "class" in tag.attr
        assert "data-value" in tag.attr
        
        # Values should be preserved as-is
        assert tag.attr["id"] == "test"
        assert tag.attr["class"] == "main"
        assert tag.attr["data-value"] == "123"

    def test_round_trip_consistency(self):
        """Test that parsing and string conversion are consistent."""
        original_xml = '<div class="test"><p>Hello <strong>world</strong>!</p></div>'
        
        # Parse the XML
        result = QwqTag.from_str(original_xml)
        assert len(result) == 1
        
        # Convert back to string
        reconstructed = str(result[0])
        
        # Parse the reconstructed string
        re_parsed = QwqTag.from_str(reconstructed)
        
        # Should have the same structure
        assert len(re_parsed) == 1
        assert re_parsed[0].name == result[0].name
        assert re_parsed[0].attr == result[0].attr
        # Note: exact content comparison might differ due to formatting
