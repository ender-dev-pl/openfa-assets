// Execute the generated page's own JavaScript with a minimal DOM/event facade.
// This checks model/presenter behavior; it does not claim a visual browser test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const page = fs.readFileSync(path.join(root, 'gallery/index.html'), 'utf8');
const inventory = JSON.parse(fs.readFileSync(path.join(root, 'gallery/catalogue.json'), 'utf8'));
const decode = text => text.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const records = [...page.matchAll(/<article\s+([^>]+)>/g)].map(match => {
  const attrs = Object.fromEntries([...match[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(a => [a[1], decode(a[2])]));
  return {dataset: {race: attrs['data-race'], type: attrs['data-type'], search: attrs['data-search']}, hidden: false};
});
assert.equal(records.length, inventory.length);
const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
function start(hash = '') {
  const cards = records.map(record => ({dataset: {...record.dataset}, hidden: false}));
  const fields = Object.fromEntries(['search', 'race', 'type', 'reset', 'count', 'empty'].map(id => [id, {
    value: '', hidden: false, textContent: '', listeners: {},
    addEventListener(event, listener) { this.listeners[event] = listener; },
    focus() { this.focused = true; }
  }]));
  const events = {};
  const location = {pathname: '/gallery/index.html', search: '', hash};
  const sandbox = {
    document: {querySelectorAll: () => cards, querySelector: selector => fields[selector.slice(1)]},
    window: {addEventListener: (event, listener) => { events[event] = listener; }},
    history: {replaceState: (_, __, url) => { location.hash = url.includes('#') ? url.slice(url.indexOf('#')) : ''; }},
    location, URLSearchParams
  };
  vm.runInNewContext(script, sandbox, {filename: 'generated-gallery.js'});
  return {cards, fields, location,
    visible: () => cards.filter(card => !card.hidden),
    change(race, type, q = '') {
      Object.assign(fields.race, {value: race}); Object.assign(fields.type, {value: type}); Object.assign(fields.search, {value: q});
      fields.type.listeners.change();
    },
    navigate(hash) { location.hash = hash; events.hashchange(); }
  };
}
const app = start();
assert.equal(app.visible().length, 303);
let combinations = 0;
for (const race of ['', ...new Set(inventory.map(row => row.culture))]) {
  for (const type of ['', ...new Set(inventory.map(row => row.category))]) {
    app.change(race, type);
    const expected = inventory.filter(row => (!race || row.culture === race) && (!type || row.category === type));
    assert.equal(app.visible().length, expected.length, `${race}/${type}`);
    assert.equal(app.fields.count.textContent, `${expected.length} of 303 assets`);
    assert.equal(app.fields.empty.hidden, expected.length !== 0);
    combinations++;
  }
}
app.change('terran', 'ships', '  combat   eagle  ');
assert.equal(app.visible().length, 1);
assert.match(app.visible()[0].dataset.search, /combat eagle/);
assert.match(app.location.hash, /race=terran/);
app.change('terran', 'hardpoints');
assert.equal(app.visible().length, 0);
app.change('shared', 'hardpoints');
assert.equal(app.visible().length, 16);
app.change('', '', '<script>');
assert.equal(app.visible().length, 0);
app.fields.reset.listeners.click();
assert.equal(app.visible().length, 303);
assert.equal(app.location.hash, '');
assert.equal(app.fields.search.focused, true);
const linked = start('#race=rigellian&type=buildings');
assert.equal(linked.visible().length, 23);
linked.navigate('#race=terran&type=missiles');
assert.equal(linked.visible().length, 13);
linked.navigate('#race=unknown&type=unknown');
assert.equal(linked.visible().length, 303);
for (const match of page.matchAll(/href="#([^"]*)"/g)) {
  const params = new URLSearchParams(decode(match[1]));
  linked.navigate('#'+decode(match[1]));
  const expected = inventory.filter(row => (!params.get('race') || row.culture === params.get('race')) && (!params.get('type') || row.category === params.get('type')));
  assert.equal(linked.visible().length, expected.length, match[1]);
}
console.log(`GALLERY_FILTER_RUNTIME_OK ${combinations} race/type combinations; search, empty/reset, deep links, invalid values and index links`);
