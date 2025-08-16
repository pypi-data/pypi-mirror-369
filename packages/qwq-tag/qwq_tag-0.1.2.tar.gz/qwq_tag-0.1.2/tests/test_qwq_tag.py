import pytest
from pydantic import ValidationError
from lxml import etree

from qwq_tag.qwq_tag import QwqTag, _escape


class TestQwqTag:
    """Test suite for QwqTag class."""

    def test_basic_tag_creation(self):
        """Test basic QwqTag object creation."""
        tag = QwqTag(name="div", content=["Hello"], attr={"class": "test"})
        assert tag.name == "div"
        assert tag.content == ["Hello"]
        assert tag.attr == {"class": "test"}

    def test_empty_tag_creation(self):
        """Test creating an empty tag."""
        tag = QwqTag(name="br", content=[], attr={})
        assert tag.name == "br"
        assert tag.content == []
        assert tag.attr == {}

    def test_nested_tag_creation(self):
        """Test creating nested tags."""
        inner_tag = QwqTag(name="span", content=["inner"], attr={})
        outer_tag = QwqTag(name="div", content=["before", inner_tag, "after"], attr={})
        
        assert outer_tag.name == "div"
        assert len(outer_tag.content) == 3
        assert outer_tag.content[0] == "before"
        assert isinstance(outer_tag.content[1], QwqTag)
        assert outer_tag.content[1].name == "span"
        assert outer_tag.content[2] == "after"

    def test_content_text_property(self):
        """Test the content_text property."""
        # Simple text content
        tag = QwqTag(name="p", content=["Hello World"], attr={})
        assert tag.content_text == "Hello World"
        
        # Multiple text pieces
        tag = QwqTag(name="p", content=["Hello", " ", "World"], attr={})
        assert tag.content_text == "Hello World"
        
        # Mixed content with nested tags
        inner_tag = QwqTag(name="strong", content=["bold"], attr={})
        tag = QwqTag(name="p", content=["Hello ", inner_tag, " World"], attr={})
        expected = "Hello <strong >bold</strong> World"
        assert tag.content_text == expected

    def test_str_representation(self):
        """Test string representation of QwqTag."""
        tag = QwqTag(name="div", content=["Hello"], attr={"class": "test", "id": "main"})
        str_repr = str(tag)
        
        # Check that it contains the expected parts
        assert str_repr.startswith("<div")
        assert str_repr.endswith("</div>")
        assert "Hello" in str_repr
        assert 'class="test"' in str_repr or 'id="main"' in str_repr


class TestQwqTagFromStr:
    """Test suite for QwqTag.from_str method."""

    def test_simple_xml_parsing(self):
        """Test parsing simple XML."""
        xml = "<p>Hello World</p>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        assert isinstance(result[0], QwqTag)
        assert result[0].name == "p"
        assert result[0].content == ["Hello World"]

    def test_xml_with_attributes(self):
        """Test parsing XML with attributes."""
        xml = '<div class="container" id="main">Content</div>'
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        tag = result[0]
        assert tag.name == "div"
        assert tag.content == ["Content"]
        assert tag.attr["class"] == "container"
        assert tag.attr["id"] == "main"

    def test_nested_xml_parsing(self):
        """Test parsing nested XML."""
        xml = "<div><p>Paragraph</p><span>Span text</span></div>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        div_tag = result[0]
        assert div_tag.name == "div"
        assert len(div_tag.content) == 2
        
        p_tag = div_tag.content[0]
        assert isinstance(p_tag, QwqTag)
        assert p_tag.name == "p"
        assert p_tag.content == ["Paragraph"]
        
        span_tag = div_tag.content[1]
        assert isinstance(span_tag, QwqTag)
        assert span_tag.name == "span"
        assert span_tag.content == ["Span text"]

    def test_mixed_content_parsing(self):
        """Test parsing mixed content (text and elements)."""
        xml = "<p>Before <strong>bold</strong> after</p>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        p_tag = result[0]
        assert p_tag.name == "p"
        assert len(p_tag.content) == 3
        assert p_tag.content[0] == "Before"
        
        strong_tag = p_tag.content[1]
        assert isinstance(strong_tag, QwqTag)
        assert strong_tag.name == "strong"
        assert strong_tag.content == ["bold"]
        
        assert p_tag.content[2] == "after"

    def test_multiple_root_elements(self):
        """Test parsing multiple root elements."""
        xml = "<p>First</p><p>Second</p>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 2
        assert result[0].name == "p"
        assert result[0].content == ["First"]
        assert result[1].name == "p"
        assert result[1].content == ["Second"]

    def test_empty_string_parsing(self):
        """Test parsing empty string."""
        result = QwqTag.from_str("")
        assert result == []
        
        result = QwqTag.from_str("   ")
        assert result == []

    def test_whitespace_only_string(self):
        """Test parsing whitespace-only string."""
        result = QwqTag.from_str("   \n\t  ")
        assert result == []

    def test_self_closing_tags(self):
        """Test parsing self-closing tags."""
        xml = "<br/><img src='test.jpg'/>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 2
        assert result[0].name == "br"
        assert result[0].content == []
        assert result[1].name == "img"
        assert result[1].attr["src"] == "test.jpg"

    def test_malformed_xml_recovery(self):
        """Test XML recovery for malformed input."""
        # Missing closing tag - should still parse with recovery
        xml = "<div><p>Unclosed paragraph</div>"
        result = QwqTag.from_str(xml)
        
        # Should still parse something
        assert len(result) >= 1

    def test_html_entities(self):
        """Test parsing HTML entities."""
        xml = "<p>&lt;Hello&gt; &amp; &quot;World&quot;</p>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        assert result[0].content == ["<Hello> & \"World\""]


