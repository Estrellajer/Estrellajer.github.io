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
      Papers and preprints, newest first, with links to arXiv and code.
    </div>
    <div class="publications-search">
      {% include bib_search.liquid %}
    </div>
  </section>

  <div class="publications">
    {% bibliography %}
  </div>
</div>
