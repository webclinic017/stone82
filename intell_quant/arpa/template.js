

/***********************************************/
// SET PARAMS
/***********************************************/
IQEnvironment.stockCommission = 0.0015;
IQEnvironment.etfCommission = 0.0015;
IQEnvironment.stockTax = 0.003;
IQEnvironment.simulationMethod = SimulationMethod.normal;

// var minFscore = 2;
var rsiPeriod = 10;             // 기술적 지표 RSI의 기간 설정. 대체로 사용되는 값은 9일, 14~15일, 25~28일 등이다.(위키백과)
var mmtMonth = 12;
var stock_ratio = 0.95; // 주식 + 채권 비율
var cash_ratio = 0.05;

var preMmtScore = 0;
var PORT_portfolio1 = {
    "weight": function () {
        return stock_ratio;
        // return stock.getBollingerBand(20, 2, 2).upper;

    },
    "targetSize": function () {
        return 30;
    },
    "filter": Filter_portfolio1,
    "factor": FactorIndex_portfolio1
};

var Filter_portfolio1 = {

    // Default filters
    "market": {
        "KOSPI": true,
        "KOSDAQ": true
    },
    "noETF": true,
    "noPS": true,
    "marketCap": {
        "equalAbove": 0,
        "equalBelow": 10000000,
        "andOr": "AND"
    },
    "percentCap": {
        "percent": 80,
        "direction": "BELOW",
        "refCapSize": 0 // 초기값
    },
    "liquidity": {
        "period": 1,
        "threshold": 0
    },
    "noNegProfit": false,
    "noNegCashflow": false,
    "noManaged": false,
};

var FactorIndex_portfolio1 = {
    /* Default factor */
    // Value factor
    "_per": [0, RankOrder.descending],
    "_pbr": [0, RankOrder.descending],
    "_psr": [0, RankOrder.descending],
    "_pcr": [0, RankOrder.descending],

    // Quality factor
    "roa": [0, RankOrder.descending],
    "roe": [0, RankOrder.descending],
    "ros": [0, RankOrder.descending],
    "gpoa": [1, RankOrder.descending],
    "_evoebitda": [0, RankOrder.descending],
    "_evoebit": [0, RankOrder.descending],

    // Momentum factor
    "tsm12": [1, RankOrder.descending],
    "tsm6": [0, RankOrder.descending],
    "tsm3": [0, RankOrder.descending],

    // Size factor
    "capsize": [0, RankOrder.ascending],

    // F-score
    "fscore": [1, RankOrder.descending],

    // Techincal factor (DEBUG)
    "_rsi": [0, RankOrder.descending]
};

// Filters for Portfolio Builder
function filterfn_portfolio1(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio1))
        return false;
    return true;
}

// Post-filters after Model Portfolio Construction
// 
function postfilterfn_portfolio1(stock) {
    return true;
}

var FactorEval_portfolio1 = {
    // Custom factors
}

// Portfolio Builder
function builder_portfolio1(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio1);
    var universe = IQStock.filter(filterfn_portfolio1);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio1[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio1) {
            if (FactorIndex_portfolio1[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio1[ind](stock));
        }
    }


    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio1) {
            if (FactorIndex_portfolio1[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio1[ind][1]);
            // logger.debug("[" + ind + "] ind_rank: " + ind_rank)

            total_rank += FactorIndex_portfolio1[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
        // logger.debug("[" + stock.code + "] rank: " + stock.getScore("total_rank"))
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });


    port_result = port_result.filter(postfilterfn_portfolio1);
    port_result = port_result.slice(0, targetSize);
    // logger.debug("port_result: " + port_result)

    return port_result;
}

