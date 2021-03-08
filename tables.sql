
--TODO: set userid, jobid as primary key
DROP TABLE IF EXISTS users;
CREATE TABLE users(
    userid varchar(16),
    password varchar(64),
    email varchar(64),
    first_name varchar(32),
    last_name varchar(32)
);

DROP TABLE IF EXISTS jobs;
CREATE TABLE jobs(
    jobid varchar(32),
    userid varchar(16),
    job_type varchar(16),
    interval int,
    start_time int,
    end_time int,
    max_num int,
    params varchar(1024)
);
