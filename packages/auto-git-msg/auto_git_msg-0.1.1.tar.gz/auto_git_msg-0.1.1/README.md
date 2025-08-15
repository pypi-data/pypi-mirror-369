# Auto Git Commit Message

`auto-git-msg` 是一个基于 Google Gemini 构建的智能 Git 提交信息生成工具。它不仅仅是一个简单的生成器，更是一个能够理解项目上下文的智能代理（Agent）。

这个工具可以通过分析暂存区（staged）或工作区（unstaged）的代码变更，自动生成符合 **Conventional Commits** 规范的高质量 Git Commit Message。

## ✨ 功能特性

-   **智能生成**: 基于强大的 Gemini 模型分析代码 `diff`，生成准确、专业的提交信息。
-   **遵循规范**: 自动格式化为 `type(scope): subject` 的 [Conventional Commits](https://www.conventionalcommits.org/) 格式。
-   **上下文感知**: 能够像开发者一样 `ls` 和 `cd`，在生成消息前探索项目结构，提高 scope 的准确性。
-   **灵活输入**:
    -   自动分析暂存区的代码变更。
    -   可通过指令分析工作区（未暂存）的变更。
    -   可以优化您手写的、不规范的 commit message。
-   **智能过滤**: 自动忽略 `*.lock` 等版本锁定文件，聚焦核心代码变更。
-   **风格参考**: 能够获取上一次的 commit message，以保持提交风格的一致性。
-   **代理支持**: 自动检测并使用系统环境变量（`https_proxy`, `http_proxy`）或配置文件中的代理。

## 🚀 安装

### 先决条件

-   Python 3.9+
-   Git

### 安装步骤

使用 `pip` 即可安装：

```bash
# 使用 pip
pip install auto-git-msg
```

## ⚙️ 配置

首次使用时，工具会提示您输入 Google Gemini API 密钥。输入后，密钥将被自动保存在您用户主目录下的 `~/.auto-git-msg.json` 文件中，后续无需再次配置。

您也可以通过命令行参数手动配置：

-   **指定密钥（自动保存）**
    ```bash
    auto-git-msg --api-key YOUR_API_KEY "Generate a commit message"
    ```

### 代理配置

如果您的网络环境需要代理才能访问 Google API，本工具会自动检测 `https_proxy` 或 `http_proxy` 环境变量。

您也可以通过命令显式设置或取消代理：

-   **设置代理**
    ```bash
    auto-git-msg --set-proxy http://127.0.0.1:7890
    ```
    此命令会将代理信息写入 `~/.auto-git-msg.json` 配置文件中。

-   **取消代理**
    ```bash
    auto-git-msg --unset-proxy
    ```

## 📖 使用方法

确保您的代码变更已经通过 `git add` 添加到暂存区。

### 基本用法

-   **为暂存区的变更生成提交信息**
    ```bash
    auto-git-msg
    ```

-   **提供额外指令或上下文**
    如果变更多而复杂，您可以给 AI 一些提示。
    ```bash
    auto-git-msg "这些改动主要重构了后端的认证模块"
    ```

-   **为未暂存的变更生成提交信息**
    ```bash
    auto-git-msg "为我所有未暂存的变更生成一个 commit message"
    ```

-   **优化已有的提交信息**
    让 AI 帮你把一个简单的想法变成规范的 commit message。
    ```bash
    auto-git-msg --message "fix: 修复登录bug"
    ```

### 高级用法

-   **在指定项目目录运行**
    使用 `-C` 或 `--chdir` 参数切换到目标目录。
    ```bash
    auto-git-msg -C ../another-project "为那个项目的改动生成 commit"
    ```

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。