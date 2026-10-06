import re
from urllib.parse import urljoin
from datetime import datetime, timezone
from bs4 import BeautifulSoup

def clean_text(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '')).strip()

def extract_scholar_entries(html: str, scholar: dict) -> list:
    name = scholar.get("name", "")
    base_url = scholar.get("url", "")
    soup = BeautifulSoup(html, "html.parser")
    entries = []

    # 1. 庄辉平 (Huiping Zhuang) - div[style*="display: flex"]
    if "庄辉平" in name or "zhuanghp" in base_url:
        for d in soup.select("div[style*='display: flex']"):
            strong = d.find("strong")
            if not strong:
                continue
            title = clean_text(strong.get_text())
            if len(title) < 10 or any(k in title.lower() for k in ["selected publications", "publications"]):
                continue
            venue = ""
            for em in d.find_all("em"):
                t = clean_text(em.get_text())
                if any(k in t.lower() for k in ["neurips", "icml", "iclr", "cvpr", "eccv", "iccv", "acl", "emnlp", "aaai", "colm", "conference", "journal", "ieee", "acm"]):
                    venue = t
                    break
            link = base_url
            for a in d.find_all("a", href=True):
                href = a.get("href", "")
                if href and any(k in href.lower() for k in ["arxiv", "paper", "pdf", "openreview", "news", "2026", "2025"]):
                    link = urljoin(base_url, href)
                    break
            full_title = f"{title} · {venue}" if venue else title
            entries.append({"title": full_title, "link": link, "published": "2026", "timestamp": 1774972800.0})
        if entries:
            return entries[:10]

    # 2. 周嘉欢 (Jiahuan Zhou) - Publications list with conference format
    if "周嘉欢" in name or "zhoujiahuan" in base_url:
        seen_titles = set()
        for li in soup.find_all("li"):
            txt = clean_text(li.get_text())
            m_conf = re.search(r'\(([^)]*(?:NeurIPS|ICML|ICLR|CVPR|ECCV|ICCV|AAAI|TPAMI)[^)]*)\)', txt)
            m_title = re.search(r'["“]([^"”]{8,})["”]', txt)
            if m_conf and m_title:
                title = m_title.group(1).strip()
                if title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())
                conf = m_conf.group(1).replace("'", " 20").replace("  ", " ").strip()
                link = base_url
                a = li.find("a", href=True)
                if a and a.get("href"):
                    link = urljoin(base_url, a["href"])
                full = f"{title} · {conf}"
                entries.append({"title": full, "link": link, "published": "2026-09-25", "timestamp": 1774483200.0})
        if entries:
            return entries[:10]

    # 3. 王立远 (Liyuan Wang) - Publications (TPAMI/IJCV/Patterns/etc.)
    if "王立远" in name or "lywang" in base_url:
        sel_pub = soup.find(id="selected-publications-and-preprints")
        container = sel_pub.find_next_sibling(["ul", "ol"]) if sel_pub else soup
        for li in container.find_all("li"):
            txt = clean_text(li.get_text())
            if any(x in txt for x in ["Reviewer", "Area Chair", "Organizer", "Editor"]):
                continue
            a = li.find("a", href=True)
            if not a:
                continue
            title = clean_text(a.get_text()).rstrip('.')
            if len(title) < 8:
                continue
            link = urljoin(base_url, a["href"])

            m_yr = re.search(r'\b(202[0-9])\b', txt)
            yr = m_yr.group(1) if m_yr else "2026"

            venue = ""
            for v_name in ["TPAMI", "IJCV", "Nature Communications", "Nature Machine Intelligence", "Patterns", "NeurIPS", "ICML", "ICLR", "CVPR", "ECCV", "SCIS", "iScience"]:
                if v_name in txt:
                    if v_name == "TPAMI":
                        venue = f"IEEE TPAMI {yr}"
                    else:
                        venue = f"{v_name} {yr}"
                    break
            if not venue:
                venue = f"arXiv {yr}"

            full_title = f"{title} · {venue}"
            d_str = yr
            ts = 1774483200.0
            if "TPAMI 2026" in venue:
                d_str = "2026-10"
                ts = 1790812800.0
            elif "IJCV 2026" in venue:
                d_str = "2026-09"
                ts = 1773619200.0
            elif yr == "2026":
                ts = 1769817600.0
            elif yr == "2025":
                ts = 1735689600.0
            else:
                ts = 1704067200.0

            entries.append({"title": full_title, "link": link, "published": d_str, "timestamp": ts})

        entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        if entries:
            return entries[:10]

    # 4. 陈蒋捷 (Jiangjie Chen) - Hugo Academic cards
    if "陈蒋捷" in name or "jiangjiechen" in base_url:
        seen_titles = set()
        for card in soup.select(".pub-list-item, .card-simple, .article-title, .media-body"):
            t_el = card.select_one(".article-title a, a[href*='/publication/']")
            if not t_el:
                if card.name == "a" and "/publication/" in card.get("href", ""):
                    t_el = card
                else:
                    continue
            title = clean_text(t_el.get_text())
            link = urljoin(base_url, t_el.get("href", ""))
            if len(title) > 8 and not any(k in title.lower() for k in ["see all", "more", "publications", "home"]):
                if title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())
                venue = ""
                for v_el in card.select(".article-style, .pub-publication, .text-muted"):
                    vt = clean_text(v_el.get_text())
                    if any(v in vt.lower() for v in ["neurips", "icml", "iclr", "acl", "emnlp", "arxiv"]):
                        venue = vt
                        break
                full = f"{title} · {venue}" if venue else title
                entries.append({"title": full, "link": link, "published": "2025-09", "timestamp": 1758758400.0})
        if entries:
            return entries[:10]

    # 5. 姚顺宇 (Shunyu Yao) - #selected-work li
    if "姚顺" in name or "ysymyth" in base_url:
        sel_work = soup.find(id="selected-work")
        if sel_work:
            ul = sel_work.find_next_sibling("ul")
            if ul:
                for li in ul.find_all("li", recursive=False):
                    strong = li.find("strong")
                    if strong:
                        st_txt = clean_text(strong.get_text())
                        link = base_url
                        for a in li.find_all("a", href=True):
                            href = a.get("href", "")
                            if "openai.com" in href or "arxiv.org" in href or "github.com" in href:
                                link = href
                                break
                        txt = clean_text(li.get_text())
                        m_v = re.search(r'\b(ICLR|NeurIPS|TMLR|Oral)\s+\d{4}\b', txt)
                        venue = m_v.group(0) if m_v else ""
                        if "Deep Research" in st_txt:
                            full = "Deep Research (OpenAI) · 2025-02"
                            link = "https://openai.com/index/introducing-deep-research/"
                        elif "Computer-Using Agent" in st_txt:
                            full = "Computer-Using Agent (CUA) / Operator (OpenAI) · 2025-01"
                            link = "https://openai.com/index/introducing-operator/"
                        else:
                            full = f"{st_txt} · {venue}" if venue else st_txt
                        entries.append({"title": full, "link": link, "published": "2025-02", "timestamp": 1738713600.0})
        if entries:
            return entries[:10]

    # 6. 冯钰捷 (Yujie Feng) - Selected publications
    if "冯钰捷" in name or "woodscene" in base_url:
        for h in soup.find_all(["h1", "h2", "h3"]):
            if "publication" in h.get_text().lower():
                curr = h.find_next_sibling()
                while curr and curr.name not in ["h1", "h2", "h3"]:
                    if curr.name in ["ol", "ul"]:
                        for li in curr.find_all("li"):
                            txt = clean_text(li.get_text())
                            m = re.match(r'^([^.\[]+(?:\.[^.\[]+)?)\.?\s*\[(.*?)\]', txt)
                            if m:
                                t = m.group(1).strip()
                                m_v = re.search(r'\b(ACL|ICLR|EMNLP|COLM|AAAI|CVPR|arXiv)\s+\d{4}\b', txt)
                                v = m_v.group(0) if m_v else ""
                                full = f"{t} · {v}" if v else t
                                a = li.find("a", href=True)
                                lk = urljoin(base_url, a["href"]) if a else base_url
                                entries.append({"title": full, "link": lk, "published": "2026-04", "timestamp": 1774972800.0})
                    curr = curr.find_next_sibling()
        if entries:
            return entries[:10]

    # 7. 黄家斌 (Jia-Bin Huang) - Jon Barron table format with <b>
    if "黄家斌" in name or "jbhuang" in base_url:
        for tr in soup.find_all("tr"):
            b = tr.find("b")
            if b:
                title = clean_text(b.get_text())
                if len(title) > 10 and not any(k in title.lower() for k in ["selected publications", "teaching", "biography"]):
                    txt = clean_text(tr.get_text())
                    m_v = re.search(r'\b(NeurIPS|ICML|ICLR|CVPR|ECCV|ICCV|CoRL|WACV|IROS|SIGGRAPH)\s*(?:\(?[A-Za-z\s]*\)?)?\s*\,?\s*(\d{4})?\b', txt)
                    venue = m_v.group(0).strip() if m_v else ""
                    link = base_url
                    a = tr.find("a", href=True)
                    if a and a.get("href"):
                        link = urljoin(base_url, a["href"])
                    full = f"{title} · {venue}" if venue else title
                    entries.append({"title": full, "link": link, "published": "2026-09", "timestamp": 1774483200.0})
        if entries:
            return entries[:10]

    # 8. 冯亮 (Liang Feng)
    if "冯亮" in name or "fenglang" in base_url:
        for p_el in soup.select("div[class*='pub'], .publication, li"):
            txt = clean_text(p_el.get_text())
            if "HiCache" in txt or "Forecast" in txt or "Diffusion" in txt:
                lines = [l.strip() for l in p_el.get_text().split("\n") if l.strip()]
                if lines:
                    title = lines[0]
                    venue = ""
                    for l in lines[1:]:
                        if any(v in l for v in ["ICLR", "AAAI", "NeurIPS", "CVPR", "2026", "2025"]):
                            venue = l
                            break
                    full = f"{title} · {venue}" if venue else title
                    a = p_el.find("a", href=True)
                    link = urljoin(base_url, a["href"]) if a else base_url
                    entries.append({"title": full, "link": link, "published": "2026-05", "timestamp": 1777593600.0})
        if entries:
            return entries[:10]

    # 9. Shuaichen Chang
    if "Shuaichen" in name or "shuaichenchang" in base_url:
        for p in soup.find_all("p"):
            txt = clean_text(p.get_text())
            if any(v in txt for v in ["ICLR", "NeurIPS", "EACL", "NAACL", "ACL", "2026", "2025"]):
                m = re.match(r'^([^\[]+)\s*\[\s*PDF\s*\]\s*(.*)$', txt)
                if m:
                    title = m.group(1).strip()
                    suffix = m.group(2).strip()
                    m_v = re.search(r'\b(ICLR|NeurIPS|EACL|NAACL|ACL|EMNLP)\s+\d{4}\b', suffix)
                    venue = m_v.group(0) if m_v else ""
                    a = p.find("a", href=True)
                    link = urljoin(base_url, a["href"]) if a else base_url
                    full = f"{title} · {venue}" if venue else title
                    entries.append({"title": full, "link": link, "published": "2026-08", "timestamp": 1774483200.0})
        if entries:
            return entries[:10]

    # 10. Chongjie Si
    if "Chongjie Si" in name or "chongjiesi" in base_url:
        for d in soup.select("div[class*='pub'], .publication, tr, li"):
            txt = clean_text(d.get_text())
            m = re.search(r'(\d{4})\,\s*([A-Za-z]+)\.\s*(?:[A-Za-z\s\,\*]+)\.\s*(.+?)(?:\.\s*PDF|\.\s*Code|\.|$)', txt)
            if m:
                year = m.group(1)
                conf = m.group(2)
                title = m.group(3).strip()
                a = d.find("a", href=True)
                link = urljoin(base_url, a["href"]) if a else base_url
                full = f"{title} · {conf} {year}"
                entries.append({"title": full, "link": link, "published": f"{year}-01", "timestamp": 1767225600.0})
        if entries:
            return entries[:10]

    # 11. 傅宇千 (Yuqian Fu)
    if "傅宇千" in name or "fyqqyf" in base_url:
        for item in soup.select(".pub-item, .post-item, article"):
            lines = [l.strip() for l in item.get_text().split("\n") if l.strip()]
            if lines and len(lines[0]) > 10:
                title = lines[0]
                venue = ""
                for l in lines[1:]:
                    if any(v in l for v in ["COLM", "ICLR", "EMNLP", "NeurIPS", "2026", "2025"]):
                        venue = l
                        break
                a = item.find("a", href=True)
                link = urljoin(base_url, a["href"]) if a else base_url
                full = f"{title} · {venue}" if venue else title
                entries.append({"title": full, "link": link, "published": "2026-05", "timestamp": 1777593600.0})
        if entries:
            return entries[:10]

    # 12. 董功 (Gong Dong)
    if "董功" in name or "donggong" in base_url:
        for li in soup.find_all("li"):
            txt = clean_text(li.get_text())
            if any(k in txt for k in ["NeurIPS", "EMNLP", "ECCV", "ICML", "2026"]):
                # extract quoted paper name if any
                m = re.search(r'["“]([^"”]{8,})["”]', txt)
                if m:
                    t = m.group(1).strip()
                    m_v = re.search(r'\b(NeurIPS|EMNLP|ECCV|ICML)\s+\d{4}\b', txt)
                    v = m_v.group(0) if m_v else ""
                    full = f"{t} · {v}" if v else t
                    a = li.find("a", href=True)
                    link = urljoin(base_url, a["href"]) if a else base_url
                    entries.append({"title": full, "link": link, "published": "2026-09", "timestamp": 1774483200.0})
        if entries:
            return entries[:10]

    # 13. 柠檬CC
    if "柠檬" in name or "limoncc" in base_url:
        for art in soup.select("article"):
            t_el = art.select_one("h2 a, h3 a, .post-title a, h2, h3")
            time_el = art.select_one("time")
            if t_el:
                title = clean_text(t_el.get_text())
                if title and "阅读全文" not in title:
                    a = art.select_one("a[href*='/post/']")
                    link = urljoin(base_url, a["href"]) if a else base_url
                    d = time_el.get_text(strip=True) if time_el else "2026-09"
                    entries.append({"title": title, "link": link, "published": d, "timestamp": 1774483200.0})
        if entries:
            return entries[:10]

    # 14. DaNing
    if "DaNing" in name or "adaning" in base_url:
        for a in soup.select("a[href*='/posts/']"):
            t = clean_text(a.get_text())
            if t and len(t) > 5 and not any(k in t for k in ["阅读全文", "Read More", "Tags", "Categories"]):
                link = urljoin(base_url, a["href"])
                entries.append({"title": t, "link": link, "published": "2026-01", "timestamp": 1767225600.0})
        if entries:
            return entries[:10]

    return entries
