// Draws the Companion's picker art as static SVGs for the site's feature list.
// Reads the engine drawings straight out of the live Companion page, so rerun it after the art changes there:
//   node scripts/engines/build.js
// Writes assets/engines/<key>.svg (160 x 100, same as the picker cards).
const fs = require("fs"), path = require("path"), vm = require("vm");
const root = path.resolve(__dirname, "../..");
const page = fs.readFileSync(path.join(root, "bribeluge/companion/launch/index.html"), "utf8");
function between(a, b) {
  const i = page.indexOf(a), j = page.indexOf(b, i);
  if (i < 0 || j < 0) throw new Error("marker not found: " + (i < 0 ? a : b));
  return page.slice(i, j);
}
const code = "var ENGINES = [], FAMILY_NAME = {}, OPTION_ART = {};\n" +
  between("// ---- Engine art: small SVG drawings", "// Art for the engine of a state") + "\n" +
  between("// ---- The drum machines as the panels draw them", "// PANEL: which engine panel") +
  "\nthis.ART = ART; this.art = art;";
const ctx = {}; vm.createContext(ctx); vm.runInContext(code, ctx);
const keys = ["tribe", "cyc", "lxr", "gin", "ultrakik", "xia", "tb303", "rings", "brophet", "bruno"];
const out = path.join(root, "assets/engines"); fs.mkdirSync(out, { recursive: true });
for (const k of keys) {
  if (!ctx.ART[k]) throw new Error("no art for " + k);
  const svg = ctx.art(k).replace('<svg viewBox="0 0 160 100" aria-hidden="true">',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 100" width="160" height="100">');
  fs.writeFileSync(path.join(out, k + ".svg"), svg + "\n");
  console.log(k, svg.length);
}
