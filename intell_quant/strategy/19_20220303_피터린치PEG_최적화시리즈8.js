var stock_basket1, stock_basket2, stock_basket3, stock_basket4, stock_basket5; // 주식 종목들을 관리하는 Basket 객체
var account1, account2, account3, account4, account5;
var stock_num = 20;             // 주식 종목 수
var stock_weight = 0.95;        // 주식 비중 (거래비용 고려 현금 5% 확보)
var thisYear, thisMonth;
var oneYearBefore;
var valueRatio = 0.2;
//초기화 함수 
function initialize() {
    account1 = IQAccount.getDefaultAccount();
    account1.accountName = "1. 영업이익 개선율";
    stock_basket1 = new Basket(IQAccount.getDefaultAccount(), stock_num, IQEnvironment.aum * stock_weight);
    stock_basket1.setPortfolioBuilder(stockPortfolioBuilder);

    account2 = IQAccount.addAccount('0000-0000-02', '2. PER', IQEnvironment.aum);
    stock_basket2 = new Basket(account2, stock_num, IQEnvironment.aum * stock_weight);
    stock_basket2.setPortfolioBuilder(stockPortfolioBuilder1);

    account3 = IQAccount.addAccount('0000-0000-03', '3. PSR', IQEnvironment.aum);
    stock_basket3 = new Basket(account3, stock_num, IQEnvironment.aum * stock_weight);
    stock_basket3.setPortfolioBuilder(stockPortfolioBuilder2);

    account4 = IQAccount.addAccount('0000-0000-04', '4. PEG 피터린치', IQEnvironment.aum);
    stock_basket4 = new Basket(account4, stock_num, IQEnvironment.aum * stock_weight);
    stock_basket4.setPortfolioBuilder(stockPortfolioBuilder3);

    account5 = IQAccount.addAccount('0000-0000-05', '5. PEG 피터린치(소형주효과)', IQEnvironment.aum);
    stock_basket5 = new Basket(account5, stock_num, IQEnvironment.aum * stock_weight);
    stock_basket5.setPortfolioBuilder(stockPortfolioBuilder4);

    IQDate.addRebalSchedule(IQDate.setMonthlyStart(1));
}
function cap(stock) { return stock.getMarketCapital() * 1000; }
//  OperatingIncome Increasing Ratio ( 전년동기대비 영업이익증가율 )
function oir(stock) {
    stock.loadPrevData(1, 6, 0);
    var oIncome0 = stock.getFundamentalOperatingIncome();  //영업이익
    var oIncome4 = stock.getFundamentalOperatingIncome(4); //전년동기 영업이익
    if (oIncome4 <= 0) { return -99999999999999; }
    if (oIncome0 <= 0) { return -99999999999999; }
    return Math.pow(10, Math.log(oIncome0 / oIncome4)) - 1;
}
//PEG 역 구하기 : EPS 성장율/ PER (클수록 좋음)
function peg(stock) {
    stock.loadPrevData(1, 6, 0);
    if (stock.isListed(oneYearBefore)) {
        var currNetProfit = stock.getFundamentalNetProfit(0)   //현재 당기순이익 
        var beforeNetProfit = stock.getFundamentalNetProfit(4) //1년전 당기순이익
        if (currNetProfit <= 0 || beforeNetProfit <= 0) { return -99999999999999; }
        var beforeCount = stock.getNoOfShare(oneYearBefore); //1년전 상장주식수
        var currCount = stock.getNoOfShare(0);                //현재 상장주식수
        //EPS 성장율 = (현재분기 당기순이익 / 현재 주식수 - 1년전 당기순이익 / 1년전 재무데이터 발표시의 주식수)  / (1년전 당기순이익 / 1년전 재무데이터 발표시의 주식수) 
        var epsGrowth = ((currNetProfit / currCount - beforeNetProfit / beforeCount) / (beforeNetProfit / beforeCount)) * 100;
        return epsGrowth / stock.getPER();
    }
    else { return 0; } //1년전 비상장 주식은 PEG 0
}
// PER역 구하기
function ep(stock) {
    return (stock.getFundamentalNetProfit()) / cap(stock);
}
// PSR역 구하기
function sp(stock) {
    return (stock.getFundamentalRevenue()) / cap(stock);
}
// 3) 필터링 함수 정의 - 필터링 조건에 따라 종목들의 포함 여부 판단
function stockFilter(stock) {
    if (stock.getMarketCapital() === 0 || stock.getClose() === 0 || stock.getTradingValue() === 0) { return false; } //시총 없는 종목 제외, 종가가 0인 종목 제외, 거래정지 중인 종목 제외   
    if (stock.getFundamentalTotalAsset() === 0 || stock.getFundamentalTotalEquity() === 0) { return false; }      // ETF, 우선주 제외(자산총계가 없음)
    if (stock.manage > 0) { return false; }                           // 관리종목, 투자유의종목 제외

    var gfcs = stock.getFundamentalCapitalStock();
    var gfte = stock.getFundamentalTotalEquity();
    if ((gfcs > gfte && gfte > 0) || gfte <= 0) { return false; } //자본잠식 제외      
    return true;
}

function stockPortfolioBuilder(targetSize) {
    var universe = IQStock.filter(stockFilter);
    var sortedByoir = universe.slice().sort(function (a, b) { return oir(b) - oir(a); });

    universe.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedByoir.indexOf(stock)
        );
    });

    var Port_Rank = universe.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    return Port_Rank.slice(0, stock_num);
}