/**** f-score 계산 ****/
function getFscore(stock) {

    // 최근 4분기 순이익
    function netProfit(stock) {
        stock.loadPrevData(1, 4, 0);
        return stock.getFundamentalNetProfit(0) + stock.getFundamentalNetProfit(1) + stock.getFundamentalNetProfit(2) + stock.getFundamentalNetProfit(3);
    }

    // 최근 4분기 영업현금
    function cashflow(stock) {
        stock.loadPrevData(1, 4, 0);
        return stock.getFundamentalOperatingCashFlow(0) + stock.getFundamentalOperatingCashFlow(1) + stock.getFundamentalOperatingCashFlow(2) + stock.getFundamentalOperatingCashFlow(3);
    }

    // 전년도 영업현금흐름
    function cashflowlastyear(stock) {
        stock.loadPrevData(2, 4, 0);
        return stock.getFundamentalOperatingCashFlow(4) + stock.getFundamentalOperatingCashFlow(5) + stock.getFundamentalOperatingCashFlow(6) + stock.getFundamentalOperatingCashFlow(7);
    }

    // 전년도 총자산경상이익률
    function ROAlastyear(stock) {
        stock.loadPrevData(2, 4, 0);
        return (stock.getFundamentalNetProfit(4) + stock.getFundamentalNetProfit(5) + stock.getFundamentalNetProfit(6) + stock.getFundamentalNetProfit(7)) / stock.getFundamentalTotalAsset(4);
    }

    // 총자산 대비 장기부채 비율
    function longtermDebt(stock) {
        return (stock.getFundamentalTotalAsset(0) - stock.getFundamentalTotalEquity(0) - stock.getFundamentalTotalLiability(0)) / stock.getFundamentalTotalAsset(0);
    }

    // 전년도 총자산 대비 장기부채 비율
    function longtermDebtlastyear(stock) {
        stock.loadPrevData(1, 4, 0);
        return (stock.getFundamentalTotalAsset(4) - stock.getFundamentalTotalEquity(4) - stock.getFundamentalCurrentLiability(4)) / stock.getFundamentalTotalAsset(4);
    }

    // 유동부채 대비 유동자산 비율
    function currentRatio(stock) {
        return stock.getFundamentalCurrentAsset(0) / stock.getFundamentalCurrentLiability(0);
    }

    // 전년도 유동비율
    function currentRatiolastyear(stock) {
        stock.loadPrevData(1, 4, 0);
        return stock.getFundamentalCurrentAsset(4) / stock.getFundamentalCurrentLiability(4);
    }

    // 매출총이익
    function salesProfit(stock) {
        return stock.getFundamentalRevenue(0) - stock.getFundamentalSalesCost(0);
    }

    // 전년도 매출총이익
    function salesProfitlastyear(stock) {
        stock.loadPrevData(1, 4, 0);
        return stock.getFundamentalRevenue(4) - stock.getFundamentalSalesCost(4);
    }

    // 총자산회전율
    function assetTurnover(stock) {
        return stock.getFundamentalRevenue(0) / stock.getFundamentalTotalAsset(0);
    }

    // 전년도 총자산회전율
    function assetTurnoverlastyear(stock) {
        stock.loadPrevData(1, 4, 0);
        return stock.getFundamentalRevenue(4) / stock.getFundamentalTotalAsset(4);
    }

    stock.loadPrevData(1, 6, 0);
    var score = 0;

    if (netProfit(stock) > 0) { score = score + 1; } // 1. 순이익 > 0

    if (cashflow(stock) > cashflowlastyear(stock)) { score = score + 1; } // 2. 작년대비 영업활동현금흐름 증가

    if (stock.getROA() > ROAlastyear(stock)) { score = score + 1; } // 3. 작년대비 총자산경상이익률 증가

    if (cashflow(stock) > netProfit(stock)) { score = score + 1; } // 4. 영업활동현금흐름이 순이익 초과

    if (longtermDebt(stock) < longtermDebtlastyear(stock)) { score = score + 1; } // 5. 작년대비 총자산대비장기부채비율 감소

    if (currentRatio(stock) > currentRatiolastyear(stock)) { score = score + 1; } // 6. 작년대비 유동비율 증가

    if (stock.getNoOfShare(0) == stock.getNoOfShare(252)) { score = score + 1; } // 7. 1년전 대비 주식수 변동없음

    if (salesProfit(stock) > salesProfitlastyear(stock)) { score = score + 1; } // 8. 작년대비 매출총이익 증가

    if (assetTurnover(stock) > assetTurnoverlastyear(stock)) { score = score + 1; } // 9. 작년대비 총자산회전율 증가

    return score;

}

