# TradingView Chart Info

Multi threaded trading view chart information extractor.

### Requirements
python > 3.8  
a 'zmq proxy' as cited in readme [here](https://github.com/Whalepool/Dispatchers)   

### Setup
Add to cron (this will just delete images older than 10mins) 
```bash
*/5 * * * * find /path/to/TVChartInfo/charts/ -mindepth 1 -mmin +10 -delete
```

### Usage example #1 as a stand alone app
```bash 
# Execute a test against a specific url 
python main.py https://www.tradingview.com/x/PvZgagfp/

# Output
{
	'crop_channels': 3,
	'crop_ext': 'png',
	'crop_fname': 'PvZgagfp_thumb_small_crop',
	'crop_fpath': '/path/to/TVChartInfo/charts/PvZgagfp_thumb_small_crop.png',
	'crop_height': 20,
	'crop_width': 200,
	'exchange': 'BITTREX',
	'input_tv_chart_ext': 'png',
	'input_tv_chart_fname': 'PvZgagfp_0_input_tv_chart',
	'input_tv_chart_fpath': '/path/to/TVChartInfo/charts/PvZgagfp_0_input_tv_chart.png',
	'input_tv_chart_height': 898,
	'input_tv_chart_width': 1560,
	'price': '0.00000092',
	'thumb_small_ext': 'png',
	'thumb_small_fname': 'PvZgagfp_thumb_small',
	'thumb_small_fpath': '/path/to/TVChartInfo/charts/PvZgagfp_thumb_small.png',
	'thumb_small_height': '650',
	'thumb_small_width': '1200',
	'ticker': 'FTCBTC',
	'time_ns': 1587979678920626505,
	'timeframe': '1M', 
	'timeframe_formatted': '1M',
	'url': 'https://www.tradingview.com/x/PvZgagfp/',
	'url_fname': 'PvZgagfp'
 }
```  
  
### Usage example #2 as a micro service   
```bash 
# Run the script as a zmq listening process
python main.py 

# You can initiate a request / reply example using 
python example_request_reply.py 
```  
  
![icon](https://i.imgur.com/rj5F5zf.png)