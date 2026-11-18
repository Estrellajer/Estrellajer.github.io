# Estrellajer.github.io

Personal homepage of Maoqi Liu (刘茂琦): <https://estrellajer.github.io>

Built with Jekyll on the [al-folio](https://github.com/alshedivat/al-folio) theme (heavily customized), deployed to GitHub Pages by `.github/workflows/deploy.yml`.

## Local preview

```bash
docker compose up   # http://localhost:8080
```

## Layout

| Path | What |
|---|---|
| `_pages/about.md` | Homepage content (hero, awards, experience) |
| `_news/` | News items on the homepage |
| `_posts/` | Blog posts (`math: true` in front matter enables MathJax) |
| `_bibliography/papers.bib` | Publications |
| `_scholar/` | Personal scholar-activity monitor (see `_scholar/README.md`) |
| `scholar/index.html` | Private `/scholar/` page (noindex), renders data from the `data` branch |