// 시가총액 % 기준 위치 찾아내기
function makeCapSizeRef(settings) {
    var universe = IQStock.filter(function (stock) {
        // 상폐종목 및 거래정지 종목 제외
        if (stock.getClose() === 0)
            return false;
        if (stock.manage & 4) // 거래정지종목
            return false;

        // KOSPI, KOSDAQ 종목 체크
        if (!(settings.market.KOSPI && stock.market === 1) && !(settings.market.KOSDAQ && stock.market === 0))
            return false;

        // ETF 제외
        if (settings.noETF && stock.isETF)
            return false;

        // 우선주 제외
        if (settings.noPS && !stock.isETF && stock.getFundamentalTotalAsset() === 0)
            return false;

        return true;
    });

    var sortedByMktCap = universe.slice().sort(function (a, b) {
        return b.getMarketCapital() - a.getMarketCapital();
    });

    // 시가총액 상위 % 기준 위치 값
    var percentile = sortedByMktCap[Math.floor(sortedByMktCap.length * (settings.percentCap.percent / 100)) - 1];
    if (percentile !== undefined) {
        settings.percentCap.refCapSize = percentile.getMarketCapital();
    } else {
        var largestMktCap = sortedByMktCap[0];
        if (largestMktCap !== undefined) {
            settings.percentCap.refCapSize = largestMktCap.getMarketCapital() + 1;
        } else {
            settings.percentCap.refCapSize = 1000000000;
        }
    }
}

function defaultFilter(stock, settings) {
    // 상폐종목 및 거래정지 종목 항상 제외
    if (stock.getClose() === 0) {
        // logger.debug('[' + stock.code + ']' + stock.name + ' getClose filtered!')
        return false;
    }
    // 거래정지종목
    if (stock.manage & 4) {
        // logger.debug('[' + stock.code + ']' + stock.name + ' manage filtered!')
        return false;
    }

    // KOSPI, KOSDAQ 종목 체크
    if (!(settings.market.KOSPI && stock.market === 1) && !(settings.market.KOSDAQ && stock.market === 0)) {
        // logger.debug('[' + stock.code + ']' + stock.name + ' KOSPI, KOSDAQ filtered!')
        return false;
    }

    // ETF 제외
    if (settings.noETF && stock.isETF) {
        // logger.debug('[' + stock.code + ']' + stock.name + ' noETF filtered!')
        return false;
    }

    // 우선주 제외
    if (settings.noPS && !stock.isETF && stock.getFundamentalTotalAsset() === 0) {
        // logger.debug('[' + stock.code + ']' + stock.name + ' getFundamentalTotalAsset filtered!')
        return false;
    }

    // 시가총액 기준
    var f_mCap1 = (stock.getMarketCapital() >= settings.marketCap.equalAbove * 100); // 시가총액 x억 이상
    var f_mCap2 = (stock.getMarketCapital() <= settings.marketCap.equalBelow * 100); // 시가총액 y억 이하
    var f_mCap = settings.marketCap.andOr === "AND" ? f_mCap1 && f_mCap2 : f_mCap1 || f_mCap2;
    if (!f_mCap)
        return false;

    // 시가총액 % 기준
    var pCapDiff = stock.getMarketCapital() - settings.percentCap.refCapSize;
    var pCap = settings.percentCap.direction === "ABOVE" ? pCapDiff >= 0 : pCapDiff <= 0;
    if (!pCap)
        return false;

    // 유동성(거래대금) 조건
    if (avgTrval(stock, settings.liquidity.period) < settings.liquidity.threshold * 100)
        return false;

    /* 건전성 필터 */

    // 당기순손실 종목 제외
    if (settings.noNegProfit && stock.getFundamentalNetProfit() <= 0)
        return false;

    // 영업현금흐름 (-)종목 제외
    if (settings.noNegCashflow && stock.getFundamentalOperatingCashFlow() <= 0)
        return false;

    // 관리종목 제외
    if (settings.noManaged && (stock.manage & 1))
        return false;

    return true;
}

