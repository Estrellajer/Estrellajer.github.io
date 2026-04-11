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
    margin-bottom: 1.7rem;
  }

  .publications-landing .publications .row {
    display: grid !important;
    grid-template-columns: 264px minmax(0, 1fr);
    gap: 1.5rem;
    margin: 0;
    align-items: start;
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
  }

  .publications-landing .publications .abbr abbr {
    width: auto !important;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.3rem 0.72rem;
    margin-bottom: 0.8rem;
    border-radius: 999px;
    background: rgba(17, 19, 23, 0.05) !important;
    color: var(--pub-soft) !important;
    font-weight: 600;
    font-size: 0.76rem;
    letter-spacing: 0.08em;
  }

  .publications-landing .publications figure {
    margin-bottom: 0;
  }

  .publications-landing .publications .preview {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: contain;
    padding: 0.45rem;
    border: 1px solid rgba(17, 19, 23, 0.08);
    border-radius: 0.9rem;
    background: #f7f8fa;
    box-shadow: none !important;
  }

  .publications-landing .publications .title {
    color: var(--pub-text);
    font-size: 1.38rem;
    line-height: 1.4;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .publications-landing .publications .author,
  .publications-landing .publications .periodical,
  .publications-landing .publications .links {
    color: var(--pub-muted);
  }

  .publications-landing .publications .links {
    margin-top: 0.85rem;
  }

  .publications-landing .publications .links a.btn {
    border-radius: 999px;
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
