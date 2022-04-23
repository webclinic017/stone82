var stockBasket;
var defaultAccount;
var stockBasketROA;
var accountROA;
var stockWeight = 0.95;	//주식 비율
var targetSize = 36		// 36 종목

function initialize() {
    IQEnvironment.simulationMethod = SimulationMethod.day;
    defaultAccount = IQAccount.getDefaultAccount();
    defaultAccount.accountName = "마법공식#3 (ROC+EY)";
    accountROA = IQAccount.addAccount('0000-0000-02', '마법공식#2 (ROA+PER)', IQEnvironment.aum);
    
    stockBasket = new Basket(defaultAccount, targetSize, IQEnvironment.aum * stockWeight);
	stockBasketROA = new Basket(accountROA, targetSize, IQEnvironment.aum * stockWeight);    
	
    stockBasket.setPortfolioBuilder(stockPortfolioBuilder);
    stockBasketROA.setPortfolioBuilder(stockPortfolioBuilderROA);    
}

function getPER(stock) {
	if (stock.getClose() === 0 || stock.getFundamentalNetProfit() === 0) return -1;
    
	stock.loadPrevData(0, 14, 0);
    //PER역순
	return (stock.getFundamentalNetProfit(0) + stock.getFundamentalNetProfit(1) + stock.getFundamentalNetProfit(2) + stock.getFundamentalNetProfit(3)) / stock.getMarketCapital();
}

function getROA(stock) {
    if (stock.getFundamentalTotalAsset() === 0) return -1;
    
    stock.loadPrevData(0, 14, 0);
    return (stock.getFundamentalNetProfit(0) + stock.getFundamentalNetProfit(1) + stock.getFundamentalNetProfit(2) + stock.getFundamentalNetProfit(3)) / stock.getFundamentalTotalAsset();
}

function getROC(stock) {
    stock.loadPrevData(0, 14, 0);    
    return (stock.getFundamentalEBIT(0) + stock.getFundamentalEBIT(1) + stock.getFundamentalEBIT(2) + stock.getFundamentalEBIT(3)) 
    / ((stock.getFundamentalCurrentAsset() - stock.getFundamentalCurrentLiability()) + (stock.getFundamentalNonLiquidAsset() - stock.getFundamentalDepreciationCost()));
}

function getEY(stock) {    
    stock.loadPrevData(0, 14, 0);
	return (stock.getFundamentalEBIT(0) + stock.getFundamentalEBIT(1) + stock.getFundamentalEBIT(2) + stock.getFundamentalEBIT(3)) 
    / stock.getFundamentalEV();
}

function stockFilter(stock) {
    if (stock.market != 1 || stock.isETF || stock.manage & 1 || stock.manage & 4 
        || stock.getFundamentalTotalAsset() == 0 || stock.getClose() == 0) return false;	//코스닥, ETF, 관리종목, 거래정지, 우선주 제외
    
	var filterMarketCapital = (stock.getMarketCapital() > 500000); // 시가총액 5000억 이상 기준
    var filterTradingValue = (stock.getTradingValue() > 500);   // 일거래대금 5억 이상 기준
    
	return (filterMarketCapital && filterTradingValue);
}

function stockPortfolioBuilderROA(targetSize) {
	var universe = IQStock.filter(stockFilter);
	var sortedByPER = universe.slice().sort(function(a, b) { return getPER(b) - getPER(a); });
    var sortedByROA = universe.slice().sort(function(a, b) { return getROA(b) - getROA(a); });
    
    universe.forEach(function(stock) {
        stock.setScore('rank_sum', sortedByPER.indexOf(stock) + sortedByROA.indexOf(stock));         
    });
    
    var factorRank = universe.slice().sort(function(a, b) { return a.getScore('rank_sum') - b.getScore('rank_sum'); });     
    return factorRank.slice(0, targetSize);
}

function stockPortfolioBuilder(targetSize) {
	var universe = IQStock.filter(stockFilter);
	var sortedByROC = universe.slice().sort(function(a, b) { return getROC(b) - getROC(a); });
    var sortedByEY = universe.slice().sort(function(a, b) { return getEY(b) - getEY(a); });
    
    universe.forEach(function(stock) {
        stock.setScore('rank_sum', sortedByROC.indexOf(stock) + sortedByEY.indexOf(stock)); 
    });
    
    var factorRank = universe.slice().sort(function(a, b) { return a.getScore('rank_sum') - b.getScore('rank_sum'); });     
    return factorRank.slice(0, targetSize);
}

var lastYear = 0;

function onDayClose(now) {
    if (lastYear == 0 || (now.getMonth() == 3 && now.getFullYear() != lastYear)) { 
        stockBasket.setBudget(defaultAccount.getTotalEquity() * stockWeight);
		stockBasket.buildPortfolio();
        
        stockBasketROA.setBudget(accountROA.getTotalEquity() * stockWeight);
        stockBasketROA.buildPortfolio();        
        
        lastYear = now.getFullYear();
	}
}

