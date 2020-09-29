from MetaTrader5 import initialize, account_info, shutdown
initialize()

account = account_info()
print(account)

shutdown()