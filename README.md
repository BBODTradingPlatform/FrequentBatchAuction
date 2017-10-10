Blockchain Board of Derivatives

The Simple MonteCarlo simulation of BBOD price discover

The Method of price discover is based on self-consistent method

The initial price is calculated as:

  deltaPrice = 0.5 * (Weighted buy price - Weighted sell price)
  
  AuctionPrice = Weighted sell price + deltaPrice

Next the self-consistent method started in loop:

  if buyersPrice > AuctionPrice then we count such a client price in next steps
  
also

  if sellersPrice < AuctionPrice then we count such a client price in next steps

  we recalculate AuctionPrice

if AuctionPrice was not changed then break loop

repeat up to 100 times

see file https://github.com/BBODTradingPlatform/FrequentBatchAuction/blob/master/simulationPriceDiscoveryInAuction.py
