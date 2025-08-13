import json as _json
import logging as _logging
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List

_logger = _logging.getLogger(__name__)


def tool_calls_to_json_str(tool_calls: _List[_Dict[str, _Any]]) -> str:
    tool_calls = [
        {
            "name": call["function"]["name"],
            "arguments": _parse_tool_call_arguments(call["function"]["arguments"]),
        }
        for call in tool_calls
    ]
    return _json.dumps(tool_calls, ensure_ascii=False)


def _parse_tool_call_arguments(arguments: str) -> _Any:
    try:
        return _json.loads(arguments)
    except _json.JSONDecodeError:
        _logger.debug("Failed to parse tool call arguments %s", arguments)
    return arguments


def tools_to_json_str(tools: _List[_Dict[str, _Any]]) -> str:
    tools = [_json.dumps(tool, ensure_ascii=False) for tool in tools]
    return "\n".join(tools)
