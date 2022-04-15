var basket1, basket2; // 주식 종목들을 관리하는 Basket 객체
var account1, account2;
var stock_num = 20;             // 주식 종목 수
var stock_weight = 0.95;        // 주식 비중 (거래비용 고려 현금 5% 확보)
var valueRatio = 0.2;           // 저평가된 상위 20%만 취한다 
var isFirst = true;
//초기화 함수 
function initialize() {
    account1 = IQAccount.getDefaultAccount();
    account1.accountName = "1. 절대적 소형주";
    basket1 = new Basket(account1, stock_num, IQEnvironment.aum * stock_weight);
    account2 = IQAccount.addAccount('0000-0000-02', '2. 절대적 가치주', IQEnvironment.aum);
    basket2 = new Basket(account2, stock_num, IQEnvironment.aum * stock_weight);
    IQDate.addRebalSchedule(IQDate.setMonthlyStart(1));
}
//number형에서 null을 0으로 고침
function nvl(value) {
    if (value === null) { return 0; }
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
// ROA 구하기 
function roa(stock) {
    return stock.getROA();
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
// 3) 필터링 함수 정의 - 필터링 조건에 따라 종목들의 포함 여부 판단
function stockFilter(stock) {
    if (stock.getMarketCapital() === 0 || stock.getClose() === 0 || stock.getTradingValue() === 0) { return false; } //시총 없는 종목 제외, 종가가 0인 종목 제외, 거래정지 중인 종목 제외   
    if (stock.getFundamentalTotalAsset() === 0 || stock.getFundamentalTotalEquity() === 0) { return false; }      // ETF, 우선주 제외(자산총계가 없음)
    if (stock.manage > 0) { return false; }                           // 관리종목, 투자유의종목 제외

    if (stock.getFundamentalCapitalStock() > stock.getFundamentalTotalEquity()) { return false; } //자본잠식 제외      
    return true;
}

function port_Small(universe, stock_number) {
    var sortedBySmallCap = universe.slice().sort(function (a, b) { return cap(a) - cap(b); });  // 종목들을 시가총액 값의 오름차순으로 정렬
    var smallCap = sortedBySmallCap.slice(0, Math.floor(sortedBySmallCap.length / 5));       // 시가총액 하위 20%
    var sortedBybp = smallCap.slice().sort(function (a, b) { return bp(b) - bp(a); });
    var sortedByroa = smallCap.slice().sort(function (a, b) { return roa(b) - roa(a); });
    var sortedBypir = smallCap.slice().sort(function (a, b) { return pir(b) - pir(a); });

    smallCap.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedBybp.indexOf(stock)
            + sortedByroa.indexOf(stock)
            + sortedBypir.indexOf(stock)
        );
    });

    var Port_Rank = smallCap.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    return Port_Rank.slice(0, stock_number);
}

function port_Value(universe, stock_number) {
    var sortedByroa = universe.slice().sort(function (a, b) { return roa(b) - roa(a); });
    var sortedBybp = universe.slice().sort(function (a, b) { return bp(b) - bp(a); });
    var sortedBypir = universe.slice().sort(function (a, b) { return pir(b) - pir(a); });

    universe.forEach(function (stock) {
        stock.setScore('rank_sum',
            sortedBybp.indexOf(stock)
            + sortedByroa.indexOf(stock)
            + sortedBypir.indexOf(stock)
        );
    });

    var Port_Rank = universe.slice().sort(function (a, b) {
        return a.getScore('rank_sum') - b.getScore('rank_sum');
    });
    var port_cut = Port_Rank.slice(0, Math.floor(Port_Rank.length * valueRatio));

    var sortedByCap = port_cut.slice().sort(function (a, b) { return cap(a) - cap(b); });
    return sortedByCap.slice(0, stock_number);
}
//시장 절대 모멘텀 측정 (1년)
function Momentum_Universe(Universe) {
    var momentumPort = Universe.slice().filter(function (stock) {
        stock.loadPrevData(0, 16, 0);
        if (stock.getAdjClose(0) >= stock.getAdjClose(250)) { return true; }     // 1년 모멘텀 음수 제외 혹은 1년 이내 신규종목 제외
        return false;
    });
    return momentumPort.length / Universe.length;
}
//주식 비중만큼 매수 
function Port_Control(basket, account, universe, AI_stockWeight) {
    var TotalEquity = account.getTotalEquity();                         //전체 예산
    var stock_Budget = (TotalEquity * AI_stockWeight) / universe.length; //종목당 예산
    basket.reset();
    universe.forEach(function (stock) {
        var quantity = Math.floor(stock_Budget / stock.getAdjClose()); //동일비중 수량 (종목당 예산 / 수정종가)       
        basket.enter(stock, quantity);
    });
}
// 리밸런싱 수행 
function onDayClose(now) {
    if (IQDate.isRebalancingDay(now) || isFirst === true) {
        var universe = IQStock.filter(stockFilter);
        var momentum_value = Momentum_Universe(universe);

        var port_small = port_Small(universe, stock_num);
        var port_value = port_Value(universe, stock_num);

        Port_Control(basket1, account1, port_small, stock_weight);
        Port_Control(basket2, account2, port_value, stock_weight); //시장이 결정한 비율에 최근 한달 모멘텀을 더해준다

        isFirst = false;
    }
}