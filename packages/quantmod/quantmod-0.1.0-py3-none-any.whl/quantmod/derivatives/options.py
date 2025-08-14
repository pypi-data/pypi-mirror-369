# Maximum Pain Level
def maxpain(strike: list, calloi: list, putoi: list) -> float:
    """
    Calculate option max pain for a given range of strike price, call and put open interest
    Max pain is the (strike) price at which least amount of pain (money is lost) by
    option writers, thereby causing maximum pain to option buyers. This level 
    is assumed to be the price at which the market is most likely to expire on 
    the (derivatives) contract mautiry date.

    Parameters
    ----------
    strike : list
        list of strike prices
    calloi : list
        list of call open interest
    putoi : list
        list of put open interst

    Returns
    -------
    float
        maximum pain strike level
    """
    
    nrows = len(strike)
    cvalue = [0]*nrows
    pvalue = [0]*nrows
    tvalue = [0]*nrows

    for i in range(nrows-1, 0, -1):
        csum = 0
        for j in range(i):
            csum = csum + (strike[i] - strike[j]) * calloi[j]
            cvalue[i] = csum

    for i in range(nrows-1):
        psum = 0
        for j in range(i+1,nrows,1):
            psum = psum +  (strike[i] - strike[j]) * -1 * putoi[j]
            pvalue[i] = psum

    for i in range(nrows):
        tvalue[i] = cvalue[i] + pvalue[i]

    mp = min(tvalue)

    return strike[tvalue.index(mp)]
