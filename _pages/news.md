---
layout: default
title: news
permalink: /news/
---

<style>
  .news-landing {
    padding-top: 1.2rem;
    padding-bottom: 3.5rem;
  }

  .news-hero {
    margin-bottom: 2.5rem;
  }

  .news-hero-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.85rem;
    margin-bottom: 1.25rem;
  }

  .news-eyebrow {
    color: var(--hl-accent);
    font-size: 0.8rem;
    font-weight: 650;
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }

  .news-back-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    background: var(--hl-surface);
    border: 1px solid var(--hl-border);
    color: var(--hl-text-muted);
    font-size: 0.83rem;
    font-weight: 550;
    text-decoration: none !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .news-back-btn:hover {
    background: var(--hl-surface-hover);
    border-color: var(--hl-border-hover);
    color: var(--hl-accent);
    transform: translateX(-2px);
    box-shadow: 0 3px 8px rgba(15, 23, 42, 0.06);
  }

  .news-title {
    margin: 0;
    font-size: clamp(2.4rem, 4.5vw, 3.6rem);
    line-height: 1.05;
    letter-spacing: -0.035em;
    font-weight: 700;
    color: var(--hl-text-primary);
  }

  .news-subtitle {
    margin-top: 0.85rem;
    max-width: 44rem;
    color: var(--hl-text-muted);
    font-size: 1.05rem;
    line-height: 1.85;
  }
</style>

<div class="news-landing">
  <section class="news-hero">
    <div class="news-hero-bar">
      <div class="news-eyebrow">News & Updates</div>
      <a class="news-back-btn" href="{{ '/' | relative_url }}">
        <i class="fa-solid fa-arrow-left"></i>
        <span>Back to Home</span>
      </a>
    </div>

    <h1 class="news-title">All News & Milestones</h1>
    <div class="news-subtitle">
      Papers, research internships, grants, and academic milestones along my journey.
    </div>
  </section>

  {% include news.liquid %}
</div>
