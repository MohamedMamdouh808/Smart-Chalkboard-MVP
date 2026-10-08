-- Smart Chalkboard persistence schema (SQLite, WAL, transactional writes).
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version     INTEGER PRIMARY KEY,
  applied_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
  id            TEXT PRIMARY KEY,
  title         TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  updated_at    TEXT NOT NULL,
  last_saved_at TEXT,
  deleted_at    TEXT
);

CREATE TABLE IF NOT EXISTS board_states (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lesson_id   TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  state_json  TEXT NOT NULL,
  save_type   TEXT NOT NULL CHECK (save_type IN ('auto','manual')),
  saved_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS command_history (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  lesson_id     TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  seq           INTEGER NOT NULL,
  command_json  TEXT NOT NULL,
  inverse_json  TEXT,
  source        TEXT NOT NULL CHECK (source IN ('voice','pen','ui')),
  status        TEXT NOT NULL CHECK (status IN ('applied','undone')),
  executed_at   TEXT NOT NULL,
  UNIQUE (lesson_id, seq)
);

CREATE TABLE IF NOT EXISTS metrics_events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lesson_id   TEXT,
  event_type  TEXT NOT NULL,
  value_ms    INTEGER,
  detail_json TEXT,
  created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_board_states_lesson ON board_states(lesson_id, saved_at);
CREATE INDEX IF NOT EXISTS idx_history_lesson_seq ON command_history(lesson_id, seq);
