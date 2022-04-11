

/***********************************************/
// SET PARAMS
/***********************************************/
IQEnvironment.stockCommission = 0.0015;
IQEnvironment.etfCommission = 0.0015;
IQEnvironment.stockTax = 0.003;
IQEnvironment.simulationMethod = SimulationMethod.normal;

var PORT_portfolio1 = {
    "weight": function () {
        return 0.9;
        // return stock.getBollingerBand(20, 2, 2).upper;

    },
    "targetSize": function () {
        return 20;
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
        "percent": 100,
        "direction": "ABOVE",
        "refCapSize": 0 // 초기값
    },
    "liquidity": {
        "period": 1,
        "threshold": 1
    },
    "noNegProfit": true,
    "noNegCashflow": true,
    "noManaged": true,
};

var FactorIndex_portfolio1 = {
    /* Default factor */
    // Value factor
    "_per": [0, RankOrder.descending],
    "_pbr": [0, RankOrder.descending],
    "_psr": [0, RankOrder.descending],
    "_pcr": [0, RankOrder.descending],

    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [0, RankOrder.descending],
    "_evoebitda": [0, RankOrder.descending],
    "_evoebit": [0, RankOrder.descending],

    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],

    // Size factor
    "_capsize": [0, RankOrder.ascending],

    // F-score
    "_fscore": [1, RankOrder.descending]
};



// Filters for Portfolio Builder
function filterfn_portfolio1(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio1))
        return false;
    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio1(stock) {
    return true;
}


var FactorEval_portfolio1 = {
    // Custom factors
}


// Portfolio Builder
function builder_portfolio1(targetSize) {
    // 종목 필터 적용
    // makeCapSizeRef(Filter_portfolio1);
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
            logger.debug
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
            total_rank += FactorIndex_portfolio1[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio1);
    port_result = port_result.slice(0, targetSize);

    return port_result;
}


/**** f-score 계산 BEGIN ****/
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

function getFscore(stock) {
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
/**** f-score 계산 END ****/



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
    // Default factors
    "_per": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        var _PER = (stock.getFundamentalNetProfit() * 4) / (stock.getMarketCapital() * 1000);
        // logger.debug('[' + stock.code + ']' + stock.name + '-> _PER: ' + _PER);
        return _PER;
    },

    "_pbr": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return stock.getFundamentalTotalEquity() / (stock.getMarketCapital() * 1000);
    },

    "_psr": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return (stock.getFundamentalRevenue() * 4) / (stock.getMarketCapital() * 1000);
    },

    "_pcr": function (stock) {
        if (stock.getMarketCapital() === 0) {
            return -99999999;
        }
        return (stock.getFundamentalOperatingCashFlow() * 4) / (stock.getMarketCapital() * 1000);
    },

    // Quality factor
    "_roa": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }
        return 4 * stock.getFundamentalNetProfit() / stock.getFundamentalTotalAsset();
    },

    "_roe": function (stock) {
        if (stock.getFundamentalTotalEquity() === 0) {
            return -99999999;
        }
        return 4 * stock.getFundamentalNetProfit() / stock.getFundamentalTotalEquity();
    },

    "_ros": function (stock) {
        if (stock.getFundamentalRevenue() === 0) {
            return -99999999;
        }
        return 4 * stock.getFundamentalNetProfit() / stock.getFundamentalRevenue();
    },

    "_gpoa": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }
        var GP = stock.getFundamentalOperatingIncome() + stock.getFundamentalSellingExpense();
        return 4 * GP / stock.getFundamentalTotalAsset();
    },

    "_evoebitda": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }


        var EV = stock.getFundamentalEV()
        var EBITDA = stock.getFundamentalEBITDA()

        // logger.debug('[' + stock.code + ']' + stock.name);
        // logger.debug('EV: ' + EV + ' / ' + 'EBITDA: ' + EBITDA + ' / ' + 'EVoEBITDA: '  + EVoEBITDA)
        // logger.debug('------------------------------------------------------------')

        if (stock.getFundamentalEV() === 0) {
            return -99999999;
        }
        if (stock.getFundamentalEBITDA() === 0) {
            return -99999999;
        }

        return (EBITDA * 4) / EV;
    },

    "_evoebit": function (stock) {
        if (stock.getFundamentalTotalAsset() === 0) {
            return -99999999;
        }


        var EV = stock.getFundamentalEV()
        var EBIT = stock.getFundamentalEBIT()

        // logger.debug('[' + stock.code + ']' + stock.name);
        // logger.debug('EV: ' + EV + ' / ' + 'EBITDA: ' + EBITDA + ' / ' + 'EVoEBITDA: '  + EVoEBITDA)
        // logger.debug('------------------------------------------------------------')

        if (stock.getFundamentalEV() === 0) {
            return -99999999;
        }
        if (stock.getFundamentalEBIT() === 0) {
            return -99999999;
        }

        return (EBIT * 4) / EV;
    },



    // Momentum factor
    "_tsm12": function (stock) {
        var daysPerMonth = 21;
        if (stock.getAdjClose(12 * daysPerMonth) === 0 || stock.getAdjClose(0) === 0) {
            return -1000;
        }
        return stock.getAdjClose(0) / stock.getAdjClose(12 * daysPerMonth);
    },

    "_tsm6": function (stock) {
        var daysPerMonth = 21;
        if (stock.getAdjClose(6 * daysPerMonth) === 0 || stock.getAdjClose(0) === 0) {
            return -1000;
        }
        return stock.getAdjClose(0) / stock.getAdjClose(6 * daysPerMonth);
    },

    "_tsm3": function (stock) {
        var daysPerMonth = 21;
        if (stock.getAdjClose(3 * daysPerMonth) === 0 || stock.getAdjClose(0) === 0) {
            return -1000;
        }
        return stock.getAdjClose(0) / stock.getAdjClose(3 * daysPerMonth);
    },

    "_capsize": function (stock) {
        return stock.getMarketCapital();
    },

    "_fscore": function (stock) {
        var score = getFscore(stock)

        logger.debug("code: " + stock.code + " score: " + score)
        // return stock.getMarketCapital();
    }
}


