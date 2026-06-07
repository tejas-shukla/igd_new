"""
IGotDomain — Weekly Blog Agent
================================
Runs every Monday via GitHub Actions.
1. Picks a founder-relevant topic (researches trending angle via Claude + web search)
2. Writes a full SEO article in IGotDomain's exact HTML format
3. Generates a branded teal SVG cover
4. Commits article-[slug].html and updates blog.html
 
Required env vars:
  ANTHROPIC_API_KEY  — your Anthropic key (set as GitHub secret)
  GITHUB_TOKEN       — auto-provided by GitHub Actions
  REPO               — auto-provided by GitHub Actions (owner/repo)
  TOPIC_OVERRIDE     — optional manual topic from workflow_dispatch
"""
 
import os, json, re, base64, datetime, requests
import anthropic
from slugify import slugify
from blog_covers import generate_cover
 
# ── Config ──────────────────────────────────────────────────────────────────
REPO           = os.environ['REPO']                     # e.g. tejas-shukla/igd_new
TOKEN          = os.environ['GITHUB_TOKEN']
API_KEY        = os.environ['ANTHROPIC_API_KEY']
TOPIC_OVERRIDE = os.environ.get('TOPIC_OVERRIDE', '').strip()
BRANCH         = 'main'
PUBLIC_DIR     = 'public'
TOPICS_FILE    = 'scripts/published_topics.json'
 
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}
 
# ── Topic pool — rotates weekly, ensures all categories are covered ──────────
# Format: (seed query for research, category, motif key, gradient variant)
TOPIC_POOL = [
    ("best domain registrar for startups 2026",           "Domains",          "domain",    0),
    ("Shopify vs Webflow for SaaS founders",              "Website Builders",  "website",   1),
    ("best business bank account for UK startups",         "Banking",          "banking",   1),
    ("Xero vs Wave accounting software small business",    "Accounting",        "checklist", 2),
    ("Stripe vs Paddle for SaaS payments 2026",           "Payments",         "pricing",   0),
    ("AI tools every founder needs in 2026",              "AI Tools",         "ai",        2),
    ("how to validate startup idea before building",      "Startup Strategy", "validate",  2),
    ("best email marketing tools for early stage startup","Marketing",         "marketing", 2),
    (".com vs .io vs .ai domain for startup",             "Domains",          "pricing",   0),
    ("Framer vs Webflow for startup website 2026",        "Website Builders",  "website",   1),
    ("Mercury vs Revolut business banking founders",      "Banking",          "banking",   1),
    ("QuickBooks vs FreeAgent for UK founder",            "Accounting",        "checklist", 1),
    ("how to set up business email Google Workspace",     "Email",            "checklist", 0),
    ("CRM tools for early stage startup founders",        "CRM",              "growth",    0),
    ("PostHog vs Mixpanel analytics for SaaS",            "Marketing",         "marketing", 2),
    ("how to choose a domain name for your startup",      "Domains",          "domain",    0),
    ("Mailchimp vs Loops email for SaaS founders",        "Marketing",         "marketing", 2),
    ("best accounting software for freelancers UK",       "Accounting",        "checklist", 1),
    ("how to register a business UK online 2026",         "Startup Strategy", "growth",    0),
    ("best no-code website builders for founders 2026",   "Website Builders",  "website",   1),
]
 
AUTHOR      = "James Okafor"
AUTHOR_INIT = "J"
SITE_URL    = "https://igotdomain.com"
 
# ─────────────────────────────────────────────────────────────────────────────
def load_published():
    url = f"https://api.github.com/repos/{REPO}/contents/{TOPICS_FILE}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = json.loads(base64.b64decode(r.json()['content']).decode())
        return data.get('slugs', []), r.json()['sha']
    return [], None
 
