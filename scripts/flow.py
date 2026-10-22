# usage: python3 scripts/flow.py <base_url> <prefix>   -> functional checks at 375/768/1280
import asyncio, sys, json, re
from playwright.async_api import async_playwright
base, prefix = sys.argv[1], sys.argv[2]
OURS = re.compile(r'cheapticketfinder|vercel\.app|localhost|booking-links|travelpayouts\.js|index\.html')
async def run(b, w):
  ctx = await b.new_context(viewport={'width': w, 'height': 900}, is_mobile=(w == 375))
  pg = await ctx.new_page(); errs = []; res = {}
  pg.on('console', lambda m: errs.append((m.text[:180], (m.location or {}).get('url', ''))) if m.type == 'error' else None)
  pg.on('pageerror', lambda e: errs.append(('PAGEERROR ' + str(e)[:180], 'page')))
  await pg.goto(base, wait_until='domcontentloaded', timeout=60000); await pg.wait_for_timeout(4000)
  # pax picker
  await pg.click('#paxToggle'); await pg.click('[aria-label="More adults"]'); await pg.click('[aria-label="More children"]')
  await pg.select_option('#paxCabin', 'business')
  if w == 375: await pg.screenshot(path=f'shots/{prefix}-{w}-pax.png')
  await pg.click('.pax-done')
  res['paxSummary'] = await pg.inner_text('#paxSummary')
  # route DAC->ZYL via JS state (modal search is UI-only), then pick dates in calendar
  for code, flds in (('zyl', 'dest'),):
    await pg.evaluate("""(c)=>{selectedDestCode=c;const a=getAllAirports().find(i=>i.code===c);if(a)document.getElementById('destDisplay').textContent=a.name||c;}""", code)
  await pg.click('[aria-label="Next month"]')
  days = pg.locator('#tripCalendarGrid .sk-day:not(.empty)')
  await days.nth(9).click(); await days.nth(14).click()
  await pg.click('#searchBtn'); await pg.wait_for_timeout(2500)
  res['url'] = pg.url
  res['flightSearch'] = re.search(r'flightSearch=([^&#]+)', pg.url).group(1) if 'flightSearch=' in pg.url else None
  res['hotelText'] = (await pg.inner_text('#hotelResults'))[:120]
  links = await pg.evaluate("()=>[...document.querySelectorAll('#cheapPathResults a, #hotelResults a, #googleBookBar a')].map(a=>[a.innerText.trim().slice(0,40),a.href])")
  res['links'] = links
  if w == 1280: await pg.screenshot(path=f'shots/{prefix}-{w}-results.png', full_page=False)
  tabs = {}
  for t in ['airlines', 'hotel', 'tour', 'sim', 'transfer', 'bd', 'air']:
    await pg.evaluate('window.scrollTo(0,0)')
    btn = pg.locator(f'.trip-tabs button[data-tab="{t}"]')
    await btn.click()
    panel = pg.locator(f'.home-panel[data-tab="{t}"]')
    tabs[t] = [await panel.is_visible(), await panel.evaluate("e=>[...e.querySelectorAll('a')].map(a=>a.href)")]
    if t == 'bd': await pg.screenshot(path=f'shots/{prefix}-{w}-bd-tab.png')
  res['tabs'] = tabs
  res['errors_all'] = errs
  res['errors_ours'] = [e for e in errs if OURS.search(e[1]) and 'insights' not in e[1]]
  await ctx.close(); return res
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--headless=new'])
    out = {w: await run(b, w) for w in (375, 768, 1280)}
    await b.close()
  print(json.dumps(out, indent=1))
asyncio.run(main())