function stockPortfolioBuilder1(targetSize) {
    var universe = IQStock.filter(stockFilter);
    var sortedByep = universe.slice().sort(function (a, b) { return ep(b) - ep(a); });

    universe.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedByep.indexOf(stock)
        );
    });

    var Port_Rank = universe.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    return Port_Rank.slice(0, stock_num);
}
function stockPortfolioBuilder2(targetSize) {
    var universe = IQStock.filter(stockFilter);
    var sortedBysp = universe.slice().sort(function (a, b) { return sp(b) - sp(a); });

    universe.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedBysp.indexOf(stock)
        );
    });

    var Port_Rank = universe.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    return Port_Rank.slice(0, stock_num);
}
function stockPortfolioBuilder3(targetSize) {
    var universe = IQStock.filter(stockFilter);
    var sortedBypeg = universe.slice().sort(function (a, b) { return peg(b) - peg(a); });

    universe.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedBypeg.indexOf(stock)
        );
    });

    var Port_Rank = universe.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    return Port_Rank.slice(0, stock_num);
}
function stockPortfolioBuilder4(targetSize) {
    var universe = IQStock.filter(stockFilter);
    var sortedBypeg = universe.slice().sort(function (a, b) { return peg(b) - peg(a); });

    universe.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedBypeg.indexOf(stock)
        );
    });

    var Port_Rank = universe.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    var port_cut = Port_Rank.slice(0, Math.floor(Port_Rank.length * valueRatio));
    var sortedByCap = port_cut.slice().sort(function (a, b) { return cap(a) - cap(b); });

    return sortedByCap.slice(0, stock_num);
}

// 리밸런싱 수행 
function onDayClose(now) {
    if (IQDate.isRebalancingDay(now)) {
        oneYearBefore = getYoYOffset();
        stock_basket1.setBudget(account1.getTotalEquity() * stock_weight);
        stock_basket1.buildPortfolio();
        stock_basket2.setBudget(account2.getTotalEquity() * stock_weight);
        stock_basket2.buildPortfolio();
        stock_basket3.setBudget(account3.getTotalEquity() * stock_weight);
        stock_basket3.buildPortfolio();
        stock_basket4.setBudget(account4.getTotalEquity() * stock_weight);
        stock_basket4.buildPortfolio();
        stock_basket5.setBudget(account5.getTotalEquity() * stock_weight);
        stock_basket5.buildPortfolio();
    }
}
//전년동기의 재무데이터 update 일자의 Offset을 가져오는 함수
function getYoYOffset() {
    var thisYear = IQIndex.getIndex("001").getDate(0).getFullYear();
    var thisMonth = IQIndex.getIndex("001").getDate(0).getMonth() + 1;
    var YoYYear;
    var YoYDate;
    if (thisMonth >= 1 && thisMonth <= 3) {
        YoYYear = thisYear - 2;
        YoYDate = YoYYear + '-12-01';
    }
    else if (thisMonth >= 4 && thisMonth <= 5) {
        YoYYear = thisYear - 1;
        YoYDate = YoYYear + '-04-01';
    }
    else if (thisMonth >= 6 && thisMonth <= 8) {
        YoYYear = thisYear - 1;
        YoYDate = YoYYear + '-06-01';
    }
    else if (thisMonth >= 9 && thisMonth <= 11) {
        YoYYear = thisYear - 1;
        YoYDate = YoYYear + '-09-01';
    }
    else if (thisMonth === 12) {
        YoYYear = thisYear - 1;
        YoYDate = YoYYear + '-12-01';
    }
    var Offset = getWorkingDayOffset(YoYDate);
    //    logger.debug( 'YoYDate:' + YoYDate + ' , Offset:' + Offset );
    return Offset;
}

function getWorkingDayOffset(date) {
    var d = new Date(date);	// date의 형식에 따라 시간이 00:00:00 이거나 09:00:00 일 수 있음
    var dt = new Date(d.getFullYear(), d.getMonth(), d.getDate());  // 시간을 00:00:00으로 통일
    var refIndex = IQIndex.getAllIndex()[0];    // 한국에서는 kospi200, 미국에서는 ^DJI
    var now = refIndex.getDate().getTime();

    if (dt.getTime() === now) {
        return 0;
    } else if (dt.getTime() > now) {
        logger.error("Cannot look up the future values!!!");
        return -1;
    }

    var t = IQDate.getPrevWorkingDay(IQDate.getNextWorkingDay(dt)).getTime();  // most recent working day of the date
    var dayDiff = parseInt((now - t) / (24 * 3600 * 1000));

    var estWorkingDayDiff = parseInt(dayDiff / 365 * 240);	// estimated difference in working days
    if (estWorkingDayDiff > 599) {
        logger.error("Out of range !!");
        return 600;
    }
    var estDate = refIndex.getDate(estWorkingDayDiff);
    var workingDayOffset = estWorkingDayDiff;

    if (estDate.getTime() < t) {	// search forward
        var diff = parseInt((t - estDate.getTime()) / (24 * 3600 * 1000));
        var w_diff = parseInt(diff / 7) * 5 + (diff % 7);
        workingDayOffset = workingDayOffset - w_diff;

        estDate = refIndex.getDate(workingDayOffset);
    }

    if (estDate.getTime() > t) {	// search backward      
        var diff2 = parseInt((estDate.getTime() - t) / (24 * 3600 * 1000));
        var tmpDate = estDate;
        for (var i = 1; i <= diff2; i++) {
            tmpDate = IQDate.getPrevWorkingDay(tmpDate);
            if (t === tmpDate.getTime())
                break;
        }
        if (i > diff2)
            logger.error("Cannot find correct offset to the date.");
        workingDayOffset = workingDayOffset + i;

        if (workingDayOffset > 599) {
            logger.error("Out of range !!");
            return workingDayOffset;
        }
    }

    if (refIndex.getDate(workingDayOffset).getTime() !== t) {
        logger.error("Something wrong?!!!");
    }

    //    logger.info("offset = " + workingDayOffset);    
    return workingDayOffset;
}