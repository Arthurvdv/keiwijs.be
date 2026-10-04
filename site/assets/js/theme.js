// Theme toggle: system → light → dark. Loaded synchronously in <head> so the stored
// choice is applied before the stylesheet paints (CSP forbids an inline script).
(function () {
  "use strict";

  var KEY = "keiwijs-theme";
  var MODES = ["system", "light", "dark"];
  var root = document.documentElement;

  function load() {
    try {
      var v = localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : "system";
    } catch (e) {
      return "system";
    }
  }

  function save(mode) {
    try {
      if (mode === "system") localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, mode);
    } catch (e) { /* storage blocked: the choice lasts for this page only */ }
  }

  function apply(mode) {
    if (mode === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", mode);
  }

  function render(btn, mode) {
    var label = btn.getAttribute("data-label-" + mode) || "";
    btn.setAttribute("data-mode", mode);
    btn.setAttribute("aria-label", label);
    btn.setAttribute("title", label);
  }

  var mode = load();
  apply(mode);

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    render(btn, mode);
    btn.hidden = false;
    btn.addEventListener("click", function () {
      mode = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
      apply(mode);
      save(mode);
      render(btn, mode);
    });
  });
})();
