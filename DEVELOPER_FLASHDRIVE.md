# Developer Flashdrive — Handover & Remote Collaboration Protocol

Purpose
-------
This document is the authoritative "flashdrive" for any external developer who cannot directly access this repository. It defines the exact protocol they must follow when requesting files, proposing changes, and delivering patches through the repo owner (you). Follow these rules to avoid assumptions, accidental code/style changes, or surprises.

Core Principles
---------------
- Always confirm which exact files and line ranges are required before making any edits.
- The external dev MUST present a short, testable "Change Plan" before producing code.
- The owner (you) will run the requested CLI commands and share the outputs or a tarball of files. Only after you confirm the plan will the dev provide a patch.
- All delivered changes must be production-ready: tests, migration plan, logging, and rollback steps included.

Protocol (step-by-step)
-----------------------
1. Request files

   - The remote dev lists the exact relative paths they need and the exact line ranges (if only part of a file is needed). Example:

     - `utilities/management/commands/seed_test_data.py:1-200`
     - `payments/utils.py` (full file)

2. Owner collects and shares files

   - The owner runs the requested commands and pastes results or uploads a `flashdrive.tar.gz` containing only the requested files.

   - Recommended commands (copy/paste):

     Show repo state and head:

     ```bash
     pwd
     git rev-parse --abbrev-ref HEAD
     git status --porcelain
     git log -n 5 --pretty=oneline
     ```

     Show committed file at HEAD (first N lines):

     ```bash
     git show HEAD:utilities/management/commands/seed_test_data.py | sed -n '1,200p'
     ```

     Show working copy file with numbered lines (if uncommitted changes exist):

     ```bash
     nl -ba utilities/management/commands/seed_test_data.py | sed -n '1,200p'
     ```

     Create a tarball containing only requested files (preferred):

     ```bash
     # if files are committed
     git archive --format=tar HEAD utilities/management/commands/seed_test_data.py payments/utils.py | gzip > flashdrive.tar.gz

     # fallback (includes uncommitted changes)
     tar -czf flashdrive.tar.gz utilities/management/commands/seed_test_data.py payments/utils.py
     ```

     Produce a patch for local, uncommitted changes:

     ```bash
     git diff -- path/to/file > mychange.patch
     ```

3. Remote dev confirms scope and writes a Change Plan

   - Change Plan template (must be filled by dev):

     - Files / line ranges:
     - Short summary of change:
     - Why change is needed (bug/security/regression/refactor):
     - Acceptance criteria (what tests / manual checks must pass):
     - Steps to implement (high level):
     - Commands owner must run to verify locally:
     - Rollback plan if something goes wrong:

4. Dev supplies a patch and verification commands

   - The patch MUST be a unified diff (`git diff` output) or a single-file patch.
   - Include exact commands to run on the owner side to verify and apply the patch:

     ```bash
     git checkout -b fix/your-short-desc
     git apply --stat mychange.patch    # inspect
     git apply --check mychange.patch   # dry-run
     git apply mychange.patch           # apply
     # run tests or commands provided by the dev
     python -m pip install -r requirements.txt --user
     python manage.py migrate --noinput
     python manage.py test payments
     ```

5. Owner verifies, pushes branch, and opens PR

   - If everything passes locally, push branch and open PR (or the dev can supply a PR patch if preferred). Example push commands:

     ```bash
     git add -A
     git commit -m "fix: brief summary"  # if commits were made locally
     git push origin HEAD:refs/heads/fix/your-short-desc
     ```

Production-Ready Checklist (must accompany every change)
------------------------------------------------------
- Tests: unit and critical integration tests that exercise the change must be included or documented.
- Database: migrations added if models change; include a data migration plan if needed.
- Secrets: ensure no secrets are committed. Use environment variables and `.env.example` only.
- Idempotency: webhooks (MPesa, payments) must be idempotent and atomic.
- Logging & monitoring: errors must be logged; webhook handlers must surface internal processing errors.
- Rollback: a clear rollback plan on how to revert a PR or database migration.
- Code style and linting: follow repo conventions.

Example developer->owner exchange (concise)
-----------------------------------------

Dev asks:

 - "Please provide lines 1-200 of `utilities/management/commands/seed_test_data.py` and the full `payments/utils.py`. Also run `python manage.py seed_test_data` and paste the final console output (or attach `flashdrive.tar.gz`)."

Owner runs the `git archive` or `nl` commands above and replies with the outputs or tarball.

Dev replies with a Change Plan and a single patch plus the `python manage.py test payments` command to verify.

Quick rules for low-token / AI handoffs
--------------------------------------
- If tokens are low, provide the smallest reproducible context: file path, line numbers, failing test name, and the minimal failing output.
- For larger edits, attach `flashdrive.tar.gz` with only requested files; do not paste the entire repo.

How to create a minimal repo flashdrive (owner)
----------------------------------------------

1) If the files are committed:

```bash
git archive --format=tar HEAD path/to/file1 path/to/file2 | gzip > flashdrive.tar.gz
sha256sum flashdrive.tar.gz
# Upload flashdrive.tar.gz to your preferred sharing location (or paste sha256+base64 for small archives)
```

2) If you need to include uncommitted files:

```bash
tar -czf flashdrive.tar.gz path/to/file1 path/to/file2
sha256sum flashdrive.tar.gz
```

Final notes
-----------
- This repository already follows these best-practices where possible. Use this document as the single source-of-truth for remote contributions.
- File location: `DEVELOPER_FLASHDRIVE.md` (this file). Keep it updated as processes evolve.

If you want, I can now:

- run a quick repo sweep (phones, localhost URLs, example secrets) and report remaining hardcoded items, or
- continue by sweeping `static/` and `scripts/` and create patches to remove remaining hardcoding.

Pick one and I will proceed.

Hosting vendor assets locally
----------------------------

This repo now prefers local vendor assets with CDN fallbacks. To host the assets locally and ensure no runtime requests to third-party CDNs, follow these steps:

1. Download vendor files into the repository

```bash
# lucide icons (UMD)
mkdir -p static/vendor static/fonts
curl -L -o static/vendor/lucide.min.js \
  "https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"

# download DM Sans woff2 files from Google Fonts and place them in static/fonts/
# then update static/css/fonts.css by uncommenting the @font-face rules and adjusting paths if needed
```

2. Verify locally

```bash
python manage.py collectstatic --noinput
python manage.py runserver
# open http://127.0.0.1:8000 and confirm icons and fonts load without hitting external CDNs
```

3. Commit and push (example)

```bash
git checkout -b host-vendor-assets
git add templates/base.html static/css/fonts.css static/vendor/README.md DEVELOPER_FLASHDRIVE.md .gitignore
git commit -m "chore: prefer local vendor assets with CDN fallbacks; add local fonts loader and vendor README"
git push origin host-vendor-assets
```

If you accidentally committed a local `.env`, remove it from history and stop tracking it:

```bash
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: remove .env from repo and ignore local env"
git push origin host-vendor-assets
```

Notes
-----
- The app will attempt to use the local `static/vendor/lucide.min.js` and `static/fonts/*` first. If the fonts are not loaded, the page will fall back to Google Fonts automatically.
- Add the actual font files (woff2) and the `lucide.min.js` file before creating your final production commit so the site does not depend on the CDN.

