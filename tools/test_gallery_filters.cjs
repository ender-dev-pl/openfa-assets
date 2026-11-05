// Execute the generated page's own JavaScript with a minimal DOM/event facade.
// This checks model/presenter behavior; it does not claim a visual browser test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const checkMedia = !process.argv.includes('--filters-only');
const page = fs.readFileSync(path.join(root, 'gallery/index.html'), 'utf8');
const models = JSON.parse(fs.readFileSync(path.join(root, 'gallery/catalogue.json'), 'utf8'));
const supplemental = JSON.parse(fs.readFileSync(path.join(root, 'gallery/supplemental-catalogue.json'), 'utf8'));
const inventory = [...models, ...supplemental];
const decode = text => text.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const records = [...page.matchAll(/<article\s+([^>]+)>/g)].map(match => {
  const attrs = Object.fromEntries([...match[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(a => [a[1], decode(a[2])]));
  return {dataset: {race: attrs['data-race'], type: attrs['data-type'], search: attrs['data-search']}, hidden: false};
});
assert.equal(records.length, inventory.length);
const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
function start(hash = '') {
  const cards = records.map(record => {
    const video = {pauseCount: 0, pause() { this.pauseCount++; }};
    return {dataset: {...record.dataset}, hidden: false, video, querySelectorAll: selector => selector === 'video' ? [video] : []};
  });
  const fields = Object.fromEntries(['search', 'race', 'type', 'reset', 'count', 'empty'].map(id => [id, {
    value: '', hidden: false, textContent: '', listeners: {},
    addEventListener(event, listener) { this.listeners[event] = listener; },
    focus() { this.focused = true; }
  }]));
  const events = {};
  const clipVideo = {pauseCount: 0, loadCount: 0, pause() { this.pauseCount++; }, load() { this.loadCount++; }};
  const clipSelect = {value: '../second.webm', listeners: {}, addEventListener(event, listener) { this.listeners[event] = listener; },
    closest() { return {querySelector: () => clipVideo}; }};
  const location = {pathname: '/gallery/index.html', search: '', hash};
  const sandbox = {
    document: {querySelectorAll: selector => selector === 'article[data-race]' ? cards : selector === '.animation-clip' ? [clipSelect] : [], querySelector: selector => fields[selector.slice(1)]},
    window: {addEventListener: (event, listener) => { events[event] = listener; }},
    history: {replaceState: (_, __, url) => { location.hash = url.includes('#') ? url.slice(url.indexOf('#')) : ''; }},
    location, URLSearchParams
  };
  vm.runInNewContext(script, sandbox, {filename: 'generated-gallery.js'});
  return {cards, fields, location, clipSelect, clipVideo,
    visible: () => cards.filter(card => !card.hidden),
    change(race, type, q = '') {
      Object.assign(fields.race, {value: race}); Object.assign(fields.type, {value: type}); Object.assign(fields.search, {value: q});
      fields.type.listeners.change();
    },
    navigate(hash) { location.hash = hash; events.hashchange(); }
  };
}
const app = start();
app.clipSelect.listeners.change();
assert.equal(app.clipVideo.src, '../second.webm');
assert.equal(app.clipVideo.pauseCount, 1);
assert.equal(app.clipVideo.loadCount, 1);
assert.equal(app.visible().length, inventory.length);
let combinations = 0;
for (const race of ['', ...new Set(inventory.map(row => row.culture))]) {
  for (const type of ['', ...new Set(inventory.map(row => row.category))]) {
    app.change(race, type);
    const expected = inventory.filter(row => (!race || row.culture === race) && (!type || row.category === type));
    assert.equal(app.visible().length, expected.length, `${race}/${type}`);
    assert.equal(app.fields.count.textContent, `${expected.length} of ${inventory.length} assets`);
    assert.equal(app.fields.empty.hidden, expected.length !== 0);
    combinations++;
  }
}
if (inventory.some(row => row.category === 'trading-goods')) {
  app.change('shared', 'trading-goods'); assert.equal(app.visible().length, 101);
  app.change('', 'trading-goods', 'TI001'); assert.equal(app.visible().length, 1);
  app.change('', 'trading-goods', 'Beers'); assert.equal(app.visible().length, 1);
}
app.change('terran', 'ships', '  combat   eagle  ');
assert.equal(app.visible().length, 1);
assert.match(app.visible()[0].dataset.search, /combat eagle/);
assert.match(app.location.hash, /race=terran/);
assert.ok(app.cards.filter(card => card.hidden).every(card => card.video.pauseCount > 0), 'Hidden animations must pause');
app.change('terran', 'hardpoints');
assert.equal(app.visible().length, 0);
app.change('shared', 'hardpoints');
assert.equal(app.visible().length, 16);
app.change('', '', '<script>');
assert.equal(app.visible().length, 0);
app.fields.reset.listeners.click();
assert.equal(app.visible().length, inventory.length);
assert.equal(app.location.hash, '');
assert.equal(app.fields.search.focused, true);
const linked = start('#race=rigellian&type=buildings');
assert.equal(linked.visible().length, 23);
linked.navigate('#race=terran&type=missiles');
assert.equal(linked.visible().length, 13);
linked.navigate('#race=unknown&type=unknown');
assert.equal(linked.visible().length, inventory.length);
for (const match of page.matchAll(/href="#([^"]*)"/g)) {
  const params = new URLSearchParams(decode(match[1]));
  linked.navigate('#'+decode(match[1]));
  const expected = inventory.filter(row => (!params.get('race') || row.culture === params.get('race')) && (!params.get('type') || row.category === params.get('type')));
  assert.equal(linked.visible().length, expected.length, match[1]);
}
console.log(`GALLERY_FILTER_RUNTIME_OK ${combinations} race/type combinations; search, empty/reset, deep links, invalid values and index links`);
const animatedStudies = models.flatMap(row => row.studies).filter(study => study.animations.length);
const extraVideos = supplemental.flatMap(row => row.category === 'scaffolds' ? [row.views.at(-1)] : [row.views[0]]).filter(view => view.video);
for (const view of extraVideos) {
  assert.ok(page.includes(view.video));
  if (checkMedia) assert.ok(fs.existsSync(path.join(root, view.video)));
}
assert.equal([...page.matchAll(/<video controls loop muted playsinline preload="none"/g)].length, animatedStudies.length + extraVideos.length);
for (const study of animatedStudies) {
  for (const clip of study.animations) {
    assert.ok(page.includes(clip.video), `Missing playable clip ${clip.video}`);
    if (checkMedia) assert.ok(fs.existsSync(path.join(root, clip.video)));
    assert.ok(clip.distinct_pose_count > 1);
  }
}
console.log(`GALLERY_PLAYABLE_PREVIEWS_OK ${animatedStudies.length} animated studies; controls, local clips, lazy preload and hidden-video pause`);

if (!checkMedia) console.log('PRESERVED_MEDIA_EXISTENCE_SKIPPED (sparse checkout); DOM/video behavior still checked');