def save_published(slugs, slug_sha, new_slug):
    slugs.append(new_slug)
    content = json.dumps({'slugs': slugs}, indent=2)
    url = f"https://api.github.com/repos/{REPO}/contents/{TOPICS_FILE}"
    body = {
        'message': f'Track published topic: {new_slug}',
        'content': base64.b64encode(content.encode()).decode(),
        'branch': BRANCH,
    }
    if slug_sha: body['sha'] = slug_sha
    requests.put(url, headers=HEADERS, json=body)
 
def pick_topic(published_slugs):
    if TOPIC_OVERRIDE:
        # Manual override from workflow_dispatch
        week = datetime.date.today().isocalendar()[1]
        _, cat, motif, var = TOPIC_POOL[week % len(TOPIC_POOL)]
        return TOPIC_OVERRIDE, cat, motif, var
    # Find the first un-published topic in rotation
    week = datetime.date.today().isocalendar()[1]
    for i in range(len(TOPIC_POOL)):
        candidate = TOPIC_POOL[(week + i) % len(TOPIC_POOL)]
        slug = slugify(candidate[0])[:60]
        if slug not in published_slugs:
            return candidate
    # All published — start repeating (add year to differentiate)
    candidate = TOPIC_POOL[week % len(TOPIC_POOL)]
    return (candidate[0] + f" {datetime.date.today().year}", *candidate[1:])
 
# ─────────────────────────────────────────────────────────────────────────────
def research_topic(client, query):
    """Use Claude + web search to find the current angle on the topic."""
    print(f"  Researching: {query}")
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search for current information about: '{query}'\n\n"
                "Return a JSON object with:\n"
                "- title: a compelling, SEO-optimised article title (include the year 2026 if relevant)\n"
                "- primary_keyword: the exact search phrase founders would type to find this\n"
                "- secondary_keywords: list of 4-6 related phrases\n"
                "- key_findings: 5-8 current facts, pricing points, or comparisons from search results\n"
                "- angle: what fresh perspective or unique value this article offers vs existing content\n"
                "- word_count_target: 900-1300 (realistic for this topic)\n\n"
                "Return ONLY the JSON, no markdown fences, no explanation."
            )
        }]
    )
    text = ''.join(b.text for b in resp.content if hasattr(b, 'text'))
    try:
        return json.loads(text)
    except:
        # Fallback if JSON extraction fails
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return json.loads(match.group()) if match else {
            'title': query.title(),
            'primary_keyword': query,
            'secondary_keywords': [],
            'key_findings': ['Information researched from current sources.'],
            'angle': 'Founder-focused practical guide.',
            'word_count_target': 1000,
        }
 
# ─────────────────────────────────────────────────────────────────────────────
ARTICLE_SYSTEM = """You are a senior content strategist for IGotDomain — a platform that helps 
founders compare and choose every tool they need to start a business (domains, website builders, 
business banking, accounting, payments, email, marketing, CRM).
 
BRAND VOICE: Practical, warm, founder-to-founder. Premium but not corporate. Direct. No buzzwords.
Write like a knowledgeable friend who has done the research so the founder doesn't have to.
 
SEO RULES:
- H1 = primary keyword (near-exact match)
- First paragraph must contain the primary keyword naturally
- Use secondary keywords once each in H2 headings or early paragraphs
- Never keyword-stuff. One keyword per sentence maximum.
- Each article must have 6-8 H2 sections with clear, searchable headings
- Include a TL;DR / quick-answer section near the top (Google featured snippet bait)
- Total length: match the word_count_target
 
INTERNAL LINKS (use these naturally, in context, as <a href="..."> tags):
- /assistant — the AI tool for comparisons ("compare in our AI assistant")
- /roadmap — the 10-stage startup roadmap
- /dashboard — the founder dashboard
- /assistant?decision=banking — for banking decisions (replace with relevant category)
- /assistant?decision=domain — for domain decisions
- /assistant?decision=website — for website builder decisions
- /assistant?decision=accounting — for accounting decisions
- /assistant?decision=payments — for payments decisions
- /assistant?decision=email — for email decisions
 
ARTICLE-CTA SECTIONS: Include 2-3 throughout the article using this exact HTML:
<div class="article-cta">
<h3>Relevant CTA heading</h3>
<p>One sentence explaining the value.</p>
<a href="/assistant?decision=CATEGORY" class="btn-primary">Compare OPTIONS free →</a>
</div>
 
OUTPUT: Return a single JSON object with:
- slug: URL-friendly filename slug (e.g. "stripe-vs-paddle-saas-2026")
- meta_title: SEO title tag (55-60 chars)
- meta_description: meta description (145-158 chars)
- tag: category tag (e.g. "Payments", "Domains", "Banking")
- h1: the article H1 (primary keyword)
- article_body_html: the full article body as HTML
  - Use <h2>, <p>, <ul>/<li>, <blockquote>, <strong> tags
  - Include the article-cta divs
  - DO NOT include <html>, <head>, <body>, <nav>, <footer>, <article> wrappers
  - Start from the first <p> and end at the last </div> of the last article-cta
- read_time_minutes: integer
 
Return ONLY the JSON, no markdown fences."""
 
