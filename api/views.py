
from django.http import JsonResponse
import base64
from django.views.decorators.csrf import csrf_exempt
#from PIL import Image
from io import BytesIO
import hashlib 
import time 
import io
import pytesseract
import os
import random
import regex as re
import csv
from .extractdata import ocr_regex
try:
    from PIL import Image
except ImportError:
    import Image

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


@csrf_exempt
def index(request):
    data = ''

    try:
        img_file = request.FILES['image']
        image = img_file.read()
        name = request.POST.get('ext')
        string_time = 'data'
        target_file = string_time + "." + name
        print(target_file)
        image = Image.open(io.BytesIO(image))
        image.save(target_file,name)
        data = ocr_regex.Main(target_file)
    except:
        print('No post data!')
        #result = pytesseract.image_to_string(Image.open('bustkt/2.jpeg'))
        data = {
            'response' : '0',
            'name': 'Nitin',
            'entryno':'2017csb1093',
            'active':'true',
        }
    return JsonResponse(data)