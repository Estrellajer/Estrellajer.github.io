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
