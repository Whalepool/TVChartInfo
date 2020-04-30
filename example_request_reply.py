from utils.zmqrelay import ZmqRelay 
import time
import zmq
# Sample data
data = {'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/PvZgagfp/' }

# Sample data with a 'big resolution' chart 
# data = {'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/62eFJCzI/' }

# Sample data with another type of chart
# data = { 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/ljDfxMRq/' }

# another
# data = { 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/syJFgexD/' }



z = ZmqRelay( 'tvchartinfo' )

# Send Data
z.send_msg( data )

# Await / Receive data
z.set_recv_timeout(5000)
try:
	msg = z.receiver.recv()
	topic, msg = z.demogrify(msg.decode("utf-8"))
	print('Received: {}'.format(msg))
except:
	print('Failed to receive any reply')

