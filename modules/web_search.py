"""
VISION AI Assistant - Web Search Module
Real-time info: weather, news, price comparison, general search.
"""
import requests
from bs4 import BeautifulSoup
import urllib.parse
import config
from modules.web_browser import open_website


def get_weather(city: str = None) -> str:
    """Get current weather using wttr.in (no API key needed)."""
    city = city or config.WEATHER_CITY or "auto"

    try:
        # Use wttr.in for simple weather (no API key needed)
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10, headers={"User-Agent": "VISION-AI"})

        if response.status_code == 200:
            data = response.json()
            current = data.get("current_condition", [{}])[0]
            area = data.get("nearest_area", [{}])[0]

            city_name = area.get("areaName", [{}])[0].get("value", city)
            country = area.get("country", [{}])[0].get("value", "")
            temp_c = current.get("temp_C", "N/A")
            feels_like = current.get("FeelsLikeC", "N/A")
            desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
            humidity = current.get("humidity", "N/A")
            wind_speed = current.get("windspeedKmph", "N/A")
            wind_dir = current.get("winddir16Point", "")

            weather_report = (
                f"[WEATHER] {city_name}, {country}:\n"
                f"  > Temperature: {temp_c} C (Feels like {feels_like} C)\n"
                f"  > Condition: {desc}\n"
                f"  > Humidity: {humidity}%\n"
                f"  > Wind: {wind_speed} km/h {wind_dir}"
            )

            # Add forecast if available
            forecast = data.get("weather", [])
            if len(forecast) >= 2:
                tomorrow = forecast[1]
                weather_report += (
                    f"\n\n  > Tomorrow: {tomorrow.get('mintempC', '?')} C - {tomorrow.get('maxtempC', '?')} C"
                )

            return weather_report
        else:
            return f"Could not get weather data. Status: {response.status_code}"

    except Exception as e:
        return f"Weather error: {str(e)}"


def get_news(topic: str = None) -> str:
    """Get latest news headlines by scraping Google News."""
    try:
        if topic:
            url = f"https://news.google.com/search?q={topic.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
        else:
            url = "https://news.google.com/topstories?hl=en-IN&gl=IN&ceid=IN:en"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=10, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article titles
            articles = []
            for article in soup.find_all('article')[:10]:
                title_elem = article.find('a', class_=True)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:
                        articles.append(title)

            if articles:
                topic_label = f" on '{topic}'" if topic else ""
                header = f"[NEWS] Latest headlines{topic_label}:\n"
                news_list = "\n".join([f"  {i+1}. {a}" for i, a in enumerate(articles[:8])])
                return header + news_list
            else:
                # Fallback - open in browser
                open_website(url)
                return f"Opening Google News in browser{' for: ' + topic if topic else ''}"
        else:
            open_website(url)
            return "Opened Google News in browser"

    except Exception as e:
        # Fallback to browser
        if topic:
            open_website(f"https://news.google.com/search?q={topic.replace(' ', '+')}")
        else:
            open_website("https://news.google.com/")
        return f"Opened Google News in browser (API error: {str(e)})"


def compare_prices(product: str) -> str:
    """Compare prices across e-commerce platforms by opening search pages."""
    platforms = {
        "Amazon": f"https://www.amazon.in/s?k={product.replace(' ', '+')}",
        "Flipkart": f"https://www.flipkart.com/search?q={product.replace(' ', '+')}",
        "Myntra": f"https://www.myntra.com/{product.replace(' ', '-')}",
        "Croma": f"https://www.croma.com/searchB?q={product.replace(' ', '+')}",
    }

    results = [f"[PRICE CHECK] {product}\n"]
    results.append("Opening search results on multiple platforms:\n")

    opened = 0
    for platform, url in platforms.items():
        try:
            result = open_website(url)
            results.append(f"  [+] {platform}: Opened")
            opened += 1
        except Exception:
            results.append(f"  [-] {platform}: Failed to open")

    if opened > 0:
        results.append(f"\nOpened {opened} platforms. Compare the prices and let me know if you need help!")
    else:
        results.append("\nCould not open any platforms. Check your internet connection.")

    return "\n".join(results)


def web_search(query: str) -> str:
    """Search the internet using DuckDuckGo HTML search and return top results."""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error searching the web: HTTP Status {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for result in soup.find_all('div', class_='result')[:5]:
            title_elem = result.find('a', class_='result__url')
            snippet_elem = result.find('a', class_='result__snippet')
            if title_elem and snippet_elem:
                title = title_elem.get_text(strip=True)
                raw_link = title_elem['href']
                
                # Resolve DuckDuckGo redirect link to direct URL
                link = raw_link
                if "uddg=" in raw_link:
                    try:
                        parsed = urllib.parse.urlparse(raw_link)
                        query_params = urllib.parse.parse_qs(parsed.query)
                        actual_url = query_params.get("uddg", [None])[0]
                        if actual_url:
                            link = actual_url
                    except Exception:
                        pass
                
                if link.startswith("//"):
                    link = "https:" + link
                    
                snippet = snippet_elem.get_text(strip=True)
                results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}\n")
        
        if not results:
            return "No results found on the web."
            
        return "\n".join(results)
    except Exception as e:
        return f"Error executing web search: {str(e)}"


def read_webpage(url: str) -> str:
    """Fetch the text content of a web page and return it."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} trying to fetch the page."

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts, styles, metadata, navigation, headers, footers
        for s in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
            s.decompose()

        # Extract text from paragraphs, list items, and headers
        chunks = []
        for elem in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
            text = elem.get_text(strip=True)
            if text and len(text) > 10:
                chunks.append(text)

        # Join and truncate content
        content = "\n".join(chunks)
        max_chars = 4000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n... [Content Truncated due to size] ..."
        
        return content if content.strip() else "The webpage did not contain any readable text content."
    except Exception as e:
        return f"Error reading page {url}: {str(e)}"

