#!/usr/bin/python3

import re
import requests
import feedparser

def get_rss_from_youtube_url(youtube_url):
    response = requests.get(youtube_url)
    if response.status_code != 200:
        return None
    
    html = response.text

    match = re.search(
        r'<link rel="canonical" href="https://www.youtube.com/channel/(UC[0-9A-Za-z_-]{22})"',
        html
    )
    if match:
        channel_id =  match.group(1)
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    else:
        return None

def is_valid_feed(url):
    feed = feedparser.parse(url)

    # .bozo == True indica que houve erro ao analisar o feed (malformado, etc)
    if feed.bozo:
        return False

    # também podemos verificar se há entradas
    if not feed.entries:
        return False

    return True

def parse_url(url):
    if "youtube" in url: 
        url = get_rss_from_youtube_url(url)
    
    
    if is_valid_feed(url):
        return url
    else:
        return None


if __name__ == "__main__":
    # URL do canal com @handle
    url = "https://www.youtube.com/@untioblancoendirecto6814"
    url = "https://www.xataka.com/feedburner.xml"

    url = parse_url(url)

    feed = feedparser.parse(url)

    # Título e descrição do feed
    print("TÍTULO DO FEED:", feed.feed.get("title", "Sem título"))
    print("DESCRIÇÃO DO FEED:", feed.feed.get("subtitle", "Sem descrição"))
    print("\n" + "=" * 50 + "\n")

    # Exibindo as entradas
    for j, entry in enumerate(feed.entries[:2]):  # pegar as 5 últimas notícias
        print(f"Título{j}:", entry.title)
        print("Link:", entry.link)
        print("Resumo:", entry.summary)
        print("Publicado em:", entry.published)
        print("\n" + "-" * 50)