def write_article(client, research, category):
    """Ask Claude to write the full article body."""
    print(f"  Writing article: {research['title']}")
    prompt = f"""Write a founder-focused SEO article for IGotDomain.
 
TOPIC RESEARCH:
{json.dumps(research, indent=2)}
 
CATEGORY: {category}
 
Follow all brand voice, SEO, and internal linking rules from your system prompt.
Produce the full article body HTML as specified.
Return ONLY the JSON object."""
 
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=ARTICLE_SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    text = ''.join(b.text for b in resp.content if hasattr(b, 'text'))
    # Strip markdown fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to extract JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise RuntimeError(f"Could not parse article JSON: {e}\n\nRaw:\n{text[:500]}")
 
# ─────────────────────────────────────────────────────────────────────────────
ARTICLE_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta_title} | IGotDomain</title>
<meta name="description" content="{meta_description}">
<link rel="canonical" href="{site_url}/{slug}">
<meta property="og:type" content="article">
<meta property="og:title" content="{meta_title}">
<meta property="og:description" content="{meta_description}">
<meta property="og:url" content="{site_url}/{slug}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{meta_title}">
<meta name="twitter:description" content="{meta_description}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{h1}","description":"{meta_description}","author":{{"@type":"Person","name":"{author}"}},"publisher":{{"@type":"Organization","name":"IGotDomain","url":"{site_url}"}},"datePublished":"{date_iso}","dateModified":"{date_iso}","mainEntityOfPage":{{"@type":"WebPage","@id":"{site_url}/{slug}"}}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<nav aria-label="Main navigation">
  <a href="/" class="nav-logo"><span class="logo-mark"><svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 1.5 14.5 8 8 14.5 1.5 8Z" fill="white"/></svg></span>IGot<span>Domain</span></a>
  <div class="nav-links">
    <a href="/how-it-works">How It Works</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/roadmap">Roadmap</a>
    <a href="/assistant">AI Assistant</a>
    <a href="/blog" class="active">Blog</a>
    <a href="/why-us">Why Us</a>
  </div>
  <a href="/assistant" class="nav-cta">Get Started Free →</a>
</nav>
 
<article class="article">
  <a class="article-back" href="/blog">← Back to all articles</a>
  <span class="article-tag">{tag}</span>
  <h1>{h1}</h1>
  <div class="article-byline">
    <div class="testi-avatar" style="font-size:15px;font-weight:700;color:var(--teal-dark);background:var(--teal-subtle);">{author_initial}</div>
    <div><div class="a-name">{author}</div><div class="a-meta">Published {date_long} · {read_time} min read</div></div>
  </div>
  <div class="article-hero-img" style="height:340px;overflow:hidden;border-radius:var(--radius);margin:24px 0 32px;">{cover_svg}</div>
 
  <div class="article-body">
{article_body}
  </div>
</article>
 
