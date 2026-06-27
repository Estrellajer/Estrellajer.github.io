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
    --blog-text: #10141a;
    --blog-muted: #3a414c;
    --blog-soft: #5c6678;
    --blog-line: rgba(17, 19, 23, 0.08);
    --blog-accent: #3d6c8c;
    --blog-accent-strong: #2f5470;
    --blog-accent-soft: rgba(61, 108, 140, 0.08);
    padding-top: 1.5rem;
  }

  .blog-hero {
    margin-bottom: 2.5rem;
  }

  .blog-eyebrow {
    margin-bottom: 0.85rem;
    color: var(--blog-accent);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }

  .blog-title {
    margin: 0;
    font-size: clamp(2.6rem, 5vw, 4rem);
    line-height: 1.05;
    letter-spacing: -0.035em;
    font-weight: 620;
    color: var(--blog-text);
  }

  .blog-subtitle {
    margin-top: 0.85rem;
    max-width: 38rem;
    color: var(--blog-muted);
    font-size: 1.05rem;
    line-height: 1.9;
  }

  .blog-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    align-items: center;
    margin-top: 1.5rem;
  }

  .blog-filter-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    align-items: center;
  }

  .blog-filter {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    min-height: 2.2rem;
    padding: 0 0.42rem 0 0.9rem;
    border-radius: 999px;
    background: var(--blog-accent-soft);
    color: var(--blog-accent-strong);
    font-size: 0.92rem;
    text-decoration: none !important;
  }

  .blog-filter-count {
    display: inline-grid;
    place-items: center;
    min-width: 1.45rem;
    height: 1.45rem;
    padding: 0 0.42rem;
    border-radius: 999px;
    background: var(--global-bg-color);
    color: var(--blog-muted);
    font-size: 0.78rem;
    font-weight: 600;
    line-height: 1;
  }

  .blog-filter:hover {
    color: var(--blog-accent);
    text-decoration: none !important;
  }

  .blog-list {
    display: grid;
    gap: 0;
    padding: 0;
    margin: 0;
    list-style: none;
  }

  .blog-item {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--blog-line);
    transition: background 0.2s ease;
  }

  .blog-item:first-child {
    padding-top: 0.2rem;
  }

  .blog-item:hover {
    background: var(--blog-accent-soft);
    margin: 0 -0.85rem;
    padding-left: 0.85rem;
    padding-right: 0.85rem;
    border-radius: 0.85rem;
    border-bottom-color: transparent;
  }

  .blog-item:first-child:hover {
    padding-top: 0.2rem;
  }

  .blog-item-grid {
    display: grid;
    gap: 1.2rem;
    align-items: start;
  }

  .blog-item-grid--with-thumb {
    grid-template-columns: minmax(0, 1fr) 200px;
  }

  .blog-item-date {
    color: var(--blog-soft);
    font-size: 0.78rem;
    font-weight: 520;
    letter-spacing: 0.05em;
    font-variant-numeric: tabular-nums;
  }

  .blog-item-title {
    display: inline-block;
    margin: 0.35rem 0 0.55rem;
    font-size: 1.38rem;
    line-height: 1.35;
    font-weight: 620;
    letter-spacing: -0.02em;
    color: var(--blog-text);
    text-decoration: none;
  }

  .blog-item-title:hover {
    color: var(--blog-accent);
    text-decoration: none;
  }

  .blog-item-desc {
    margin: 0 0 0.55rem;
    color: var(--blog-muted);
    line-height: 1.85;
    font-size: 0.98rem;
    max-width: 48rem;
  }

  .blog-item-meta {
    display: inline;
    color: var(--blog-soft);
    font-size: 0.94rem;
    line-height: 1.8;
  }

  .blog-item-taxonomy {
    display: inline;
    color: var(--blog-soft);
    font-size: 0.94rem;
    line-height: 1.8;
  }

  .blog-item-taxonomy::before {
    content: " . ";
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
    border-radius: 0.85rem;
    border: 1px solid var(--blog-line);
    background: var(--global-card-bg-color);
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
    color: var(--blog-accent-strong);
  }

  @media (max-width: 800px) {
    .blog-item-grid,
    .blog-item-grid--with-thumb {
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
    <h1 class="blog-title">{{ site.blog_name }}</h1>
    <div class="blog-subtitle">
      科研札记、工程实践与一些生活复盘。
    </div>

    <div class="blog-filters">
      <div class="blog-filter-group">
        {% assign preferred_categories = "Research,Engineering,Learning,Life" | split: "," %}
        {% assign shown_categories = "" %}
        {% for preferred_category in preferred_categories %}
          {% for category in site.categories %}
            {% if category[0] == preferred_category %}
              {% assign visible_category_posts = category[1] | where_exp: "post", "post.hidden != true" %}
              {% if visible_category_posts.size > 0 %}
                <a class="blog-filter" href="{{ category[0] | slugify | prepend: '/blog/category/' | relative_url }}">
                  <span>{{ category[0] }}</span>
                  <span class="blog-filter-count" aria-label="{{ visible_category_posts.size }} posts">{{ visible_category_posts.size }}</span>
                </a>
                {% assign shown_categories = shown_categories | append: "|" | append: category[0] | append: "|" %}
              {% endif %}
            {% endif %}
          {% endfor %}
        {% endfor %}
        {% for category in site.categories %}
          {% assign category_key = category[0] | prepend: "|" | append: "|" %}
          {% unless shown_categories contains category_key %}
            {% assign visible_category_posts = category[1] | where_exp: "post", "post.hidden != true" %}
            {% if visible_category_posts.size > 0 %}
              <a class="blog-filter" href="{{ category[0] | slugify | prepend: '/blog/category/' | relative_url }}">
                <span>{{ category[0] }}</span>
                <span class="blog-filter-count" aria-label="{{ visible_category_posts.size }} posts">{{ visible_category_posts.size }}</span>
              </a>
            {% endif %}
          {% endunless %}
        {% endfor %}
      </div>
    </div>

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
        <div class="blog-item-grid{% if post.thumbnail %} blog-item-grid--with-thumb{% endif %}">
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
            {% if categories != "" %}
              <div class="blog-item-taxonomy">
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
