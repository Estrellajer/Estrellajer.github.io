---
layout: default
permalink: /publications/
title: publications
nav: true
nav_order: 2
---

<style>
  .publications-landing {
    --pub-text: var(--global-text-color);
    --pub-muted: #69717d;
    --pub-soft: #8d96a3;
    --pub-line: rgba(17, 19, 23, 0.1);
    --pub-accent: #557a9f;
    --pub-accent-soft: rgba(85, 122, 159, 0.12);
    padding-top: 1rem;
  }

  .publications-landing a:hover {
    color: var(--pub-accent);
    text-decoration: none;
  }

  .publications-hero {
    margin-bottom: 2.2rem;
  }

  .publications-eyebrow {
    margin-bottom: 0.9rem;
    color: var(--pub-accent);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
  }

  .publications-title {
    margin: 0;
    font-size: clamp(2.6rem, 5vw, 4.2rem);
    line-height: 0.98;
    letter-spacing: -0.04em;
    font-weight: 600;
  }

  .publications-subtitle {
    margin-top: 0.9rem;
    max-width: 44rem;
    color: var(--pub-muted);
    font-size: 1.05rem;
    line-height: 1.85;
  }

  .publications-search {
    margin-top: 1.3rem;
  }

  .publications-search .search {
    width: 100%;
    max-width: 24rem;
    min-height: 2.8rem;
    padding: 0 1rem;
    border: 1px solid var(--pub-line);
    border-radius: 999px;
    background: transparent;
    color: var(--pub-text);
  }

  .publications-landing .publications {
    margin-top: 0;
  }

  .publications-landing .publications h2.bibliography {
    margin: 2rem 0 1rem;
    padding-top: 0;
    border-top: 0;
    color: var(--pub-text);
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    text-align: left;
  }

  .publications-landing .publications ol.bibliography {
    margin-bottom: 0;
  }

  .publications-landing .publications ol.bibliography li {
    margin-bottom: 1.2rem;
    padding: 0.78rem 0.95rem;
    border: 1px solid rgba(85, 122, 159, 0.14);
    border-radius: 1.1rem;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(247, 250, 253, 0.99)),
      var(--global-card-bg-color);
    box-shadow: 0 12px 30px rgba(16, 24, 40, 0.06);
    transition:
      transform 0.18s ease,
      box-shadow 0.18s ease,
      border-color 0.18s ease;
  }

  .publications-landing .publications ol.bibliography li:hover {
    transform: translateY(-2px);
    border-color: rgba(85, 122, 159, 0.22);
    box-shadow: 0 18px 36px rgba(16, 24, 40, 0.09);
  }

  .publications-landing .publications .row {
    display: grid !important;
    grid-template-columns: 168px minmax(0, 1fr);
    gap: 1rem;
    margin: 0;
    align-items: stretch;
  }

  .publications-landing .publications .abbr,
  .publications-landing .publications [class*="col-sm-"],
  .publications-landing .publications [class^="col-sm-"] {
    max-width: none;
    flex: none;
    padding: 0;
  }

  .publications-landing .publications .abbr {
    margin-bottom: 0;
    height: 100%;
  }

  .publications-landing .publications .publication-preview figure {
    margin-bottom: 0;
  }

  .publications-landing .publications .publication-copy {
    display: flex;
    flex-direction: column;
  }

  .publications-landing .publications .publication-copy .links {
    margin-top: auto;
  }

  .publications-landing .publications .publication-meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-bottom: 0.28rem;
  }

  .publications-landing .publications .publication-tag,
  .publications-landing .publications .publication-meta-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    max-width: 100%;
    min-height: 1.5rem;
    padding: 0.16rem 0.52rem;
    border: 1px solid rgba(63, 97, 137, 0.16);
    border-radius: 999px;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    line-height: 1.2;
    text-decoration: none !important;
    text-transform: uppercase;
  }

  .publications-landing .publications .publication-tag {
    background: linear-gradient(180deg, rgba(85, 122, 159, 0.11), rgba(85, 122, 159, 0.07));
    color: #315578 !important;
  }

  .publications-landing .publications .publication-meta-link {
    background: rgba(17, 19, 23, 0.035);
    color: var(--pub-soft) !important;
  }

  .publications-landing .publications .publication-tag:hover {
    color: #254869 !important;
    border-color: rgba(63, 97, 137, 0.24);
    background: linear-gradient(180deg, rgba(85, 122, 159, 0.16), rgba(85, 122, 159, 0.09));
  }

  .publications-landing .publications .publication-meta-link:hover {
    color: var(--pub-muted) !important;
    border-color: rgba(63, 97, 137, 0.2);
    background: rgba(17, 19, 23, 0.06);
  }

  .publications-landing .publications .publication-preview {
    overflow: hidden;
    border-radius: 0.75rem;
    height: 100%;
  }

  .publications-landing .publications .publication-preview,
  .publications-landing .publications .publication-preview figure,
  .publications-landing .publications .publication-preview picture {
    display: block;
    margin: 0;
  }

  .publications-landing .publications .publication-preview figure,
  .publications-landing .publications .publication-preview picture,
  .publications-landing .publications .publication-preview img.preview,
  .publications-landing .publications .publication-preview .preview {
    display: block;
    width: 100%;
    height: 100%;
    min-height: 0;
    padding: 0;
    object-fit: cover;
    border-radius: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .publications-landing .publications .publication-media-fallback {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    min-height: 6rem;
    border-radius: 0.75rem;
    background:
      repeating-linear-gradient(
        -45deg,
        rgba(85, 122, 159, 0.05),
        rgba(85, 122, 159, 0.05) 10px,
        rgba(255, 255, 255, 0.72) 10px,
        rgba(255, 255, 255, 0.72) 20px
      ),
      linear-gradient(180deg, #f9fbfd 0%, #eef3f8 100%);
  }

  .publications-landing .publications .publication-media-fallback-mark {
    color: var(--pub-soft);
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }

  .publications-landing .publications .title {
    color: var(--pub-text);
    font-size: 1.12rem;
    line-height: 1.3;
    margin-bottom: 0.24rem;
    font-weight: 600;
  }

  .publications-landing .publications .author,
  .publications-landing .publications .links {
    color: var(--pub-muted);
  }

  .publications-landing .publications .author,
  .publications-landing .publications .periodical {
    font-size: 0.86rem;
    line-height: 1.5;
  }

  .publications-landing .publications .periodical {
    color: var(--pub-soft);
    margin-top: 0.12rem;
  }

  .publications-landing .publications .links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.38rem;
    margin-top: 0.55rem;
    padding-top: 0;
  }

  .publications-landing .publications .links a.btn {
    border: 1px solid rgba(85, 122, 159, 0.16);
    border-radius: 999px;
    background: rgba(85, 122, 159, 0.06);
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    line-height: 1.2;
    transition:
      background 0.18s ease,
      border-color 0.18s ease,
      color 0.18s ease;
  }

  .publications-landing .publications .links a.btn:hover {
    background: rgba(85, 122, 159, 0.12);
    border-color: rgba(85, 122, 159, 0.28);
  }

  @media (max-width: 900px) {
    .publications-landing .publications .row {
      grid-template-columns: 1fr;
    }
  }
</style>

<div class="publications-landing">
  <section class="publications-hero">
    <div class="publications-eyebrow">Publications</div>
    <h1 class="publications-title">Selected papers and ongoing work.</h1>
    <div class="publications-subtitle">
      A focused list of recent work, with previews, venue labels, and direct links to preprints or code when available.
    </div>
    <div class="publications-search">
      {% include bib_search.liquid %}
    </div>
  </section>

  <div class="publications">
    {% bibliography %}
  </div>
</div>
