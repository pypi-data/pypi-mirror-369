# 告别手写 Git Commit Message，Commity 带你进入 AI 自动化时代！

你是否曾为如何写出清晰、规范的 Git commit message 而烦恼？或者在项目紧张时，为了赶进度而写下 `fix bug` 或 `update` 这样毫无意义的提交信息？

在快节奏的软件开发中，高质量的 commit message 是高效团队协作和项目维护的基石。它不仅记录了代码的变更历史，更是团队成员之间沟通的重要桥梁。然而，手动编写符合规范的 commit message 既耗时又费力。

现在，是时候让 AI 来改变这一切了！向你隆重介绍 **Commity**——一款能为你自动生成智能 Git commit message 的命令行工具。

## 什么是 Commity？

**Commity** 是一款开源的、基于 AI 的 Git commit message 生成工具。它能够分析你暂存区的代码变更（`git diff --staged`），并自动生成符合[**Conventional Commits**](https://www.conventionalcommits.org/) 规范的提交信息，甚至还能为你加上可爱的 emoji！

只需一个简单的 `commity` 命令，你就能得到像这样专业而清晰的 commit message：

```
feat(api): ✨ add user authentication endpoint
```

## 为什么选择 Commity？

1.  **节省时间，解放大脑**：将编写 commit message 的繁琐工作交给 AI，让你更专注于编码。
2.  **提升代码库质量**：自动遵循 Conventional Commits 规范，让你的提交历史清晰、一致且专业。
3.  **支持多种 AI 模型**：无论你喜欢 OpenAI 的强大、Ollama 的本地化部署，还是 Google 的 Gemini，Commity 都完美支持。你可以自由选择最适合你的模型。
4.  **配置灵活，上手简单**：通过命令行参数、环境变量或配置文件，你可以轻松定制 Commity 的行为。
5.  **个性化支持**：喜欢在 commit message 中添加 emoji？没问题！`commity --emoji` 帮你搞定。

## 快速上手

体验 Commity 只需两步：

**1. 安装 Commity**

使用 `pip` 或 `uv` 即可轻松安装：

```bash
# 使用 pip
pip install commity

# 或者使用 uv
uv tool install commity
```

**2. 配置你的 AI 模型**

最简单的方式是创建一个配置文件。例如，如果你使用 Ollama 和 Llama3 模型：

```bash
# 创建配置目录
mkdir -p ~/.commity

# 创建并编辑配置文件
touch ~/.commity/config.json
```

然后将以下内容添加到 `config.json` 文件中：

```json
{
  "PROVIDER": "ollama",
  "MODEL": "llama3",
  "BASE_URL": "http://localhost:11434"
}
```

当然，你也可以配置使用 OpenAI 或 Gemini。

**3. 生成你的第一条 Commit Message**

现在，进入你的项目目录，暂存一些代码变更，然后运行：

```bash
git add .
commity
```

见证奇迹的时刻到了！Commity 会为你生成一条高质量的 commit message，并等待你的确认。

## 立即体验，为我们点亮星星！

Commity 致力于让每一位开发者的工作流都变得更简单、更高效。我们相信，一个好的工具能够极大地提升开发幸福感。

如果你也厌倦了手写 commit message，或者希望提升团队的代码提交规范，那么 Commity 绝对值得一试！

我们是一个开源项目，你的支持是我们不断前进的动力。如果你喜欢 Commity，请访问我们的 GitHub 仓库，为我们点亮一颗宝贵的 **Star** ⭐！

*   **GitHub 仓库**: [https://github.com/freboe/commity](https://github.com/freboe/commity)
*   **PyPI 项目页**: [https://pypi.org/project/commity/](https://pypi.org/project/commity/)

让我们一起用 AI 赋能开发，告别繁琐，拥抱高效！
