import logging
import xml.sax.saxutils
from typing import Any

from lxml import etree
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class QwqTag(BaseModel):
    name: str
    content: list["str | QwqTag"]
    attr: dict[str, str]

    @staticmethod
    def from_str(string: str):
        """Parse the complete XML string."""
        if not string.strip():
            return []

        try:
            # Wrap the input in a root element to handle multiple top-level elements or mixed content
            wrapped_xml = f"<qwq_root>{string}</qwq_root>"

            # Use parser with recovery
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(wrapped_xml, parser=parser)

            # Convert to our format and return the content
            root_tag = QwqTag.from_lxml(root)
            return root_tag.content
        except Exception as e:
            raise ValidationError(f"Could not parse XML/HTML even with recovery: {e}") from e

    @staticmethod
    def from_lxml(element: etree._Element):
        """Convert lxml Element to Tag object."""
        content = []
    
        # Add text content if it exists and is not just whitespace
        if element.text and element.text.strip():
            content.append(element.text.strip())
    
        # Process child elements
        for child in element: # type: ignore
            child_tag = QwqTag.from_lxml(child)
            content.append(child_tag)
    
            # Add tail text if it exists and is not just whitespace
            if child.tail and child.tail.strip():
                content.append(child.tail.strip())
    
        # Handle attributes - lxml provides attrib as a dict-like object
        attr = dict({k.lower(): v for k, v in element.attrib.items()})
        # if "content" in attr:
        #     content.append(attr["content"].strip())

        return QwqTag(name=element.tag, content=content, attr=attr)
    
    def __str__(self) -> str:
        attr_str = " ".join(
            [
                f'{k}="{_escape(v)}"'
                for k, v in self.attr.items()
            ]
        )
        return f"<{self.name} {attr_str}>{self.content_text}</{self.name}>"

    @property
    def content_text(self) -> str:
        return "".join(str(c) for c in self.content)


def _escape(string: Any):
    return xml.sax.saxutils.escape(str(string), {'"': "&quot;"})