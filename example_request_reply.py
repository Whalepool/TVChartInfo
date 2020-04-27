from utils.zmqrelay import ZmqRelay 
import time

# Sample data
data = {'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/PvZgagfp/' }


z = ZmqRelay( 'tvchartinfo' )

# Send Data
z.send_msg( data )

# Await / Receive data
msg = z.receiver.recv()
topic, msg = z.demogrify(msg.decode("utf-8"))
print('Received: {}'.format(msg))