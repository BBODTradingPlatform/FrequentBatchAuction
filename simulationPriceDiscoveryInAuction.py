'''
Blockchain Board of Derivatives
by wonabru & BBOD team
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

repeat up tp 100 times
'''
import numpy as np
import random
import sys

stablePriceCount = 0
stableVolumeCount = 0
totalPriceCount = 0
totalVolumeCount = 0
finalAuctionpriceList = []
finalnoPartiesList = []
totalnoPartiesList = []
totalRounds = 1000  # here you can set how many rounds of MonteCralo you would like to run
for z in range(totalRounds):
    if z%100 == 0:
        print("%f %% was done" % (z/totalRounds * 100))
    totalPartiesSELL = random.getrandbits(8) # this function gives random integers between 0 and 255, here is total number of SELLers in Auction
    totalPartiesBUY = random.getrandbits(8) # total number of BUYers in auction
    xlistSELL = []
    for i in range(totalPartiesSELL):
        xlistSELL.append([random.getrandbits(8), random.getrandbits(8)]) # first number is the SELL price and second in list is just volume to SELL price all ranges randomly from 0 to 255
    xlistBUY = []

    for i in range(totalPartiesBUY):
        xlistBUY.append([random.getrandbits(8), random.getrandbits(8)]) # first number is the BUY price and second in list is just volume to BUY price
   
    xsumSELL = 0
    xsumBUY = 0
    volumeBUY = 0
    volumeSELL = 0
    for i in range(len(xlistSELL)):
        xsumSELL += xlistSELL[i][0] * xlistSELL[i][1] # weighted (by volume) sum of SELL price
        volumeSELL += xlistSELL[i][1] # sum of volume on SELL side

    for i in range(len(xlistBUY)):
        xsumBUY += xlistBUY[i][0] * xlistBUY[i][1] #weighted (by volume) sum of BUY price
        volumeBUY += xlistBUY[i][1] # sum of volume on BUY side

    totalVolumeCount += volumeBUY + volumeSELL # sum of all sums of volume SELL and BUY side only just for use in statistics
    totalPriceCount += 1 # in the end will be just totalRounds

    if volumeBUY > 0 and volumeSELL > 0: # just to check that we not divide by zero
        dxprice = (xsumSELL/volumeSELL - xsumBUY/volumeBUY) / 2.0 # deltaPrice (see the beginning of file)
        xprice = xsumSELL/volumeSELL + dxprice #calculate of initial price (see AuctionPrice at introduction on beginning of file)
    else:
        xprice = 0
    xpricecurrent = 0
    for q in range(100): # self-consistent method main loop
        if xpricecurrent == 0:
            xpricecurrent = xprice # just initialization of price
        else:
            xprice = xpricecurrent
        xsumSELL = 0
        xsumBUY = 0
        volumeBUY = 0
        volumeSELL = 0
        noPartiesSELL = 0
        noPartiesBUY = 0
        for i in range(len(xlistBUY)):
            if xpricecurrent < xlistBUY[i][0]: # just check if buyers limit price is above auction price, so then he is taker, in other case he is maker
                xsumBUY += xlistBUY[i][0] * xlistBUY[i][1]
                volumeBUY += xlistBUY[i][1]
                noPartiesBUY += 1
        for i in range(len(xlistSELL)):
            if xpricecurrent > xlistSELL[i][0]: # just check if seller limit price is below auction price, so then he is taker, in other case he is maker
                xsumSELL += xlistSELL[i][0] * xlistSELL[i][1]
                volumeSELL += xlistSELL[i][1]
                noPartiesSELL += 1

        
        if volumeBUY > 0 and volumeSELL > 0:
            dxprice = (xsumBUY/volumeBUY - xsumSELL/volumeSELL) / 2.0 # temporary deltaPrice 
            xpricecurrent = xsumSELL/volumeSELL + dxprice # temporary AuctionPrice in self-consistent method loop
        else:
            xpricecurrent = 0;
            xprice = 0
            break # if there is no buyers or no sellers just self-consistent method fail to find stable price
        if xprice == xpricecurrent:
            break # if the price was not further changed in loop, so get out of loop. Hurra, we have stable AuctionPrice !!!

      #  print("Current auction price: %f with volumeBUY = %f and volumeSell = %f" % (xpricecurrent, volumeBUY, volumeSELL))
   # print("no of SELL clients = %f [%%], no of BUY clients = %f [%%]" % (noPartiesSELL/totalPartiesSELL * 100, noPartiesBUY/totalPartiesBUY * 100))

    if xpricecurrent > 0 and q < 100: # if AuctionPrice is above zero (so we found stable price). Also we check if the loop finished before reaching 100, means we truely find stable price. if q == 100, means the price is unstable or perdiodicaly changed.
        stablePriceCount += 1
        finalnoPartiesList.append(noPartiesSELL/totalPartiesSELL * 50 + noPartiesBUY/totalPartiesBUY * 50)
        totalnoPartiesList.append(totalPartiesSELL + totalPartiesBUY )
        finalAuctionpriceList.append(xpricecurrent)
        if volumeSELL > volumeBUY:
            stableVolumeCount += volumeBUY
        else:
            stableVolumeCount += volumeSELL

  #  print("Final auction price: %f with volumeBUY = %f and volumeSell = %f" % (xpricecurrent, volumeBUY, volumeSELL))
print(finalAuctionpriceList) # list of all final stable prices in Auction
print("Stable Price = %f [%%], Stable Volume = %f [%%]" % (stablePriceCount/totalPriceCount * 100, stableVolumeCount/totalVolumeCount * 2 * 100))
print("Average Price = %f, SD of price = %f" % (np.mean(finalAuctionpriceList), np.std(finalAuctionpriceList)))  
print("Average no of takers = %f [%%], SD of no of takers = %f [%%]" % (np.mean(finalnoPartiesList), np.std(finalnoPartiesList)))
print("Average no of clients = %f, SD of no of clients = %f" % (np.mean(totalnoPartiesList), np.std(totalnoPartiesList)))
sys.stdin.read(1)

