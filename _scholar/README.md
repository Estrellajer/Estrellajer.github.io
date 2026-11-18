# Scholar Monitor

定时监控学者博客/主页更新的工具，通过 GitHub Actions 每天自动运行。

## 工作流程

1. 对每个站点 **优先检测 RSS**（Jekyll/Hugo/WordPress/Substack 等框架通常自带 RSS）
2. 有 RSS 的 → 直接解析新条目（最可靠、最干净）
3. 无 RSS 的 → 提取页面正文内容 → 与上次快照做 diff → 报告具体变化

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 从浏览器收藏夹生成初始配置
python scripts/generate_config.py favorites.html

# 3. 批量探测 RSS
python scripts/discover_rss.py

# 4. 手动检查一次
python scripts/monitor.py
```

## 数据流

- 代码在 `main`，状态全部在 `data` 分支（`_snapshots/` 的内容：快照、`events_history.json`、`feed.json`、`feed.xml`、`latest_report.md`）。
- Actions 把 `data` 分支检出到 `_scholar/_snapshots`，跑完后以单个 squash 提交强推回 `data`，不往 `main` 写任何东西。
- `/scholar/`（noindex，不进 sitemap）由 `assets/js/scholar.js` 在浏览器里读取
  `https://raw.githubusercontent.com/Estrellajer/Estrellajer.github.io/data/feed.json`；本地调试可加 `?data=<url>` 指向别的 JSON。
- Atom 订阅：`https://raw.githubusercontent.com/Estrellajer/Estrellajer.github.io/data/feed.xml`。
- 抓取失败等运维信息只出现在 Actions 的 job summary / warning 注解和 `data` 分支的 `latest_report.md`，页面上不展示。
- 本地重新生成数据（不联网）：先 `git worktree add _snapshots data`（在 `_scholar/` 下），再 `python scripts/monitor.py --report-only`。

## 配置

编辑 `config.yaml`，每个学者可自定义：

```yaml
scholars:
  - name: "苏剑林"
    url: "https://kexue.fm/"
    category: blog
    selectors:           # 正文提取的 CSS 选择器（按优先级尝试）
      - "article"
      - ".entry-content"
      - ".post-content"
    remove_selectors:    # 要排除的区域
      - ".comments"
      - "#respond"
      - ".sidebar"
```

## 自定义 CSS Selectors

不同网站布局不同，通过 selectors 适配：

| 站点类型 | 常用 selectors |
|---------|---------------|
| GitHub Pages (Jekyll) | `article`, `.post-content`, `.entry-content` |
| 学术主页 | `main`, `.content`, `#content`, `#publications` |
| Substack | `.main`, `.post`, `article` |
| 知乎 | `.RichText`, `.ContentItem` |
| CSDN/博客园 | `#article_content`, `.post`, `article` |

如果某个学者页面变了但你没看到内容变化，可以修改其 selectors 并重新运行。
