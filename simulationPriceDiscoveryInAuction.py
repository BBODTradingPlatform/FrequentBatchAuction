'''
Blockchain Board of Derivatives
by wonabru & BBOD team
The Simple MonteCarlo simulation of BBOD price discover
The Method of price discover is based on self-consistent method
The initial price is calculated as:
AuctionPrice = 0.5 * (Weighted buy price + Weighted sell price)

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

# function of auctionPrice calculation
def calculateAuctionPrice(priceVolumeTemp):
    sum = {}
    auctionPrice = {}
    for side in ["sell", "buy"]:

        # here we weight price with volume
        priceVolumeTemp[side]["priceVolume"] = np.multiply(priceVolumeTemp[side]["price"], priceVolumeTemp[side]["volume"])
        sum[side] = {"priceVolume": np.sum(priceVolumeTemp[side]["priceVolume"]), "volume": np.sum(priceVolumeTemp[side]["volume"])}

        # actionPrice is the weighted price with volume for sell and buy separetly
        auctionPrice[side] = sum[side]["priceVolume"]/sum[side]["volume"] if sum[side]["volume"] > 0 else 0 

        # We take average of weighted sell and buy price, also  it is returned volume generated in auction as the min value of sell and buy side
    return (auctionPrice["sell"] + auctionPrice["buy"])/2.0, min(sum["sell"]["volume"], sum["buy"]["volume"])

#here we initiate the global parameters
stablePriceCount = 0
auctionVolume = 0
totalVolume = 0

# parameter describes how large random numbers will be, so max = 2 ** noOfBitsInRandom
noOfBitsInRandom = 10
totalRounds = 1000  # here you can set how many rounds of MonteCralo you would like to run
for z in range(totalRounds):

    #just to show the progress
    if z%100 == 0:
        print("%.0f %% was done" % (z/totalRounds * 100))

    # this function gives random integers between 0 and 2 ** noOfBitsInRandom, here are total number of Sellers and Buyers in Auction
    totalNoUsers = {"sell": random.getrandbits(noOfBitsInRandom), "buy": random.getrandbits(noOfBitsInRandom)} 
    
    # here we generate random values (limit price and volume) for each user in Auction
    priceVolume = {}
    for side in ["sell", "buy"]:
        priceVolume[side] = {"price": [random.getrandbits(noOfBitsInRandom) for i in range(totalNoUsers[side])], 
                                "volume": [random.getrandbits(noOfBitsInRandom) for i in range(totalNoUsers[side])]}

        #we take into account both sides, so we have to divide by factor of 2
        totalVolume += np.sum(priceVolume[side]["volume"])/2.0
    
    # we initaite inital value of auctionPrice for the porpose if in the loop auctionPrice is changing
    previousAuctionPrice = 0

    #we calculate initAuctionPrice and volume taken place in this auction
    currentAuctionPrice, currentAuctionVolume = calculateAuctionPrice(priceVolume.copy())
    priceVolumeTemp = {}

    # self-consistent method main loop
    for no in range(100): 
        side = "sell"
        priceVolumeTemp[side] = {}
        priceAccepted = np.array([currentAuctionPrice>priceVolume[side]["price"]])

        # we prune offer prices of Makers (which should not be counted in auctionPrice). Only takers determine auctionPrice
        for type in ["price", "volume"]:
            if np.any(priceAccepted == True):
                priceVolumeTemp[side][type] = [priceVolume[side][type][i] for i in range(totalNoUsers[side]) if currentAuctionPrice > priceVolume[side]["price"][i]]
        
        side = "buy"
        priceVolumeTemp[side] = {}
        priceAccepted = np.array([currentAuctionPrice<priceVolume[side]["price"]])

        # we prune offer prices of Makers (which should not be counted in auctionPrice). Only takers determine auctionPrice
        for type in ["price", "volume"]:
            if np.any(priceAccepted == True):
                priceVolumeTemp[side][type] = [priceVolume[side][type][i] for i in range(totalNoUsers[side]) if currentAuctionPrice < priceVolume[side]["price"][i]]
        
        # here it is checked if there is both sell and buy side 
        if len(priceVolumeTemp["sell"]) + len(priceVolumeTemp["buy"]) == 4:
            currentAuctionPrice, currentAuctionVolume = calculateAuctionPrice(priceVolumeTemp.copy())
        else:

            # we break loop if it is only sellers or buyers
            currentAuctionPrice = 0
            break

        # we break loops becuase auctionPrice is not stable and does not gives correct value
        if currentAuctionPrice <= 0:
            break 

        # if the price was not further changed in loop, so get out of loop. Hurra, we have stable AuctionPrice !!!
        if currentAuctionPrice == previousAuctionPrice and previousAuctionPrice > 0:
            break 

        previousAuctionPrice = currentAuctionPrice
        #print("Final auction price: %f with volume = %f" % (currentAuctionPrice, currentAuctionVolume))

    # if AuctionPrice is above zero (so we found stable price). 
    # Also we check if the loop finished before reaching 100, means we truely find stable price. 
    # if q == 100, means the price is unstable or perdiodicaly changed.
    if currentAuctionPrice > 0 and no < 100:
        stablePriceCount += 1
        auctionVolume += currentAuctionVolume
    
#we print out statistics from MonteCarlo simulation
print("Percent of Stable Auction Price = %.2f %%, Percent of Stable Auction Volume = %.2f %%" % (stablePriceCount/totalRounds * 100, auctionVolume/totalVolume * 100))
sys.stdin.read(1)

