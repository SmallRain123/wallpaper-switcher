# 📦 发布指南

## 自动构建流程

本项目使用 GitHub Actions 实现完全自动化的构建和发布流程。

### 触发方式

#### 1. 开发构建（每次提交）
推送到 `master` 或 `main` 分支时自动触发：
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin master
```

**产物**：在 Actions 页面的 Artifacts 中下载 `WallpaperSwitcher-dev-{commit}.exe`

#### 2. 正式发布（打标签）
创建并推送 `v*` 标签时自动创建 GitHub Release：
```bash
# 创建标签
git tag v1.0.0

# 推送标签到远程
git push origin v1.0.0
```

**产物**：
- 自动创建 GitHub Release
- 附带 `WallpaperSwitcher-v1.0.0.exe`
- 附带 `checksums.txt` 校验文件
- 生成完整的 Release Notes

#### 3. 手动触发
在 GitHub 仓库页面：
1. 进入 **Actions** 标签页
2. 选择 **Build** workflow
3. 点击 **Run workflow** 按钮
4. 选择分支，点击运行

## 版本号规范

推荐使用语义化版本号（Semantic Versioning）：

- `v1.0.0` - 主版本.次版本.修订号
- `v1.0.0-beta.1` - 预发布版本
- `v1.0.0-rc.1` - 候选发布版本

### 示例

```bash
# 修复 bug
git tag v1.0.1
git push origin v1.0.1

# 新增功能
git tag v1.1.0
git push origin v1.1.0

# 重大更新
git tag v2.0.0
git push origin v2.0.0

# 预发布版本
git tag v1.2.0-beta.1
git push origin v1.2.0-beta.1
```

## 发布检查清单

在创建新版本之前，确保完成以下步骤：

- [ ] 所有功能已测试通过
- [ ] 更新 README.md 中的版本信息和功能描述
- [ ] 本地运行 `build.bat` 验证构建成功
- [ ] 测试生成的 exe 文件能正常运行
- [ ] 检查 Git 状态，确保所有更改已提交
- [ ] 决定版本号（遵循语义化版本规范）
- [ ] 创建并推送标签

## Release 内容

每个 GitHub Release 将包含：

1. **可执行文件**：`WallpaperSwitcher-v{version}.exe`
   - 单文件便携版
   - 双击即用，无需安装
   - 包含所有依赖

2. **校验和文件**：`checksums.txt`
   - SHA256 校验值
   - 用于验证文件完整性

3. **Release Notes**：
   - 功能列表
   - 下载说明
   - 校验和信息
   - 自动生成的变更日志

## 常见问题

### Q: 如何删除错误的标签？

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0
```

### Q: 如何查看所有标签？

```bash
# 列出所有标签
git tag -l

# 查看标签详情
git show v1.0.0
```

### Q: 构建失败怎么办？

1. 进入 GitHub Actions 页面查看错误日志
2. 常见问题：
   - 依赖安装失败 → 检查 `requirements.txt`
   - PyInstaller 打包失败 → 检查导入和资源文件
   - 权限问题 → 确保仓库有 `contents: write` 权限

### Q: 如何修改 Release 内容？

1. 在 GitHub Release 页面找到对应版本
2. 点击 **Edit release** 编辑
3. 修改标题、描述或上传新文件
4. 保存更改

## 本地构建

如果需要本地构建而不发布到 GitHub：

```bash
# 运行构建脚本
build.bat

# 产物位置
release\WallpaperSwitcher.exe
```

## 高级用法

### 创建预发布版本

```bash
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

在 GitHub 上手动编辑 Release，勾选 "This is a pre-release"。

### 批量标签管理

```bash
# 查看远程所有标签
git ls-remote --tags origin

# 拉取所有标签
git fetch --tags

# 推送所有本地标签
git push origin --tags
```

## 工作流程图

```
┌─────────────┐
│  代码开发    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  git commit  │────▶│  git push    │
└─────────────┘     └──────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ GitHub Actions  │
                  │   自动构建      │
                  └────────┬───────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
   ┌─────────────────┐         ┌──────────────────┐
   │  普通提交        │         │   标签提交        │
   │  (Artifact)     │         │  (Release)       │
   └─────────────────┘         └──────────────────┘
            │                             │
            ▼                             ▼
   ┌─────────────────┐         ┌──────────────────┐
   │ Actions 页面     │         │ Releases 页面     │
   │ 下载 Artifact    │         │ 公开下载链接      │
   └─────────────────┘         └──────────────────┘
```

## 参考资源

- [GitHub Actions 文档](https://docs.github.com/actions)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [PyInstaller 文档](https://pyinstaller.org/)
