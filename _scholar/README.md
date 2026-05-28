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
