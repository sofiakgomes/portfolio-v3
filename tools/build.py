#!/usr/bin/env python3
"""Generates the static pages (plain HTML) so the shared header/footer live in one place.

Usage:  python3 tools/build.py [output_dir]      (default: the repo root)
Writes index.html, about/, work/, work/<slug>/, 404.html, sitemap.xml, robots.txt and .nojekyll.
"""
import html
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
OUT = sys.argv[1] if len(sys.argv) > 1 else ROOT
DOMAIN = 'https://www.sofiakgomes.com'  # keep in step with the CNAME file
SITE = 'SOFIA GOMES'
EMAIL = 'sofiakfourigomes@gmail.com'
INSTAGRAM = 'https://www.instagram.com/sofiagomespontes/'
LINKEDIN = 'https://www.linkedin.com/in/sofiakpgomes/'
RESUME = '/assets/Sofia-Gomes-Resume.pdf'

ICONS = {
    'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor" stroke="none"/></svg>',
    'linkedin': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3.3a2.5 2.5 0 110 5 2.5 2.5 0 010-5zM3 9.8h4V21H3zM9.5 9.8h4v1.6c.5-1 1.8-2 3.8-2 3.9 0 4.7 2.6 4.7 6.1V21h-4v-4.9c0-1.2-.3-2.7-1.8-2.7-1.6 0-2.7 1.3-2.7 2.6V21H9.5z"/></svg>',
    'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 5.5h18v13H3z"/><path d="M3 7l9 6.5L21 7"/></svg>',
}
CHEVRON_L = '<svg viewBox="0 0 14 28" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M13 1L1 14l12 13"/></svg>'
CHEVRON_R = '<svg viewBox="0 0 14 28" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M1 1l12 13L1 27"/></svg>'


def esc(text):
    return html.escape(text, quote=False)


def social():
    return (
        f'<a href="{INSTAGRAM}" aria-label="Instagram" target="_blank" rel="noopener">{ICONS["instagram"]}</a>'
        f'<a href="{LINKEDIN}" aria-label="LinkedIn" target="_blank" rel="noopener">{ICONS["linkedin"]}</a>'
        f'<a href="mailto:{EMAIL}" aria-label="{EMAIL}">{ICONS["mail"]}</a>'
    )


# ---------------------------------------------------------------- images

# tools/images.txt: "<folder> <name>" per gallery image, in display order; the files are
# assets/img/<folder>/<name>.webp (full size) and assets/img/<folder>/thumb/<name>.webp
GALLERY = {}
with open(os.path.join(TOOLS, 'images.txt'), encoding='utf-8') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            folder, name = line.split()
            GALLERY.setdefault(folder, []).append(name + '.webp')


# ---------------------------------------------------------------- building blocks


def video(name, cls=''):
    classes = ' '.join(('player', cls)) if cls else 'player'
    return (f'<div class="{classes}"><video preload="metadata" playsinline '
            f'data-src="/assets/video/{name}.mp4" poster="/assets/video/{name}.webp"></video>'
            f'<button class="play" aria-label="Play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button></div>')


def paras(items):
    return ''.join(f'<p class="reveal">{p}</p>' for p in items)


def stat(label, value):
    return f'<p class="reveal"><b>{label}:</b> {value}</p>'


def gallery(dirname, files):
    tiles = ''.join(
        f'<a class="reveal" href="/assets/img/{dirname}/{f}" data-lightbox>'
        f'<img src="/assets/img/{dirname}/thumb/{f}" alt="" loading="lazy"></a>\n' for f in files)
    return f'<div class="gallery">\n{tiles.rstrip(chr(10))}\n</div>'


def col(title, text, name):
    return (f'<div class="col reveal"><div class="txt"><h3>{title}</h3><p>{text}</p></div>'
            + video(name, 'tall') + '</div>')


def intro(cls, label, name):
    return f'<div class="intro {cls} reveal"><p>{label}</p>' + video(name) + '</div>'


def trio(name):
    return '<div class="reveal">' + video(name, 'tall') + '</div>'


