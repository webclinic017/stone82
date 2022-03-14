# 데이터 베이스 

## 간단한 SQL 문법 및 도커 접근

|cmd|내용
|------|---|
|CREATE DATABASE [DB name];|데이터 베이스 생성|
|SHOW DATABASES;|데이터 베이스 출력|
|USE [DB name];|데이터 베이스 선택|
|DROP DATABASE [DB name];|[!] 데이터 베이스 삭제|
|SHOW TABLES;|데이터 베이스 Field 출력|
|SELECT * [DB Field name] (key1, key2); |데이터 베이스내에 데이터 접근|
|테스트1|테스트2|
```
docker exec -it db bash
mysql -u root -p
Enter password: 
# 비밀번호는 'MYSQL_ROOT_PASSWORD' 에 있음 ( export | grep 'MYSQL_ROOT_PASSWORD' 도커 내부에서 실행)
MariaDB[(none)]> # command 입력 (위에 표 참고)

```