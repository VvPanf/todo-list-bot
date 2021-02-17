create table if not exists users (
	id serial not null primary key,
    user_id integer not null,
    state integer not null,
    language_code varchar(10) not null
);

create index if not exists users_id_index on users(id);

create table  if not exists lists (
	id serial not null primary key,
    name varchar(255) not null,
    users_id integer not null,
    foreign key (users_id) references users (id) on delete cascade
);

create index if not exists lists_id_index on lists(id);

create table if not exists item (
	id serial not null primary key,
    content varchar(255) not null,
    checked boolean not null,
    lists_id integer not null,
    foreign key (lists_id) references lists (id) on delete cascade
);

create index if not exists item_id_index on item(id);