<section class="related">
  <div class="container">
    <div class="section-label" style="justify-content:flex-start">Keep Reading</div>
    <h2 class="section-title" style="font-size:28px;margin-bottom:28px">Related Articles</h2>
    <div class="blog-grid">
      <a class="blog-card" href="/article-i-have-a-domain-now-what">
        <div class="blog-thumb" style="overflow:hidden;height:180px;">{related_cover_1}</div>
        <div class="blog-content"><div class="blog-tag">Domain Setup</div><h3 class="blog-title">I Have a Domain Name, Now What?</h3><p class="blog-excerpt">The 8 essential steps every founder must take after registering a domain name.</p><div class="blog-meta"><span>9 min read</span></div></div>
      </a>
      <a class="blog-card" href="/article-launch-checklist">
        <div class="blog-thumb" style="overflow:hidden;height:180px;">{related_cover_2}</div>
        <div class="blog-content"><div class="blog-tag">Launch Guides</div><h3 class="blog-title">The Complete Founder's Launch Checklist</h3><p class="blog-excerpt">47 steps from idea to launch day — in the right order.</p><div class="blog-meta"><span>12 min read</span></div></div>
      </a>
    </div>
  </div>
</section>
 
<footer>
  <div class="footer-grid">
    <div class="footer-brand"><div class="nav-logo">IGot<span>Domain</span></div><div class="footer-desc">Helping founders launch better businesses through AI-guided, step-by-step processes. Free forever.</div></div>
    <div class="footer-col"><h4>Product</h4><a href="/how-it-works">How It Works</a><a href="/dashboard">Dashboard</a><a href="/assistant">AI Assistant</a></div>
    <div class="footer-col"><h4>Resources</h4><a href="/blog">Blog</a><a href="/why-us">FAQ</a></div>
    <div class="footer-col"><h4>Company</h4><a href="/why-us">About</a><a href="#">Privacy Policy</a><a href="#">Terms of Service</a></div>
  </div>
  <div class="footer-bottom"><div class="footer-copy">© {year} IGotDomain. All rights reserved.</div><div class="footer-legal"><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Cookies</a></div><div class="footer-social"><a href="#">𝕏</a><a href="#">in</a></div></div>
</footer>
 
<a href="/assistant" class="float-chat" aria-label="Open assistant">
  <span class="float-tooltip">Launch your business</span>
  <span class="float-btn"><svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
