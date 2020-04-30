from utils.zmqrelay import ZmqRelay 
import time
import zmq
# Sample data
examples = [
	{'pos': 1, 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/PvZgagfp/' },
	{'pos': 2, 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/62eFJCzI/' },
	{'pos': 3, 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/ljDfxMRq/' },
	{'pos': 4, 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/syJFgexD/' },
	{'pos': 5, 'id': time.time_ns(), 'url': 'https://www.tradingview.com/x/zTT81sRi/' },
]

z = ZmqRelay( 'tvchartinfo' )

for data in examples: 

	# Send Data
	z.send_msg( data )

	# Await / Receive data
	z.set_recv_timeout(5000)
	try:
		msg = z.receiver.recv()
		topic, msg = z.demogrify(msg.decode("utf-8"))
		print('{} - Received: {}'.format(data['pos'], msg))
	except:
		print('{} - Failed to receive any reply'.format(data['pos']))

