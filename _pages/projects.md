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
    --projects-text: #10141a;
    --projects-muted: #3a414c;
    --projects-soft: #5c6678;
    --projects-line: rgba(17, 19, 23, 0.08);
    --projects-accent: #3d6c8c;
    --projects-accent-soft: rgba(61, 108, 140, 0.08);
    --projects-surface: #ffffff;
    padding-top: 1.5rem;
  }

  .projects-hero {
    margin-bottom: 2.5rem;
  }

  .projects-eyebrow {
    margin-bottom: 0.85rem;
    color: var(--projects-accent);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }

  .projects-title {
    margin: 0;
    font-size: clamp(2.6rem, 5vw, 4rem);
    line-height: 1.05;
    letter-spacing: -0.035em;
    font-weight: 620;
    color: var(--projects-text);
  }

  .projects-subtitle {
    margin-top: 0.85rem;
    max-width: 38rem;
    color: var(--projects-muted);
    font-size: 1.05rem;
    line-height: 1.9;
  }

  .projects-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.1rem;
  }

  .project-card {
    display: grid;
    gap: 0.9rem;
    padding: 1.15rem;
    border: 1px solid var(--projects-line);
    border-radius: 1rem;
    background: var(--projects-surface);
    box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    text-decoration: none !important;
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease,
      border-color 0.2s ease;
  }

  .project-card:hover {
    transform: translateY(-2px);
    border-color: rgba(61, 108, 140, 0.18);
    box-shadow: 0 6px 24px rgba(16, 24, 40, 0.08);
  }

  .project-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
  }

  .project-card-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }

  .project-badge,
  .project-link-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    min-height: 1.8rem;
    padding: 0 0.68rem;
    border: 1px solid var(--projects-line);
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
  }

  .project-badge {
    background: var(--projects-accent-soft);
    color: var(--projects-accent);
    border-color: rgba(61, 108, 140, 0.14);
  }

  .project-link-pill {
    background: var(--projects-surface);
    color: var(--projects-soft);
  }

  .project-card-thumb-wrap {
    padding: 0.65rem;
    border: 1px solid var(--projects-line);
    border-radius: 0.85rem;
    background: var(--projects-accent-soft);
  }

  .project-card-thumb {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: contain;
    padding: 0.3rem;
    border: 1px solid var(--projects-line);
    border-radius: 0.7rem;
    background: var(--projects-surface);
  }

  .project-card-copy {
    display: grid;
    gap: 0.5rem;
  }

  .project-card-title {
    margin: 0;
    color: var(--projects-text);
    font-size: 1.22rem;
    font-weight: 620;
    line-height: 1.34;
  }

  .project-card-desc {
    margin: 0;
    color: var(--projects-muted);
    line-height: 1.78;
    font-size: 0.96rem;
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
