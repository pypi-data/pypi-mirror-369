from enum import Enum


class ElementCondition(Enum):
    ELEMENT_PRESENCE = 'element_presence'
    ELEMENT_CLICKABLE = 'element_clickable'
    TEXT_PRESENT_IN_ELEMENT = 'text_to_be_present_in_element'
