// R Coins ICO

pragma solidity ^0.4.25;

contract rcoin_ico {

    // Introducing the maximum number of Rcoins available for sale
    uint public max_rcoins = 1000000;

    // Introducing the USD to Rcoins conversion rate
    uint public usd_to_rcoins = 1000;

    // Introducing the total number of Rcoins that have been bought by the investors
    uint public total_rcoins_bought = 0;

    // Mapping from the investor address to its equity in Rcoins and USD
    mapping(address => uint) equity_rcoins;
    mapping(address => uint) equity_usd;

    // Checking if an investor can buy Rcoins
    modifier can_buy_rcoins(uint usd_invested) {
        require (usd_invested * usd_to_rcoins + total_rcoins_bought <= max_rcoins);
        _; // the underscore only does the modifier if the condition is true
    }

    // Getting the equity in Rcoins of an investor
    function equity_in_rcoins(address investor) external constant returns (uint) {
        return equity_rcoins[investor];
    }

    // Getting the equity in USD of an investor
    function equity_in_usd(address investor) external constant returns (uint) {
        return equity_usd[investor];
    }

    // Buying Rcoins
    function buy_rcoins(address investor, uint usd_invested) external
    can_buy_rcoins(usd_invested) {
        uint rcoins_bought = usd_invested * usd_to_rcoins;
        equity_rcoins[investor] += rcoins_bought;
        equity_usd[investor] = equity_rcoins[investor] / 1000;
        total_rcoins_bought += rcoins_bought;
    }

    // Selling Rcoins
    function sell_rcoins(address investor, uint rcoins_toSell) external {
        equity_rcoins[investor] -= rcoins_toSell;
        equity_usd[investor] = equity_rcoins[investor] / 1000;
        total_rcoins_bought -= rcoins_toSell;
    }
}
