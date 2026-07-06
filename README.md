# 🖼️ Wallpaper Switcher

Windows 桌面壁纸切换工具 —— 支持本地图片、URL 直链、GitHub 仓库三种来源，原生窗口运行，无需浏览器。

[![Build](https://github.com/SmallRain123/wallpaper-switcher/actions/workflows/build.yml/badge.svg)](https://github.com/SmallRain123/wallpaper-switcher/actions/workflows/build.yml)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

## ✨ 功能

- **📁 本地图片** — 选择本地图片文件直接设为壁纸
- **🔗 URL 直链** — 输入图片直链，自动下载并应用
- **🐙 GitHub 仓库** — 输入仓库地址，浏览目录树选择图片
- **🕐 历史记录** — 缩略图预览历史壁纸，支持一键恢复 / 删除
- **📌 当前壁纸** — 实时预览当前桌面壁纸

## 🛠️ 技术栈

| 层级 | 技术 |
|---|---|
| 后端 | Python 3.10+ · FastAPI · httpx |
| 前端 | Vue 3 (CDN) · CSS3 Glassmorphism |
| 桌面窗口 | pywebview (原生 Windows 窗口) |
| 打包 | PyInstaller (单文件 EXE) |
| 安装器 | Inno Setup 6 |
| CI/CD | GitHub Actions |
| 系统 API | Win32 `SystemParametersInfoW` |

## 📂 项目结构

```
wallpaper-switcher/
├── .github/workflows/build.yml  # GitHub Actions CI
├── app.py                       # 桌面入口（pywebview 原生窗口）
├── server.py                    # FastAPI 后端
├── requirements.txt             # Python 依赖
├── start.bat                    # 开发环境一键启动
├── build.bat                    # 构建脚本（打包 + 安装器）
├── installer.iss                # Inno Setup 安装器配置
├── icon.ico                     # 应用图标
├── static/
│   └── index.html               # Vue 3 前端界面
└── README.md
```

## 🚀 快速开始

### 方式一：双击 `start.bat`（推荐）

脚本自动安装 `uv`、创建虚拟环境、安装依赖、启动服务。

### 方式二：手动启动

```powershell
# 1. 安装 uv（如未安装）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. 创建虚拟环境并安装依赖
uv venv
uv pip install -r requirements.txt

# 3. 启动开发服务器
.venv\Scripts\python server.py
```

浏览器访问 **http://127.0.0.1:8899**

## 📦 构建

### 本地构建

运行 `build.bat` 一键构建：

```cmd
build.bat
```

脚本自动完成：安装 uv → 创建 venv → 安装依赖 → PyInstaller 打包 → 可选 Inno Setup 安装包。

**产物**：

| 文件 | 说明 |
|---|---|
| `release\WallpaperSwitcher.exe` | 便携版，双击即用 |
| `release\WallpaperSwitcher-Setup-x.x.x.exe` | 安装版（需安装 Inno Setup 6） |

### GitHub Actions 自动构建

推送代码后自动触发，也可在 [Actions](https://github.com/SmallRain123/wallpaper-switcher/actions) 页面手动运行。构建产物可在对应 Run 的 Summary 页面下载。

## 💿 安装器

`installer.iss` 为 Inno Setup 6 脚本：

- 安装路径：`%LOCALAPPDATA%\Programs\Wallpaper Switcher`（用户级，无需管理员权限）
- 压缩：LZMA2 极限 + 固实压缩
- 可选创建桌面快捷方式
- 安装后可选立即启动

> 生成安装包需先安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)，然后运行 `build.bat`。

## 🔌 API 接口

所有接口绑定 `127.0.0.1:8899`，仅本机访问。

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/wallpaper/current` | 获取当前壁纸路径 |
| `GET` | `/api/current-wallpaper-image` | 获取当前壁纸图片 |
| `POST` | `/api/wallpaper/local` | 上传本地图片设为壁纸 |
| `POST` | `/api/wallpaper/url` | 下载 URL 图片设为壁纸 |
| `POST` | `/api/wallpaper/github` | 浏览 GitHub 仓库 / 下载图片 |
| `GET` | `/api/history` | 获取历史壁纸列表 |
| `POST` | `/api/wallpaper/set` | 从历史记录恢复壁纸 |
| `DELETE` | `/api/wallpaper/{filename}` | 删除历史壁纸 |

## 📝 注意事项

- 仅支持 Windows 系统
- 服务仅绑定 `127.0.0.1`，不暴露到局域网
- 支持图片格式：JPG / PNG / BMP / GIF / WebP / TIFF
- GitHub 未认证 API 限制 **60 次/小时**，频繁使用建议配置 Token
