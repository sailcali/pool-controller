import requests

def logging(string=None):
        
        result = requests.post("http://192.168.86.205/pool/notification", json={"message":string})
        result.close()