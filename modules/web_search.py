"""
VISION AI Assistant - Web Search Module
Real-time info: weather, news, price comparison, general search.
"""
import requests
from bs4 import BeautifulSoup
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
