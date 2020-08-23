
#!pip install pytesseract


#!pip install regex


import pytesseract
import os
import random
import regex as re
import csv
import argparse
import sys
try:
	from PIL import Image
except ImportError:
	import Image
# import image clearing python script   
from . import scanner
import cv2


pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract' #r'C:\Program Files\Tesseract-OCR\tesseract.exe'


dict_from = {}
dict_to = {}
dict_price = {}
dict_date = {}
dict_time = {}
dict_passengers = {}
dict_per_price = {}


def levD(str1, str2):
	m = len(str1)
	n = len(str2)
	dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
	for i in range(m + 1):
		for j in range(n + 1):
			if i == 0:
				dp[i][j] = j
			elif j == 0:
				dp[i][j] = i
			elif str1[i-1] == str2[j-1]:
				dp[i][j] = dp[i-1][j-1]
			else:
				dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])

	return dp[m][n]


def find_dist(s1, s2):
	#s1 <= DB
	#s2 <= ext
	n = len(s2)
	m = len(s1)
	if(m<=3 or n<=3):
		return -1
	if m<n:
		return levD(s1,s2[:m])
	else:
		mini = n
		for i in range(m-n+1):
			str1 = s1[i:i+n]
			dist = levD(str1,s2)
			if(dist<mini):
				mini = dist
		return mini


