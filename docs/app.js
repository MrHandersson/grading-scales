/* Percent-to-grade converter. Reads data/grading-scales.json (same file as the download). MIT licensed. */
(function () {
  "use strict";

  // Pick the band for a percentage. Bands are inclusive; a mark that falls in a
  // gap between integer bands (e.g. 92.5 between 90-92 and 93-100) goes to the lower band.
  function convert(bands, percent) {
    var sorted = bands
      .filter(function (b) { return b.min_percent !== null && b.max_percent !== null; })
      .sort(function (a, b) { return b.min_percent - a.min_percent; });
    for (var i = 0; i < sorted.length; i++) {
      if (percent >= sorted[i].min_percent && percent <= 100) return sorted[i];
    }
    return null;
  }

  // Show 4.0-style points with one decimal (4.0, 3.0); leave other scales as-is (10, 17.5).
  function formatPoints(x) {
    return x % 1 === 0 && x <= 5 ? x.toFixed(1) : String(x);
  }

  function systemsWithPercent(rows) {
    var map = {};
    var order = [];
    rows.forEach(function (r) {
      if (r.min_percent === null) return;
      var key = r.country + " | " + r.system;
      if (!map[key]) { map[key] = []; order.push(key); }
      map[key].push(r);
    });
    return { map: map, order: order };
  }

  function init(rows) {
    var select = document.getElementById("conv-system");
    var input = document.getElementById("conv-percent");
    var form = document.getElementById("convert-form");
    var out = document.getElementById("conv-result");
    if (!select || !form) return;
    var systems = systemsWithPercent(rows);
    select.innerHTML = "";
    systems.order.forEach(function (key) {
      var opt = document.createElement("option");
      opt.value = key;
      opt.textContent = key.replace(" | ", ": ");
      select.appendChild(opt);
    });

    function run() {
      var p = parseFloat(input.value);
      out.textContent = "";
      if (isNaN(p) || p < 0 || p > 100) {
        out.textContent = "Enter a percentage between 0 and 100.";
        return;
      }
      var band = convert(systems.map[select.value] || [], p);
      if (!band) {
        out.textContent = "The source lists no band for " + p + "% in this system.";
        return;
      }
      var strong = document.createElement("strong");
      strong.textContent = band.grade;
      out.appendChild(document.createTextNode(p + "% = "));
      out.appendChild(strong);
      var extra = " (" + band.min_percent + "\u2013" + band.max_percent + "%";
      if (band.gpa_points !== null) extra += ", " + formatPoints(band.gpa_points) + " points";
      extra += "). " + band.description;
      out.appendChild(document.createTextNode(extra));
    }

    form.addEventListener("submit", function (e) { e.preventDefault(); run(); });
    select.addEventListener("change", function () { if (input.value !== "") run(); });
  }

  if (typeof window !== "undefined") {
    window.GradingScales = { convert: convert };
    fetch("data/grading-scales.json")
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(init)
      .catch(function () {
        var out = document.getElementById("conv-result");
        if (out) out.textContent = "Could not load the dataset.";
      });
  }
})();
