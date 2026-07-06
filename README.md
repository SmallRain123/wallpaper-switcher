# 🖼️ Wallpaper Switcher

基于 Python + Vue 3 的 Windows 桌面壁纸切换工具，支持本地图片、URL 直链、GitHub 仓库三种来源。

## ✨ 功能

- **📁 本地图片** — 选择本地图片文件直接设为壁纸
- **🔗 URL 地址** — 输入图片直链，自动下载并设置
- **🐙 GitHub 仓库** — 输入仓库地址，浏览目录树选择图片
- **🕐 历史记录** — 缩略图预览历史壁纸，支持一键恢复 / 删除
- **📌 当前壁纸** — 实时预览当前桌面壁纸

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+ / FastAPI / httpx |
| 前端 | Vue 3 (CDN) / CSS3 Glassmorphism |
| 桌面窗口 | pywebview (原生 Windows 窗口) |
| 打包 | PyInstaller (单文件 EXE) |
| 安装器 | Inno Setup 6 |
| 系统 API | Win32 `SystemParametersInfoW` |

## 🚀 快速开始

### 方式一：双击 `start.bat`（推荐）

脚本会自动检测并安装 `uv`，创建虚拟环境，安装依赖，启动服务。

### 方式二：手动启动

```bash
# 安装 uv（如未安装）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 创建虚拟环境并安装依赖
uv venv
uv pip install -r requirements.txt

# 启动
.venv\Scripts\python server.py
```

### 3. 打开界面

浏览器访问 **http://127.0.0.1:8899**

## 📦 桌面打包

运行 `build.bat` 一键构建：

```bash
build.bat
```

脚本会自动完成以下步骤：

1. 检测 / 安装 `uv` 包管理器
2. 创建虚拟环境并安装依赖
3. 使用 PyInstaller `--onefile` 打包为单文件 EXE
4. 输出便携版到 `release\WallpaperSwitcher.exe`
5. 如已安装 Inno Setup 6，自动编译安装包

构建产物：

| 文件 | 说明 |
|---|---|
| `release\WallpaperSwitcher.exe` | 便携版，双击即用 |
| `release\WallpaperSwitcher-Setup-x.x.x.exe` | 安装版（需 Inno Setup） |

## 💿 安装器

项目包含 Inno Setup 脚本 `installer.iss`，配置如下：

- 默认安装路径：`%LOCALAPPDATA%\Programs\Wallpaper Switcher`（用户级，无需管理员权限）
- 封装方式：LZMA2 极限压缩 + 固实压缩，单文件安装包
- 自动创建桌面快捷方式（可选）
- 安装后可选立即启动

如需生成安装包，请先安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)，再运行 `build.bat`。

## 🔌 API 接口

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

- 服务仅绑定 `127.0.0.1`，不暴露到局域网
- GitHub 未认证 API 限制 **60 次/小时**，频繁使用建议配置 Token
- 支持的图片格式：JPG / PNG / BMP / GIF / WebP / TIFF
- 仅支持 Windows 系统

## 📂 项目结构

```
wallpaper-switcher/
├── app.py              # 桌面入口（pywebview 原生窗口）
├── server.py           # FastAPI 后端
├── requirements.txt    # Python 依赖
├── start.bat           # 开发环境启动脚本
├── build.bat           # 构建脚本（打包 + 安装器）
├── installer.iss       # Inno Setup 安装器配置
├── icon.ico            # 应用图标
├── README.md
└── static/
    └── index.html      # Vue 3 前端
```
