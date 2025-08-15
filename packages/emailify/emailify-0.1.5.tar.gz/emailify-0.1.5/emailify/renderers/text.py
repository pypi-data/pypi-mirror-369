from emailify.models import Text
from emailify.renderers.core import _render
from emailify.renderers.style import render_extra_props


def render_text(text: Text) -> str:
    return _render(
        "text",
        text=text,
        extra_props=render_extra_props("text", text.style),
    )
