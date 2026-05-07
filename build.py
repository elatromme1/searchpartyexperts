#!/usr/bin/env python3
"""Build script: reads _data/guests/*.yml and generates static HTML pages."""
import os, yaml, html as html_module, json
from pathlib import Path

SITE_URL = "https://searchpartyexperts.netlify.app"
TAGLINE = "Primary-source knowledge of Entrepreneurship-Through-Acquisition for value creation"
PODCAST_NAME = "Search Party"
PODCAST_URL = "https://searchpartychannel.substack.com"
LOGO_FILE = "search-party-logo.png"

LOGO_HTML_GUEST = f"""    <div class="site-logo-wrap">
      <a href="{PODCAST_URL}/" target="_blank" rel="noopener">
        <img src="../images/{LOGO_FILE}" alt="{PODCAST_NAME}" class="site-logo" />
      </a>
    </div>"""

SEARCH_JS = """
<script>
  const searchInput = document.getElementById('guest-search');
  const cards = Array.from(document.querySelectorAll('.guest-card'));
  const noResults = document.getElementById('no-results');

  searchInput.addEventListener('input', function() {
    const q = this.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(function(card) {
      const text = card.getAttribute('data-search');
      const match = !q || text.includes(q);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    noResults.style.display = visible === 0 ? 'block' : 'none';
  });

  searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      this.value = '';
      this.dispatchEvent(new Event('input'));
    }
  });
</script>
"""

def esc(s):
    return html_module.escape(str(s or ''), quote=True)

def capitalize_first(s):
    s = s.strip()
    if not s:
        return s
    words = s.split(' ')
    words[0] = words[0].capitalize()
    return ' '.join(words)

ABOUT_SECTION = f"""<div class="about-section">
  <h2>Welcome to {PODCAST_NAME}!</h2>
  <h3>About {PODCAST_NAME}</h3>
  <p>Search Party is a video-podcast dedicated to elevating knowledge of the Entrepreneurship-Through-Acquisition (ETA) model for value creation. The podcast features curated interviews and panel discussions with ETA searchers, CEOs, exited CEOs and investors — covering everything from the search and acquisition process to operations, financing, and exits.</p>
  <p>Search Party is hosted by financial journalist David Snow, a long-time chronicler of the alternative investment market.</p>
  <div class="substack-embed-wrap">
    <iframe src="{PODCAST_URL}/embed" width="480" height="320" style="border:1px solid #EEE; background:white;" frameborder="0" scrolling="no"></iframe>
  </div>
</div>"""

def get_photo_src(gid, g, for_index=False):
    headshot = g.get('headshot', '')
    if headshot:
        filename = headshot.split('/')[-1]
        if for_index:
            return f'images/{filename}'
        else:
            return f'../images/{filename}'
    if for_index:
        return f'images/{gid}.jpg'
    else:
        return f'../images/{gid}.jpg'

def json_str(s):
    return json.dumps(s)

def build_guest_page(gid, g):
    name = g.get('name', '')
    title = g.get('title', '')
    firm = g.get('firm', '')
    bio = g.get('bio', '')
    topics = [capitalize_first(t) for t in g.get('topics', [])]
    ep_title = g.get('episodeTitle', '')
    ep_url = g.get('episodeUrl', '')

    bio_short = esc(bio[:160]) + '\u2026' if len(bio) > 160 else esc(bio)
    topics_li = '\n'.join(f'          <li>{esc(t)}</li>' for t in topics)
    bio_html = f'<p class="guest-bio">{esc(bio)}</p>' if bio else ''

    job_title = title.split(',')[0].split('&')[0].strip()
    photo_src = get_photo_src(gid, g, for_index=False)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(name)} | {PODCAST_NAME} Video-Podcast</title>
  <meta name="description" content="{bio_short}">
  <meta property="og:title" content="{esc(name)} | {PODCAST_NAME}">
  <meta property="og:description" content="{bio_short}">
  <meta property="og:image" content="{photo_src}">
  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "{name}",
  "jobTitle": "{job_title}",
  "worksFor": {{
    "@type": "Organization",
    "name": "{firm}"
  }},
  "description": {json_str(bio)},
  "url": "{SITE_URL}/guests/{gid}.html",
  "appearanceOn": {{
    "@type": "PodcastEpisode",
    "name": "{ep_title}",
    "url": "{ep_url}"
  }}
}}
  </script>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <div class="site-wrapper">

