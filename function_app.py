import datetime
import logging
import azure.functions as func
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

app = func.FunctionApp()
class MyWrapper(EWrapper):
    def __init__(self):
        self.positions = []

    def position(self, account, contract, position, avg_cost):
        self.positions.append({
            "account": account,
            "symbol": contract.symbol,
            "position": position,
            "avg_cost": avg_cost
        })

@app.schedule(schedule="0 0 0 1 1 *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def CheckValues(myTimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    wrapper = MyWrapper()
    client = EClient(wrapper)
    
    # Connect to the IBKR trading server (use paper trading account for testing)
    client.connect("127.0.0.1", 5000, clientId=0)

    # Verify that the connection is established
    if client.isConnected():
        # Request account positions
        client.reqPositions()

        # Wait for positions to be received (you can implement an event handler for this)
        client.run()  # This will process incoming messages and populate the positions list

        # Find the position for SVIX
        svix_position = next((pos for pos in wrapper.positions if pos["symbol"] == "SVIX"), None)

        if svix_position:
            print(f"Symbol: {svix_position['symbol']}")
            print(f"Position: {svix_position['position']}")
        else:
            print("SVIX position not found in the account.")

        # Disconnect from the IBKR trading server
        client.disconnect()
    else:
        print("Connection to IBKR failed.")