import requests

apikey=""
a = requests.get("https://api.dell.com/support/v2/assetinfo/warranty/tags.json?svctags=3P3JR32&apikey="+apikey)