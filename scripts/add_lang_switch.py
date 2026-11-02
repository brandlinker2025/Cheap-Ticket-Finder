#!/usr/bin/env python3
"""Add a Bangla ⇄ English switch to every page that has both versions (add-only, idempotent)."""
import glob, os, re
MARK = 'class="ctf-lang-switch"'
PILL = ('<div class="ctf-lang-switch" style="margin:4px 0 10px;font-size:13px;font-weight:700">'
        '<span style="display:inline-flex;border:1px solid rgba(201,162,75,.6);border-radius:999px;overflow:hidden;background:rgba(255,255,255,.75)">'
        '{en}{bn}</span></div>')
def seg(label, href, active, lang):
    st = 'padding:4px 12px;text-decoration:none;'
    if active:
        return f'<span style="{st}background:#0c4a6e;color:#fff" aria-current="true" lang="{lang}">{label}</span>'
    return f'<a href="{href}" hreflang="{lang}" lang="{lang}" style="{st}color:#0c4a6e">{label}</a>'
def pill(en_url, bn_url, cur):
    return PILL.format(en=seg('English', en_url, cur == 'en', 'en'), bn=seg('বাংলা', bn_url, cur == 'bn', 'bn'))
logo = re.compile(r'(<a href="/(?:bn/)?" aria-label="Cheap Ticket Finder[^"]*home"[^>]*>.*?</a>)', re.S)
n = 0
for bn in glob.glob('bn/*/index.html'):
    slug = bn.split('/')[1]; en = f'{slug}/index.html'
    if not os.path.exists(en): continue
    # English pages stay English-only (no visible Bangla switch); Bangla pages link back to English.
    for f, cur in ((bn, 'bn'),):
        t = open(f, encoding='utf-8').read()
        if MARK in t: continue
        t2, k = logo.subn(lambda m: m.group(1) + '\n            ' + pill(f'/{slug}/', f'/bn/{slug}/', cur), t, count=1)
        assert k == 1, f
        open(f, 'w', encoding='utf-8').write(t2); n += 1
# Bangla homepage
f = 'bn/index.html'; t = open(f, encoding='utf-8').read()
if MARK not in t:
    t = t.replace('<a class="lang" href="/" hreflang="en" lang="en">English version</a>', pill('/', '/bn/', 'bn'), 1); open(f, 'w', encoding='utf-8').write(t); n += 1
print('updated', n, 'files')
