# 데이터 베이스 

## 간단한 SQL 문법 및 도커 접근

|cmd|내용
|------|---|
|CREATE DATABASE [DB];|DB 생성|
|SHOW DATABASES;|DB 출력|
|USE [DB];|DB 선택|
|DROP DATABASE [DB];|[!] DB 삭제|
|SHOW TABLES;|TABLE 출력|
|SELECT * [column name] (key1, key2); |DB내에 데이터 접근|
|SHOW COLUMNS FROM [TABLE];| column 정보 조회|
|ALTER TABLE [TABLE] ADD [column] [data type] null;| 테이블에 column 추가|
|ALTER TABLE [TABLE] DROP COLUMN [column] ;| 테이블에 column 삭제|
```
docker exec -it db bash
mysql -u root -p
Enter password: 
# 비밀번호는 'MYSQL_ROOT_PASSWORD' 에 있음 ( export | grep 'MYSQL_ROOT_PASSWORD' 도커 내부에서 실행)
MariaDB[(none)]> # command 입력 (위에 표 참고)

```
