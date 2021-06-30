import requests

url = 'https://us-central1-proyecto-final-cloud-318204.cloudfunctions.net/fxConsultaVideo'
myobj = {'keyword': 'cars'}

x = requests.post(url, data = myobj)

print(x.text)