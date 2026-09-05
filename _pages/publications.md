---
layout: default
permalink: /publications/
title: publications
nav: true
nav_order: 2
---

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