</a>
<div class="cookie-banner" id="cookieBanner"><div class="cookie-text">We use cookies to save your progress and improve your experience. <a href="#">Cookie Policy</a></div><div class="cookie-actions"><button class="cookie-btn cookie-accept" onclick="closeCookie()">Accept All</button><button class="cookie-btn cookie-reject" onclick="closeCookie()">Reject Non-Essential</button></div></div>
<script src="app.js"></script>
</body>
</html>'''
 
# ─────────────────────────────────────────────────────────────────────────────
def build_html(article, cover_svg, related1, related2):
    today = datetime.date.today()
    return ARTICLE_TEMPLATE.format(
        meta_title     = article['meta_title'][:60],
        meta_description = article['meta_description'][:158],
        site_url       = SITE_URL,
        slug           = article['slug'],
        h1             = article['h1'],
        tag            = article['tag'],
        author         = AUTHOR,
        author_initial = AUTHOR_INIT,
        date_iso       = today.isoformat(),
        date_long      = today.strftime('%B %Y'),
        read_time      = article.get('read_time_minutes', 8),
        cover_svg      = cover_svg,
        article_body   = article['article_body_html'],
        related_cover_1 = related1,
        related_cover_2 = related2,
        year           = today.year,
    )
 
# ─────────────────────────────────────────────────────────────────────────────
def get_file(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return base64.b64decode(data['content']).decode(), data['sha']
    return None, None
 
def commit_file(path, content, message, sha=None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    body = {
        'message': message,
        'content': base64.b64encode(content.encode()).decode(),
        'branch': BRANCH,
    }
    if sha: body['sha'] = sha
    r = requests.put(url, headers=HEADERS, json=body)
    r.raise_for_status()
    print(f"  ✓ Committed: {path}")
 
def update_blog_html(slug, title, tag, excerpt, cover_svg, sha):
    """Prepend the new article card to the blog grid."""
    blog_html, blog_sha = get_file(f'{PUBLIC_DIR}/blog.html')
    if not blog_html:
        print("  ⚠ Could not fetch blog.html — skipping update")
        return
 
    new_card = (
        f'\n      <a class="blog-card reveal" data-cat="{tag}" href="/{slug}">'
        f'<div class="blog-thumb" style="overflow:hidden;height:180px;">{cover_svg}</div>'
        f'<div class="blog-content"><div class="blog-tag">{tag}</div>'
        f'<h3 class="blog-title">{title}</h3>'
        f'<p class="blog-excerpt">{excerpt}</p>'
        f'<div class="blog-meta"><span>8 min read</span><span>·</span>'
        f'<span>{datetime.date.today().strftime("%b %Y")}</span></div>'
        f'</div></a>'
    )
 
    # Insert after the opening of the blog grid div
    updated = re.sub(
        r'(<div class="blog-grid"[^>]*id="blogGrid"[^>]*>)',
        r'\1' + new_card,
        blog_html,
        count=1
    )
    if updated == blog_html:
        # Fallback: find any blog-grid opening
        updated = re.sub(
            r'(<div class="blog-grid"[^>]*>)\s*\n',
            r'\1' + new_card + '\n',
            blog_html, count=1
        )
 
    commit_file(f'{PUBLIC_DIR}/blog.html', updated,
                f'Add blog card: {title}', blog_sha)
 
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("═" * 60)
    print("IGotDomain Weekly Blog Agent")
    print(f"Date: {datetime.date.today()}")
    print("═" * 60)
 
    client = anthropic.Anthropic(api_key=API_KEY)
 
    # 1. Load published topics
    published, topics_sha = load_published()
    print(f"✓ Loaded {len(published)} published topics")
 
    # 2. Pick this week's topic
    query, category, motif_key, motif_var = pick_topic(published)
    slug_base = slugify(query)[:60]
    print(f"✓ Topic: {query}")
    print(f"  Category: {category} | Motif: {motif_key}")
 
    # 3. Research the topic
    research = research_topic(client, query)
    print(f"✓ Research complete: {research.get('title', '?')}")
 
    # 4. Write the article
    article = write_article(client, research, category)
    slug = article.get('slug', slug_base)
    print(f"✓ Article written: {article.get('h1', '?')}")
    print(f"  Slug: {slug}")
 
    # 5. Generate cover SVGs
    cover_svg  = generate_cover(motif_key, motif_var)
    related_1  = generate_cover('domain', 0)
    related_2  = generate_cover('checklist', 1)
    print("✓ Cover art generated")
 
    # 6. Build the full HTML
    html = build_html(article, cover_svg, related_1, related_2)
    print(f"✓ HTML built ({len(html):,} chars)")
 
    # 7. Commit article file
    filepath = f'{PUBLIC_DIR}/article-{slug}.html'
    _, existing_sha = get_file(filepath)
    commit_file(filepath, html,
                f'Blog: {article.get("h1", slug)}', existing_sha)
 
    # 8. Update blog.html
    excerpt = article.get('meta_description', '')[:140]
    update_blog_html(f'article-{slug}', article.get('h1', slug),
                     article.get('tag', category), excerpt, cover_svg, topics_sha)
 
    # 9. Mark as published
    save_published(published, topics_sha, slug)
 
    # 10. Write title for git commit message
    with open('/tmp/article_title.txt', 'w') as f:
        f.write(article.get('h1', slug))
 
    print("═" * 60)
    print(f"✅ Done! Article live at: {SITE_URL}/article-{slug}")
    print("   Vercel will auto-deploy within 60 seconds.")
    print("═" * 60)
 
if __name__ == '__main__':
    main()
