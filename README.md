# wayland-snip

GNOME Wayland 原生截图 + 贴图 + 标注工具。

基于 xdg-desktop-portal 调用 GNOME 原生截图 API，高分屏无偏移，支持多屏。

> 本仓库是 [cyhuauin/WayLand-Snip](https://github.com/cyhuauin/WayLand-Snip) 的 fork，聚焦 **Ubuntu 24.04 / GNOME 46 Wayland** 环境的兼容与体验打磨。原项目已不再维护依赖，本 fork 保持可用。

## ✨ 功能

- 📸 **截图** — 调用 GNOME 原生截图 UI（xdg-desktop-portal），支持区域/窗口/全屏
- 📌 **贴图** — 截图自动贴在屏幕上，可拖拽移动、滚轮缩放
- ✏️ **标注** — 画笔、矩形、箭头、直线、文字
- 🎨 **颜色** — 8 种预设颜色 + 自定义调色盘
- 📏 **线粗** — 5 档线宽可选
- 📋 **剪贴板** — 截图自动复制到剪贴板，含标注复制；贴图窗口内 `Ctrl+C` 直接复制
- 🔠 **OCR 文字识别** — 弹出右侧结果面板，可拖选部分文字复制，也可一键全部复制（tesseract，默认中英混合）
- 🖥️ **系统托盘** — 最小化到托盘，右键菜单操作
- ⚙️ **设置** — 可配置快捷键、截图行为、标注默认值、开机启动
- 🔄 **多次截图** — 一个实例内可多次截图，不会重复启动
- 🚀 **单实例** — 自动检测已有实例，避免重复运行

## 🔧 本 fork 的改动（相对上游）

### Ubuntu 24.04 / Python 3.12 兼容
- **入口脚本**：shebang 改为 `#!/usr/bin/python3`。Ubuntu 24.04 默认 `python3` 可能指向无 `pygobject` 的 Homebrew/3.14 等环境，需使用系统自带的 Python 3.12。
- **托盘依赖**：Ubuntu 22.10+ 已移除 `AppIndicator3`，`tray.py` 改为优先 `AyatanaAppIndicator3`（API 相同，`as AppIndicator3` 别名）。

### 贴图窗口（`pinwin.py`）
- **修复贴图占满/溢出全屏**：GTK3 在 Wayland 下 `Gdk.Monitor.get_geometry()` 返回**物理像素**（如 2880×1800），除以 `mon.get_scale_factor()` 归一化为逻辑尺寸（1440×900）后，贴图才会按预期比例显示，工具栏也不会被挤出屏幕。
- **修复标注笔画偏移**：鼠标 → 图像坐标换算（`_w2i`）与渲染（`_on_draw`）改用**同一个 `scale` 变换**，杜绝光标与笔画错位。
- **窗口高度**：用真实工具栏高度替代硬编码 `+36`，避免布局挤压。
- **Esc 关闭**：贴图窗口内按 `Esc` 关闭当前贴图。

### 工具栏美化（`icons.py` + `pinwin.py`）
- Snipaste 风格**深色工具栏**，图标单色重染为浅色（`icons.py` 新增 `color` 参数）。
- 修复缩放后工具栏样式丢失的 bug（CSS 尺寸与主题拆分两个 provider，避免互相覆盖）。

### 新功能：Ctrl+C 复制 + OCR（`pinwin.py` + `ocrwin.py` + `icons/ocr.svg`）
- **Ctrl+C 直接复制**：贴图窗口内按 `Ctrl+C` 即复制当前图（含标注）到剪贴板，并自动退出贴图（工具栏 📋 按钮行为一致）。
- **OCR 文字识别**：工具栏 ⛶ 按钮或 `Ctrl+Shift+O`。tesseract 后台线程识别（UI 不卡顿），完成后在**贴图右侧弹出结果面板**：文字可自由拖选，「复制选中」只复制高亮部分，「复制全部」一键全复制，**复制成功后面板自动关闭**；面板右侧放不下自动换左侧。
- **OCR 识别率优化**：送入 tesseract 前按图像尺寸自动放大 1–3 倍（实测小字号截图命中率 9/16 → 12/16）。
- **修复文字标注中文变豆腐块**：标注含中文时自动选用 CJK 字体（fc-list 探测）。

## 📦 依赖

- 系统 Python 3.8+（Ubuntu 24.04 为 3.12）
- GTK 3 + PyCairo
- xdg-desktop-portal + xdg-desktop-portal-gnome
- AyatanaAppIndicator3（托盘支持，可选）
- tesseract-ocr + 中文语言包（OCR 功能，可选）

```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-cairo gir1.2-gtk-3.0 \
    xdg-desktop-portal-gnome gir1.2-ayatanaappindicator3-0.1

# OCR 支持（可选）
sudo apt install tesseract-ocr tesseract-ocr-chi-sim
```

## 🚀 安装

### 从源码安装

```bash
git clone https://github.com/hasakiikiiPRO/WayLand-Snip.git
cd WayLand-Snip
sudo ./install.sh
```

### 手动安装（Ubuntu 24.04，系统 Python 3.12）

```bash
# 复制程序
sudo cp gnome-snip /usr/local/bin/gnome-snip
sudo cp -r gnome_snip /usr/local/lib/python3.12/dist-packages/gnome_snip
sudo chmod +x /usr/local/bin/gnome-snip

# 复制图标
sudo cp icon.png /usr/local/bin/gnome-snip-icon.png

# 注册应用（出现在 Ubuntu 应用列表中）
sudo cp gnome-snip.desktop /usr/share/applications/
```

> ⚠️ 手动安装时请确认目标目录为系统 Python（`/usr/bin/python3`）对应的 site-packages，并检查 `/usr/local/bin/gnome-snip` 首行为 `#!/usr/bin/python3`。

## 📖 使用

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| F1 | 截图并贴屏（可在设置中自定义） |
| Esc | 关闭当前贴图 |
| Ctrl+C | 复制当前图（含标注）并退出贴图 |
| Ctrl+Shift+O | OCR 识别并弹出结果面板（贴图窗口内） |

### 底部工具栏

| 按钮 | 功能 |
|------|------|
| ↔ | 移动模式（拖拽移动窗口） |
| ✏ | 画笔（自由绘制） |
| □ | 矩形标注 |
| → | 箭头标注 |
| ╱ | 直线标注 |
| T | 文字标注 |
| 🎨 | 颜色选择（预设 + 自定义） |
| · ─ ━ ▬ ■ | 线粗选择 |
| ↩ | 撤销上一步 |
| ⌫ | 清除所有标注 |
| −/+ | 缩放 |
| ⛶ | OCR 识别文字，弹出结果面板（需 tesseract） |
| 📋 | 复制到剪贴板（含标注）并退出贴图（同 Ctrl+C） |
| ❌ | 关闭贴图 |

### 贴图操作

- **滚轮** — 缩放贴图
- **拖拽** — 移动贴图（↔ 模式下直接拖拽图片区域）
- **选择画笔/矩形等工具后再拖拽** — 在图上标注
- **单击 ❌** — 关闭贴图

### 托盘菜单

- 📸 截图 — 触发截图
- ⚙ 设置 — 打开设置界面
- ❓ 帮助 — 使用说明
- 🔄 重新启动 — 重启程序
- ⏏️ 退出 — 关闭程序

## ⚙️ 设置

右键托盘图标 → 设置，可配置：

- **快捷键**：自定义截图快捷键（GNOME 级别全局快捷键）
- **截图行为**：自动复制到剪贴板、自动贴屏、保存目录、最大贴图数
- **OCR**：识别语言 `ocr_langs`（编辑配置文件，默认 `chi_sim+eng`）
- **标注默认值**：初始缩放比例、默认线宽、默认工具
- **系统**：开机自动启动

配置文件：`~/.config/gnome-snip/settings.json`

## 🏗️ 项目结构

```
wayland-snip/
├── gnome-snip              # 入口脚本
├── install.sh              # 安装脚本
├── gnome-snip.desktop      # 桌面文件（Ubuntu 应用列表）
├── icon.png                # 托盘图标
├── README.md               # 说明文档
├── LICENSE                 # 开源协议
└── gnome_snip/
    ├── __init__.py         # 版本信息
    ├── app.py              # 主应用（托盘、快捷键、截图调度）
    ├── portal.py           # xdg-desktop-portal 截图接口
    ├── pinwin.py           # 贴图窗口（标注、缩放、拖拽）
    ├── ocrwin.py           # OCR 结果面板（可选中复制）
    ├── settings.py         # 设置管理 + 快捷键/开机启动
    ├── prefs.py            # 设置界面
    ├── tray.py             # 系统托盘图标
    └── single.py           # 单实例管理（Unix Socket）
```

## 🐛 限制

- Wayland 下窗口置顶取决于合成器（GNOME Mutter 支持）
- 不支持撤销单步标注（只能逐步撤销或全部清除）
- 文字标注弹出对话框，可能影响流畅度
- 部分 Wayland 合成器可能不支持 always-on-top

## 📄 License

MIT License（同上游 [cyhuauin/WayLand-Snip](https://github.com/cyhuauin/WayLand-Snip)）。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request
