# Mysql master-slave creation flow.
1. Create 3 mysql containers: mysql-m, mysql-s1 and mysql-s2 using docker compose.
2. Create cnf files and data folders for each.
3. Add required fields to master.cnf
4. Restart containers
5. Create user in master mysql with permission or replication:
```
CREATE USER 'slave'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'slave'@'%';
FLUSH PRIVILEGES;
```
6. Create event table to which script will insert data.
```
create table mydb.event
(
    id        int auto_increment
        primary key,
    data      varchar(50) not null,
    timestamp timestamp   not null
);
```
7. Lock tables in master.
```
USE mydb;
FLUSH TABLES WITH READ LOCK;
```
8. Show master status:
```
+----------------+--------+------------+----------------+-----------------+
|File            |Position|Binlog_Do_DB|Binlog_Ignore_DB|Executed_Gtid_Set|
+----------------+--------+------------+----------------+-----------------+
|mysql-bin.000001|158     |mydb        |                |                 |
+----------------+--------+------------+----------------+-----------------+
```
9. Create dump from master DB: 
```
docker exec -it replication-mysql-m-1 bash -c "/usr/bin/mysqldump -u root -proot_password mydb > /tmp/dump.sql"

docker cp replication-mysql-m-1:/tmp/dump.sql ./dump.sql
```
10. Unlock tables:
```
UNLOCK TABLES;
```
11. Load dump.sql to both slave DBs:
```
docker cp ./dump.sql replication-mysql-s1-1:/tmp/dump.sql
docker exec -it replication-mysql-s1-1 bash -c "mysql -u myuser -pmypassword mydb < /tmp/dump.sql"

docker cp ./dump.sql replication-mysql-s2-1:/tmp/dump.sql
docker exec -it replication-mysql-s2-1 bash -c "mysql -u myuser -pmypassword mydb < /tmp/dump.sql"
```
12. Configure slave connection on both slaves:
```
CHANGE MASTER TO MASTER_HOST='mysql-m', MASTER_USER='slave', MASTER_PASSWORD='password',
    MASTER_LOG_FILE = 'mysql-bin.000001', MASTER_LOG_POS = 158;
```
13. Launch slave connections:
```
START SLAVE;
```
14. Run script for data generation and ensure that data is added to slaves too.
15. Remove columns
From middle:
```
Worker 1 failed executing transaction 'ANONYMOUS' at source log mysql-bin.000003, end_log_pos 51437; Column 1 of table 'mydb.event' cannot be converted from type 'varchar(200(bytes))' to type 'timestamp', Error_code: MY-013146
```
Last column: Replication continues!