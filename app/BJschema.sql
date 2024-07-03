CREATE TABLE IF NOT EXISTS gamestates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP WITH TIMEZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    player TEXT NOT NULL,
    money INTEGER NOT NULL,
    disableBets BOOLEAN NOT NULL,
    activeHand INTEGER NOT NULL,
    dealer TEXT NOT NULL,
    deck TEXT NOT NULL,
    over BOOLEAN NOT NULL,
    message TEXT NOT NULL
);
