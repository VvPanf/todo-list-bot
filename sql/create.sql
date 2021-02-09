create table users (
	id integer not null primary key auto_increment,
    user_id integer not null,
    state integer not null,
    language_code varchar(10) not null
);

create index users_id_index on users(id);

create table lists (
	id integer not null primary key auto_increment,
    name varchar(255) not null,
    users_id integer not null,
    foreign key (users_id) references users (id) on delete cascade
);

create index lists_id_index on lists(id);

create table item (
	id integer not null primary key auto_increment,
    content varchar(255) not null,
    checked boolean not null,
    lists_id integer not null,
    foreign key (lists_id) references lists (id) on delete cascade
);

create index item_id_index on item(id);

