from abc import abstractmethod
from tor_request.clients import RequestsClient
from tor_request.types import RequestsClientConfig


def _validate_port(port: int):
    """포트가 9011~9091 범위이고 1로 끝나는지 검증."""
    if not (9011 <= port <= 9091):
        raise ValueError(f"포트 {port}는 9011~9091 범위여야 합니다.")
    if port % 10 != 1:
        raise ValueError(f"포트 {port}는 1로 끝나야 합니다.")


def shared_request_config(port=9031) -> RequestsClientConfig:
    """포트 유효성 검증 후 해당 포트에 맞는 RequestsClientConfig 생성."""
    _validate_port(port)

    proxy_port = port - 1  # 프록시 포트는 control_port - 1
    proxies = {
        "http": f"socks5h://127.0.0.1:{proxy_port}",
        "https": f"socks5h://127.0.0.1:{proxy_port}"
    }

    return RequestsClientConfig(
        control_port=port,
        proxies=proxies
    )

class Get:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr/"
        }
        self.rc = RequestsClient(config=shared_request_config(9031))

    def read(self, **params):
        resp = self.rc.request_with_retry(url=self.url, headers=self.headers, params=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError

class Post:
    def __init__(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://data.krx.co.kr/"
        }
        if headers is not None:
            self.headers.update(headers)

        self.rc = RequestsClient(config=shared_request_config(9031))

    def read(self, **params):
        resp = self.rc.request_with_retry(url=self.url, method="post", headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError
