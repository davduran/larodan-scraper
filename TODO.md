# Arquitectura del Web Scraper: Explicació i Millores

## Organització del Codi

L'organització del codi en diferents mòduls segueix els principis SOLID i les millors pràctiques de desenvolupament de programari. Aquesta estructura modular ens proporciona diversos avantatges:

### Models (models.py)
Aquest mòdul conté la definició de les estructures de dades utilitzant `dataclasses`. Hem separat els models perquè:
- Facilita la mantenibilitat del codi
- Permet la reutilització de les estructures de dades en altres parts del projecte
- Proporciona una interfície clara per a la manipulació de dades
- Facilita futures ampliacions o modificacions de l'estructura de dades

### Utils (utils.py)
El mòdul d'utilitats conté funcions auxiliars que:
- Són reutilitzables en diferents parts del codi
- No estan directament relacionades amb la lògica principal del scraping
- Proporcionen funcionalitats comunes com la configuració de logging o la gestió de directoris
- Faciliten el testing unitari de components individuals

### Scraper (scraper.py)
El component principal que:
- Implementa la lògica específica del web scraping
- Gestiona les connexions HTTP i les sessions
- Processa la informació obtinguda
- Coordina l'extracció i emmagatzematge de dades

### Main (__main__.py)
El punt d'entrada que:
- Gestiona els arguments de línia de comandes
- Inicialitza el scraper
- Proporciona una interfície simple per a l'usuari final

## Possibles Millores

### 1. Rotació d'Agents
```python
class UserAgentRotator:
    def __init__(self):
        self.agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        self.current = 0
    
    def get_next(self):
        agent = self.agents[self.current]
        self.current = (self.current + 1) % len(self.agents)
        return agent
```

### 2. Simulació de Comportament Humà
```python
class HumanBehaviorSimulator:
    async def random_delay(self):
        # Simula temps variable entre peticions
        delay = random.uniform(2, 5)
        await asyncio.sleep(delay)
    
    async def random_scroll(self):
        # Simula scroll aleatori
        scroll_amount = random.randint(100, 500)
        return f"window.scrollBy(0, {scroll_amount})"
```

### 3. Gestió de Proxies
```python
class ProxyManager:
    def __init__(self):
        self.proxies = [
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080'
        ]
        
    async def get_proxy(self):
        return random.choice(self.proxies)
        
    async def create_session(self):
        proxy = await self.get_proxy()
        return aiohttp.ClientSession(connector=
            aiohttp.TCPConnector(ssl=False),
            proxy=proxy)
```

### 4. Sistema de Cues i Rate Limiting
```python
class RequestQueue:
    def __init__(self, requests_per_minute=60):
        self.queue = asyncio.Queue()
        self.rate_limit = requests_per_minute
        self.last_request = 0
    
    async def add_request(self, url):
        await self.queue.put(url)
    
    async def get_request(self):
        # Esperar si s'ha superat el límit
        current_time = time.time()
        if current_time - self.last_request < (60 / self.rate_limit):
            await asyncio.sleep((60 / self.rate_limit))
        self.last_request = current_time
        return await self.queue.get()
```

### 5. Sistema de Retry i Circuit Breaker
```python
class RetryManager:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, func, *args):
        for attempt in range(self.max_retries):
            try:
                return await func(*args)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                delay = self.backoff_factor ** attempt
                await asyncio.sleep(delay)
```

### 6. Cache de Resultats
```python
class ResultCache:
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    async def get(self, key):
        if key in self.cache and time.time() < self.expiry[key]:
            return self.cache[key]
        return None
    
    async def set(self, key, value, ttl=3600):
        self.cache[key] = value
        self.expiry[key] = time.time() + ttl
```

## Implementació de les Millores

Per implementar aquestes millores, hauríem de:

1. Crear un nou mòdul `enhancements.py` amb totes aquestes classes
2. Modificar la classe `LarodanScraper` per utilitzar aquests components
3. Afegir configuració per cada millora al fitxer de configuració
4. Implementar logs i monitoratge per aquestes noves funcionalitats
5. Afegir tests unitaris per cada nou component
6. Documentar l'ús de cada nova funcionalitat

### Exemple d'Integració:

```python
class EnhancedScraper(LarodanScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_agents = UserAgentRotator()
        self.behavior = HumanBehaviorSimulator()
        self.proxy_manager = ProxyManager()
        self.request_queue = RequestQueue()
        self.retry_manager = RetryManager()
        self.cache = ResultCache()
    
    async def get_page_content(self, url):
        await self.behavior.random_delay()
        headers = {'User-Agent': self.user_agents.get_next()}
        return await self.retry_manager.execute_with_retry(
            super().get_page_content, url
        )
```

Aquesta arquitectura millorada proporcionaria:
- Major robustesa contra bloquejos
- Millor gestió dels recursos
- Major escalabilitat
- Més facilitat per mantenir i modificar el codi
- Millor monitoratge i control d'errors
