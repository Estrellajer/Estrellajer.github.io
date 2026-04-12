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
    gap: 0.95rem;
    padding: 1.2rem;
    border: 1px solid rgba(85, 122, 159, 0.14);
    border-radius: 1.15rem;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(243, 247, 252, 0.98)),
      var(--global-card-bg-color);
    box-shadow: 0 14px 34px rgba(16, 24, 40, 0.06);
    text-decoration: none !important;
    transition:
      transform 0.18s ease,
      box-shadow 0.18s ease,
      border-color 0.18s ease;
  }

  .project-card:hover {
    transform: translateY(-3px);
    border-color: rgba(85, 122, 159, 0.24);
    box-shadow: 0 22px 40px rgba(16, 24, 40, 0.1);
  }

  .project-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
  }

  .project-card-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    align-items: center;
  }

  .project-badge,
  .project-link-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    min-height: 1.9rem;
    padding: 0 0.74rem;
    border: 1px solid rgba(85, 122, 159, 0.14);
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .project-badge {
    background: linear-gradient(180deg, rgba(85, 122, 159, 0.12), rgba(85, 122, 159, 0.08));
    color: #3b5c7e;
  }

  .project-link-pill {
    background: rgba(17, 19, 23, 0.04);
    color: var(--projects-soft);
  }

  .project-card-thumb-wrap {
    padding: 0.72rem;
    border: 1px solid rgba(85, 122, 159, 0.12);
    border-radius: 1rem;
    background:
      radial-gradient(circle at top left, rgba(85, 122, 159, 0.08), transparent 44%),
      linear-gradient(180deg, #fafcff 0%, #eef3f8 100%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.78);
  }

  .project-card-thumb {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: contain;
    padding: 0.35rem;
    border: 1px solid rgba(85, 122, 159, 0.08);
    border-radius: 0.88rem;
    background: rgba(255, 255, 255, 0.86);
  }

  .project-card-copy {
    display: grid;
    gap: 0.55rem;
  }

  .project-card-title {
    margin: 0;
    color: var(--projects-text);
    font-size: 1.3rem;
    font-weight: 600;
    line-height: 1.34;
  }

  .project-card-desc {
    margin: 0;
    color: #5f6977;
    line-height: 1.78;
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