class TestQwqTagFromLxml:
    """Test suite for QwqTag.from_lxml method."""

    def test_simple_element_conversion(self):
        """Test converting a simple lxml element."""
        element = etree.Element("div")
        element.text = "Hello"
        
        tag = QwqTag.from_lxml(element)
        assert tag.name == "div"
        assert tag.content == ["Hello"]
        assert tag.attr == {}

    def test_element_with_attributes(self):
        """Test converting element with attributes."""
        element = etree.Element("div")
        element.set("class", "test")
        element.set("ID", "MAIN")  # Test case conversion
        element.text = "Content"
        
        tag = QwqTag.from_lxml(element)
        assert tag.name == "div"
        assert tag.content == ["Content"]
        assert tag.attr["class"] == "test"
        assert tag.attr["id"] == "MAIN"  # Should be lowercase key

    def test_nested_elements_conversion(self):
        """Test converting nested elements."""
        root = etree.Element("div")
        child = etree.SubElement(root, "p")
        child.text = "Paragraph"
        
        tag = QwqTag.from_lxml(root)
        assert tag.name == "div"
        assert len(tag.content) == 1
        assert isinstance(tag.content[0], QwqTag)
        assert tag.content[0].name == "p"
        assert tag.content[0].content == ["Paragraph"]

    def test_mixed_content_conversion(self):
        """Test converting mixed content."""
        root = etree.Element("p")
        root.text = "Before "
        
        strong = etree.SubElement(root, "strong")
        strong.text = "bold"
        strong.tail = " after"
        
        tag = QwqTag.from_lxml(root)
        assert tag.name == "p"
        assert len(tag.content) == 3
        assert tag.content[0] == "Before"
        assert isinstance(tag.content[1], QwqTag)
        assert tag.content[1].name == "strong"
        assert tag.content[2] == "after"

    def test_whitespace_handling(self):
        """Test that whitespace-only text is ignored."""
        root = etree.Element("div")
        root.text = "   \n\t   "  # Only whitespace
        
        child = etree.SubElement(root, "p")
        child.text = "Content"
        child.tail = "  \n  "  # Only whitespace
        
        tag = QwqTag.from_lxml(root)
        assert tag.name == "div"
        assert len(tag.content) == 1  # Only the child element, no whitespace text
        assert isinstance(tag.content[0], QwqTag)


class TestEscapeFunction:
    """Test suite for _escape function."""

    def test_basic_escaping(self):
        """Test basic HTML/XML entity escaping."""
        assert _escape("Hello") == "Hello"
        assert _escape("<tag>") == "&lt;tag&gt;"
        assert _escape("Tom & Jerry") == "Tom &amp; Jerry"
        assert _escape('Say "Hello"') == "Say &quot;Hello&quot;"

    def test_combined_escaping(self):
        """Test escaping multiple special characters."""
        text = '<div class="test">Tom & Jerry</div>'
        expected = '&lt;div class=&quot;test&quot;&gt;Tom &amp; Jerry&lt;/div&gt;'
        assert _escape(text) == expected

    def test_non_string_input(self):
        """Test escaping non-string input."""
        assert _escape(123) == "123"
        assert _escape(True) == "True"
        assert _escape(None) == "None"

    def test_empty_string(self):
        """Test escaping empty string."""
        assert _escape("") == ""


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_deeply_nested_structure(self):
        """Test handling deeply nested structures."""
        xml = "<div>" + "<p>" * 10 + "Deep content" + "</p>" * 10 + "</div>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        # Navigate to the deepest level
        current = result[0]
        for _ in range(10):
            assert current.name in ["div", "p"]
            current = current.content[0]
        
        # At this point, current should be the deepest QwqTag with the text content
        assert isinstance(current, QwqTag)
        assert current.name == "p"
        assert current.content == ["Deep content"]

    def test_large_attribute_values(self):
        """Test handling large attribute values."""
        large_value = "x" * 1000
        xml = f'<div data-large="{large_value}">Content</div>'
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        assert result[0].attr["data-large"] == large_value

    def test_unicode_content(self):
        """Test handling Unicode content."""
        xml = "<p>Hello 世界 🌍</p>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        assert result[0].content == ["Hello 世界 🌍"]

    def test_special_tag_names(self):
        """Test handling special tag names."""
        xml = "<custom-tag data-value='test'>Content</custom-tag>"
        result = QwqTag.from_str(xml)
        
        assert len(result) == 1
        assert result[0].name == "custom-tag"
        assert result[0].attr["data-value"] == "test"