var BL_portfolio = [PORT_portfolio1];
var BL_builder = [builder_portfolio1];
var BL_basket = [];

function initialize() {

    for (var i = 0; i < BL_portfolio.length; i++) {
        var acc = IQAccount.getDefaultAccount();
        BL_basket[i] = new Basket(acc, 0, 0);
        BL_basket[i].setPortfolioBuilder(BL_builder[i]);
    }

    IQDate.addRebalSchedule(IQDate.setMonthlyStart(1));
}

var isFirst = true;

/**** RUN STAGE ****/
function onDayClose(now) {
    if (IQDate.isRebalancingDay(now) || isFirst === true) {
        logger.debug('리밸런싱을 진행합니다!');

        var acc = IQAccount.getDefaultAccount();
        var currentTotalEquity = acc.getTotalEquity();
        logger.debug('현재 계좌 평가액 : ' + IQUtil.getNumberWithCommas(currentTotalEquity.toFixed(2)));
        logger.debug('누적수수료= ' + IQUtil.getNumberWithCommas(acc.cumCommission.toFixed(2)) + ',  누적세금= ' + IQUtil.getNumberWithCommas(acc.cumTax.toFixed(2)) + ',  회전율= ' + Math.floor(acc.turnover * 100) + '%');

        for (var i = 0; i < BL_portfolio.length; i++) {
            BL_basket[i].targetSize = BL_portfolio[i].targetSize();
            BL_basket[i].setBudget(currentTotalEquity * BL_portfolio[i].weight());
            BL_basket[i].buildPortfolio();

            var eggArray = BL_basket[i].newEggs.values();
            var wgt = BL_portfolio[i].weight();
            for (var j = 0; j < eggArray.length; j++) {
                var _stock = eggArray[j].stock;
                logger.info(_stock.code + '(' + _stock.name + '), ' + _stock.getAdjClose().toFixed(2) + ', ' + (eggArray[j].quantity) + '주 (' + (wgt * eggArray[j].ratio * 100).toFixed(2) + '%)');
            }
            logger.info('--------------------------------------------------------------');

        }


    }
    isFirst = false;

}

