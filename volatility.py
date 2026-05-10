def calculate_volatility(data):
    # daily return = today's price vs yesterday's price (percentage change)
    data = data.copy()
    data['Returns'] = data['Close'].pct_change()
    data = data.dropna()
    
    # annualized volatility = std of daily returns * sqrt(252 trading days in a year)
    volatility = data['Returns'].std() * (252**0.5)
    return float(volatility)
