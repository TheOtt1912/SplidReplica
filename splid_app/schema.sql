DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS usersInTrip;
DROP TABLE IF EXISTS debts;

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL 
)STRICT;

CREATE TABLE trips(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_name TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL ,
    FOREIGN KEY (creator_id) REFERENCES users(id)
)STRICT;

CREATE TABLE usersInTrip(
    user_id INTEGER NOT NULL,
    trip_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (trip_id) REFERENCES trips(id),
    PRIMARY KEY (user_id, trip_id)
)STRICT;

CREATE TABLE transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    title TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    trip_id INTEGER NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (trip_id) REFERENCES trips(id)
)STRICT;

CREATE TABLE debts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    owed_by_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT CHECK(status IN ('owing','paid')) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (owed_by_id) REFERENCES users(id)

)STRICT;