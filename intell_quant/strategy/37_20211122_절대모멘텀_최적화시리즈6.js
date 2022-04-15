var basket1, basket2, basket3, basket4; // 주식 종목들을 관리하는 Basket 객체
var account1, account2, account3, account4;
var stock_num = 20;             // 주식 종목 수
var stock_weight = 0.3;       // 자산배분시 주식 비중 
var valueRatio = 0.2;           // 저평가된 상위 20%만 취한다 
var isFirst = true;             // 시뮬레이션 시작일에 바로 포트폴리오 신규 구성을 하기 위해 사용될 상태 변수
var valueWeightRatio1 = 0.5;    // 가치가중 100%
var powerNumber = 1;            // 숫자를 높게주면 가치가중 효과를 증폭시킴. 기본값 1
var preMomentumScore = 0;
var MonthCount = 12;             //모멘텀 개월수. 12로 주면 12개의 모멘텀을 측정하여 점수를 주식비중을 결정한다.
var rsiPeriod = 10;             //기술적 지표 RSI의 기간 설정. 대체로 사용되는 값은 9일, 14~15일, 25~28일 등이다.(위키백과)
//초기화 함수 
function initialize() {
    account1 = IQAccount.getDefaultAccount();
    account1.accountName = "1. 자산배분";
    basket1 = new Basket(account1, stock_num, IQEnvironment.aum * stock_weight);
    account2 = IQAccount.addAccount('0000-0000-02', '2. 모멘텀 스코어', IQEnvironment.aum);
    basket2 = new Basket(account2, stock_num, IQEnvironment.aum * stock_weight);
    account3 = IQAccount.addAccount('0000-0000-03', '3. 가속모멘텀 스코어', IQEnvironment.aum);
    basket3 = new Basket(account3, stock_num, IQEnvironment.aum * stock_weight);
    account4 = IQAccount.addAccount('0000-0000-04', '4. 절대모멘텀', IQEnvironment.aum);
    basket4 = new Basket(account4, stock_num, IQEnvironment.aum * stock_weight);
    IQDate.addRebalSchedule(IQDate.setMonthlyStart(1));
}
//number형에서 null을 0으로 고침
function nvl(value) {
    if (value === null || isNaN(value)) { return 0; }
    return value;
};
function cap(stock) { return stock.getMarketCapital() * 1000; }
// PBR역 구하기
function bp(stock) {
    return (stock.getFundamentalTotalEquity()) / cap(stock);
}
// PCR역 구하기
function cp(stock) {
    return (stock.getFundamentalOperatingCashFlow()) / cap(stock);
}
// PSR역 구하기
function sp(stock) {
    return (stock.getFundamentalRevenue()) / cap(stock);
}
// PER역 구하기
function ep(stock) {
    return (stock.getFundamentalNetProfit()) / cap(stock);
}
// POR역 구하기
function op(stock) {
    return (stock.getFundamentalOperatingIncome()) / cap(stock);
}
// 영업이익증가액/시가총액
function pir(stock) {
    stock.loadPrevData(1, 4, 0);
    var oIncome0 = stock.getFundamentalOperatingIncome();
    var oIncome4 = stock.getFundamentalOperatingIncome(4);
    if (oIncome0 <= 0 || oIncome4 < 0) { return -99999999999999; }
    var vreturn = (oIncome0 - oIncome4) / cap(stock);
    return vreturn
}
//EV/EBIT 역 구하기
function eveb(stock) {
    if (stock.getFundamentalEV() <= 0) { return -99999999999999; }
    return (stock.getFundamentalEBIT()) / stock.getFundamentalEV();
}
// PGR 구하기 : (매출액 - 매출원가)/시총 
function gp(stock) {
    var Revenue = stock.getFundamentalRevenue();          //매출액
    var SalesCost = nvl(stock.getFundamentalSalesCost()); //매출원가
    if (SalesCost === 0) { return 0; }
    if (Revenue === 0) { return -99999999999999; }
    return ((Revenue - SalesCost) * 4) / cap(stock);
}
// GPA 구하기 : 매출총이익/자산총계 
function gpa(stock) {
    var Revenue = stock.getFundamentalRevenue();          //매출액
    var SalesCost = nvl(stock.getFundamentalSalesCost()); //매출원가
    if (SalesCost === 0) { return 0; }
    if (Revenue === 0) { return -99999999999999; }
    return ((Revenue - SalesCost) * 4) / stock.getFundamentalTotalAsset();
}
function roa(stock) {
    return stock.getROA();
}
// 배열 합계 구하기 함수
function sum(array) {
    var result = 0.0;
    for (var i = 0; i < array.length; i++) {
        result = result + array[i];
    }
    return result; //null 처리
}
function bnd(stock) {            //볼린저밴드 폭
    stock.loadPrevData(1, 4, 0);
    var retValue = ((stock.getBollingerBand(240, 1, 1).upper / stock.getBollingerBand(240, 1, 1).lower) * 100);
    if (retValue === Infinity || isNaN(retValue)) {
        logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
        return -99999999;
    }
    return retValue;
}
function rsi(stock) {
    stock.loadPrevData(0, 4, 0);
    return stock.getRSI(rsiPeriod);
}
//한달거래금액의 중간값(median) 구하기 Monthly Median Transaction Amount
function MMTA(stock) {
    var arrayMMTA = [];
    stock.loadPrevData(0, 4, 0);
    for (var i = 0; i < 21; i++) {
        arrayMMTA[i] = stock.getTradingValue(i);
    }
    arrayMMTA.sort(function (a, b) { return a - b; }); // 오름차순    
    return arrayMMTA[10];
}
function TradingValueFilter(stock) {
    var FilterPass_yn = 'Y'
    var thisYear = IQIndex.getIndex("001").getDate(0).getFullYear();
    var mata = MMTA(stock);
    if (thisYear >= 2015 && thisYear < 2016 && mata < 64.03) { FilterPass_yn = 'N'; }
    else if (thisYear >= 2016 && thisYear < 2017 && mata < 68.85) { FilterPass_yn = 'N'; }
    else if (thisYear >= 2017 && thisYear < 2018 && mata < 74.04) { FilterPass_yn = 'N'; }
    else if (thisYear >= 2018 && thisYear < 2019 && mata < 79.62) { FilterPass_yn = 'N'; }
    else if (thisYear >= 2019 && thisYear < 2020 && mata < 85.62) { FilterPass_yn = 'N'; }
    else if (thisYear >= 2020 && thisYear < 2021 && mata < 92.07) { FilterPass_yn = 'N'; }
    else if (thisYear >= 2021 && mata < 99) { FilterPass_yn = 'N'; }
    return FilterPass_yn;
}
//자산배분 ETF 매수하기
function basketEnter(basket, account, code, ratio) {
    var sse = IQStock.getStock(code);
    if (sse !== null) {
        var bond_amt = account.getTotalEquity() * ratio
        var BO_quantity = Math.floor(bond_amt / sse.getAdjClose());  //수량 (종목당 예산 / 수정종가)
        basket.enter(sse, BO_quantity);
    }
}
// 3) 필터링 함수 정의 - 필터링 조건에 따라 종목들의 포함 여부 판단
function stockFilter(stock) {
    if (stock.getMarketCapital() === 0 || stock.getClose() === 0 || stock.getTradingValue() === 0) { return false; } //시총 없는 종목 제외, 종가가 0인 종목 제외, 거래정지 중인 종목 제외   
    if (stock.getFundamentalTotalAsset() === 0 || stock.getFundamentalTotalEquity() === 0) { return false; }      // ETF, 우선주 제외(자산총계가 없음)
    if (stock.manage > 0) { return false; }                           // 관리종목, 투자유의종목 제외

    if (stock.getFundamentalCapitalStock() > stock.getFundamentalTotalEquity()) { return false; } //자본잠식 제외      
    return true;
}
function port_Value(universe, stock_number) {
    var UniverseFilter = universe.slice().filter(function (stock) {
        if (TradingValueFilter(stock) === 'N') { return false; }
        return true;
    });
    var sortedBybp = UniverseFilter.slice().sort(function (a, b) { return bp(b) - bp(a); });
    var sortedByeveb = UniverseFilter.slice().sort(function (a, b) { return eveb(b) - eveb(a); });
    var sortedBygpa = UniverseFilter.slice().sort(function (a, b) { return gpa(b) - gpa(a); });

    UniverseFilter.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedBybp.indexOf(stock)
            + sortedByeveb.indexOf(stock)
            + sortedBygpa.indexOf(stock)
        );
    });

    var Port_Rank = UniverseFilter.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });

    var port_cut = Port_Rank.slice(0, Math.floor(Port_Rank.length * valueRatio));
    var sortedByCap = port_cut.slice().sort(function (a, b) { return cap(a) - cap(b); });

    return sortedByCap.slice(0, stock_number);
}
//동일비중 투자는 stockWeight 0으로 설정하고, 0보다 크면 가치가중으로 매수함 
function Port_Control(basket, account, universe, stockWeight, value_weight, pcrRatio, psrRatio, perRatio, porRatio, pirRatio, bndRatio, rsiRatio) {
    var TOT_PSR_SCORE, TOT_PCR_SCORE, TOT_PER_SCORE, TOT_POR_SCORE, TOT_PIR_SCORE, TOT_BND_SCORE, TOT_RSI_SCORE;
    var PCR_SCORE = [];
    var PSR_SCORE = [];
    var PER_SCORE = [];
    var POR_SCORE = [];
    var PIR_SCORE = [];
    var BND_SCORE = [];
    var RSI_SCORE = [];
    var i = -1;
    universe.forEach(function (stock) {
        var vsp = sp(stock);
        if (vsp <= 0) { vsp = 0; }
        PSR_SCORE[PSR_SCORE.length] = Math.pow(vsp, powerNumber);

        var vcp = cp(stock);
        if (vcp <= 0) { vcp = 0; }
        PCR_SCORE[PCR_SCORE.length] = Math.pow(vcp, powerNumber);

        var vep = ep(stock);
        if (vep <= 0) { vep = 0; }
        PER_SCORE[PER_SCORE.length] = Math.pow(vep, powerNumber);

        var vop = op(stock);
        if (vop <= 0) { vop = 0; }
        POR_SCORE[POR_SCORE.length] = Math.pow(vop, powerNumber);

        var vpir = pir(stock);
        if (vpir <= 0) { vpir = 0; }
        PIR_SCORE[PIR_SCORE.length] = Math.pow(vpir, powerNumber);

        var vbnd = 1 / bnd(stock);
        if (vbnd <= 0) { vbnd = 0; }
        BND_SCORE[BND_SCORE.length] = Math.pow(vbnd, powerNumber);

        var vrsi = 100 - rsi(stock);
        if (vrsi > 100) { vrsi = 0; }
        RSI_SCORE[RSI_SCORE.length] = Math.pow(vrsi, powerNumber);
    });

    var TotalEquity = account.getTotalEquity();
    var port_Budget = TotalEquity * stockWeight;                     //전체금액중 주식에 투자할 금액
    var stock_Budget = (TotalEquity * stockWeight) / universe.length; //동일 비중시 종목당 예산

    TOT_PCR_SCORE = sum(PCR_SCORE);
    TOT_PSR_SCORE = sum(PSR_SCORE);
    TOT_PER_SCORE = sum(PER_SCORE);
    TOT_POR_SCORE = sum(POR_SCORE);
    TOT_PIR_SCORE = sum(PIR_SCORE);
    TOT_BND_SCORE = sum(BND_SCORE);
    TOT_RSI_SCORE = sum(RSI_SCORE);
    if (TOT_PCR_SCORE === 0) { pcrRatio = 0; TOT_PCR_SCORE = 1; } //2003년 6월 이전은 PCR 이 없음으로 가치가중에서 제거한다.
    if (TOT_BND_SCORE === 0) { bndRatio = 0; TOT_BND_SCORE = 1; } //2001년 2월 이전은 1년 볼린저밴드 스코어가 없음으로 가치가중에서 제거한다.

    basket.reset();
    i = -1;
    universe.forEach(function (stock) {
        i = i + 1;
        var total_stock_budget = port_Budget * (
            ((PSR_SCORE[i] / TOT_PSR_SCORE) * psrRatio +
                (PCR_SCORE[i] / TOT_PCR_SCORE) * pcrRatio +
                (PER_SCORE[i] / TOT_PER_SCORE) * perRatio +
                (POR_SCORE[i] / TOT_POR_SCORE) * porRatio +
                (PIR_SCORE[i] / TOT_PIR_SCORE) * pirRatio +
                (BND_SCORE[i] / TOT_BND_SCORE) * bndRatio +
                (RSI_SCORE[i] / TOT_RSI_SCORE) * rsiRatio
            ) / (pcrRatio + psrRatio + perRatio + porRatio + pirRatio + bndRatio + rsiRatio)
        );

        var quantity;
        var same_weight_ratio = 1 - value_weight
        if (value_weight === 0) { quantity = Math.floor(stock_Budget / stock.getAdjClose()); } //동일비중 수량 (종목당 예산 / 수정종가)       
        else { quantity = Math.floor((total_stock_budget * value_weight + (port_Budget * same_weight_ratio) / universe.length) / stock.getAdjClose()); }  //수량 (종목당 예산 / 수정종가)
        basket.enter(stock, quantity);
        var stock_ratio = ((quantity * stock.getAdjClose()) / TotalEquity) * 100;
        if (stock_ratio > 10) { logger.info('단일 종목의 비중이 10%를 넘음. 비중: ' + stock_ratio.toPrecision(4) + '%' + ' , 종목수: ' + universe.length + ' , 전략명: ' + account.accountName) }

    });
    AssetAllocation(basket, account, stockWeight);
}
// 주식을 매수하고 남은 비중으로 자산배분(자산배분은 2011년 3월 부터 가능)
function AssetAllocation(basket, account, stockWeight) {

    if (stockWeight < 0.95) {
        var gold_ratio = (1 - stockWeight) * 0.15;                            //골드 비중 : (1 - 주식비중) * 15%. ex) 주식비중 30% 인 경우 대략 15% 
        var bond_ratio = (1 - stockWeight) - gold_ratio - 0.02;//채권 비중 : 1 -  주식비중 - 골드비중. 2% 는 현금 

        var US10Y_Tresaury = IQStock.getStock('A305080'); //TIGER 미국채10년선물 305080 2018년 08월 30일
        var KR10Y_Tresaury = IQStock.getStock('A148070'); //KOSEF 국고채10년 148070 2011년 10월 20일
        var USD = IQStock.getStock('A138230'); //KOSEF 미국달러선물 138230 2011년 02월
        var KR_GOLD = IQStock.getStock('A132030'); //KODEX 골드선물(H) 2010년 10월 01일     
        var KR3Y_Tresaury = IQStock.getStock('A114100'); //KBSTAR 국고채3년 114100 2009년 07월 29일

        if (KR3Y_Tresaury == null) {
            logger.debug("자산 배분을 수행할 수 없습니다. 투자 기간을 2009년 8월 이후로 조정하세요.");
            gold_ratio = 0;
        }
        else if (KR3Y_Tresaury.getClose() > 0 && KR_GOLD == null) {
            basketEnter(basket, account, 'A114100', bond_ratio + gold_ratio); //KBSTAR 국고채3년
            var BondPct = (bond_ratio + gold_ratio) * 100;
            logger.debug('전략명: ' + account.accountName + " , 자산 비중: KBSTAR 국고채3년 " + assetRatio.toPrecision(5) + '%');
            gold_ratio = 0;
        }
        else if (KR_GOLD.getClose() > 0 && USD == null) {
            basketEnter(basket, account, 'A114100', bond_ratio);             //KBSTAR 국고채3년 
            var BondPct = bond_ratio * 100;
            var GoldPct = gold_ratio * 100;
            logger.debug('전략명: ' + account.accountName + " , 자산 비중: 국고채3년 " + BondPct.toPrecision(4) + '% , ' + ' Gold선물 ' + GoldPct + '%');
        }
        else if (USD.getClose() > 0 && KR10Y_Tresaury == null) {
            basketEnter(basket, account, 'A138230', bond_ratio * 0.5);        //KOSEF 미국달러선물  
            basketEnter(basket, account, 'A114100', bond_ratio * 0.5);        //KBSTAR 국고채3년
            var BondPct = bond_ratio * 0.5 * 100;
            var GoldPct = gold_ratio * 100;
            logger.debug('전략명: ' + account.accountName + " , 자산 비중: 국고채3년 " + BondPct.toPrecision(4) + '% , ' + '달러선물 ' + BondPct.toPrecision(4) + '% , ' + ' Gold선물 ' + GoldPct.toPrecision(4) + '%');
        }
        else if (KR10Y_Tresaury.getClose() > 0 && US10Y_Tresaury == null) {
            basketEnter(basket, account, 'A148070', bond_ratio * 0.5);        //KOSEF 국고채10년 
            basketEnter(basket, account, 'A138230', bond_ratio * 0.5);        //KOSEF 미국달러선물 
            var BondPct = bond_ratio * 0.5 * 100;
            var GoldPct = gold_ratio * 100;
            logger.debug('전략명: ' + account.accountName + " , 자산 비중: 국고채10년 " + BondPct.toPrecision(4) + '% , ' + '달러선물 ' + BondPct.toPrecision(4) + '% , ' + ' Gold선물 ' + GoldPct.toPrecision(4) + '%');
        }
        else if (US10Y_Tresaury.getClose() > 0) {
            basketEnter(basket, account, 'A305080', bond_ratio);           //TIGER 미국채10년선물 
            var BondPct = bond_ratio * 100;
            var GoldPct = gold_ratio * 100;
            logger.debug('전략명: ' + account.accountName + " , 자산 비중: 미국채10년선물 " + BondPct.toPrecision(4) + '% , ' + ' Gold선물 ' + GoldPct.toPrecision(4) + '%');
        }

        if (gold_ratio > 0) {
            basketEnter(basket, account, 'A132030', gold_ratio);             //KODEX 골드선물(H)               
        }
    }
}
/////////////////////////////////////////////////////////////////////
//                        시장 절대모멘텀                           //
////////////////////////////////////////////////////////////////////
function AbsoluteMomentum(IndexCode) {
    /*IndexCode
    001 : KOSPI
    101 : KOSPI 200
    002 : KOSPI 대형주
    003 : KOSPI 중형주
    004 : KOSPI 소형주
    301 : KOSDAQ */

    var Kindex = IQIndex.getIndex(IndexCode);  //001 
    Kindex.loadPrevData(0, 16, 0);
    var current_price = Kindex.getClose();
    var PRICE_252 = Kindex.getClose(252);     //1년전 주가        
    var PRICE_42 = Kindex.getClose(42);      //두달전 주가        
    var MomentmRatio = 0.95 // 주식비중
    if (current_price < PRICE_252 && (current_price < PRICE_42))  //절대모멘텀(1년)이 적용되고 최근 2개월 모멘텀도 음수일때 
    {
        var KR3Y_Tresaury = IQStock.getStock('A114100'); //KBSTAR 국고채3년 114100 2009년 07월 29일            
        if (KR3Y_Tresaury == null) { MomentmRatio = 0; } else { MomentmRatio = 0.3; }
        logger.debug('절대모멘텀 적용. 주식비중 : ' + MomentmRatio * 100 + '%');
    }
    return MomentmRatio;
}
// 모멘텀 스코어로 주식비중을 결정한다.
function MomentumRatio(MomScore, totalMonth, accelMom_yn) {
    var StockRatio;
    if (accelMom_yn === 'Y' && MomScore > preMomentumScore) { StockRatio = (MomScore + (MomScore - preMomentumScore)) / totalMonth; } //전월에 비해 모멘텀 스코어가 커졌으면 1점 추가
    else { StockRatio = MomScore / totalMonth; }
    if (StockRatio >= 1) { StockRatio = 0.98; }
    if (StockRatio < 0) { StockRatio = 0; }
    return StockRatio;
}
function MomScore(MonthCount) {
    var Kospi = IQIndex.getIndex('001');  //001 : KOSPI
    var current_price = Kospi.getClose();
    var Kospi_Momenum = [];
    Kospi.loadPrevData(0, 16, 0);
    for (var i = 1; i <= MonthCount; i++) {  //12개월 모멘텀 측정        
        if (current_price > Kospi.getClose(i * 21)) { Kospi_Momenum[i - 1] = 1; }
        else { Kospi_Momenum[i - 1] = 0; }
    }
    return sum(Kospi_Momenum);
}
// 리밸런싱 수행 
function onDayClose(now) {
    if (IQDate.isRebalancingDay(now) || isFirst === true) {
        var universe = IQStock.filter(stockFilter);
        var port_value = port_Value(universe, stock_num);
        var MomentumScore = MomScore(MonthCount);  //MonthCount 만큼의 개월의 모멘텀을 측정한 점수

        var MomentumWeight = MomentumRatio(MomentumScore, MonthCount, 'N'); //모멘텀 스코어로 주식비중을 결정한다.
        var AccelMomWeight = MomentumRatio(MomentumScore, MonthCount, 'Y'); //모멘텀 스코어에 가속 모멘텀을 적용(Acceleration Momentum)
        var AbsoluteWeight = AbsoluteMomentum('004') //kospi 소형주 절대모멘텀

        //주식비중,      가치가중비율,   pcrRatio, psrRatio, perRatio, porRatio, pirRatio, bndRatio, rsiRatio
        Port_Control(basket1, account1, port_value, stock_weight, 1, 1, 1, 1, 1, 1, 1, 1);
        Port_Control(basket2, account2, port_value, MomentumWeight, valueWeightRatio1, 1, 1, 1, 1, 1, 1, 1);
        Port_Control(basket3, account3, port_value, AccelMomWeight, valueWeightRatio1, 1, 1, 1, 1, 1, 1, 1);
        Port_Control(basket4, account4, port_value, AbsoluteWeight, valueWeightRatio1, 1, 1, 1, 1, 1, 1, 1);

        isFirst = false;
        preMomentumScore = MomentumScore;
    }
}
// 시뮬레이션 종료 함수
function onComplete() {
    logger.debug("계좌 총 평가금액은 " + IQUtil.getNumberWithCommas(Math.floor(account4.getTotalEquity())) + " 입니다.");
    //    IQLive.addPortfolio(stock_basket, stock_weight);
}