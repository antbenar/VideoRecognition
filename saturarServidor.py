import requests

url = 'https://www.w3schools.com/python/demopage.php'
myobj = {'keyword': 'cars'}

x = requests.post(url, data = myobj)

print(x.text)