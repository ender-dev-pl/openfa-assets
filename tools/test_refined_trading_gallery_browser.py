from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse,shutil
import json
ap=argparse.ArgumentParser();ap.add_argument('--base-url',default='http://127.0.0.1:8765');ap.add_argument('--chromium');a=ap.parse_args();root=Path(__file__).resolve().parents[1];base=a.base_url.rstrip('/');binary=a.chromium or shutil.which('chromium') or shutil.which('chromium-browser');assert binary,'Install Chromium or pass --chromium'
(root/'artifacts/trading-goods-refining').mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=binary,headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base+'/gallery/index.html#type=trading-goods')
 page.wait_for_function("document.querySelector('#type').value==='trading-goods'")
 assert page.locator('article[data-type="trading-goods"]:visible').count()==101
 assert page.locator('article[data-type="trading-goods"] figure').count()==202
 for query in ['Beers','TI007','TI010','TI025','TI041','TI048','TI064','TI067','TI101']:
  page.locator('#search').fill(query)
  page.wait_for_function("[...document.querySelectorAll('article[data-race]')].filter(e=>!e.hidden).length===1")
  imgs=page.locator('article:visible img');assert imgs.count()==2
  for n,width in [(0,768),(1,1024)]:
   imgs.nth(n).evaluate('(i)=>i.decode()');assert imgs.nth(n).evaluate('(i)=>i.naturalWidth')==width
  assert page.locator('article:visible figcaption').nth(1).inner_text().find('material-refined')>=0
  assert page.locator('article:visible a[aria-label^="Open full-resolution"]').count()==2
 page.locator('#search').fill('TI007');page.screenshot(path=str(root/'artifacts/trading-goods-refining/gallery-desktop.png'))
 page.locator('article:visible a[aria-label^="Open full-resolution"]').nth(1).click()
 page.wait_for_url('**/trading-goods-refined/TI007/front-quarter.png')
 page.locator('img').evaluate('(i)=>i.decode()');assert page.locator('img').evaluate('(i)=>i.naturalWidth')==1024
 page.goto(base+'/gallery/index.html#type=trading-goods&q=TI041')
 page.set_viewport_size({'width':390,'height':844});page.locator('#search').fill('TI041')
 page.wait_for_function("[...document.querySelectorAll('article[data-race]')].filter(e=>!e.hidden).length===1")
 page.locator('article:visible img').nth(1).evaluate('(i)=>i.decode()')
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'mobile horizontal overflow'
 page.screenshot(path=str(root/'artifacts/trading-goods-refining/gallery-mobile.png'),full_page=True)
 assert not errors,errors
 browser.close()
print('REFINED_GALLERY_BROWSER_OK 101 cards, 202 variants; representative source images decoded; full PNG link; mobile layout; no JS errors')
