// 제목: (블록 알고리즘) 퀀트전략 7개 (2015년 ~ 2020년) 살펴보기
// 작성자: Chris
// 작성일: 2020.03.06



var X, stock;

/**
 * 이 함수를 설명하세요...
 */
function F_EC_8A_A4_EC_BD_94_EC_96_B4(stock) {
    X = 0;
    if (stock.getFundamentalNetProfit(0) > 0) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalOperatingCashFlow(0) > 0) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalNetProfit(0) / stock.getFundamentalTotalAsset(0) > stock.getFundamentalNetProfit(4) / stock.getFundamentalTotalAsset(4)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalOperatingCashFlow(0) > stock.getFundamentalNetProfit(0)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalTotalLiability(0) / stock.getFundamentalTotalEquity(0) < stock.getFundamentalTotalLiability(1) / stock.getFundamentalTotalEquity(1)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalCurrentAsset(0) / stock.getFundamentalCurrentLiability(0) > stock.getFundamentalCurrentAsset(1) / stock.getFundamentalCurrentLiability(1)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalCapitalStock(0) == stock.getFundamentalCapitalStock(1)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if ((stock.getFundamentalRevenue(0) - stock.getFundamentalSalesCost(0)) / stock.getFundamentalRevenue(0) >= (stock.getFundamentalRevenue(1) - stock.getFundamentalSalesCost(1)) / stock.getFundamentalRevenue(1)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    if (stock.getFundamentalRevenue(0) / stock.getFundamentalTotalAsset(0) > stock.getFundamentalRevenue(1) / stock.getFundamentalTotalAsset(1)) {
        X = (typeof X == 'number' ? X : 0) + 1;
    }
    return X;
}




var PORT_portfolio2 = {
    "weight": function () {
        return (18.81 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 30;
    },
    "filter": Filter_portfolio2,
    "factor": FactorIndex_portfolio2
};

var Filter_portfolio2 = {

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

    // Custom filters
    "filter1": function (stock) {
        return (stock.getPBR() > 0.2);
    },

};


// Filters for Portfolio Builder
function filterfn_portfolio2(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio2))
        return false;

    // Custom filters
    if (!Filter_portfolio2.filter1(stock))
        return false;

    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio2(stock) {

    return true;
}


var FactorIndex_portfolio2 = {
    /* Default factor */
    // Value factor
    "_per": [0, RankOrder.descending],
    "_pbr": [1, RankOrder.descending],
    "_psr": [0, RankOrder.descending],
    "_pcr": [0, RankOrder.descending],
    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [0, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],


};


var FactorEval_portfolio2 = {
    // Custom factors

}


