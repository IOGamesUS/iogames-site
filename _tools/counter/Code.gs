/**
 * IO Games puzzle counter.
 * Records anonymous completions (date, game, puzzle number, result, score) and
 * moves each game to its next puzzle overnight, but only if the current puzzle was played.
 * No names, emails, IP addresses or cookies are stored.
 */

// Number of puzzles in each game's queue. Update these when new puzzles are added to the site.
var GAMES = { wordtangle: 39, pemdash: 32 };
var TZ = 'America/New_York';

// Run once from the editor: creates the sheets, sets each game to puzzle 1 and adds the nightly trigger.
function setup() {
  var ss = SpreadsheetApp.getActive();
  if (!ss.getSheetByName('Plays')) ss.insertSheet('Plays').appendRow(['Date', 'Game', 'Puzzle', 'Result', 'Score']);
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

// The games read today's puzzle number from here.
function doGet() {
  var props = PropertiesService.getScriptProperties();
  var out = {};
  Object.keys(GAMES).forEach(function (g) {
    out[g] = { current: Number(props.getProperty(g + ':current') || 1), total: GAMES[g] };
  });
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

// The games send one message per finished puzzle per device.
function doPost(e) {
  var body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return done(); }
  var game = String(body.game || '');
  var puzzle = Number(body.puzzle);
  if (!GAMES.hasOwnProperty(game) || !(puzzle >= 1 && puzzle <= GAMES[game] && puzzle % 1 === 0)) return done();
  var result = body.result === 'solved' ? 'solved' : 'failed';
  var score = typeof body.score === 'number' && body.score >= 0 && body.score < 100 ? body.score : '';
  var day = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    SpreadsheetApp.getActive().getSheetByName('Plays').appendRow([day, game, puzzle, result, score]);
  } finally {
    lock.releaseLock();
  }
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
