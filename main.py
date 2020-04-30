import os, sys, io, logging, re, requests, time, json, threading, queue
import coloredlogs, setproctitle, yaml, imutils, cv2, pytesseract
import numpy as np 
from PIL import Image
from pprint import pprint
from utils.zmqrelay import ZmqRelay 


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)
setproctitle.setproctitle('tvchartinfo')

global q 
q = queue.Queue()

global z 
z = ZmqRelay( 'tvchartinfo', server=True )


global PATH
PATH = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))


global config
config_file = "{}/config.yaml".format(PATH)
logger.info( "Loading config {}".format(config_file) ) 
with open(config_file) as fp:
	config = yaml.load(fp, Loader=yaml.BaseLoader)

config['ZMQ_PUBLISH_TO_PORT']   = int(config['ZMQ_PUBLISH_TO_PORT'])
config['MAX_NUMBER_OF_THREADS'] = int(config['MAX_NUMBER_OF_THREADS'])
config['THUMB_SMALL_WIDTH']     = int(config['THUMB_SMALL_WIDTH'])
config['THUMB_SMALL_HEIGHT']    = int(config['THUMB_SMALL_HEIGHT'])
config['PYTESSERACT_IMG_WIDTH'] = int(config['PYTESSERACT_IMG_WIDTH'])


def error(msg):
	logger.error(msg)


def parse_tv_url(url):
	response = {} 
	response['time_ns'] = time.time_ns()


	# Get link components
	regex_query = "(https:\/\/www\.tradingview\.com\/x\/([A-Za-z0-9]+)\/)"
	link_components = re.findall(r""+regex_query, url)

	if len(link_components) < 1:
		error('Unable to split link into components: {} -- {}'.format(url, link_components))
		return 
	else:
		response['url'] = url
		response['url_fname'] = link_components[0][1]



	# Get Image
	req_resp = requests.get(url)
	pil_image = Image.open(io.BytesIO(req_resp.content))

	response['input_tv_chart_fname'] = "{}_0_input_tv_chart".format( response['url_fname'] )
	response['input_tv_chart_ext']   = "png"
	response['input_tv_chart_fpath'] = "{}/charts/{}.{}".format( PATH, response['input_tv_chart_fname'], response['input_tv_chart_ext'] )
	response['input_tv_chart_width'], response['input_tv_chart_height'] = pil_image.size

	pil_image.save( response['input_tv_chart_fpath'] )



	# Save a thumbnail of it 
	response['thumb_small_fname'] = "{}_thumb_small".format( response['url_fname'] )
	response['thumb_small_ext']   = "png"
	response['thumb_small_fpath'] = "{}/charts/{}.{}".format( PATH, response['thumb_small_fname'], response['thumb_small_ext'] )
	response['thumb_small_width'] = str(config['THUMB_SMALL_WIDTH'])
	response['thumb_small_height'] = str(config['THUMB_SMALL_HEIGHT'])

	small_thumb = pil_image.resize((config['THUMB_SMALL_WIDTH'],config['THUMB_SMALL_HEIGHT']))
	small_thumb.save( response['thumb_small_fpath'] )



	# Crop bit cointaining text
	response['crop_fname'] = "{}_crop".format( response['thumb_small_fname'] )
	response['crop_ext']   = "png"
	response['crop_fpath'] = "{}/charts/{}.{}".format( PATH, response['crop_fname'], response['crop_ext'] )

	image = np.array(pil_image) 
	local_img = imutils.resize(image, width=1500)
	cv2.imwrite(
			"{}/charts/{}_local_.{}".format( PATH, response['crop_fname'], response['crop_ext'] )
			, local_img)
	# Exchange:Ticker, Timeframe, Price 
	crop_img = local_img[18:40, 0:400]
	# All top text data
	# crop_img = image[0:43, 0:700]
	cv2.imwrite(response['crop_fpath'], crop_img) 
	response['crop_height'], response['crop_width'], response['crop_channels'] = crop_img.shape


	# PYTessteract it 
	image = imutils.resize(crop_img, width=config['PYTESSERACT_IMG_WIDTH'])
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
	thresh = cv2.GaussianBlur(thresh, (3,3), 0)
	cv2.imwrite(
			"{}/charts/{}_thresh_.{}".format( PATH, response['crop_fname'], response['crop_ext'] )
			, thresh)
	data = pytesseract.image_to_string(crop_img, lang='eng',config='--psm 6')


	regex_query = '([A-Z_]+)[:]([A-Z.!0-9]+), ([0-9A-Z]+) ([0-9.]+)'
	chart_data_results = re.findall(r""+regex_query, data)
	if len(chart_data_results) < 1:
		error('Error: {}'.format(chart_data_results))
		return 

	response['exchange'], response['ticker'], response['timeframe'], response['price'] = chart_data_results[0]


	response['timeframe_formatted'] = response['timeframe']
	has_letter_in_tf = re.search('[a-zA-Z]', response['timeframe'])
	if has_letter_in_tf == None:
		minutes = int(response['timeframe'])
		if minutes >= 60:
			response['timeframe_formatted'] = "{:d}H".format( int(minutes/60) )

	return response






if __name__ == '__main__':

	# We maybe have a requested url to parse.. 
	if len(sys.argv) > 1: 
		response = parse_tv_url(url=sys.argv[1])
		pprint(response)


	else:

		def worker(q, multiplicity=5, maxlevel=3, lock=threading.Lock()):

			for task in iter(q.get, None):  # blocking get until None is received
				try:
					logger.info("Actioning job: {}, Thead {}".format(task, threading.current_thread().name))
					
					# try:
					response = parse_tv_url(task['url'])
					response['id'] = task['id']
					# except:
						# response = {}
						# response['error'] = 'Error in parsing TV URL'
						# logger.error(response['error'])

					z.send_msg( response )

				finally:
					q.task_done()

		threads = []
		for i in range(2):
			thread = threading.Thread(target=worker, args=[q], daemon=True).start()
			threads.append( thread ) 


		def process_zmq_inbound(q):

			while True:
				# Blocking 
				msg = z.receiver.recv()
				topic, msg = z.demogrify(msg.decode("utf-8"))
				print('Received: {}'.format(msg))

				if 'id' not in msg:
					logger.error('Missing unique id')
				else:
					q.put(msg)

		threading.Thread(target=process_zmq_inbound, args=[q], daemon=True).start()

		# Keep the script alive..
		while True:
			# Sleep for 5 minutes
			time.sleep( 60*5 )
			logger.info('ping')