// 평균 거래대금 계산함수
function avgTrval(stock, period) {
    if (period <= 1)
        return stock.getTradingValue();

    var avgVol = 0;
    var volCount = 0;
    for (var i = 0; i < period; i++) {
        if (stock.getTradingVolume(period - i - 1) === 0) {
            continue;
        }
        avgVol += stock.getTradingValue(period - i - 1);
        volCount += 1;
    }
    if (volCount > 0) {
        avgVol /= volCount;
    }
    return avgVol;
}

// Factor evaluation functions
var FactorEval_default = {
    /**** Value Factors ****/
    // PER(역): 시가총액 / 당기순이익 := 주가수익비율 (낮을수록 좋음)
    "_per": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return (stock.getFundamentalNetProfit() * 4) / (stock.getMarketCapital() * 1000);
    },

    // PBR(역): 시가총액 / 순자산 := 주가순자산비율 (낮을수록 좋음)
    "_pbr": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return stock.getFundamentalTotalEquity() / (stock.getMarketCapital() * 1000);
    },

    // PSR(역): 시가총액 / 매출액 := 주가매출액비율 (낮을수록 좋음)
    "_psr": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return (stock.getFundamentalRevenue() * 4) / (stock.getMarketCapital() * 1000);
    },

    // PCR(역): 시가총액 / 주당현금흐름 := 주가현금흐름비율 (낮을수록 좋음)
    "_pcr": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return (stock.getFundamentalOperatingCashFlow() * 4) / (stock.getMarketCapital() * 1000);
    },

    /**** Quality Factors ****/
    // ROA: 당기순이익 / 총자산 := 총자산순이익률 (높을수록 좋음)
    "roa": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }
        return 4 * stock.getFundamentalNetProfit() / stock.getFundamentalTotalAsset();
    },

    // ROE: 당기순이익 / 순자산 := 자기자본이익률 (높을수록 좋음)
    "roe": function (stock) {
        if (stock.getFundamentalTotalEquity() === 0) {
            return -99999999;
        }
        return 4 * stock.getFundamentalNetProfit() / stock.getFundamentalTotalEquity();
    },

    // ROS: 당기순이익 / 매출액 := 매출액순이익률 (높을수록 좋음)
    "ros": function (stock) {
        if (stock.getFundamentalRevenue() === 0) {
            return -99999999;
        }
        return 4 * stock.getFundamentalNetProfit() / stock.getFundamentalRevenue();
    },

    // GP/A: 매출총이익 / 총자산 (높을수록 좋음)
    // * 재무제표에서 최상위 지표 (변질될 가능성이 낮음)
    "gpoa": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }
        var GP = stock.getFundamentalOperatingIncome() + stock.getFundamentalSellingExpense();

        return 4 * GP / stock.getFundamentalTotalAsset();
    },

    // EV/EBIT(역): 기업가치 / 영업이익 (낮을수록 좋음)
    // * EV = 시가총액+부채-현금-비영업자산
    // * 기업을 통채로 샀을때 투자금액을 회수하는 데 걸리는 연수와 비슷
    "_evoebit": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }


        // var EV = stock.getFundamentalEV()
        // var EBIT = stock.getFundamentalEBIT()

        // logger.debug('[' + stock.code + ']' + stock.name);
        // logger.debug('EV: ' + EV + ' / ' + 'EBITDA: ' + EBITDA + ' / ' + 'EVoEBITDA: '  + EVoEBITDA)
        // logger.debug('------------------------------------------------------------')

        if (stock.getFundamentalEV() === 0) {
            return -99999999;
        }
        if (stock.getFundamentalEBIT() === 0) {
            return -99999999;
        }

        return stock.getFundamentalEBIT() / stock.getFundamentalEV();
    },

    // EV/EBITDA(역): 기업가치 / (영업이익+감가상각비+감모상각비) (낮을수록 좋음)
    "_evoebitda": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }


        // var EV = stock.getFundamentalEV()
        // var EBITDA = stock.getFundamentalEBITDA()

        // logger.debug('[' + stock.code + ']' + stock.name);
        // logger.debug('EV: ' + EV + ' / ' + 'EBITDA: ' + EBITDA + ' / ' + 'EVoEBITDA: '  + EVoEBITDA)
        // logger.debug('------------------------------------------------------------')

        if (stock.getFundamentalEV() === 0) {
            return -99999999;
        }
        if (stock.getFundamentalEBITDA() === 0) {
            return -99999999;
        }

        return stock.getFundamentalEBITDA() / stock.getFundamentalEV();
    },

    // Momentum factor
    "tsm12": function (stock) {
        var daysPerMonth = 21;
        if (stock.getAdjClose(12 * daysPerMonth) === 0 || stock.getAdjClose(0) === 0) {
            return -1000;
        }
        return stock.getAdjClose(0) / stock.getAdjClose(12 * daysPerMonth);
    },

    "tsm6": function (stock) {
        var daysPerMonth = 21;
        if (stock.getAdjClose(6 * daysPerMonth) === 0 || stock.getAdjClose(0) === 0) {
            return -1000;
        }
        return stock.getAdjClose(0) / stock.getAdjClose(6 * daysPerMonth);
    },

    "tsm3": function (stock) {
        var daysPerMonth = 21;
        if (stock.getAdjClose(3 * daysPerMonth) === 0 || stock.getAdjClose(0) === 0) {
            return -1000;
        }
        return stock.getAdjClose(0) / stock.getAdjClose(3 * daysPerMonth);
    },

    "capsize": function (stock) {
        return stock.getMarketCapital();
    },

    "fscore": function (stock) {

        var score = getFscore(stock)
        if (score === Infinity || isNaN(score)) {
            logger.warning('[F-Score] 종목코드 ' + stock.code + '에 대한 F-score 지표값이 (' + score + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }

        return score;
    },

    // TODO: DEBUG & VERIFICATE
    "_rsi": function (stock) {
        stock.loadPrevData(0, 4, 0);
        var test = stock.getRSI(rsiPeriod);
        logger.debug("debug: " + test);
        return stock.getRSI(rsiPeriod);
    }
}

