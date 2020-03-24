drop table t_jobs;
create table t_jobs(
    job_id                int,
    job_name              varchar(100),
    job_schedule          varchar(100),
    last_running_time     timestamp(6),
    last_running_state    varchar(100),
    next_time             timestamp(6),
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
    exec_condition_id     int,
    prev_task_ids         varchar(100),
    valid_start_time      timestamp,
    valid_end_time        timestamp
);

drop table t_job_logs;
create table t_job_logs (
    id                    int,
    group_id              int,
    job_id                int,
    task_id               int,
    log_time              timestamp,
    log_level             varchar(10),
    message               text,
    execute_host          varchar(10)
);