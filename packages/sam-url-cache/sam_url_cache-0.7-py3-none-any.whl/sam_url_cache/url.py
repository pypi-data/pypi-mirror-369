import requests
import logging
from .cache import _URLCacheDB
import random

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(name)s: %(message)s'
)

USER_AGENTS = [
    # Chrome variants
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Apple M1 Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    
    # Internet Explorer
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
    
    # Firefox variants
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:116.0) Gecko/20100101 Firefox/116.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:114.0) Gecko/20100101 Firefox/114.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
]

BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'DNT': '1',
}

class URLCache:
    def __init__(self, database_path: str = 'url_cache.db'):
        self.url_cache_db = _URLCacheDB(database_path)

    def get_url(self, url: str) -> str:
        check = self.url_cache_db.get(url)
        if check is None:
            live = self.__get_url(url)
            self.url_cache_db.put(url, live)
            return live
        return check

    def __get_url(self, url: str) -> str:
        headers = BASE_HEADERS.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)
        output = requests.get(url, headers=headers)
        if output.status_code == 403:
            logger.error("403: Access Denied")
            raise Exception("403: Access Denied")
        if output.status_code == 429:
            raise Exception("429: Too Many Requests")
        if output.status_code == 200:
            return output.text
        logger.error("Unknown Exception: %s", output.status_code)
        raise Exception("Unknown Exception: " + str(output.status_code))

    def seen_before(self, url: str) -> bool:
        check = self.url_cache_db.get(url)
        if check is None:
            return False
        return True
    
    def delete_url(self, url: str) -> None:
        self.url_cache_db.delete(url)

if __name__ == '__main__':
    raise Exception("Do not run this directly.")