var BL_portfolio = [PORT_portfolio1, PORT_portfolio1, PORT_portfolio1, PORT_portfolio1, PORT_portfolio1, PORT_portfolio1];
var BL_builder = [builder_portfolio1, builder_portfolio1, builder_portfolio1, builder_portfolio1, builder_portfolio1, builder_portfolio1];
var BL_basket = [];
var BL_name = ['1-모멘텀', '2-가속모멘텀', '3-절대모멘텀', '4-모멘텀(계절성)', '5-가속모멘텀(계절성)', '6-절대모멘텀(계절성)'];

function initialize() {

    for (var i = 0; i < BL_portfolio.length; i++) {
        if (i === 0) {
            var acc = IQAccount.getDefaultAccount();
            acc.accountName = BL_name[i];
        } else {
            var acc = IQAccount.addAccount('0000-0000-0' + String(i), BL_name[i], IQEnvironment.aum);
        }
        BL_basket[i] = new Basket(acc, 0, 0);
        BL_basket[i].setPortfolioBuilder(BL_builder[i]);
    }

    IQDate.addRebalSchedule(IQDate.setMonthlyStart(1));
    // IQDate.addRebalSchedule(IQDate.setYearly(4, 1));
    // IQDate.addRebalSchedule(IQDate.setYearly(6, 1));
    // IQDate.addRebalSchedule(IQDate.setYearly(9, 1));
    // IQDate.addRebalSchedule(IQDate.setYearly(12, 1));
}

