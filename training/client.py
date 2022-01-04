import requests

url = 'http://20.107.24.221:5000/predict'
files = {'image':  open('test_images/testing.png', 'rb')}

x = requests.post(url, files= files)

print(x.text)
