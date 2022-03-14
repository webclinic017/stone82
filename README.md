# 돌팔이 프로젝트


## 참고사항
[서버개발노트 - Terminal 관련](https://github.com/coolseaweed/NOTE-server/tree/master/Terminal)

[서버개발노트 - Network 관련](https://github.com/coolseaweed/NOTE-server/tree/master/Network)

---
## Env. setup



```
git clone git@github.com:coolseaweed/stone82.git
cd stone82
docker-compose -f up -d
docker exec -it master bash # access to master container 
docker exec -it db bash # access to db container 

```

---
## DB
- 전반적인 금융데이터 저장용도
    > 기업별 일일 주식 데이터
    
    > 기업별 재무제표
- 기술적 분석 및 기본적 분석을 위한 데이터 
    > 데이터의 신뢰성이 중요
    
    > Analyzer를 통해 결측치 제거 및 개선 알고리즘 필요

- MYSQL (MariaDB) 기반
- DB 디렉토리내에 [README.md](https://github.com/coolseaweed/stone82/blob/feature/DB-finance-cralwer/DB/README.md) 참고

---
## Slack bot
- Slack API를 통해 slack-bot 과 interactive 하게 커맨드를 주고 받기 위함
```
python run.py
```

---
## Analyzer
- DB로 부터 받아온 금융데이터를 분석 및 리포트 하는 모듈
- TODO:
    - 재무제표에서 결측치(null, None) 값들 비율 및 오차범위 측정

```
FUTURE WORK
```
---
## Trader
- 자동매수 매도 프로그램을 위한 모듈
- 크레온 API를 기반으로 만듬 (`python 32bit`: ubuntu <--> window 사이에서 고민하게 되는 포인트)
- Analyzer 로 부터 분석된 데이터를 바탕으로 매수 매도 하도록 만드는 것이 목표
```
FUTURE WORK
```



---


## [!] Trouble shooting

####  git clone 관련해서 command 동작하지 않을 경우
Git hub 에서 SSH KEY 값 등록 
```
ssh-keygen

cat ~/.ssh/id_rsa.pub # copy to setting > SSH & GPG KEY > new SSH KEY
```
---