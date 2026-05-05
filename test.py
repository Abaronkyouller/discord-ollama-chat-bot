import requests
from bs4 import BeautifulSoup


url = "https://www.weather25.com/europe/germany/hesse/darmstadt?page=today"

def access_another_link(url):
    try:
        res = requests.get(url=url, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        text = " ".join(text.split())[:3000]
        print(text)

    except Exception as e:
        print("error")

print(access_another_link(url))