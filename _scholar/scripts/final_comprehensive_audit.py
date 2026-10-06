import json
import re

with open('_scholar/_snapshots/events_history.json', 'r', encoding='utf-8') as f:
    hist = json.load(f)

SUSPICIOUS_ENDS = [
    ' in', ' to', ' a', ' an', ' the', ' of', ' for', ' with', ' via',
    ' and', ' or', ' &', ' as', ' by', ':', ',', '-', '·'
]

FORBIDDEN_PHRASES = [
    'has been accepted', 'have been accepted', 'our papers', 'our paper',
    '🎉', '🔥', '🥳', '✨', '👉', '💡', 'One paper has been accepted',
    'Three of our papers', 'Two papers have been accepted'
]

print(f"=== COMPREHENSIVE AUDIT OF {len(hist)} SCHOLARS ===")

errors = []
warnings = []

for idx, item in enumerate(hist):
    scholar = item.get('scholar', '')
    url = item.get('scholar_url', '')
    headline = item.get('text', '')
    hl_link = item.get('link', '')
    sub_items = item.get('sub_items', [])

    # 1. Headline validation
    if not headline or len(headline.strip()) < 5:
        errors.append(f"[{idx:02d}] {scholar}: Headline empty or too short!")

    for end in SUSPICIOUS_ENDS:
        if headline.lower().endswith(end):
            errors.append(f"[{idx:02d}] {scholar}: Headline ends with '{end}': {headline}")

    for p in FORBIDDEN_PHRASES:
        if p.lower() in headline.lower():
            errors.append(f"[{idx:02d}] {scholar}: Headline contains forbidden phrase '{p}': {headline}")

    if not hl_link or not hl_link.startswith('http'):
        errors.append(f"[{idx:02d}] {scholar}: Headline link invalid: {hl_link}")

    # Check headline venue split if any
    if ' · ' in headline:
        title_part = headline.split(' · ')[0].strip()
        for end in SUSPICIOUS_ENDS:
            if title_part.lower().endswith(end):
                errors.append(f"[{idx:02d}] {scholar}: Headline title-part ends with '{end}': {headline}")

    # 2. Sub-items validation & deduplication
    seen_texts = {headline.strip().lower()}
    seen_links = {hl_link.strip().lower()}

    for s_idx, sub in enumerate(sub_items):
        st = sub.get('text', '')
        slink = sub.get('link', '')

        if not st or len(st.strip()) < 5:
            errors.append(f"[{idx:02d}] {scholar}: Sub-item {s_idx} empty or too short!")

        for end in SUSPICIOUS_ENDS:
            if st.lower().endswith(end):
                errors.append(f"[{idx:02d}] {scholar}: Sub-item {s_idx} ends with '{end}': {st}")

        for p in FORBIDDEN_PHRASES:
            if p.lower() in st.lower():
                errors.append(f"[{idx:02d}] {scholar}: Sub-item {s_idx} contains forbidden phrase '{p}': {st}")

        if ' · ' in st:
            title_part = st.split(' · ')[0].strip()
            for end in SUSPICIOUS_ENDS:
                if title_part.lower().endswith(end):
                    errors.append(f"[{idx:02d}] {scholar}: Sub-item {s_idx} title-part ends with '{end}': {st}")

        # Duplication check
        st_norm = st.strip().lower()
        if st_norm in seen_texts:
            errors.append(f"[{idx:02d}] {scholar}: Duplicate sub-item text found with headline or prior sub-item: {st}")
        seen_texts.add(st_norm)

        # Link check (warn if exact duplicate link within scholar)
        if slink and slink.strip().lower() in seen_links:
            # Only warn if it's not a generic homepage
            if not any(domain in slink for domain in ['github.io', 'limoncc.com', 'transformer-circuits']):
                warnings.append(f"[{idx:02d}] {scholar}: Duplicate link {slink} in sub-item {s_idx}")
        if slink:
            seen_links.add(slink.strip().lower())

    # 3. Specific Scholar Assertions:
    if '姚顺宇' in scholar:
        print(f"--> Checked 姚顺宇: headline='{headline}', sub_items={len(sub_items)}")
        if 'Deep Research' not in headline:
            errors.append("姚顺宇: Headline should be Deep Research (OpenAI)")
        if len(sub_items) < 3:
            errors.append("姚顺宇: Sub-items count too low (< 3)")

    if '冯钰捷' in scholar:
        print(f"--> Checked 冯钰捷: headline='{headline}', sub_items={len(sub_items)}")
        if 'FOREVER' not in headline:
            errors.append("冯钰捷: Headline should be FOREVER ACL 2026")
        if len(sub_items) < 3:
            errors.append("冯钰捷: Sub-items count too low (< 3)")

print("\n" + "=" * 50)
if errors:
    print(f"AUDIT FAILED! Found {len(errors)} errors:")
    for err in errors:
        print("  [ERROR]", err)
else:
    print("ALL AUDIT CHECKS PASSED! 0 ERRORS FOUND!")

if warnings:
    print(f"\nWarnings ({len(warnings)}):")
    for w in warnings[:10]:
        print("  [WARN]", w)
print("=" * 50)