def pager(i):
    prev = PROJECTS[i - 1] if i > 0 else None
    nxt = PROJECTS[i + 1] if i < len(PROJECTS) - 1 else None
    left = (f'<a class="prev" href="/work/{prev["slug"]}/">{CHEVRON_L}<span>{esc(prev["h2"])}</span></a>'
            if prev else '<span></span>')
    right = (f'<a class="next" href="/work/{nxt["slug"]}/"><span>{esc(nxt["h2"])}</span>{CHEVRON_R}</a>'
             if nxt else '<span></span>')
    return f'<nav class="pager">{left}{right}</nav>'


def head(title, desc, path, font=False, indexed=True):
    """The <head> shared by every page. `path` is the page's URL path (for the canonical/social URLs)."""
    url = DOMAIN + path
    lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{html.escape(title)}</title>',
        f'<meta name="description" content="{html.escape(desc)}">',
    ]
    if indexed:
        lines += [
            f'<link rel="canonical" href="{url}">',
            '<meta property="og:type" content="website">',
            f'<meta property="og:site_name" content="{SITE}">',
            f'<meta property="og:title" content="{html.escape(title)}">',
            f'<meta property="og:description" content="{html.escape(desc)}">',
            f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{DOMAIN}/assets/img/og.jpg">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta name="twitter:card" content="summary_large_image">',
        ]
    else:
        lines.append('<meta name="robots" content="noindex">')
    lines += [
        '<link rel="icon" href="/favicon.ico" sizes="32x32">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
    ]
    if font:
        lines.append('<link rel="preload" href="/assets/fonts/oswald-latin.woff2" as="font" type="font/woff2" crossorigin>')
    lines.append('<link rel="stylesheet" href="/css/style.css">')
    return '\n'.join(lines)


