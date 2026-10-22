# usage: python3 scripts/shoot.py <base_url> <prefix>
import asyncio, sys, json
from playwright.async_api import async_playwright
base, prefix = sys.argv[1], sys.argv[2]
async def main():
  out = {}
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--headless=new'])
    for w in (375, 768, 1280):
      ctx = await b.new_context(viewport={'width': w, 'height': 900}, is_mobile=(w == 375))
      pg = await ctx.new_page(); errs = []
      pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
      pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)[:200]))
      await pg.goto(base, wait_until='domcontentloaded', timeout=60000); await pg.wait_for_timeout(5000)
      await pg.screenshot(path=f'shots/{prefix}-{w}-top.png')
      await pg.evaluate('window.scrollTo(0, 700)'); await pg.wait_for_timeout(600)
      await pg.screenshot(path=f'shots/{prefix}-{w}-scrolled.png')
      tabs = await pg.evaluate("""()=>{const n=document.querySelector('.trip-tabs');const r=n.getBoundingClientRect();return [...n.querySelectorAll('button')].map(b=>{const q=b.getBoundingClientRect();return [b.dataset.tab, Math.round(q.left), Math.round(q.right), q.right<=Math.min(r.right,innerWidth)+1 && q.left>=Math.max(r.left,0)-1]})}""")
      sw = await pg.evaluate('document.documentElement.scrollWidth')
      out[w] = {'errors': errs, 'tabs': tabs, 'scrollWidth': sw}
      await ctx.close()
    await b.close()
  print(json.dumps(out, indent=1))
asyncio.run(main())
