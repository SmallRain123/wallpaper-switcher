# 🚀 快速开始 - 自动发布流程

## 📋 概览

你的项目现在已经配置了完整的自动构建和发布流程！

## 🎯 三种发布方式

### 方式 1：使用发布脚本（最简单）✨

```bash
# 双击运行或命令行执行
release.bat
```

脚本会引导你：
1. ✅ 检查未提交的更改
2. 📝 输入版本号（例如 v1.0.0）
3. ✔️ 确认发布信息
4. 🚀 自动创建并推送标签

### 方式 2：手动命令行

```bash
# 1. 提交所有更改
git add .
git commit -m "准备发布 v1.0.0"

# 2. 推送到 GitHub
git push origin master

# 3. 创建并推送标签
git tag v1.0.0
git push origin v1.0.0
```

### 方式 3：GitHub 网页操作

1. 进入你的仓库页面
2. 点击右侧 **Releases**
3. 点击 **Draft a new release**
4. 填写标签名（如 v1.0.0）
5. 点击 **Publish release**

## 📦 发布后会发生什么？

一旦推送标签，GitHub Actions 会自动：

1. **构建** - 在 Windows 环境下编译打包（约 3-5 分钟）
2. **生成产物**：
   - `WallpaperSwitcher-v1.0.0.exe` - 可执行文件
   - `checksums.txt` - SHA256 校验和
3. **创建 Release** - 自动发布到 Releases 页面
4. **生成说明** - 包含下载链接、功能列表、校验信息

## 🔍 查看构建状态

### 在线查看
访问：https://github.com/SmallRain123/wallpaper-switcher/actions

### 本地查看
```bash
# 使用 GitHub CLI（如已安装）
gh run list
gh run watch
```

## 📥 下载产物

### 开发版本（每次提交）
1. 进入 **Actions** 页面
2. 选择对应的构建任务
3. 滚动到底部 **Artifacts** 区域
4. 下载 `WallpaperSwitcher-dev-{commit}.zip`

### 正式版本（标签发布）
1. 进入 **Releases** 页面
2. 找到对应版本
3. 下载 `WallpaperSwitcher-v{version}.exe`

## ⚡ 常用命令

```bash
# 查看所有标签
git tag -l

# 查看最近的标签
git describe --tags --abbrev=0

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0

# 推送所有本地标签
git push origin --tags

# 查看当前分支
git branch

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline -10
```

## 📝 版本号建议

遵循语义化版本规范：

```
v1.0.0 - 主版本.次版本.修订号
  │ │ │
  │ │ └─ 修复 bug，向后兼容
  │ └─── 新增功能，向后兼容  
  └───── 重大更新，可能不兼容

示例：
v1.0.0 - 首次正式发布
v1.0.1 - 修复 bug
v1.1.0 - 新增功能
v2.0.0 - 重大更新

预发布版本：
v1.0.0-beta.1  - Beta 测试版
v1.0.0-rc.1    - 候选发布版
```

## 🛠️ 故障排查

### 构建失败
1. 查看 Actions 页面的错误日志
2. 常见问题：
   - 依赖安装失败 → 检查 requirements.txt
   - 打包失败 → 检查 PyInstaller 配置
   - 权限错误 → 仓库需要 `contents: write` 权限

### 标签冲突
```bash
# 如果标签已存在，先删除
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# 然后重新创建
git tag v1.0.0
git push origin v1.0.0
```

### Release 没有自动创建
检查：
- ✅ 标签必须以 `v` 开头（如 v1.0.0）
- ✅ 已推送到 origin 远程仓库
- ✅ 构建成功完成
- ✅ 仓库有 Actions 和 Releases 权限

## 📚 下一步

- 📖 详细发布指南：查看 [RELEASE.md](RELEASE.md)
- 🔧 本地构建测试：运行 `build.bat`
- 📊 监控构建状态：访问 Actions 页面
- 🎉 分享你的 Release：复制 Release 页面链接

## 🎬 完整示例

```bash
# 1. 开发功能
# ... 编写代码 ...

# 2. 测试
build.bat  # 本地构建测试

# 3. 提交代码
git add .
git commit -m "feat: 添加新的壁纸来源支持"
git push origin master

# 4. 发布新版本（使用脚本）
release.bat
# 输入: v1.1.0
# 确认发布

# 5. 等待构建（3-5 分钟）
# 访问：https://github.com/SmallRain123/wallpaper-switcher/actions

# 6. 下载发布产物
# 访问：https://github.com/SmallRain123/wallpaper-switcher/releases
```

---

🎉 **就是这么简单！现在你可以专注于开发，让 GitHub Actions 处理构建和发布。**
