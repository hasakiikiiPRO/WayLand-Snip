"""图标加载工具"""
import os
import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Rsvg', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

ICON_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "icons"),
    os.path.join(os.path.dirname(__file__), "..", "..", "gnome_snip_icons"),
    "/usr/local/lib/python3.12/dist-packages/gnome_snip_icons",
]


def _find_icon(name):
    for base in ICON_PATHS:
        path = os.path.join(base, f"{name}.svg")
        if os.path.exists(path):
            return path
    return None


def _tint(pb, color):
    """把图标重染成单色，保留原 alpha 形状（用于深色工具栏）"""
    w, h = pb.get_width(), pb.get_height()
    if w <= 0 or h <= 0:
        return pb
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    ctx.set_source_rgba(color[0], color[1], color[2], 1.0)
    src = Gdk.cairo_surface_create_from_pixbuf(pb, 1, None)
    ctx.mask_surface(src, 0, 0)
    return Gdk.pixbuf_get_from_surface(surface, 0, 0, w, h)


def load_icon(name, size=16, color=None):
    """加载 SVG 图标（2x 超采样渲染，可选单色重染）"""
    path = _find_icon(name)
    if not path:
        return None
    try:
        import rsvg
        handle = rsvg.Handle(file=path)
        w, h = handle.get_dimension_data()[:2]
        # 2x 超采样
        render_size = size * 2
        scale = render_size / max(w, h)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, render_size, render_size)
        ctx = cairo.Context(surface)
        ctx.scale(scale, scale)
        handle.render_cairo(ctx)
        surface.flush()
        # 缩小到目标尺寸（高质量）
        pb_full = Gdk.pixbuf_get_from_surface(surface, 0, 0, render_size, render_size)
        if pb_full:
            pb = pb_full.scale_simple(size, size, GdkPixbuf.InterpType.HYPER)
            if color:
                pb = _tint(pb, color)
            return pb
    except Exception:
        pass

    # 回退
    try:
        img = Gtk.Image.new_from_file(path)
        pb = img.get_pixbuf()
        if pb:
            pb = pb.scale_simple(size, size, GdkPixbuf.InterpType.HYPER)
            if color:
                pb = _tint(pb, color)
            return pb
    except Exception:
        pass
    return None


def load_icon_as_image(name, size=16, color=None):
    pb = load_icon(name, size, color)
    if pb:
        return Gtk.Image.new_from_pixbuf(pb)
    return None
