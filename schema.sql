drop table if exists books;
create table books (
  id integer primary key autoincrement,
  title text not null,
  author text not null
);
drop table if exists keywords;
create table keywords (
  id integer primary key autoincrement,
  book_id integer not null,
  keyword text not null
);