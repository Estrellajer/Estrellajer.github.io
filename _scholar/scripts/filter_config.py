#!/usr/bin/env python3
"""Post-process config: filter & rename."""
import yaml

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

blacklist_urls = [".pdf", "openreview.net/profile"]
blacklist_names = [
    "Introducing Nested Learning",
    "白嫖 Cloudflare",
    "Generative Artificial Intelligence",
    "Evaluation Guidebook",
]

scholars = [s for s in config["scholars"]
    if not any(b in s["url"] for b in blacklist_urls)
    and not any(b in s["name"] for b in blacklist_names)]

rename_map = {
    "My Github Blog": "percent4 Blog",
    "科学空间|Scientific Spaces": "苏剑林 - 科学空间",
    "关于 | DaNing": "DaNing Blog",
    "Interconnects | Nathan Lambert": "Nathan Lambert",
    "Stay Hungry,Stay Foolish.": "Tobias Lee Blog",
    "Geeks_Z": "Hwzhao Blog",
    "工具导航 | YY": "YY Blog",
    "熊大如如的猪窝": "Xiongda Blog",
    "博客 | A. Weers": "A. Weers Blog",
    "blog | Ziming Liu": "Ziming Liu Blog",
    "Connectionism - Thinking Machines Lab": "Thinking Machines Lab",
    "PKU-OV3 周嘉欢主页": "周嘉欢 Homepage",
    "About - Shunyu Yao": "Shunyu Yao Homepage",
    "Da-Wei Zhou - Homepage": "Da-Wei Zhou Homepage",
    "Yongjin Yang | AI Alignment": "Yongjin Yang Homepage",
    "苏俊杰 - Junjie Su": "Junjie Su(苏俊杰)",
    "沉宇腾 - Yuteng Shen": "Yuteng Shen(沉宇腾)",
    "Zhen-Yu Zhang @ RIKEN-AIP": "Zhen-Yu Zhang Homepage",
    "陈江杰 - Jiangjie Chen": "Jiangjie Chen Homepage",
    "王紫峰的个人主页": "Zifeng Wang Homepage",
    "Liang Feng": "Liang Feng Homepage",
    "Enneng Yang - Homepage": "Enneng Yang Homepage",
    "Yifei Zhang Home Page": "Yifei Zhang Homepage",
    "主页 - 胡椒的 Coding Room": "Junyao Hu Blog",
}

for s in scholars:
    for old, new in rename_map.items():
        if s["name"].startswith(old) or old in s["name"]:
            s["name"] = new
            break

config["scholars"] = scholars
with open("config.yaml", "w", encoding="utf-8") as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=None, sort_keys=False, width=1000)
print(f"Filtered to {len(scholars)} scholars")
