// Loads docs/index.html in jsdom, serves docs/data via a stubbed fetch, runs
// docs/app.js and checks the converter. Run: npm install && npm test
"use strict";
const fs = require("fs");
const path = require("path");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const docs = path.join(__dirname, "..", "docs");
const html = fs.readFileSync(path.join(docs, "index.html"), "utf8");
const json = fs.readFileSync(path.join(docs, "data", "grading-scales.json"), "utf8");
const appJs = fs.readFileSync(path.join(docs, "app.js"), "utf8");

const dom = new JSDOM(html.replace('<script src="app.js" defer></script>', ""), {
  url: "https://mrhandersson.github.io/grading-scales/",
  runScripts: "outside-only",
});
const { window } = dom;
window.fetch = (url) => {
  assert.strictEqual(url, "data/grading-scales.json");
  return Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(json)) });
};
window.eval(appJs);

const tick = () => new Promise((r) => setTimeout(r, 20));
const $ = (id) => window.document.getElementById(id);

function convertVia(systemKey, percent) {
  $("conv-system").value = systemKey;
  assert.strictEqual($("conv-system").value, systemKey, "option missing: " + systemKey);
  $("conv-percent").value = String(percent);
  $("convert-form").dispatchEvent(new window.Event("submit", { cancelable: true }));
  return $("conv-result").textContent;
}

(async () => {
  await tick();
  const opts = [...$("conv-system").options].map((o) => o.value);
  console.log("systems in converter:", opts.length);
  assert.ok(opts.length >= 5);
  assert.ok(!opts.some((o) => o.startsWith("Germany")), "non-percent systems must be excluded");

  const cases = [
    ["United States | College letter grades (4.0 GPA, plus/minus)", 95, /= A \(93–100%, 4\.0 points\)/],
    ["United States | College letter grades (4.0 GPA, plus/minus)", 92.5, /= A- \(90–92%/],
    ["United States | College letter grades (4.0 GPA, plus/minus)", 88, /= B\+ .*3\.3 points/],
    ["United States | College letter grades (4.0 GPA, plus/minus)", 59, /= F /],
    ["United Kingdom | University undergraduate degree classification", 68, /Upper second-class honours \(2:1\)/],
    ["United Kingdom | University undergraduate degree classification", 70, /First-class/],
    ["United Kingdom | University taught master's degree", 30, /no band/],
    ["India | University 10-point CGPA (UGC CBCS)", 91, /= O .*10 points/],
    ["Canada | University of Toronto (example university scale)", 78, /= B\+ .*3\.3 points/],
    ["Australia | University grade bands (UNSW)", 85, /High Distinction/],
    ["Australia | University grade bands (UNSW)", 0, /Fail \(FL\)/],
  ];
  for (const [sys, p, re] of cases) {
    const out = convertVia(sys, p);
    assert.match(out, re, `${sys} ${p}% -> "${out}"`);
    console.log(`ok  ${p}% ${sys.split(" | ")[0]} -> ${out}`);
  }
  assert.match(convertVia(cases[0][0], 101), /between 0 and 100/);
  assert.ok(window.document.querySelectorAll("#scales table").length === 17, "17 tables rendered");
  console.log("all converter tests passed");
})().catch((e) => { console.error(e); process.exit(1); });