// Portfolio Builder
function builder_portfolio2(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio2);
    var universe = IQStock.filter(filterfn_portfolio2);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio2[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio2) {
            if (FactorIndex_portfolio2[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio2[ind](stock));
        }
    }

    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio2) {
            if (FactorIndex_portfolio2[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio2[ind][1]);
            total_rank += FactorIndex_portfolio2[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio2);
    port_result = port_result.slice(0, targetSize);

    return port_result;
}

var PORT_portfolio3 = {
    "weight": function () {
        return (21.91 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 10;
    },
    "filter": Filter_portfolio3,
    "factor": FactorIndex_portfolio3
};

var Filter_portfolio3 = {

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


// Filters for Portfolio Builder
function filterfn_portfolio3(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio3))
        return false;


    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio3(stock) {

    return true;
}


var FactorIndex_portfolio3 = {
    /* Default factor */
    // Value factor
    "_per": [1, RankOrder.descending],
    "_pbr": [1, RankOrder.descending],
    "_psr": [0, RankOrder.descending],
    "_pcr": [1, RankOrder.descending],
    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [0, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],


};


var FactorEval_portfolio3 = {
    // Custom factors

}


// Portfolio Builder
function builder_portfolio3(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio3);
    var universe = IQStock.filter(filterfn_portfolio3);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio3[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio3) {
            if (FactorIndex_portfolio3[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio3[ind](stock));
        }
    }

    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio3) {
            if (FactorIndex_portfolio3[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio3[ind][1]);
            total_rank += FactorIndex_portfolio3[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio3);
    port_result = port_result.slice(0, targetSize);

    return port_result;
}

var PORT_portfolio4 = {
    "weight": function () {
        return (23.74 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 30;
    },
    "filter": Filter_portfolio4,
    "factor": FactorIndex_portfolio4
};

var Filter_portfolio4 = {

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


// Filters for Portfolio Builder
function filterfn_portfolio4(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio4))
        return false;


    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio4(stock) {

    return true;
}


var FactorIndex_portfolio4 = {
    /* Default factor */
    // Value factor
    "_per": [0, RankOrder.descending],
    "_pbr": [1, RankOrder.descending],
    "_psr": [0, RankOrder.descending],
    "_pcr": [0, RankOrder.descending],
    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [1, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],


};


var FactorEval_portfolio4 = {
    // Custom factors

}


// Portfolio Builder
function builder_portfolio4(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio4);
    var universe = IQStock.filter(filterfn_portfolio4);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio4[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio4) {
            if (FactorIndex_portfolio4[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio4[ind](stock));
        }
    }

    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio4) {
            if (FactorIndex_portfolio4[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio4[ind][1]);
            total_rank += FactorIndex_portfolio4[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio4);
    port_result = port_result.slice(0, targetSize);

    return port_result;
}

var PORT_portfolio5 = {
    "weight": function () {
        return (31.21 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 10;
    },
    "filter": Filter_portfolio5,
    "factor": FactorIndex_portfolio5
};

var Filter_portfolio5 = {

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


// Filters for Portfolio Builder
function filterfn_portfolio5(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio5))
        return false;


    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio5(stock) {

    return true;
}


var FactorIndex_portfolio5 = {
    /* Default factor */
    // Value factor
    "_per": [1, RankOrder.descending],
    "_pbr": [1, RankOrder.descending],
    "_psr": [1, RankOrder.descending],
    "_pcr": [1, RankOrder.descending],
    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [0, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],


};


var FactorEval_portfolio5 = {
    // Custom factors

}


// Portfolio Builder
function builder_portfolio5(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio5);
    var universe = IQStock.filter(filterfn_portfolio5);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio5[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio5) {
            if (FactorIndex_portfolio5[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio5[ind](stock));
        }
    }

    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio5) {
            if (FactorIndex_portfolio5[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio5[ind][1]);
            total_rank += FactorIndex_portfolio5[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio5);
    port_result = port_result.slice(0, targetSize);

    return port_result;
}

var PORT_portfolio1 = {
    "weight": function () {
        return (24.21 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 10;
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


var FactorIndex_portfolio1 = {
    /* Default factor */
    // Value factor
    "_per": [0, RankOrder.descending],
    "_pbr": [1, RankOrder.descending],
    "_psr": [0, RankOrder.descending],
    "_pcr": [0, RankOrder.descending],
    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [0, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],

    /* Custom factors */
    "F스코어": [1, RankOrder.descending],
};


var FactorEval_portfolio1 = {
    // Custom factors

    "F스코어": function (stock) {
        var retValue = (F_EC_8A_A4_EC_BD_94_EC_96_B4(stock));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

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

var PORT_portfolio6 = {
    "weight": function () {
        return (53.4 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 10;
    },
    "filter": Filter_portfolio6,
    "factor": FactorIndex_portfolio6
};

var Filter_portfolio6 = {

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


// Filters for Portfolio Builder
function filterfn_portfolio6(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio6))
        return false;


    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio6(stock) {

    return true;
}


var FactorIndex_portfolio6 = {
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
    "_gpoa": [1, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],

    /* Custom factors */
    "F스코어2": [1, RankOrder.descending],
};


var FactorEval_portfolio6 = {
    // Custom factors

    "F스코어2": function (stock) {
        var retValue = (F_EC_8A_A4_EC_BD_94_EC_96_B4(stock));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

}


// Portfolio Builder
function builder_portfolio6(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio6);
    var universe = IQStock.filter(filterfn_portfolio6);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio6[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio6) {
            if (FactorIndex_portfolio6[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio6[ind](stock));
        }
    }

    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio6) {
            if (FactorIndex_portfolio6[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio6[ind][1]);
            total_rank += FactorIndex_portfolio6[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio6);
    port_result = port_result.slice(0, targetSize);

    return port_result;
}

var PORT_portfolio7 = {
    "weight": function () {
        return (28.27 / 201.55 - 0.01);
    },
    "targetSize": function () {
        return 20;
    },
    "filter": Filter_portfolio7,
    "factor": FactorIndex_portfolio7
};

var Filter_portfolio7 = {

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

    // Custom filters
    "filter1": function (stock) {
        return (stock.getFundamentalTotalAsset(0) > 0);
    },

    "filter2": function (stock) {
        return (stock.getAdjClose(250) > 0);
    },

    "filter3": function (stock) {
        return (stock.getFundamentalNetProfit(0) > 0);
    },

    "filter4": function (stock) {
        return (stock.getFundamentalCapitalStock(0) > 0);
    },

    "filter5": function (stock) {
        return (stock.getFundamentalOperatingCashFlow(0) > 0);
    },

    "filter6": function (stock) {
        return (stock.getFundamentalEBITDA(0) > 0);
    },

    "filter7": function (stock) {
        return (stock.getFundamentalDividend(0) > 0);
    },

    "filter8": function (stock) {
        return (stock.getFundamentalCapitalStock(1) == stock.getFundamentalCapitalStock(0));
    },

};


// Filters for Portfolio Builder
function filterfn_portfolio7(stock) {
    // Default filters
    if (!defaultFilter(stock, Filter_portfolio7))
        return false;

    // Custom filters
    if (!Filter_portfolio7.filter1(stock))
        return false;

    if (!Filter_portfolio7.filter2(stock))
        return false;

    if (!Filter_portfolio7.filter3(stock))
        return false;

    if (!Filter_portfolio7.filter4(stock))
        return false;

    if (!Filter_portfolio7.filter5(stock))
        return false;

    if (!Filter_portfolio7.filter6(stock))
        return false;

    if (!Filter_portfolio7.filter7(stock))
        return false;

    if (!Filter_portfolio7.filter8(stock))
        return false;

    return true;
}



// Post-filters after Model Portfolio Construction
function postfilterfn_portfolio7(stock) {

    return true;
}


var FactorIndex_portfolio7 = {
    /* Default factor */
    // Value factor
    "_per": [1, RankOrder.descending],
    "_pbr": [1, RankOrder.descending],
    "_psr": [1, RankOrder.descending],
    "_pcr": [1, RankOrder.descending],
    // Quality factor
    "_roa": [0, RankOrder.descending],
    "_roe": [0, RankOrder.descending],
    "_ros": [0, RankOrder.descending],
    "_gpoa": [1, RankOrder.descending],
    // Momentum factor
    "_tsm12": [0, RankOrder.descending],
    "_tsm6": [0, RankOrder.descending],
    "_tsm3": [0, RankOrder.descending],
    // Size factor
    "_capsize": [0, RankOrder.ascending],

    /* Custom factors */
    "index1": [1, RankOrder.descending],
    "index2": [1, RankOrder.descending],
    "index3": [1, RankOrder.descending],
    "index4": [1, RankOrder.descending],
    "index5": [1, RankOrder.descending],
    "index6": [1, RankOrder.descending],
    "index7": [1, RankOrder.descending],
    "index8": [1, RankOrder.descending],
    "index9": [1, RankOrder.descending],
    "index10": [1, RankOrder.descending],
    "index11": [1, RankOrder.descending],
    "index12": [1, RankOrder.descending],
    "index13": [1, RankOrder.descending],
    "index14": [1, RankOrder.descending],
};


var FactorEval_portfolio7 = {
    // Custom factors

    "index1": function (stock) {
        var retValue = (stock.getFundamentalEV(0) / stock.getFundamentalEBITDA(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index2": function (stock) {
        var retValue = stock.getDividendYieldRatio(0);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index3": function (stock) {
        var retValue = ((stock.getFundamentalOperatingIncome(0) + stock.getFundamentalSellingExpense(0)) / stock.getFundamentalTotalAsset(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index4": function (stock) {
        var retValue = ((stock.getFundamentalOperatingIncome(0) + stock.getFundamentalSellingExpense(0)) / stock.getFundamentalTotalAsset(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index5": function (stock) {
        var retValue = ((stock.getFundamentalOperatingIncome(0) + stock.getFundamentalSellingExpense(0)) / stock.getFundamentalTotalAsset(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index6": function (stock) {
        var retValue = ((stock.getFundamentalOperatingIncome(0) + stock.getFundamentalSellingExpense(0)) / stock.getFundamentalTotalAsset(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index7": function (stock) {
        var retValue = ((stock.getFundamentalOperatingIncome(0) + stock.getFundamentalSellingExpense(0)) / stock.getFundamentalTotalAsset(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index8": function (stock) {
        var retValue = ((stock.getFundamentalOperatingIncome(0) + stock.getFundamentalSellingExpense(0)) / stock.getFundamentalTotalAsset(0));
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index9": function (stock) {
        var retValue = (stock.getAdjClose(0) / stock.getAdjClose(250) - 1);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index10": function (stock) {
        var retValue = (stock.getAdjClose(0) / stock.getAdjClose(250) - 1);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index11": function (stock) {
        var retValue = (stock.getAdjClose(0) / stock.getAdjClose(250) - 1);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index12": function (stock) {
        var retValue = (stock.getAdjClose(0) / stock.getAdjClose(250) - 1);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index13": function (stock) {
        var retValue = (stock.getAdjClose(0) / stock.getAdjClose(250) - 1);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

    "index14": function (stock) {
        var retValue = (stock.getAdjClose(0) / stock.getAdjClose(250) - 1);
        if (retValue === Infinity || isNaN(retValue)) {
            logger.debug('WARNING: 종목코드 ' + stock.code + '에 대한 지표값이 (' + retValue + ') 입니다. -99999999으로 대체합니다.');
            return -99999999;
        }
        return retValue;
    },

}


// Portfolio Builder
function builder_portfolio7(targetSize) {
    // 종목 필터 적용
    makeCapSizeRef(Filter_portfolio7);
    var universe = IQStock.filter(filterfn_portfolio7);

    // 종목선정 기본지표 및 사용자정의 지표 통합
    for (var property in FactorEval_default) {
        FactorEval_portfolio7[property] = FactorEval_default[property];
    }

    // 랭킹계산 전 팩터의 값들을 미리 setScore를 사용하여 넣어줍니다.
    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        for (var ind in FactorIndex_portfolio7) {
            if (FactorIndex_portfolio7[ind][0] === 0) {
                continue;
            }
            stock.setScore(ind, FactorEval_portfolio7[ind](stock));
        }
    }

    for (var i = 0; i < universe.length; i++) {
        var stock = universe[i];
        var total_rank = 0;

        for (var ind in FactorIndex_portfolio7) {
            if (FactorIndex_portfolio7[ind][0] === 0) {
                continue;
            } // factor 가중치 값이 0이면 계산하지 않고 넘어갑니다.

            var ind_rank = stock.getRank(universe, ind, FactorIndex_portfolio7[ind][1]);
            total_rank += FactorIndex_portfolio7[ind][0] * ind_rank;

        }
        stock.setScore("total_rank", total_rank);
    }

    var port_result = universe.slice().sort(function (a, b) {
        return a.getScore("total_rank") - b.getScore("total_rank");
    });

    port_result = port_result.filter(postfilterfn_portfolio7);
    port_result = port_result.slice(0, targetSize);

    return port_result;
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

    // 건전성 필터
    if (settings.noNegProfit && stock.getFundamentalNetProfit() <= 0) // 당기순손실 종목 제외
        return false;
    if (settings.noNegCashflow && stock.getFundamentalOperatingCashFlow() <= 0) // 영업현금흐름 (-)종목 제외
        return false;
    if (settings.noManaged && (stock.manage & 1)) // 관리종목 제외
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
        return (stock.getFundamentalNetProfit() * 4) / (stock.getMarketCapital() * 1000);
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
    }
}


IQEnvironment.stockCommission = 0.0015;
IQEnvironment.etfCommission = 0.0015;
IQEnvironment.stockTax = 0.003;
IQEnvironment.simulationMethod = SimulationMethod.average;

var BL_portfolio = [PORT_portfolio2, PORT_portfolio3, PORT_portfolio4, PORT_portfolio5, PORT_portfolio1, PORT_portfolio6, PORT_portfolio7];
var BL_builder = [builder_portfolio2, builder_portfolio3, builder_portfolio4, builder_portfolio5, builder_portfolio1, builder_portfolio6, builder_portfolio7];
var BL_basket = [];

function initialize() {

    for (var i = 0; i < BL_portfolio.length; i++) {
        var acc = IQAccount.getDefaultAccount();

        BL_basket[i] = new Basket(acc, 0, 0);
        BL_basket[i].setPortfolioBuilder(BL_builder[i]);
    }

    IQDate.addRebalSchedule(IQDate.setYearly(4, 1));
    IQDate.addRebalSchedule(IQDate.setYearly(6, 1));
    IQDate.addRebalSchedule(IQDate.setYearly(9, 1));
    IQDate.addRebalSchedule(IQDate.setYearly(12, 1));
}

var isFirst = true;

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

        isFirst = false;
    }
}

function onComplete() {
    var acc = IQAccount.getDefaultAccount();
    logger.debug('최종 계좌 평가액 : ' + IQUtil.getNumberWithCommas(acc.getTotalEquity().toFixed(2)));
    logger.debug('누적수수료= ' + IQUtil.getNumberWithCommas(acc.cumCommission.toFixed(2)) + ',  누적세금= ' + IQUtil.getNumberWithCommas(acc.cumTax.toFixed(2)) + ',  회전율= ' + Math.floor(acc.turnover * 100) + '%');

    for (var i = 0; i < BL_portfolio.length; i++) {
        IQLive.addPortfolio(BL_basket[i], BL_portfolio[i].weight());
    }
}