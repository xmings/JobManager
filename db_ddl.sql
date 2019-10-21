drop table t_jobs;
create table t_jobs(
    job_id                int,
    job_name              varchar(100),
    job_cron               varchar(100),
    depends_job_id         int,
    start_time            timestamp,
    end_time              timestamp,
    next_time             timestamp,
    state                 varchar(10),
    valid_start_time      timestamp,
    valid_end_time        timestamp
);

drop table t_tasks;
create table t_tasks (
    task_id               int,
    job_id                int,
    task_name             varchar(10),
    task_content          text,
    task_type             varchar(10),
    when_prev_stat        varchar(10),
    next_task_id          int,
    state                 varchar(10),
    valid_start_time      timestamp,
    valid_end_time        timestamp
);

drop table t_job_logs;
create table t_job_logs (
    id                 int,
    group_id           int,
    job_id             int,
    task_id            int,
    log_time           timestamp,
    log_level          varchar(10),
    message            text,
    execute_host       varchar(10)
)