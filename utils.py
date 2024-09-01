import random
def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_random_languages():
    accept_languages = [
        'en-US,en;q=0.5',
        'fr-FR,fr;q=0.9,en;q=0.5',
        'de-DE,de;q=0.9,en;q=0.5',
        'es-ES,es;q=0.9,en;q=0.5',
        'it-IT,it;q=0.9,en;q=0.5',
        'ja-JP,ja;q=0.9,en;q=0.5'
    ]
    return random.choice(accept_languages)

def get_random_referers():
    referers = [
        'https://www.google.com',
        'https://www.bing.com',
        'https://www.duckduckgo.com',
        'https://www.yahoo.com',
        'https://www.baidu.com'
    ]
    return random.choice(referers)

def get_random_connection():
    connections = ['keep-alive', 'close']
    return random.choice(connections)

def get_headers():
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
        'Accept-Language': get_random_languages(),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': get_random_connection(),
        'Referer': get_random_referers()}  