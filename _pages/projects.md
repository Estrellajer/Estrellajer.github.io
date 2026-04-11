---
layout: default
title: projects
permalink: /projects/
nav: true
nav_order: 3
description: A small selection of research systems and side projects.
---

<style>
  .projects-landing {
    --projects-text: var(--global-text-color);
    --projects-muted: #69717d;
    --projects-soft: #8d96a3;
    --projects-line: rgba(17, 19, 23, 0.1);
    --projects-accent: #557a9f;
    --projects-accent-soft: rgba(85, 122, 159, 0.12);
    padding-top: 1rem;
  }

  .projects-hero {
    margin-bottom: 2.2rem;
  }

  .projects-eyebrow {
    margin-bottom: 0.9rem;
    color: var(--projects-accent);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
  }

  .projects-title {
    margin: 0;
    font-size: clamp(2.6rem, 5vw, 4.2rem);
    line-height: 0.98;
    letter-spacing: -0.04em;
    font-weight: 600;
  }

  .projects-subtitle {
    margin-top: 0.9rem;
    max-width: 44rem;
    color: var(--projects-muted);
    font-size: 1.05rem;
    line-height: 1.85;
  }

  .projects-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.35rem;
  }

  .project-card {
    display: grid;
    gap: 1rem;
    padding: 1.15rem;
    border: 1px solid rgba(17, 19, 23, 0.08);
    border-radius: 1.05rem;
    background: rgba(255, 255, 255, 0.76);
    text-decoration: none !important;
  }

  .project-card-thumb {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: contain;
    padding: 0.45rem;
    border: 1px solid rgba(17, 19, 23, 0.08);
    border-radius: 0.9rem;
    background: #f7f8fa;
  }

  .project-card-title {
    margin: 0;
    color: var(--projects-text);
    font-size: 1.24rem;
    font-weight: 600;
    line-height: 1.38;
  }

  .project-card-desc {
    margin: 0.48rem 0 0;
    color: var(--projects-muted);
    line-height: 1.8;
  }

  .project-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
  }

  .project-pill {
    display: inline-flex;
    align-items: center;
    min-height: 2rem;
    padding: 0 0.8rem;
    border-radius: 999px;
    background: rgba(17, 19, 23, 0.05);
    color: var(--projects-soft);
    font-size: 0.84rem;
    letter-spacing: 0.03em;
  }

  @media (max-width: 800px) {
    .projects-grid {
      grid-template-columns: 1fr;
    }
  }
</style>

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
        {% if project.img %}
          <img class="project-card-thumb" src="{{ project.img | relative_url }}" alt="{{ project.title }}">
        {% endif %}
        <div>
          <h2 class="project-card-title">{{ project.title }}</h2>
          <p class="project-card-desc">{{ project.description }}</p>
        </div>
        <div class="project-card-meta">
          {% if project.category %}
            <span class="project-pill">{{ project.category }}</span>
          {% endif %}
          {% if project.github %}
            <span class="project-pill">GitHub</span>
          {% endif %}
        </div>
      </a>
    {% endfor %}
  </div>
</div>
