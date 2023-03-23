import requests

response = requests.get(
  url='https://proxy.scrapeops.io/v1/',
  params={
      'api_key': '19a71f07-5272-4fe2-8d2a-a6c780a82769',
      'url': 'https://www.revolico.com/insertar-anuncio.html', 
  },
)

print('Response Body: ', response.ok)