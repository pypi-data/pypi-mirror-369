from enum import Enum


class ActionType(Enum):
    WAIT_FOR = 'wait_for'
    WAIT = 'wait'
    SCROLL = 'scroll'
    CLICK = 'click'
    SELECT_BY_VALUE = 'select_by_value'
    FIND = 'find'
    INPUT = 'input'
    REPEAT_WHILE = 'repeat_while'
    GET_PAGE_SOURCE = 'get_page_source'
    GET_XHR = 'get_xhr'
    FINISH = 'finish'
