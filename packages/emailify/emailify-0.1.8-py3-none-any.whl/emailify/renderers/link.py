from email.mime.application import MIMEApplication

from emailify.models import Link
from emailify.renderers.core import _render
from emailify.renderers.style import render_extra_props


def render_link(link: Link) -> tuple[str, list[MIMEApplication]]:
    body = _render(
        "link",
        link=link,
        extra_props=render_extra_props("link", link.style),
    )
    return body, []
