/** UI logic regressions with a minimal DOM substitute; no browser is simulated. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

/** Build the nodes used by prediction and language switching. */
function setup() {
  const nodes = new Map();
  /** Create a small element substitute with the methods exercised by this suite. */
  function element() {
    return {
      value: "", textContent: "", innerHTML: "", style: {}, disabled: false,
      children: [], classList: { toggle() {}, add() {}, remove() {} },
      appendChild(child) { this.children.push(child); },
      setAttribute() {}, addEventListener() {},
    };
  }
  const ids = ["btn", "riskText", "riskBadge", "advice", "explain", "errorText",
    "gaugeNeedle", "lightProb", "dangerousProb", "btnText", "btnLoading", "resultSection"];
  for (const id of ids) nodes.set(id, element());
  const heading = element();
  const message = element();
  nodes.get("errorText").querySelector = (selector) => selector === "h3" ? heading : message;
  const document = {
    readyState: "loading", documentElement: { lang: "en", dir: "ltr" },
    getElementById: (id) => nodes.get(id),
    querySelector: (selector) => ({ ".btn-text": nodes.get("btnText"),
      ".btn-loading": nodes.get("btnLoading"), ".result-section": nodes.get("resultSection") })[selector],
    querySelectorAll: () => [], createElement: element, addEventListener() {},
  };
  const context = vm.createContext({ document, TypeError,
    window: { location: { port: "8000", hostname: "127.0.0.1" } },
    localStorage: { setItem() {}, getItem() { return null; } },
    fetch: async () => { throw new TypeError("offline"); },
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../frontend/script.js"), "utf8"), context);
  const options = vm.runInContext("selectOptions", context);
  for (const [id, choices] of Object.entries(options)) {
    const node = element();
    node.value = choices[0].value;
    nodes.set(id, node);
  }
  return { context, nodes, heading, message, options };
}

test("every frontend option uses an authoritative mapping key", () => {
  const { options } = setup();
  const mappings = JSON.parse(fs.readFileSync(path.join(__dirname,
    "../backend/services/feature_value_mappings.json"), "utf8"));
  for (const [field, choices] of Object.entries(options)) {
    if (field.startsWith("SHAA_")) continue;
    for (const choice of choices) assert.ok(Object.hasOwn(mappings[field], choice.value), `${field}:${choice.value}`);
  }
});

for (const lang of ["en", "he"]) {
  test(`${lang}: network error replaces validation text and a later prediction recovers`, async () => {
    const { context, nodes, heading, message } = setup();
    context.document.documentElement.lang = lang;
    nodes.get("HODESH_TEUNA").value = "";
    await context.predict();
    assert.match(message.textContent, lang === "en" ? /Missing fields/ : /שדות חסרים/);
    nodes.get("HODESH_TEUNA").value = "january";
    await context.predict();
    assert.equal(heading.textContent, vm.runInContext(`i18n.${lang}.unable_calculate`, context));
    assert.equal(message.textContent, vm.runInContext(`i18n.${lang}.network_error`, context));
    assert.equal(nodes.get("btn").disabled, false);
    context.fetch = async () => ({ ok: true, json: async () => ({ prediction: 0,
      light_probability: 0.7704, dangerous_probability: 0.2296 }) });
    await context.predict();
    assert.equal(nodes.get("errorText").style.display, "none");
    assert.equal(nodes.get("dangerousProb").textContent, "23%");
    assert.equal(nodes.get("lightProb").textContent, "77%");
    context.setLanguage(lang === "en" ? "he" : "en");
    assert.equal(context.document.documentElement.dir, lang === "en" ? "rtl" : "ltr");
    assert.equal(nodes.get("HODESH_TEUNA").value, "january");
    assert.equal(nodes.get("dangerousProb").textContent, "23%");
    assert.match(nodes.get("explain").innerHTML, lang === "en" ? /תאונה קלה/ : /Light Accident/);
  });

  test(`${lang}: server error replaces stale validation text`, async () => {
    const { context, heading, message } = setup();
    context.document.documentElement.lang = lang;
    context.showValidationError("old validation message");
    context.fetch = async () => ({ ok: false, status: 500 });
    await context.predict();
    assert.equal(heading.textContent, vm.runInContext(`i18n.${lang}.unable_calculate`, context));
    assert.equal(message.textContent, vm.runInContext(`i18n.${lang}.server_error`, context));
  });
}
