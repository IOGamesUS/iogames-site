/**
 * IO Games puzzle counter.
 * Records anonymous completions (date, game, puzzle number, result, score, seconds) and
 * moves each game to its next puzzle overnight, but only if the current puzzle was played.
 * Also answers "how did everyone else do on this puzzle" so players can see their percentile.
 * No names, emails, IP addresses or cookies are stored.
 */

// Number of puzzles in each game's queue. Update these when new puzzles are added to the site.
var GAMES = { wordtangle: 39, pemdash: 32, meld: 32, crazypath: 32, pokerrows: 32 };
var TZ = 'America/New_York';

// Run once from the editor: creates the sheets, sets each game to puzzle 1 and adds the nightly trigger.
function setup() {
  var ss = SpreadsheetApp.getActive();
  if (!ss.getSheetByName('Plays')) ss.insertSheet('Plays').appendRow(['Date', 'Game', 'Puzzle', 'Result', 'Score', 'Seconds']);
  if (!ss.getSheetByName('Log')) ss.insertSheet('Log').appendRow(['Date', 'Game', 'Puzzle', 'Plays', 'Action']);
  var props = PropertiesService.getScriptProperties();
  Object.keys(GAMES).forEach(function (g) {
    if (!props.getProperty(g + ':current')) props.setProperty(g + ':current', '1');
  });
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'advance') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('advance').timeBased().everyDays(1).atHour(0).nearMinute(5).inTimezone(TZ).create();
}

function validGame(g) { return Object.prototype.hasOwnProperty.call(GAMES, g); }
function validPuzzle(g, n) { return n >= 1 && n <= GAMES[g] && n % 1 === 0; }

// The games read today's puzzle numbers from here.
// With ?game=<name>&puzzle=<n> it also returns every finished result for that puzzle as [score, seconds],
// with score -1 for a puzzle the player ran out of checks on.
function doGet(e) {
  var props = PropertiesService.getScriptProperties();
  var out = {};
  Object.keys(GAMES).forEach(function (g) {
    out[g] = { current: Number(props.getProperty(g + ':current') || 1), total: GAMES[g] };
  });
  var p = (e && e.parameter) || {};
  var game = String(p.game || ''), puzzle = Number(p.puzzle);
  if (validGame(game) && validPuzzle(game, puzzle)) {
    var key = 'dist:' + game + ':' + puzzle;
    var cache = CacheService.getScriptCache();
    var hit = cache.get(key);
    var dist;
    if (hit) {
      dist = JSON.parse(hit);
    } else {
      dist = SpreadsheetApp.getActive().getSheetByName('Plays').getDataRange().getValues().slice(1)
        .filter(function (r) { return r[1] === game && Number(r[2]) === puzzle; })
        .map(function (r) { return [r[3] === 'solved' ? Number(r[4]) : -1, Number(r[5]) || 0]; });
      cache.put(key, JSON.stringify(dist), 30);
    }
    out.results = { game: game, puzzle: puzzle, dist: dist };
  }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

// The games send one message per finished puzzle per device.
function doPost(e) {
  var body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return done(); }
  var game = String(body.game || '');
  var puzzle = Number(body.puzzle);
  if (!validGame(game) || !validPuzzle(game, puzzle)) return done();
  var result = body.result === 'solved' ? 'solved' : 'failed';
  var score = typeof body.score === 'number' && body.score >= 0 && body.score < 100 ? body.score : '';
  var secs = typeof body.secs === 'number' && body.secs >= 0 && body.secs < 86400 ? Math.round(body.secs) : '';
  var day = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    SpreadsheetApp.getActive().getSheetByName('Plays').appendRow([day, game, puzzle, result, score, secs]);
  } finally {
    lock.releaseLock();
  }
  CacheService.getScriptCache().remove('dist:' + game + ':' + puzzle);
  return done();
}

function done() {
  return ContentService.createTextOutput('ok');
}

// Runs every night just after midnight Eastern.
function advance() {
  var ss = SpreadsheetApp.getActive();
  var rows = ss.getSheetByName('Plays').getDataRange().getValues().slice(1);
  var log = ss.getSheetByName('Log');
  var props = PropertiesService.getScriptProperties();
  var day = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
  Object.keys(GAMES).forEach(function (g) {
    var cur = Number(props.getProperty(g + ':current') || 1);
    var plays = rows.filter(function (r) { return r[1] === g && Number(r[2]) === cur; }).length;
    var action = 'kept';
    if (plays > 0 && cur < GAMES[g]) { props.setProperty(g + ':current', String(cur + 1)); action = 'advanced'; }
    else if (plays > 0) { action = 'queue empty, kept'; }
    log.appendRow([day, g, cur, plays, action]);
  });
}