def page(title, desc, path, body, active='', cls='', font=True, indexed=True):
    work_active = ' class="active"' if active == 'work' else ''
    about_active = ' class="active"' if active == 'about' else ''
    body_attr = f' class="{cls}"' if cls else ''
    return f'''<!doctype html>
<html lang="en">
<head>
{head(title, desc, path, font, indexed)}
</head>
<body{body_attr}>
<header class="site-header">
  <nav class="nav"><a href="/work/"{work_active}>WORK</a><a href="/about/"{about_active}>ABOUT</a></nav>
  <a class="logo" href="/"><img src="/assets/img/site/logo.webp" width="480" height="100" alt="SOFIA GOMES"></a>
  <div class="social">{social()}</div>
  <button class="burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
</header>
<div class="mobile-menu" aria-hidden="true">
  <nav><a href="/work/">WORK</a><a href="/about/">ABOUT</a></nav>
  <div class="social">{social()}</div>
</div>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="social">{social()}</div>
</footer>
<script src="/js/main.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- content

AGENCY = 'Momentum Worldwide'
WALMART_CREDITS = ('<b>VP CD:</b> Jeff Vermeersch <b>CD’s:</b> Qiana Lee &amp; Bridget Kelly <b>ACD:</b> Becky Wong '
                   '<b>SR. CW’s:</b> Caitlin Condon &amp; Jessica Rodriguez <b>AD:</b> Sofia Gomes')
JORDAN_CREDITS = '<b>CD:</b> Jordan Chlapecka <b>SR. CW:</b> Jessica Rodriguez <b>AD:</b> Sofia Gomes'

# One entry per project page, in display order (also the previous/next order).
#   h2     title shown on the page (and in the previous/next links)
#   grid   title on the Work grid tile, when it differs from h2
#   cls    extra classes on the .narrow wrapper (they control the gap above the title)
#   hero   video name, or hero_img=True to use the first gallery image
#   extra  HTML blocks between the text and the gallery
PROJECTS = [
    dict(
        slug='buldakglorilla', dir='buldak', title='Buldak & GloRilla | Coachella', h2='RIDE THE BULDAK HIGH',
        desc='Buldak hot sauce’s US launch at Coachella with GloRilla: 27,860 visitors, 107,880 samples and 761M+ social media impressions. Art direction by Sofia Gomes.',
        thumb='buldak.webp', cls='', hero='buldak-hero',
        text=[
            'Since Buldak launched in the US market, it has become a viral sensation. Hotheads, Spicophiles, Ramen-lovers, Foodies, Darers, Gen Zers, People in general…they love it. Just one problem though, most people still don’t know about it.',
            'So we needed to launch Buldak in the US, at the hottest place on earth. And who better to host our fire launch party than the hottest act in music? GloRilla.',
            'And boooooyyy, did we launch. We launched attendees (after they took a literal shot of hot sauce). We launched celebrities. And we definitely launched an impressive amount of product. Resulting in fire content, and the hottest Buldak Hot Sauce launch ever.',
        ],
        stats=[('VISITORS', '27,860'), ('SAMPLES', '107,880'), ('SOCIAL MEDIA IMPRESSIONS', '761 M+'),
               ('NEWS MEDIA IMPRESSIONS', '884 M+'), ('LAUNCHES', '6,013'), ('VIEWS', '750 M+'), ('LIKES', '160 M+')],
        credits=['<b>ECD:</b> Bharat Kumar <b>CD:</b> Jordan Chlapecka <b>SR. CW:</b> Jessica Rodriguez <b>AD:</b> Sofia Gomes'],
        extra=[
            '<div class="cols">',
            col('GLORILLA ANNOUNCEMENT', 'So in the run-up to Coachella, Glo helped spread the word about our Buldak Launch. Sending spicy fans to our one-of-a-kind space on the grounds.', 'buldak-glorilla'),
            col('COACHELLA POST', 'Throughout the grounds, we gave fans ways to try Buldak… Resulting in a total of 107,880 scorched mouths outside of our activation', 'buldak-coachella'),
            col('SOCIAL RECAP', 'That’s right, we attracted influencers, celebs (including our girl, GloRilla) and 27K+ heat-seeking, pepper-punishing, fire-breathing fans to the Buldak Launch.', 'buldak-social'),
            '</div>',
        ],
    ),
    dict(
        slug='walmartheroesheadliners', dir='heroes', title='Heroes & Headliners | Walmart', h2='WALMART HEROES & HEADLINERS',
        desc='Walmart Heroes & Headliners: a free concert for 14,000 members of the military community with H.E.R., Imagine Dragons and Chris Stapleton. Art direction by Sofia Gomes.',
        thumb='Heroes_Headliners_23-145.webp', cls='heroes t72', hero='heroes-hero',
        text=['Most Americans were unaware of Walmart’s steadfast support for the military community, so our mission was to change that perception through a powerful, uplifting experience for Veterans, active service members, and their families. We produced a free concert for 14,000 members of the military community, hosted by Camille Kostek and Rob Gronkowski, with performances by H.E.R., Imagine Dragons, and Chris Stapleton, generating 233 million engagements both in person and online. Our team was involved at every stage—from concept and promotion to pre- and post-production and the live broadcast—ensuring every element of the project reflected Walmart’s commitment.'],
        stats=[('REACH', '4 million earned social media impressions, 9 million views'),
               ('AWARDS', 'ANA Multicultural Excellence Award | Rising Multicultural Segments')],
        credits=[WALMART_CREDITS],
        extra=[
            '<h3 class="sec reveal">ARTISTS’ INTROS</h3>',
            '<div class="intros">',
            intro('stapleton', 'CHRIS STAPLETON', 'heroes-stapleton'),
            intro('dan', 'DAN REYNOLDS | IMAGINE DRAGONS', 'heroes-dan'),
            intro('her', 'H.E.R.', 'heroes-her'),
            '</div>',
            '<div class="content-row">',
            '<h3 class="sec reveal">CONTENT</h3>',
            '<div class="trio">',
            trio('heroes-content-1'), trio('heroes-content-2'), trio('heroes-content-3'),
            '</div></div>',
        ],
    ),
    dict(
        slug='merryexpress', dir='merry', title="Merry Express | Sam's Club", h2='SAM’S CLUB MERRY EXPRESS',
        desc='Sam’s Club Merry Express: 50 parking lots turned into immersive holiday train stations. Art direction by Sofia Gomes.',
        grid="SAM'S CLUB MERRY EXPRESS", thumb='MerryExpress23-3.webp', cls='t72', hero='merry-hero',
        text=['Sam’s Club wanted to bring the magic of the holidays to life for their members, so we created The Merry Express—an immersive winter activation designed to spark wonder, joy, and connection. We transformed 50 Sam’s Club parking lots across the country into whimsical holiday train stations where families could play games, share wishes with Santa, and enjoy sweet seasonal treats. From a larger-than-life “Gift Grab” machine with a mechanical arm handing out presents, to a reindeer ring toss that lit up Rudolph’s nose, every detail was crafted to surprise and delight. With trains whistling, steam blowing, and festive music filling the air, the experience wrapped guests in a surreal, joy-filled winter wonderland.'],
        credits=[JORDAN_CREDITS],
    ),
    dict(
        slug='summerrewind', dir='summer', title='Summer Rewind | Walmart', h2='WALMART SUMMER REWIND',
        desc='Walmart Summer Rewind: a 33-city, Y2K-inspired experiential tour in store parking lots. Art direction by Sofia Gomes.',
        thumb='SRW_6.webp', cls='', hero='summer-hero', hero_cls='tall solo',
        text=['Walmart wanted to bring nostalgic joy to communities across the country with Summer Rewind—a 33-city experiential tour that transformed local store parking lots into playful, Y2K-inspired wonderlands. Designed to rekindle childhood memories, the installation let customers do all the things they dreamed of as kids—like diving into a giant Walmart ball cage or sneaking treats from the freezer aisle—without the rules. The immersive activation encouraged families to reconnect, laugh, and relive the magic of peak 2000s Walmart in a fun, unforgettable way.'],
        credits=[WALMART_CREDITS],
    ),
    dict(
        slug='duo-miles', dir=None, title='Duolingo & Delta | Duomiles', h2='DUOMILES',
        desc='Duomiles: Duolingo and Delta’s program that rewards language lessons with SkyMiles. Copywriting and art direction by Sofia Gomes.',
        thumb='duomiles.webp', cls='t72', hero='duomiles-hero',
        text=[
            'For many, travel is the main reason to learn a new language—whether for leisure, work, or study—because it opens the door to exploring new places with confidence and connecting more deeply with the culture. But mastering the language is only part of the journey; you still need a plane ticket to get there. That’s why Duolingo is here to break more than just the language barrier—we’re also helping bridge the distance to your destination.',
            'Introducing DuoMiles, a new program in partnership with Delta Airlines that rewards you with SkyMiles for every lesson you complete, bringing you one step closer to your destination with every assignment.',
        ],
        credits=None,  # only a creative credit, no agency line
        credit_html='<b>CW &amp; AD:</b> Sofia Gomes',
    ),
    dict(
        slug='anthemsofpride', dir='anthems', title='Anthems of Pride | American Express', h2='AMEX & PLAYBILL: PRIDE',
        desc='Anthems of Pride: American Express and Playbill’s first-ever NYC Pride concert, with Broadway performances. Art direction by Sofia Gomes.',
        grid='ANTHEMS OF PRIDE', thumb='DSC09831-GC-FINAL-3.webp', cls='t96', hero_img=True, hero_size=(2500, 1406),
        text=['American Express, in partnership with Playbill®, celebrated NYC Pride in 2023 with the first-ever “Anthems of Pride” concert featuring performances from hit Broadway shows like Funny girl, SIX, Hamilton, Parade, and more.'],
        credits=[JORDAN_CREDITS],
    ),
]


def project_body(p):
    files = GALLERY.get(p['dir'], [])
    if p.get('hero_img'):  # the first image is the hero; the rest form the gallery
        hero = (f'<a class="hero-img" href="/assets/img/{p["dir"]}/{files[0]}" data-lightbox>'
                f'<img src="/assets/img/{p["dir"]}/{files[0]}" width="{p["hero_size"][0]}" height="{p["hero_size"][1]}" '
                f'fetchpriority="high" alt=""></a>')
        files = files[1:]
    else:
        hero = video(p['hero'], p.get('hero_cls', ''))
    if p['credits'] is None:
        credit_lines = [p['credit_html']]
    else:
        credit_lines = [f'<b>AGENCY:</b> {AGENCY}'] + p['credits']
    parts = [
        f'<div class="narrow {p["cls"]}">'.replace(' "', '"'),
        hero,
        f'<h2 class="reveal">{esc(p["h2"])}</h2>',
        paras(p['text']),
        *[stat(*s) for s in p.get('stats', [])],
        *[f'<p class="reveal">{c}</p>' for c in credit_lines],
        '</div>',
        *p.get('extra', []),
    ]
    if files:
        parts.append(gallery(p['dir'], files))
    return '\n'.join(parts)


ABOUT = f'''<div class="about">
  <div class="portrait"><img src="/assets/img/site/portrait.webp" alt="Sofia Gomes"></div>
  <div class="about-text">
    <p>Olá &amp; Welcome<br>take a seat,<br>let’s get cozy!</p>
    <p>So far you’ve probably figured out my name is Sofia and I’m an Art Director.</p>
    <p>But we should get to know each other more.</p>
    <p>I like Coke Zero, the color yellow and Art Deco posters.<br>I talk way too much about my dog Diana. She’s terrible and all I think about.<br>I’m originally from Brazil and I bring it up in almost every conversation because Brazil is awesome.<br>I live in New York and I bring it up in almost every conversation because New York is awesome.<br>I don’t like celery.<br>I don’t understand skiing. Why spend money to be tired, cold and in pain?<br>I’m scared of whales.</p>
    <p>I enjoy having ideas. I enjoy it even more when I get to bring them to life with awesome people.<br>I enjoy it eeeeven more when we make other folks happy, or scared, or impressed, or entertained (or a mix of all the above) with said idea.</p>
    <p>Curious? Peek at my <a href="{RESUME}">resume</a>.<br>Chatty? Shoot me an email at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </div>
