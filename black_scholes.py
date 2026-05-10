import math
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    
    # d1 = measures how far the stock price is from strike price, adjusted for time and risk
    d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    
    # d2 = d1 adjusted for volatility over time, used to find probability of profit
    d2 = d1 - sigma*math.sqrt(T)
    
    if option_type == 'call':
        # call price = current stock value - discounted strike price (right to BUY)
        price = S*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
    else:
        # put price = discounted strike price - current stock value (right to SELL)
        price = K*math.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
    
    return price, d1, d2
