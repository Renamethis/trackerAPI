CREATE DATABASE IF NOT EXISTS trackers;
use trackers;
CREATE TABLE IF NOT EXISTS trackers(room varchar(40) not null primary key,
ip varchar(40) not null,
port int not null);