function getMmtScore(MonthCount) {
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

function getMmtRatio(mmtScore, MonthCount, accelMom_yn) {

    var StockRatio;
    if (accelMom_yn === 'Y' && mmtScore > preMmtScore) {
        StockRatio = (mmtScore + (mmtScore - preMmtScore)) / MonthCount;
    } //전월에 비해 모멘텀 스코어가 커졌으면 1점 추가
    else { StockRatio = mmtScore / MonthCount; }

    if (StockRatio >= stock_ratio) { StockRatio = stock_ratio; }
    if (StockRatio < 0) { StockRatio = 0; }

    return StockRatio;
}


function getAbsMmtRatio(IndexCode) {
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
    var MomentmRatio = stock_ratio // 주식비중
    if (current_price < PRICE_252 && (current_price < PRICE_42))  //절대모멘텀(1년)이 적용되고 최근 2개월 모멘텀도 음수일때 
    {
        var KR3Y_Tresaury = IQStock.getStock('A114100'); //KBSTAR 국고채3년 114100 2009년 07월 29일            
        if (KR3Y_Tresaury == null) { MomentmRatio = 0; } else { MomentmRatio = 0.3; }
        logger.debug('절대모멘텀 적용. 주식비중 : ' + MomentmRatio * 100 + '%');
    }
    return MomentmRatio;
}

function basketEnter(basket, account, code, ratio) {
    var sse = IQStock.getStock(code);
    if (sse !== null) {
        var bond_amt = account.getTotalEquity() * ratio
        var BO_quantity = Math.floor(bond_amt / sse.getAdjClose());  //수량 (종목당 예산 / 수정종가)
        basket.enter(sse, BO_quantity);
    }
}


// 주식을 매수하고 남은 비중으로 자산배분(자산배분은 2011년 3월 부터 가능)
function AssetAllocation(basket, account, stockWeight) {

    if (stockWeight < 1 - cash_ratio) {

        //골드 비중 : (1 - 주식비중) * 15%. ex) 주식비중 30% 인 경우 대략 15%
        var gold_ratio = (1 - stockWeight - cash_ratio) * 0.15;

        //채권 비중 : 1 -  주식비중 - 골드비중. 2% 는 현금               
        var bond_ratio = (1 - stockWeight) - gold_ratio - cash_ratio;

        //TIGER 미국채10년선물 305080 2018년 08월 30일
        var US10Y_Tresaury = IQStock.getStock('A305080');

        //KOSEF 국고채10년 148070 2011년 10월 20일
        var KR10Y_Tresaury = IQStock.getStock('A148070');

        //KOSEF 미국달러선물 138230 2011년 02월
        var USD = IQStock.getStock('A138230');

        //KODEX 골드선물(H) 2010년 10월 01일
        var KR_GOLD = IQStock.getStock('A132030');

        //KBSTAR 국고채3년 114100 2009년 07월 29일
        var KR3Y_Tresaury = IQStock.getStock('A114100');

        if (KR3Y_Tresaury == null) {
            logger.debug("자산 배분을 수행할 수 없습니다. 투자 기간을 2009년 8월 이후로 조정하세요.");
            gold_ratio = 0;
        }
        else if (KR3Y_Tresaury.getClose() > 0 && KR_GOLD == null) {
            basketEnter(basket, account, 'A114100', bond_ratio + gold_ratio); //KBSTAR 국고채3년
            var BondPct = (bond_ratio + gold_ratio) * 100;
            logger.debug('전략명: ' + account.accountName + " , 자산 비중: KBSTAR 국고채3년 " + BondPct.toPrecision(5) + '%');
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

// 배열 합계 구하기 함수
function sum(array) {
    var result = 0.0;
    for (var i = 0; i < array.length; i++) {
        result = result + array[i];
    }
    return result; //null 처리
}

var isFirst = true;

// 시즈널리티 적용 : 5~10 월에 주식비중 30%로 투자함. 모멘텀 주식비중이 30% 보다 낮을 경우는 그대로 적용함
function getSeasonality(mmtWeight, ntlWeight) {
    var seasonRatio = mmtWeight;
    var thisMonth = IQIndex.getIndex("004").getDate(0).getMonth() + 1;
    if (thisMonth >= 5 && thisMonth <= 10 && mmtWeight > ntlWeight) { seasonRatio = ntlWeight; }
    return seasonRatio;
}

/**** RUN STAGE ****/
function onDayClose(now) {
    if (IQDate.isRebalancingDay(now) || isFirst === true) {
        logger.debug('리밸런싱을 진행합니다!');

        var wgt = stock_ratio;

        // mmtMonth 만큼의 개월의 모멘텀을 측정한 점수
        var mmtScore = getMmtScore(mmtMonth);

        // 모멘텀 스코어로 주식비중을 결정한다.
        var mmtWeight = getMmtRatio(mmtScore, mmtMonth, 'N');

        // 가속 모멘텀 스코어로 주식비중을 결정한다.
        var accMmtWeight = getMmtRatio(mmtScore, mmtMonth, 'Y');

        // 절대 모멘텀 스코어로 주식비중을 결정한다.
        var absMntWeight = getAbsMmtRatio('004');

        // 모멘텀 스코어에 시즈널리티(중립)를 적용한 주식비중
        var mmtWeight_season = getSeasonality(mmtWeight, 0.5);

        // 가속 모멘텀에 시즈널리티(중립)를 적용한 주식비중
        var accMmtWeight_season = getSeasonality(accMmtWeight, 0.5);

        // 절대 모멘텀에 시즈널리티(중립)를 적용한 주식비중
        var absMntWeight_season = getSeasonality(absMntWeight, 0.5);

        logger.debug("mmtScore: " + mmtScore.toFixed(2))
        logger.debug("mmtWeight: " + mmtWeight.toFixed(2))
        logger.debug("accMmtWeight: " + accMmtWeight.toFixed(2))
        logger.debug("absMntWeight: " + absMntWeight.toFixed(2))
        logger.debug("mmtWeight_season: " + mmtWeight_season.toFixed(2))
        logger.debug("accMmtWeight_season: " + accMmtWeight_season.toFixed(2))
        logger.debug("absMntWeight_season: " + absMntWeight_season.toFixed(2))


        for (var i = 0; i < BL_portfolio.length; i++) {
            logger.info('-------------------- ' + BL_name[i] + ' --------------------');

            // var wgt = BL_portfolio[i].weight();
            if (i === 0) { wgt = mmtWeight; }
            else if (i === 1) { wgt = accMmtWeight; }
            else if (i === 2) { wgt = absMntWeight; }
            else if (i === 3) { wgt = mmtWeight_season; }
            else if (i === 4) { wgt = accMmtWeight_season; }
            else { wgt = absMntWeight_season; }

            var acc = BL_basket[i].account;
            var currentTotalEquity = acc.getTotalEquity();
            logger.debug('현재 계좌 평가액 : ' + IQUtil.getNumberWithCommas(currentTotalEquity.toFixed(2)));
            logger.debug('누적수수료= ' + IQUtil.getNumberWithCommas(acc.cumCommission.toFixed(2)) + ',  누적세금= ' + IQUtil.getNumberWithCommas(acc.cumTax.toFixed(2)) + ',  회전율= ' + Math.floor(acc.turnover * 100) + '%');
            logger.debug('투자금액 : ' + IQUtil.getNumberWithCommas((currentTotalEquity * wgt).toFixed(2)));
            logger.debug('주식비율 : ' + wgt.toFixed(2) * 100 + ' %');

            BL_basket[i].targetSize = BL_portfolio[i].targetSize();
            BL_basket[i].setBudget(currentTotalEquity * wgt);
            BL_basket[i].buildPortfolio();
            AssetAllocation(BL_basket[i], acc, wgt);

            // logger.info('-------------------- 종목 리스트 --------------------');
            // var eggArray = BL_basket[i].newEggs.values();
            // for (var j = 0; j < eggArray.length; j++) {
            //     var _stock = eggArray[j].stock;
            //     logger.info(_stock.code + '(' + _stock.name + '), ' + _stock.getAdjClose().toFixed(2) + ', ' + (eggArray[j].quantity) + '주 (' + (wgt * eggArray[j].ratio * 100).toFixed(2) + '%)');
            // }
            // logger.info('--------------------------------------------------------------');

        }

        preMmtScore = mmtScore;

    }
    isFirst = false;

}

