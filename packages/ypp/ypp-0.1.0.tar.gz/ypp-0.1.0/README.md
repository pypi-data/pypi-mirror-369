# ypp

多分支 worktree 管理工具（支持 `krepo-ng` 与 `git`）。

## 安装

```bash
pip install ypp
```

## 使用

- 创建 worktree：

```bash
ypp add <path> <branch>
```

这会在 `~/<path>/wpsmain` 和 `~/<path>/wpsweb` 下分别创建或切换到 `<branch>`。

- 列出 worktree：

```bash
ypp list
```

## 依赖

- 需要本机已安装并在 PATH 中可用：`krepo-ng`、`git`。

## 许可

MIT