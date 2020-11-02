

def isacquisitionsignal(values):
    # [val, mean, bollup, bolldown, index]
    curr = values[0]
    prev_1 = values[1]

    #current value is LOWER than BollDown
    #previous value is LOWER than BollDown
    #and current value is bigger than previous value
    #and distance of curr value to lower band is smaller than n times distance to upper band
    #and distance beteween bands is higher than a percent of the value
    isas =  ((curr[0]<curr[3])
             and (prev_1[0]<prev_1[3])
             and (prev_1[0]<curr[0])
             and (2*abs(curr[0]-curr[3])<(abs(curr[2]-curr[0])))
             and ((curr[2]-curr[3])>(0.03*curr[0])))

    return isas


def issalesignal(values):
    # [val, mean, bollup, bolldown, index]
    curr = values[0]
    prev_1 = values[1]
    # current value is LOWER than BollUp
    # previous value is HIGHER than BollUp
    # and current value is lower than previous value
    isas = ((curr[0] < curr[2]) and (prev_1[0] > prev_1[2]) and (prev_1[0] > curr[0]))
    return isas