</div>'''

DESC_SITE = 'Sofia Gomes is an Art Director from Brazil based in New York.'
DESC_WORK = 'Selected work by Sofia Gomes, Art Director: experiential and social campaigns for Walmart, Sam’s Club, American Express, Duolingo and Buldak.'
DESC_ABOUT = 'About Sofia Gomes, an Art Director from Brazil living in New York.'


def splash():
    return f'''<!doctype html>
<html lang="en">
<head>
{head(SITE, DESC_SITE, '/')}
</head>
<body class="splash">
<a class="splash-link" href="/work/" aria-label="Enter site"><img src="/assets/img/site/splash.webp" width="546" height="582" fetchpriority="high" alt="SOFIA GOMES — Art Director"></a>
<script src="/js/main.js"></script>
</body>
</html>
'''


def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    write('index.html', splash())

    tiles = '\n'.join(
        f'<a class="tile reveal" href="/work/{p["slug"]}/"><img src="/assets/img/work/{p["thumb"]}" alt="{esc(p.get("grid", p["h2"]))}">'
        f'<span class="tile-title">{esc(p.get("grid", p["h2"]))}</span></a>'
        for p in PROJECTS)
    write('work/index.html', page(f'WORK — {SITE}', DESC_WORK, '/work/', f'<div class="work-grid">\n{tiles}\n</div>', 'work'))
    write('about/index.html', page(f'About — {SITE}', DESC_ABOUT, '/about/', ABOUT, 'about', font=False))
    for i, p in enumerate(PROJECTS):
        path = f'/work/{p["slug"]}/'
        write(path[1:] + 'index.html',
              page(f'{p["title"]} — {SITE}', p['desc'], path, project_body(p) + pager(i), 'work', 'p-' + p['slug']))

    write('404.html', page(f'Page not found — {SITE}', 'This page does not exist.', '/404.html',
                           '<div class="notfound">\n<p>This page doesn’t exist.</p>\n<p><a href="/work/">Back to the work</a></p>\n</div>',
                           font=False, indexed=False))

    urls = ['/', '/work/', '/about/'] + [f'/work/{p["slug"]}/' for p in PROJECTS]
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{DOMAIN}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n')
    write('.nojekyll', '')  # serve every file as is, without GitHub's Jekyll step


if __name__ == '__main__':
    main()
