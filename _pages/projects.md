---
layout: default
title: projects
permalink: /projects/
nav: true
nav_order: 3
description: A small selection of research systems and side projects.
---

<div class="projects-landing">
  <section class="projects-hero">
    <div class="projects-eyebrow">Projects</div>
    <h1 class="projects-title">Research systems and focused side work.</h1>
    <div class="projects-subtitle">
      A small set of representative projects, shown with the same quieter visual language as the homepage and publications.
    </div>
  </section>

  <div class="projects-grid">
    {% assign sorted_projects = site.projects | sort: "importance" %}
    {% for project in sorted_projects %}
      <a class="project-card" href="{{ project.url | relative_url }}">
        <div class="project-card-head">
          <div class="project-card-badges">
            {% if project.category %}
              <span class="project-badge">{{ project.category }}</span>
            {% endif %}
          </div>
          {% if project.github %}
            <span class="project-link-pill">
              <i class="fa-brands fa-github"></i>
              <span>GitHub</span>
            </span>
          {% endif %}
        </div>
        {% if project.img %}
          <div class="project-card-thumb-wrap">
            <img class="project-card-thumb" src="{{ project.img | relative_url }}" alt="{{ project.title }}">
          </div>
        {% endif %}
        <div class="project-card-copy">
          <h2 class="project-card-title">{{ project.title }}</h2>
          <p class="project-card-desc">{{ project.description }}</p>
        </div>
      </a>
    {% endfor %}
  </div>
</div>
