from flexx import flx


def css_visible(widget: flx.Widget, visible: bool):
    widget.apply_style({"visibility": "visible" if visible else "hidden"})
