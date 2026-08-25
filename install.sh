#!/bin/bash
# gnome-snip 安装脚本（Ubuntu 24.04 / GNOME Wayland）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="/usr/local/bin"

# 优先用系统 Python（/usr/bin/python3 才自带 pygobject；避免 Homebrew 等无 gi 的解释器）
if [ -x /usr/bin/python3 ]; then
    PYTHON_BIN=/usr/bin/python3
else
    PYTHON_BIN="$(command -v python3 || true)"
    [ -n "$PYTHON_BIN" ] || { echo "缺少 python3，请先安装"; exit 1; }
fi

# 自动探测 site-packages 目录（兼容 python3.8 ~ 3.13，无需写死版本号）
PKG_BASE="$("$PYTHON_BIN" -c 'import sysconfig; print(sysconfig.get_path("purelib"))' 2>/dev/null || true)"
[ -n "$PKG_BASE" ] || PKG_BASE="/usr/local/lib/python3.12/dist-packages"
PKG_DIR="$PKG_BASE/gnome_snip"
ICON_DIR="$PKG_BASE/gnome_snip_icons"

echo "=== gnome-snip 安装 ==="
echo "  Python : $PYTHON_BIN"
echo "  目标目录: $PKG_BASE"

# 检查依赖
echo "检查依赖..."
"$PYTHON_BIN" -c "import gi; gi.require_version('Gtk','3.0')" 2>/dev/null || {
    echo "安装 GTK3..."
    sudo apt install -y python3-gi gir1.2-gtk-3.0
}

"$PYTHON_BIN" -c "import cairo" 2>/dev/null || {
    echo "安装 PyCairo..."
    sudo apt install -y python3-cairo
}

dpkg -l 2>/dev/null | grep -q xdg-desktop-portal-gnome || {
    echo "安装 xdg-desktop-portal-gnome..."
    sudo apt install -y xdg-desktop-portal-gnome
}

# 托盘：Ubuntu 22.10+ 为 AyatanaAppIndicator3（旧 AppIndicator3 已移除）
if "$PYTHON_BIN" -c "import gi; gi.require_version('AyatanaAppIndicator3','0.1')" 2>/dev/null; then
    echo "  已检测到 AyatanaAppIndicator3"
elif "$PYTHON_BIN" -c "import gi; gi.require_version('AppIndicator3','0.1')" 2>/dev/null; then
    echo "  已检测到 AppIndicator3（旧版兼容）"
else
    echo "安装 AyatanaAppIndicator3..."
    sudo apt install -y gir1.2-ayatanaappindicator3-0.1 2>/dev/null || true
fi

# OCR（可选）：tesseract + 中文语言包
if command -v tesseract >/dev/null 2>&1; then
    echo "  已检测到 tesseract（OCR 可用）"
else
    echo "  提示: 未安装 tesseract，OCR 功能不可用（可选）"
    echo "        安装: sudo apt install tesseract-ocr tesseract-ocr-chi-sim"
fi

# 安装程序
echo "安装 gnome-snip..."
sudo mkdir -p "$PKG_DIR"
sudo cp "$SCRIPT_DIR/gnome_snip/"*.py "$PKG_DIR/"
sudo mkdir -p "$ICON_DIR"
sudo cp "$SCRIPT_DIR/icons/"*.svg "$ICON_DIR/" 2>/dev/null || true
sudo cp "$SCRIPT_DIR/gnome-snip" "$INSTALL_DIR/gnome-snip"
sudo cp "$SCRIPT_DIR/icon.png" "$INSTALL_DIR/gnome-snip-icon.png" 2>/dev/null || true
sudo chmod +x "$INSTALL_DIR/gnome-snip"
echo "✓ 已安装到 $INSTALL_DIR/gnome-snip"

# 安装 .desktop 文件（出现在 Ubuntu 应用列表中）
echo "注册应用..."
sudo cp "$SCRIPT_DIR/wayland-snip.desktop" /usr/share/applications/gnome-snip.desktop
sudo chmod +x /usr/share/applications/gnome-snip.desktop
echo "✓ 已添加到应用列表"

echo ""
echo "安装完成！"
echo "  应用列表: 在 Ubuntu 中搜索 gnome-snip"
echo "  命令行: gnome-snip"
echo "  托盘: 右键托盘图标访问设置和截图"
