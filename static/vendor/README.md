Hosting vendor assets locally
----------------------------

This folder is intended to contain third-party assets that we prefer to serve from our own server instead of a CDN.

Recommended files:

- `static/vendor/lucide.min.js` — lucide icons UMD build
- `static/fonts/*` — DM Sans woff2 files

How to install (example commands):

1) Download lucide:

```bash
mkdir -p static/vendor
curl -L -o static/vendor/lucide.min.js \
  "https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"
```

2) Download DM Sans fonts

 - Visit https://fonts.google.com/specimen/DM+Sans and download the family, or use a helper tool to fetch woff2 files.
 - Place the woff2 files into `static/fonts/` and update `static/css/fonts.css` by uncommenting the `@font-face` rules.

3) Verify locally

```bash
# collect static for local testing (if using Django staticfiles)
python manage.py collectstatic --noinput

# start dev server
python manage.py runserver

# visit the app and confirm icons and fonts load without referencing external CDNs
```

Licensing

Ensure you comply with the licenses of any third-party assets you vendor. Google fonts are typically open; lucide is MIT-licensed.
