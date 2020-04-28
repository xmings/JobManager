# job_manager

job_manager is a simple distributed job management system based on zookeeper and redis. 

## Quick start
1. Install the lastest version of Zookeeper
2. Install the lastest version of Redis
3. Modify the code about the connection info
4. Start flask web
5. Send the GET request to web server using the following URL
  ```
    http://127.0.0.1:5000/job?job_id=1
  ```
