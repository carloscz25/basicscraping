

def isacquisitionsignal(values):
    # [val, mean, bollup, bolldown, index]
    curr = values[0]
    prev_1 = values[1]
    prev_2 = values[2]
    #current value is greater than BollDown
    #and current value is lower than mean and lower than BollUp
    #and current BollDown is greater than previous value
    isas =  ((curr[0]>curr[3] and curr[0] < curr[1] and curr[0] < curr[2]) and prev_1[0]<curr[3])
    return isas

def issalesignal(values):
    # [val, mean, bollup, bolldown, index]
    curr = values[0]
    prev_1 = values[1]
    prev_2 = values[2]
    # current value is lower than BollUp
    # and current value is bigger than mean and bigger than BollDown
    # and current BollUp is lower than previous value
    isas = ((curr[0] < curr[2] and curr[0] > curr[1] and curr[0] > curr[3]) and prev_1[0] > curr[2])
    return isas

def calculate_rsi(values, previousrsi):
