import re
from urllib.parse import urlparse

class NMIEndpoint:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"Endpoint(IP: {self.ip}, Port: {self.port})"

    def __repr__(self):
        return f"Endpoint(ip='{self.ip}', port={self.port})"

    def is_valid(self) -> bool:
        return self.is_valid_ip() and self.is_valid_port()

    def is_valid_ip(self) -> bool:
        import re
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not pattern.match(self.ip):
            return False
        
        parts = self.ip.split('.')
        return all(0 <= int(part) < 256 for part in parts)

    def is_valid_port(self) -> bool:
        return 0 <= self.port <= 65535
    
    @classmethod
    def from_url(cls, url: str):
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        
        if not host or port is None:
            raise ValueError("Geçersiz URL: IP adresi veya port bulunamadı.")
        
        if not cls.is_valid_ip_address(host):
            raise ValueError("Geçersiz IP adresi.")
        
        if not (0 <= port <= 65535):
            raise ValueError("Geçersiz port numarası.")
        
        return cls(ip=host, port=port)
    
    @staticmethod
    def is_valid_ip_address(ip: str) -> bool:
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not pattern.match(ip):
            return False
        
        parts = ip.split('.')
        return all(0 <= int(part) < 256 for part in parts)

    def to_string(self) -> str:
        return f"http://{self.ip}:{self.port}/"