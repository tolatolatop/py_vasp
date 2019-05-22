DROP TABLE IF EXISTS test;

CREATE TABLE structures(
    id          integer primary key autoincrement,
    x1          real                not null,
    x2          real                not null,
    x3          real                not null,
    y1          real                not null,
    y2          real                not null,
    y3          real                not null,
    z1          real                not null,
    z2          real                not null,
    z3          real                not null,
    spacegroup  int                 not null,
    formula     text                not null,
    prettyformula   text            not null,
    Nsite       integer             not null check(Nsite > 0),
    Nelement    integer             not null check(Nelement > 0)
);

CREATE TABLE atoms(
    id          integer primary key autoincrement,
    a1          real                not null check(a1 <= 1),
    a2          real                not null check(a2 <= 1),
    a3          real                not null check(a3 <= 1),
    element     text                not null,
    sid         integer foreign key references strcutres(id) not null 
)

CREATE TABLE calculations(
    id          integer primary key autoincrement,
    incar       text                not null,
    kpoints     text                not null,
    sid         integer foreign key references strcutres(id) not null,   
    type        text                not null,
    energy      real                not null,
    energy_pa   real                not null,
    encut       real                not null,
    prec        text                not null,
    ediff       real                not null,
    ediffg      real                not null,
    band_spin1  BLOB                default null,
    band_spin2  BLOB                default null,

    dos         BLOB                default null,
    bandgap     real                default 0 check(bandgap >= 0)
)

CREATE TABLE potcar(
    id          integer primary key autoincrement,
    potcar      BLOB                not null
)

CREATE TABLE potcartocalc(
    id          integer primary key autoincrement,
    cid         foreign key references calculations(id) not null,
    pid         foreign key references potcar(id) not null 
)