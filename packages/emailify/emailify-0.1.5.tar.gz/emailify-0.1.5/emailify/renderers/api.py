import json
from functools import lru_cache
from importlib.resources import files

from quickjs import Context

from emailify.models import Component, Fill, Image, Table, Text
from emailify.renderers.core import _render
from emailify.renderers.fill import render_fill
from emailify.renderers.image import render_image
from emailify.renderers.table import render_table
from emailify.renderers.text import render_text

RENDER_MAP = {
    Table: render_table,
    Text: render_text,
    Fill: render_fill,
    Image: render_image,
}


def _read_bundle_text() -> str:
    return (
        files("emailify")
        .joinpath("resources", "js", "mjml-browser.js")
        .read_text(encoding="utf-8")
    )


def _read_js_text(name: str) -> str:
    return (
        files("emailify").joinpath("resources", "js", name).read_text(encoding="utf-8")
    )


def _build_ctx() -> Context:
    ctx = Context()
    ctx.eval(_read_js_text("setup_shim.js"))
    bundle_js = _read_bundle_text()
    ctx.eval(bundle_js)
    ctx.eval(_read_js_text("capture_export.js"))
    return ctx


@lru_cache(maxsize=1)
def _get_ctx() -> Context:
    return _build_ctx()


def mjml2html(
    mjml: str,
    **options,
) -> str:
    template = _read_js_text("call_mjml.js")
    js = template.replace("__MJML__", json.dumps(mjml)).replace(
        "__OPTIONS__", json.dumps(options or {})
    )
    try:
        return _get_ctx().eval(js)
    except Exception as e:
        raise RuntimeError(str(e)) from None


def render(
    *components: Component,
) -> str:
    parts: list[str] = []
    for component in components:
        parts.append(RENDER_MAP[type(component)](component))
    body_str = _render(
        "index",
        content="".join(parts),
    )
    return mjml2html(body_str)
