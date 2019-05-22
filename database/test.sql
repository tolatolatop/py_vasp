DROP TABLE IF EXISTS test;

CREATE TABLE test(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME              TEXT NOT NULL,
    AGE                INT NOT NULL,
    ADDRESS       CHAR(50),
    SALARY            REAL DEFAULT 5000.0 CHECK(SALARY > 0),
    PSSKEY             INT UNIQUE,
    FILE              BLOB
);

insert into test values (Null, 'Alice', 17, '2434', 23.0,12,Null);
'select id,name,address from test;
