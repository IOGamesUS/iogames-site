/* IO Games: shown under every finished daily puzzle.
   Adds "how you stack up" (percentile against today's players) and links to the other daily puzzles.
   Reads the game's own saved progress from this device; asks the play counter for everyone else's results. */
(function () {
  "use strict";
  var API = "{{API}}", CUR = "{{GAME}}";
  var GAMES = {{GAMES}};
  function get(k) { try { var r = localStorage.getItem(k); return r ? JSON.parse(r) : null; } catch (e) { return null; } }
  function fmt(s) { var m = Math.floor(s / 60), x = s % 60; return m + ":" + (x < 10 ? "0" : "") + x; }
  var me = GAMES.filter(function (g) { return g.id === CUR; })[0];
  var result = document.getElementById("result");
  if (!me || !result) return;

  function scoreOf(id, S) {
    if (id === "wordtangle" || id === "pemdash") return (S.checks || 0) + (S.hintCount || 0);
    if (id === "meld") return (S.breaks || 0) + (S.hints || 0);
    return (S.backs || 0) + (S.hints || 0);
  }
  function today(g) {
    var cur = get(g.key + ":current") || get(g.key + ":last") || 1;
    return { id: cur, S: get(g.key + ":p:" + cur) };
  }

  var box = document.createElement("div");
  box.className = "after";
  box.innerHTML =
    '<style>' +
    '.after{display:grid;gap:12px}' +
    '.after .rank{padding:12px 14px;background:var(--bg);border:2px solid var(--edge);display:grid;gap:8px}' +
    '.after .rank b{color:var(--gold)}' +
    '.after .rank .bar{height:10px;background:var(--panel);border:2px solid var(--edge);position:relative}' +
    '.after .rank .bar i{position:absolute;inset:0 auto 0 0;background:var(--teal)}' +
    '.after .rank .note{font:.75rem/1.4 var(--mono);color:var(--muted)}' +
    '.after .more-h{font:700 .75rem/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--teal);margin:0}' +
    '.after .more{list-style:none;margin:0;padding:0;display:grid;gap:8px}' +
    '.after .more a{display:flex;justify-content:space-between;align-items:center;gap:10px;min-height:48px;padding:8px 14px;background:var(--bg);border:2px solid var(--edge);color:var(--ink);text-decoration:none;font:700 .9375rem/1.2 var(--mono)}' +
    '.after .more a:hover{border-color:var(--teal)}' +
    '.after .more .st{font:.75rem/1.2 var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.08em;white-space:nowrap}' +
    '.after .more .st.done{color:var(--teal)}' +
    '.after .home-l{font:700 .8125rem/1.3 var(--mono);color:var(--gold);text-underline-offset:3px}' +
    '</style>' +
    '<div class="rank" aria-live="polite"><span class="txt">Checking how everyone else did&hellip;</span></div>' +
    '<p class="more-h">More daily puzzles</p><ul class="more"></ul>' +
    '<a class="home-l" href="/#daily">&lsaquo; All puzzles at iogames.us</a>';
  var share = document.getElementById("sharePre");
  result.insertBefore(box, share);

  function fillMore() {
    var ul = box.querySelector(".more");
    ul.innerHTML = "";
    GAMES.forEach(function (g) {
      if (g.id === CUR) return;
      var t = today(g), st = t.S && t.S.status, done = st === "solved" || st === "failed";
      var li = document.createElement("li");
      li.innerHTML = '<a href="/' + g.id + '/"><span></span><span class="st' + (done ? " done" : "") + '">' + (done ? "Done today" : "Play") + "</span></a>";
      li.querySelector("span").textContent = g.name;
      ul.appendChild(li);
    });
  }

  var asked = null;
  function fillRank() {
    var t = today(me), S = t.S;
    if (!S || (S.status !== "solved" && S.status !== "failed")) return;
    if (asked === t.id) return;
    asked = t.id;
    var txt = box.querySelector(".rank");
    var mine = [S.status === "solved" ? scoreOf(CUR, S) : -1, Math.round((S.elapsed || 0) / 1000)];
    if (!API) { txt.hidden = true; return; }
    /* wait a moment so this device's own result has reached the counter */
    setTimeout(function () {
      fetch(API + "?game=" + encodeURIComponent(CUR) + "&puzzle=" + t.id).then(function (r) { return r.json(); }).then(function (d) {
        var dist = d && d.results && d.results.dist;
        if (!dist) { txt.hidden = true; return; }
        /* lower score is better, then faster time; a puzzle you ran out of checks on ranks below every solve */
        function worse(a, b) {
          if (a[0] < 0 && b[0] >= 0) return true;
          if (a[0] >= 0 && b[0] < 0) return false;
          if (a[0] !== b[0]) return a[0] > b[0];
          return a[1] > b[1];
        }
        var others = dist.slice(), own = -1;
        for (var i = 0; i < others.length; i++) if (others[i][0] === mine[0] && Math.abs(others[i][1] - mine[1]) <= 1) { own = i; break; }
        if (own >= 0) others.splice(own, 1);
        var n = others.length;
        if (!n) {
          txt.innerHTML = "<span>You're the first to finish today's puzzle. Check back later to see how you stack up.</span>";
          return;
        }
        var beat = others.filter(function (o) { return worse(o, mine); }).length;
        var pct = Math.round(100 * beat / n);
        var line = mine[0] < 0
          ? "Tough one. " + (n === 1 ? "1 other player" : n + " other players") + " have finished today's puzzle."
          : "You did better than <b>" + pct + "%</b> of today's players.";
        txt.innerHTML = '<span class="txt">' + line + '</span>' +
          (mine[0] >= 0 ? '<div class="bar" role="img" aria-label="' + pct + ' percent"><i style="width:' + pct + '%"></i></div>' : "") +
          '<span class="note">Compared with ' + (n === 1 ? "1 other player" : n + " other players") + " on puzzle #" + t.id + ". Fewer strokes wins, then the faster time" + (mine[0] >= 0 ? " (yours: " + fmt(mine[1]) + ")" : "") + ".</span>";
      }).catch(function () { txt.hidden = true; });
    }, 1500);
  }

  function update() { if (!result.hidden) { fillMore(); fillRank(); } }
  new MutationObserver(update).observe(result, { attributes: true, attributeFilter: ["hidden"] });
  update();
})();
