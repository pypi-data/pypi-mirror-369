"""Pytest fixtures for qwq-tag tests."""

import pytest
from qwq_tag.qwq_tag import QwqTag


@pytest.fixture
def simple_tag():
    """A simple QwqTag fixture for testing."""
    return QwqTag(
        name="div", 
        content=["Hello World"], 
        attr={"class": "test"}
    )


@pytest.fixture
def nested_tag():
    """A nested QwqTag fixture for testing."""
    inner_tag = QwqTag(name="span", content=["inner text"], attr={})
    return QwqTag(
        name="div", 
        content=["Before ", inner_tag, " after"], 
        attr={}
    )


@pytest.fixture
def complex_xml():
    """Complex XML string for parsing tests."""
    return """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body class="main">
            <h1 id="title">Welcome to Test Page</h1>
            <p>This is a test paragraph with <a href="#">a link</a>.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def malformed_xml_samples():
    """A collection of malformed XML samples for testing recovery."""
    return [
        # Unclosed tags
        "<div><p>Unclosed paragraph</div>",
        "<span>Unclosed span<div>Another tag</span>",
        
        # Missing opening tags
        "<div>Content</p></div>",
        
        # Malformed attributes
        '<div class="test id="main">Content</div>',
        '<img src=test.jpg alt="Test">',
        
        # Self-closing tags without proper syntax
        "<img src='test.jpg' alt='Test'>",
        "<br>",
        
        # Mixed case and invalid nesting
        "<DIV><P>Mixed case</div></P>",
        
        # Multiple root elements with malformed structure
        "<p>First</p><div>Second<span>nested</div></span>",
        
        # Tags with special characters
        "<custom-tag-123 data-value='test'>Content</custom-tag-123>",
        
        # Empty and whitespace content with malformed structure
        "<div>   </p>   <span></div>",
        
        # Quotes issues
        '<div class=test id="main\'>Content</div>',
        
        # Namespace-like syntax that might confuse parser
        "<ns:tag xmlns:ns='http://example.com'>Content</ns:tag>",
    ]