def SearchInDB(str):
	str1 = ""
	for i in range(len(str)):
		if(str[i].isalnum()):
			str1 += str[i]
	str = str1.upper()
	res = ""
	if(len(str)<3):
		return res
	mini = len(str)
	ln = 100
	with open('bus_stations.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			dist = find_dist(row[0].upper(), str)
			#print(dist, row[0])
			if(dist != -1 and dist<mini and dist<len(row[0])):
				mini = dist
				res = row[0]
				ln = len(row[0])
			if(dist != -1 and dist==mini and dist<len(row[0]) and ln>len(row[0])):
				mini = dist
				res = row[0]
				ln = len(row[0])
	return res


allowed_chars = ['.', ':', '/', '-']


def clean_text(txt):
	res = ""
	for i in range(len(txt)):
		''' for cleaning price (sometimes '.' is read as ',' 
		, also to handle 1,500 like cases)'''
		if(txt[i] == ',' and i+2<len(txt)):
			if(txt[i+1]>='0' and txt[i+1]<='9' and txt[i+2]>='0' and txt[i+2]<='9'):
				if(i+3<len(txt) and txt[i+3]>='0' and txt[i+3]<='9'):
					continue
				else:
					res += '.'
					continue

		if(txt[i]=='\n'):
			res += '\n'
			continue

		# to remove unwanted special chars  
		cnt = 0         
		if(txt[i].isalnum() == False):
			for j in allowed_chars:
				if(txt[i] == j):
					res += txt[i]
					cnt = 1
					break
			if cnt == 0:
				res += ' '

		else:
			res += txt[i]

	return res




def clean_price(i):
	for j in range(len(i)):
		if(i[j]=='.'):
			break
	prc = (i[:j])

	return prc



def most_frequent(List): 
	return max(set(List), key = List.count)



def _regex(result,is_original):
	# 0 : from cleared_image and sure
	# 1 : from cleared_image but   not sure
	# 2 : from original_image and sure
	# 3 : from original_image and   not sure
	ext_from = 0
	ext_to = 0
	ext_price = 0
	ext_date = 0
	ext_time = 0
	ext_passengers = 0
	ext_per_price = 0

	From1 = re.search(r'(?P<From>([a-z]|[A-Z]|[0-9])+(.*))([t|T][o|O|0])', result)
	To1 = re.search(r'([t|T][o|O|0])(?P<To>(.*)([a-z]|[A-Z]|[0-9])+)', result)
	flgfr = 0
	flgTo = 0

	if not From1:
		From1 = re.search(r'(?P<From>([a-z]|[A-Z])+(.*))([1|t|T][o|O|0|D])', result)
		flgfr = 1
	if From1:
		From1 = From1.group('From')
		From2 = ""
		for i in range(len(From1)):
			if(From1[i].isalnum()):
				From2 += From1[i]

	if not To1:
		To1 = re.search(r'([1|t|T][o|O|0|D])(?P<To>(.*)([a-z]|[A-Z])+)', result)
		flgTo = 1
	if To1:
		To1 = To1.group('To')
		To2 = ""
		for i in range(len(To1)):
			if(To1[i].isalnum()):
				To2 += To1[i]
	
	if(From1):
		#print("From_initial: ", From2)
		From2_s = SearchInDB(From2)
		levDF = levD(str(From2_s), From2)
		if(flgfr!=0 or levDF>2):
			if is_original == 0:
				ext_from = 1
			else:
				ext_from = 3
			if levDF<2:
				dict_from[ext_from] = From2_s
			else: 
				dict_from[ext_from] = str(From2) 
		else:
			if is_original == 0:
				ext_from = 0
			else:
				ext_from = 2
			dict_from[ext_from] = From2_s
	else:
		if is_original == 0:
			ext_from = 1
		else:
			ext_from = 3
		dict_from[ext_from] = ""
	if(To1):
		#print("To_initial: ", len(To2))
		To2_s = SearchInDB(To2)
		levDT = levD(str(To2_s), To2)
		if(flgTo!=0 or levDT>2):
			if is_original == 0:
				ext_to = 1
			else:
				ext_to = 3
			if levDT<2:
				dict_to[ext_to] = To2_s
			else: 
				dict_to[ext_to] = str(To2)
		else:
			if is_original == 0:
				ext_to = 0
			else:
				ext_to = 2
			dict_to[ext_to] = To2_s
	else:
		if is_original == 0:
			ext_to = 1
		else:
			ext_to = 3
		dict_to[ext_to] = ""

		
	date =  re.search(r'[0-3][0-9]/[0|1][0-9]/[2]{0,1}[0]{0,1}[01|2][0-9]', result)
	chksum = 0
	if not date:
		chksum = 1
		date = re.search(r'[0-3][0-9]/[0|1][0-9]', result)
	if not date:
		chksum = 2
		date = re.search(r'[0|1][0-9]/[2]{0,1}[0]{0,1}[0|1|2][0-9]', result)
	if date:
		Format = ""
		if(chksum==0):
			ext_date = 0
			Format = "date/month/year"
		if(chksum==1):
			ext_date = 1
			Format = "date/month"
		if(chksum==2):
			ext_date = 1
			Format = "month/year"
		if is_original == 0:
			if chksum == 0:
				ext_date = 0
			else:
				ext_date = 1
		else:
			if chksum == 0:
				ext_date = 2
			else:
				ext_date = 3
		dict_date[ext_date] = str(date.group()) + "|" + Format
	else:
		if is_original == 0:
			ext_date = 1
		else:
			ext_date = 3
		dict_date[ext_date] = ""

		
		
	time = re.search(r'[0-2]{0,1}[0-9](:[0-5]{0,1}[0-9])+', result)
	if time:
		if is_original == 0:
			ext_time = 0
		else:
			ext_time = 2
		dict_time[ext_time] = str(time.group())
	else:
		if is_original == 0:
			ext_time = 1
		else:
			ext_time = 3
		dict_time[ext_time] = ""

		
		
	per_h_price = 0
	net_rate = 0
	total_travellers = 0
	per_head_price = re.search(r'([0-9]+)(.*?)([x|X|\*| ])(.*?)([0-9]+\.[0-9]+)', result)   
	total_price = re.findall(r'([0-9]+\.[0-9]+)', result)
	net_price = []
	for i in range(len(total_price)):
		net_price.append(clean_price(total_price[i]))
	if len(net_price) > 0 :
		net_rate =  most_frequent(net_price)
	
	if per_head_price and net_rate!=0 :
		per_h_price = clean_price(per_head_price.group(5))
		total_travellers = per_head_price.group(1)
		if( int(net_rate) == (int(total_travellers) * int(per_h_price)) ):
			if is_original == 0:
				ext_price = 0
				ext_passengers = 0
				ext_per_price = 0
			else:
				ext_price = 2
				ext_passengers = 2
				ext_per_price = 2
			dict_price[ext_price] = net_rate
			dict_passengers[ext_passengers] = total_travellers
			dict_per_price[ext_per_price] = per_h_price
		else:
			if is_original == 0:
				ext_price = 1
				ext_passengers = 1
				ext_per_price = 1
			else:
				ext_price = 3
				ext_passengers = 3
				ext_per_price = 3
			dict_price[ext_price] = net_rate 
			dict_passengers[ext_passengers] = ""
			dict_per_price[ext_per_price] = ""
	else:
		if is_original == 0:
			ext_price = 1
			ext_passengers = 1
			ext_per_price = 1
		else:
			ext_price = 3
			ext_passengers = 3
			ext_per_price = 3
		if net_rate!=0:
			dict_price[ext_price] = net_rate 
		else:
			dict_price[ext_price] = ""
		dict_passengers[ext_passengers] = ""
		dict_per_price[ext_per_price] = ""


def show_results():
	From = ""
	To = ""
	date = ""
	price = ""
	time = ""
	passengers = ""
	per_price = ""
	i0 = 0
	i1 = 1
	i2 = 2
	i3 = 3
	if i0 in dict_from.keys() and len(dict_from[i0])>0:
		From = dict_from[i0]
	elif i2 in dict_from.keys() and len(dict_from[i2])>0:
		From = dict_from[i2]
	elif i1 in dict_from.keys() and len(dict_from[i1])>0:
		From = dict_from[i1] + "  not sure"
	elif i3 in dict_from.keys() and len(dict_from[i3])>0:
		From = dict_from[i3] + "  not sure"
	print("From : ", From)
	if i0 in dict_to.keys() and len(dict_to[i0])>0:
		To = dict_to[i0]
	elif i2 in dict_to.keys() and len(dict_to[i2])>0:
		To = dict_to[i2]
	elif i1 in dict_to.keys() and len(dict_to[i1])>0:
		To = dict_to[i1] + "  not sure"
	elif i3 in dict_to.keys() and len(dict_to[i3])>0:
		To = dict_to[i3] + "  not sure"
	print("To : ", To)
	if i0 in dict_date.keys() and len(dict_date[i0])>0:
		date = dict_date[i0]
	elif i2 in dict_date.keys() and len(dict_date[i2])>0:
		date = dict_date[i2]
	elif i1 in dict_date.keys() and len(dict_date[i1])>0:
		date = dict_date[i1] + "  not sure"
	elif i3 in dict_date.keys() and len(dict_date[i3])>0:
		date = dict_date[i3] + "  not sure"
	print("Date : ", date)
	if i0 in dict_time.keys() and len(dict_time[i0])>0:
		time = dict_time[i0]
	elif i2 in dict_time.keys() and len(dict_time[i2])>0:
		time = dict_time[i2]
	print("Time : ", time)
	if i0 in dict_price.keys() and len(dict_price[i0])>0:
		price = dict_price[i0]
	elif i2 in dict_price.keys() and len(dict_price[i2])>0:
		price = dict_price[i2]
	elif i1 in dict_price.keys() and len(dict_price[i1])>0:
		price = dict_price[i1] + "     not sure"
	elif i3 in dict_price.keys() and len(dict_price[i3])>0:
		price = dict_price[i3] + "     not sure"
	print("Net price : ", price)
	if i0 in dict_passengers.keys() and len(dict_passengers[i0])>0:
		passengers = dict_passengers[i0]
		print("No. of travellers : ", passengers)
	elif i2 in dict_passengers.keys() and len(dict_passengers[i2])>0:
		passengers = dict_passengers[i2]
		print("No. of travellers : ", passengers)
	if i0 in dict_per_price.keys() and len(dict_per_price[i0])>0:
		per_price = dict_per_price[i0]
		print("Per head price : ", per_price)
	elif i2 in dict_passengers.keys() and len(dict_per_price[i2])>0:
		per_price = dict_per_price[i2]
		print("Per head price : ", per_price)
	
	data = {
		'response' : '1',
		'FromTo': From + ' To ' + To,
		'date' : date,
		'time' : time ,
		'PerHeadPrice' : per_price,
		'total_travellers' : passengers,
		'total_price' : price
	}
	return data



def create_arg_parser():
	parser = argparse.ArgumentParser(description='Description of your app.')
	parser.add_argument('image_path', help='Path to the input directory.')
	return parser


def Main(img_path):

	"""arg_parser = create_arg_parser()
	parsed_args = arg_parser.parse_args(sys.argv[1:])
	img_path = parsed_args.image_path"""


	scanner.Main(img_path)
	cleared_image = cv2.imread(img_path+'1.jpg')
	filtered_image = cv2.imread(img_path+'2.jpg')
	filtered_image_orig = cv2.imread(img_path+'3.jpg')
	result_original = pytesseract.image_to_string(Image.open(img_path))
	result_original = clean_text(result_original)
	result_clr = pytesseract.image_to_string(cleared_image)
	result_clr = clean_text(result_clr)
	result_fltr = pytesseract.image_to_string(filtered_image)
	result_fltr = clean_text(result_fltr)
	result_fltr_orig = pytesseract.image_to_string(filtered_image_orig)
	result_fltr_orig = clean_text(result_fltr_orig)
	#print(result_original)
	_regex(result_original,1)
	_regex(result_fltr_orig,1)	
	_regex(result_clr,0)
	_regex(result_fltr,0)
	os.remove(img_path+'1.jpg')
	os.remove(img_path+'2.jpg')
	os.remove(img_path+'3.jpg')
	return show_results()