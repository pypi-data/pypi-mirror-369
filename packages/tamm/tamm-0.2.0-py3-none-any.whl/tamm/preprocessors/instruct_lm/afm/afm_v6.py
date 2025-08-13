import json as _json
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Optional as _Optional

from tamm import tokenizers as _tokenizers
from tamm.preprocessors.instruct_lm import jinja as _jinja
from tamm.preprocessors.instruct_lm.afm import utils as _utils

DEFAULT_SYSTEM_MESSAGE = "A conversation between a user and a helpful assistant."


V6_JINJA_CHAT_TEMPLATE = """
{{- '<turn_start> ' + messages[0]['role'] + '<n>' + messages[0]['content'] -}}
{% if tools %}
    {{- ('<n>system tools: ' + (tools | map('tojson') | join('<n>'))) -}}
{% endif %}
{{- '<turn_end>' -}}
{% for message in messages[1:] %}
    {{- '<turn_start> ' + message['role'] + '<n>' + message['content'] + '<turn_end>' -}}
{% endfor %}
{% if add_generation_prompt is defined and add_generation_prompt %}
    {% if messages[-1]['role'] != target_role %}
        {{- '<turn_start> ' + target_role + '<n>' -}}
    {% endif %}
{% endif %}
""".strip()


class AFMChatTemplateV6Preprocessor(_jinja.JinjaChatTemplatePreprocessor):
    def __init__(
        self,
        tokenizer_spec: _tokenizers.TokenizerSpecType,
        generate_prefix: bool = False,
        max_sequence_length: _Optional[int] = None,
        prepend_system_message: bool = True,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        target_role: str = "assistant",
        ignored_id: int = -100,
    ):
        super().__init__(
            tokenizer_spec=tokenizer_spec,
            chat_template=V6_JINJA_CHAT_TEMPLATE,
            generate_prefix=generate_prefix,
            max_sequence_length=max_sequence_length,
            prepend_system_message=prepend_system_message,
            system_message=system_message,
            strip_first_token=True,
            prepend_eos=True,
            target_role=target_role,
            ignored_id=ignored_id,
        )

    def maybe_update_message(self, message: _Dict[str, _Any]) -> _Dict[str, _Any]:
        """
        Updates the message to add tool calling and response format capabilities.
        """

        tool_calls = message.pop("tool_calls", None)
        if tool_calls is not None:
            tool_calls = _utils.tool_calls_to_json_str(tool_calls)
            message[
                "content"
            ] += f"<executable_start> ```function\n{tool_calls}```<executable_end>"

        if message["role"] in ("tool", "function"):
            message["role"] = "tool"
            content = message.pop("content")
            if isinstance(content, dict):
                # tool response case
                content = _json.dumps(content, ensure_ascii=False)
            elif isinstance(content, list):
                # newly added tools case
                tools = _utils.tools_to_json_str(content)
                content = f"new tools: {tools}"
            message["content"] = content

        response_format = message.pop("response_format", None)
        if response_format is not None:
            if response_format["type"] != "json_schema":
                raise ValueError(f"Unrecognized response format {response_format}")
            message["content"] += self._response_format_to_str(response_format)

        return message

    @staticmethod
    def _response_format_to_str(response_format: _Dict[str, _Any]) -> str:
        json_schema = response_format["json_schema"]

        pieces = ["\n\nresponse format in json.\n"]

        for key in ["name", "description"]:
            value = json_schema.get(key)
            pieces.append(f"{key}: {value}\n")

        schema = json_schema["schema"]
        schema_value = _json.dumps(schema, ensure_ascii=False)
        pieces.append(f"schema: {schema_value}")

        return "".join(pieces)
