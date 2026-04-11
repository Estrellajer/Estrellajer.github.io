---
layout: default
permalink: /blog/
title: blog
nav: true
nav_order: 1
pagination:
  enabled: true
  collection: posts
  permalink: /page/:num/
  per_page: 5
  sort_field: date
  sort_reverse: true
  trail:
    before: 1
    after: 3
---

<style>
  .blog-landing {
    --blog-text: var(--global-text-color);
    --blog-muted: #69717d;
    --blog-soft: #8d96a3;
    --blog-line: rgba(17, 19, 23, 0.1);
    --blog-accent: #557a9f;
    --blog-accent-soft: rgba(85, 122, 159, 0.12);
    padding-top: 1rem;
  }

  .blog-hero {
    margin-bottom: 2.2rem;
  }

  .blog-eyebrow {
    margin-bottom: 0.9rem;
    color: var(--blog-accent);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
  }

  .blog-title {
    margin: 0;
    font-size: clamp(2.6rem, 5vw, 4.2rem);
    line-height: 0.98;
    letter-spacing: -0.04em;
    font-weight: 600;
  }

  .blog-subtitle {
    margin-top: 0.9rem;
    max-width: 42rem;
    color: var(--blog-muted);
    font-size: 1.05rem;
    line-height: 1.85;
  }

  .blog-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.7rem;
    margin-top: 1.4rem;
  }

  .blog-filter {
    display: inline-flex;
    align-items: center;
    min-height: 2.2rem;
    padding: 0 0.9rem;
    border-radius: 999px;
    background: var(--blog-accent-soft);
    color: #496885;
    font-size: 0.92rem;
    text-decoration: none !important;
  }

  .blog-list {
    display: grid;
    gap: 1.8rem;
    padding: 0;
    margin: 0;
    list-style: none;
  }

  .blog-item {
    padding-top: 1.8rem;
    border-top: 1px solid var(--blog-line);
  }

  .blog-item:first-child {
    padding-top: 0;
    border-top: 0;
  }

  .blog-item-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 220px;
    gap: 1.5rem;
    align-items: start;
  }

  .blog-item-date {
    color: var(--blog-soft);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  .blog-item-title {
    display: inline-block;
    margin: 0.45rem 0 0.7rem;
    font-size: 1.45rem;
    line-height: 1.35;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--blog-text);
    text-decoration: none;
  }

  .blog-item-title:hover {
    text-decoration: none;
  }

  .blog-item-desc {
    margin: 0 0 0.8rem;
    color: var(--blog-muted);
    line-height: 1.85;
  }

  .blog-item-meta,
  .blog-item-taxonomy {
    color: var(--blog-soft);
    font-size: 0.95rem;
    line-height: 1.8;
  }

  .blog-item-taxonomy a {
    color: inherit;
    text-decoration: none;
  }

  .blog-item-taxonomy a:hover {
    color: var(--blog-accent);
    text-decoration: none;
  }

  .blog-item-thumb {
    width: 100%;
    aspect-ratio: 16 / 10;
    object-fit: cover;
    border-radius: 1rem;
    border: 1px solid rgba(17, 19, 23, 0.08);
    background: #eef2f6;
  }

  .blog-pagination .pagination {
    margin-top: 2.2rem;
    gap: 0.35rem;
  }

  .blog-pagination .page-link {
    border: 1px solid var(--blog-line);
    border-radius: 999px !important;
    color: var(--blog-text);
    background: transparent;
    min-width: 2.6rem;
    text-align: center;
  }

  .blog-pagination .page-item.active .page-link,
  .blog-pagination .page-link:hover {
    background: var(--blog-accent-soft);
    border-color: transparent;
    color: #496885;
  }

  @media (max-width: 800px) {
    .blog-item-grid {
      grid-template-columns: 1fr;
    }

    .blog-item-thumb {
      max-width: 320px;
    }
  }
</style>

<div class="blog-landing">
  <section class="blog-hero">
    <div class="blog-eyebrow">Blog</div>
    <h1 class="blog-title">Notes on research, coding, and life.</h1>
    <div class="blog-subtitle">
      A quieter archive for technical notes, project logs, and occasional reflections.
    </div>

    {% if site.display_tags and site.display_tags.size > 0 or site.display_categories and site.display_categories.size > 0 %}
      <div class="blog-filters">
        {% for tag in site.display_tags %}
          <a class="blog-filter" href="{{ tag | slugify | prepend: '/blog/tag/' | relative_url }}"># {{ tag }}</a>
        {% endfor %}
        {% for category in site.display_categories %}
          <a class="blog-filter" href="{{ category | slugify | prepend: '/blog/category/' | relative_url }}">{{ category }}</a>
        {% endfor %}
      </div>
    {% endif %}

  </section>

  <ul class="blog-list">
    {% if page.pagination.enabled %}
      {% assign postlist = paginator.posts %}
    {% else %}
      {% assign postlist = site.posts %}
    {% endif %}

    {% assign postlist = postlist | where_exp: "post", "post.hidden != true" %}

    {% for post in postlist %}
      {% if post.external_source == blank %}
        {% assign read_time = post.content | number_of_words | divided_by: 180 | plus: 1 %}
      {% else %}
        {% assign read_time = post.feed_content | strip_html | number_of_words | divided_by: 180 | plus: 1 %}
      {% endif %}

      <li class="blog-item">
        <div class="blog-item-grid">
          <div>
            <div class="blog-item-date">{{ post.date | date: "%b %d, %Y" }}</div>

            {% if post.redirect == blank %}
              <a class="blog-item-title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
            {% elsif post.redirect contains '://' %}
              <a class="blog-item-title" href="{{ post.redirect }}" target="_blank">{{ post.title }}</a>
            {% else %}
              <a class="blog-item-title" href="{{ post.redirect | relative_url }}">{{ post.title }}</a>
            {% endif %}

            {% if post.description %}
              <p class="blog-item-desc">{{ post.description }}</p>
            {% endif %}

            <div class="blog-item-meta">{{ read_time }} min read</div>

            {% assign tags = post.tags | join: "" %}
            {% assign categories = post.categories | join: "" %}
            {% if tags != "" or categories != "" %}
              <div class="blog-item-taxonomy">
                {% for tag in post.tags %}
                  <a href="{{ tag | slugify | prepend: '/blog/tag/' | relative_url }}"># {{ tag }}</a>{% unless forloop.last %} · {% endunless %}
                {% endfor %}
                {% if tags != "" and categories != "" %} · {% endif %}
                {% for category in post.categories %}
                  <a href="{{ category | slugify | prepend: '/blog/category/' | relative_url }}">{{ category }}</a>{% unless forloop.last %} · {% endunless %}
                {% endfor %}
              </div>
            {% endif %}
          </div>

          {% if post.thumbnail %}
            <div>
              <img class="blog-item-thumb" src="{{ post.thumbnail | relative_url }}" alt="{{ post.title }}">
            </div>
          {% endif %}
        </div>
      </li>
    {% endfor %}

  </ul>

{% if page.pagination.enabled %}

<div class="blog-pagination">
{% include pagination.liquid %}
</div>
{% endif %}

</div>
