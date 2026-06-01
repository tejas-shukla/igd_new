# Igotdomain

A premium, mobile-first marketing site + guided AI launch assistant for founders.
Static multi-page site (HTML/CSS/JS) — no build step required.

## What's inside

```
.
├── public/                       ← everything served to visitors
│   ├── index.html                ← homepage (animated dashboard, chat teaser, how-it-works)
│   ├── how-it-works.html         ← 5-step process, launch score, roadmap
│   ├── dashboard.html            ← animated business launch dashboard
│   ├── assistant.html            ← interactive AI assistant (the core experience)
│   ├── blog.html                 ← blog listing with category filtering
│   ├── why-us.html               ← trust / free-forever / FAQ (FAQ schema)
│   ├── article-launch-checklist.html
│   ├── article-domain-name.html
│   ├── article-ai-faster.html
│   ├── styles.css                ← shared design system
│   ├── app.js                    ← shared JS (Soft Aurora hero, modal, cookie, reveals)
│   ├── sitemap.xml
│   └── robots.txt
├── vercel.json                   ← clean URLs, security headers, caching
├── package.json
└── .gitignore
```

The AI assistant (`/assistant`) takes a business idea or a domain, suggests available
names, then compares **domain prices**, **website builders**, **business accounts**, and
**accounting software** (sample data for now).

## Deploy to Vercel

### Option A — Vercel CLI (fastest)
```bash
npm i -g vercel      # if you don't have it
cd igotdomain        # this folder
vercel               # follow prompts → preview URL
vercel --prod        # promote to production
```
When asked for settings, accept the defaults:
- Framework Preset: **Other**
- Build Command: *(leave empty)*
- Output Directory: **public**

### Option B — Git + Vercel dashboard
1. Push this folder to a new GitHub/GitLab/Bitbucket repo.
2. In Vercel, **Add New → Project** and import the repo.
3. Settings:
   - Framework Preset: **Other**
   - Build Command: *(empty)*
   - Output Directory: **public**
4. **Deploy.**

### Option C — Drag & drop
Go to vercel.com → new project → drag the **`public`** folder in.

## Local preview
```bash
npx serve public
# then open the printed http://localhost:3000
```
(Or any static server — e.g. `python3 -m http.server` from inside `public/`.)

## Custom domain
In Vercel → Project → **Settings → Domains**, add `igotdomain.com` and follow the DNS steps.
After connecting, update the absolute URLs (canonical tags, `sitemap.xml`, `robots.txt`,
Open Graph URLs) if your final domain differs.

## Notes
- Clean URLs are enabled (`/assistant`, not `/assistant.html`).
- Comparison figures in the assistant are **sample data** — wire them to live provider
  data/APIs for production.
- For a production app with real email-progress persistence and live domain lookups,
  migrate to the Next.js + TypeScript stack from the original brief; this static build is
  a high-fidelity, deployable front end.