{LOGO_HTML_GUEST}

    <a class="back-link" href="../index.html">&larr; Back to all guests</a>

    <div class="guest-header">
      <img class="guest-photo" src="{photo_src}" alt="Photo of {esc(name)}" />
      <div class="guest-meta">
        <div class="podcast-label">{PODCAST_NAME} Video-Podcast</div>
        <div class="podcast-tagline">{TAGLINE}</div>
        <div class="guest-speaker-label">Guest Speaker</div>
        <h1 class="guest-name">{esc(name)}</h1>
        <div class="guest-title-firm">{esc(title)}, {esc(firm)}</div>

        {bio_html}

        <div class="topics-label">Topics covered on {PODCAST_NAME}:</div>
        <ul class="topics-list">
{topics_li}
        </ul>

        <div class="episodes-label">{PODCAST_NAME} episodes in which {esc(name.split()[0])} appears:</div>
        <a class="episode-link" href="{esc(ep_url)}" target="_blank" rel="noopener">{esc(ep_title)}</a>
      </div>
    </div>

    <a class="back-link-bottom" href="../index.html">&larr; Back to all guests</a>

    {ABOUT_SECTION}

  </div>
</body>
</html>"""
    return page

def build_search_data(g):
    parts = [
        g.get('name', ''),
        g.get('title', ''),
        g.get('firm', ''),
        g.get('bio', ''),
        g.get('episodeTitle', ''),
    ]
    parts += g.get('topics', [])
    return ' '.join(str(p) for p in parts).lower()

def build_index(guests_list):
    cards = []
    for gid, g in guests_list:
        name = g.get('name', '')
        title = g.get('title', '')
        firm = g.get('firm', '')
        search_data = build_search_data(g)
        photo_src = get_photo_src(gid, g, for_index=True)
        cards.append(f"""    <a class="guest-card" href="guests/{gid}.html" data-search="{esc(search_data)}">
      <img src="{photo_src}" alt="{esc(name)}" />
      <div class="card-info">
        <div class="card-name">{esc(name)}</div>
        <div class="card-title">{esc(title)}</div>
        <div class="card-firm">{esc(firm)}</div>
      </div>
    </a>""")

    cards_html = '\n'.join(cards)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{PODCAST_NAME} | Directory of Experts</title>
  <meta name="description" content="Meet the experts who have appeared on {PODCAST_NAME}, the video-podcast about Entrepreneurship-Through-Acquisition.">
  <link rel="stylesheet" href="style.css">
  <script src="https://identity.netlify.com/v1/netlify-identity-widget.js"></script>
  <script>
    if (window.location.hash && (window.location.hash.includes('invite_token') || window.location.hash.includes('recovery_token'))) {{
      window.location = '/admin/' + window.location.hash;
    }}
  </script>
</head>
<body>

  <div class="hero-banner logo-only-banner">
    <a href="{PODCAST_URL}/" target="_blank" rel="noopener">
      <img src="images/{LOGO_FILE}" alt="{PODCAST_NAME}" class="hero-logo-large" />
    </a>
  </div>

  <div class="site-wrapper">

    <div class="directory-heading">
      <h1>Directory of Experts</h1>
      <p class="directory-subtitle">Search for people, firms and topics to have appeared on the {PODCAST_NAME} video-podcast</p>
    </div>

    <div class="search-wrap">
      <input
        type="search"
        id="guest-search"
        class="guest-search"
        placeholder="Search by name, firm, topic, keyword&hellip;"
        autocomplete="off"
        spellcheck="false"
      />
    </div>

    <div class="guest-grid" id="guest-grid">
{cards_html}
    </div>
    <p id="no-results" class="no-results" style="display:none;">No guests match your search.</p>

    {ABOUT_SECTION}
  </div>
{SEARCH_JS}
</body>
</html>"""

def main():
    data_dir = Path('_data/guests')
    guests_dir = Path('guests')
    guests_dir.mkdir(exist_ok=True)

    guests_list = []
    for yml_file in sorted(data_dir.glob('*.yml')):
        gid = yml_file.stem
        with open(yml_file) as f:
            g = yaml.safe_load(f)
        guests_list.append((gid, g))
        page = build_guest_page(gid, g)
        out_path = guests_dir / f'{gid}.html'
        out_path.write_text(page)
        print(f'Built {out_path}')

    index = build_index(guests_list)
    Path('index.html').write_text(index)
    print(f'Built index.html with {len(guests_list)} guests')

if __name__ == '__main__':
    main()
