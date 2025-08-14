import requests
from .NMIEndpoint import NMIEndpoint

class NMICommand:
    def __init__(self, endpoint: NMIEndpoint, prefix: str, command: str, payload: dict = None):
        self.endpoint = endpoint
        self.prefix = prefix
        self.command = command
        self.payload = payload if payload is not None else {}

    def get_url(self) -> str:
        """Komut URL'sini oluşturur."""
        return f"{self.endpoint.to_string()}{self.prefix}/{self.command}"

    def execute_get(self)->dict:
        """GET isteği yapar ve yanıtı döner."""
        url = self.get_url()
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                _responseJson = response.json()
                if("ResponseStatus" in _responseJson):
                    if(_responseJson["ResponseStatus"]==False):
                        try:
                            print(_responseJson["message"])
                        except:
                            pass             
                return _responseJson 
            else:             
                return None
        except requests.RequestException as e:
            return None

    def execute_post(self):
        """POST isteği yapar ve yanıtı döner."""
        url = self.get_url()
        try:
            response = requests.post(url, json=self.payload)
            status_code = response.status_code
            if status_code == 200:
                _responseJson = response.json()
                if("ResponseStatus" in _responseJson):
                    if(_responseJson["ResponseStatus"]==False):
                        try:
                            print(_responseJson["message"])
                        except:
                            pass             
                return _responseJson 
            else:                
                return None
        except requests.RequestException as e:
            return None

# Kullanım örneği
if __name__ == "__main__":
    # NMIEndpoint nesnesi oluştur
    endpoint = NMIEndpoint("192.168.10.53", 9024)

    # NMICommand nesnesi oluştur
    command = NMICommand(endpoint, "APP", "Get_Commands", {"key": "value"})

    # GET isteği örneği
    get_response = command.execute_get()
    if get_response:
        print("GET yanıtı:", get_response)
    else:
        print("GET isteği başarısız oldu.")

    ## POST isteği örneği
    #post_response = command.execute_post()
    #if post_response:
    #    print("POST yanıtı:", post_response)
    #else:
    #    print("POST isteği başarısız oldu.")