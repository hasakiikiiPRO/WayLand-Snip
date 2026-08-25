"""OCR 结果面板：贴图右侧弹出，文字可选中按需复制"""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib


class OcrResultWin(Gtk.Window):
    """OCR 识别结果窗口：TextView 可选中，「复制选中」与「复制全部」分离"""

    WIDTH = 380

    def __init__(self, pin, text):
        super().__init__()
        self.pin = pin
        self.set_title("OCR 识别结果")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)

        css = Gtk.CssProvider()
        css.load_from_data(b"""
            .ocr-win { background: rgba(28, 28, 33, 0.96); border-radius: 8px; }
            .ocr-head { color: #e8e8ec; font-size: 13px; font-weight: bold; padding: 8px 10px 2px 10px; }
            .ocr-close { color: #ff7070; }
            .ocr-text, .ocr-text text {
                background: rgba(255, 255, 255, 0.06);
                color: #f0f0f4;
                font-size: 13px;
                padding: 6px;
            }
            .ocr-btns button { padding: 5px 12px; border-radius: 7px; }
            .btn-all { color: #e8e8ec; background: rgba(255, 255, 255, 0.10); }
            .btn-sel { color: #0d1117; background: #54c08a; font-weight: bold; }
        """)
        self.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        root.get_style_context().add_class("ocr-win")
        root.set_border_width(8)
        self.add(root)

        head = Gtk.Box(spacing=6)
        lbl = Gtk.Label(label=f"识别结果 · {len(text)} 字（可拖选部分文字）")
        lbl.get_style_context().add_class("ocr-head")
        lbl.set_halign(Gtk.Align.START)
        head.pack_start(lbl, True, True, 0)
        x = Gtk.Button(label="✕")
        x.set_relief(Gtk.ReliefStyle.NONE)
        x.get_style_context().add_class("ocr-close")
        x.connect("clicked", lambda _: self.destroy())
        head.pack_end(x, False, False, 0)
        root.pack_start(head, False, False, 0)

        self._txt = Gtk.TextView()
        self._txt.set_editable(False)
        self._txt.set_cursor_visible(True)
        self._txt.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._txt.get_style_context().add_class("ocr-text")
        self._txt.get_buffer().set_text(text)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self._txt)
        root.pack_start(scroll, True, True, 0)

        btns = Gtk.Box(spacing=6, halign=Gtk.Align.END)
        btns.get_style_context().add_class("ocr-btns")
        self._btn_all = Gtk.Button(label="复制全部")
        self._btn_all.get_style_context().add_class("btn-all")
        self._btn_all.connect("clicked", self._copy_all)
        self._btn_sel = Gtk.Button(label="复制选中")
        self._btn_sel.get_style_context().add_class("btn-sel")
        self._btn_sel.connect("clicked", self._copy_selected)
        btns.pack_start(self._btn_all, False, False, 0)
        btns.pack_end(self._btn_sel, False, False, 0)
        root.pack_start(btns, False, False, 0)

        self.connect("key-press-event", self._on_key)

        ph = self._place(pin)
        self.set_default_size(self.WIDTH, ph)
        self.show_all()
        self.present()

    def _place(self, pin):
        """定位到贴图右侧；右侧放不下换左侧，再兜底夹回屏幕内。返回建议高度"""
        disp = self.get_display()
        mon = None
        if pin.get_window():
            mon = disp.get_monitor_at_window(pin.get_window())
        mon = mon or disp.get_primary_monitor() or disp.get_monitor_at_point(0, 0)
        g = mon.get_geometry()
        sf = float(mon.get_scale_factor() or 1)
        mx, my, mw, mh = g.x / sf, g.y / sf, g.width / sf, g.height / sf

        px, py = pin.get_position()
        pw, ph = pin.get_size()

        h = max(220, min(int(ph * 0.9), 520))
        x = px + pw + 10
        if x + self.WIDTH > mx + mw:
            x = px - self.WIDTH - 10
        x = max(mx + 4, min(x, mx + mw - self.WIDTH - 4))
        y = max(my + 4, min(py, my + mh - h - 40))
        self.move(int(x), int(y))
        return h

    def _on_key(self, _w, e):
        if Gdk.keyval_name(e.keyval) == 'Escape':
            self.destroy()
            return True
        return False

    def _selected_text(self):
        buf = self._txt.get_buffer()
        s, e = buf.get_selection_bounds()
        if s and e:
            return buf.get_text(s, e, False).strip()
        return ""

    def _flash_btn(self, btn):
        old = btn.get_label()
        btn.set_label("未选择文字")
        GLib.timeout_add(1200, self._restore_btn, btn, old)
        return False

    @staticmethod
    def _restore_btn(btn, old):
        btn.set_label(old)
        return False

    def _put_clipboard(self, text):
        cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        cb.set_text(text, -1)
        cb.store()

    def _copy_all(self, btn):
        buf = self._txt.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False).strip()
        if not text:
            return
        self._put_clipboard(text)
        self.destroy()

    def _copy_selected(self, btn):
        text = self._selected_text()
        if not text:
            self._flash_btn(btn)
            return
        self._put_clipboard(text)
        self.destroy()
