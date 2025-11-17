import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime
import os
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'MergedNewsRSSBot/1.0 (+https://github.com/your-username/merged-news-rss)'}

SITES = [
    {
        "name": "Drop Site News",
        "url": "https://dropsitenews.com",
        "article_selector": "article",
        "title_selector": "h2 a, h3 a, .post-title a",
        "link_selector": "h2 a, h3 a, .post-title a",
        "desc_selector": ".excerpt, .summary, p",
        "base_url": "https://dropsitenews.com"
    },
    {
        "name": "Ground News Blindspot",
        "url": "https://ground.news/blindspot",
        "article_selector": ".story-card",
        "title_selector": ".story-title a",
        "link_selector": ".story-title a",
        "desc_selector": ".story-summary",
        "base_url": "https://ground.news"
    },
    {
        "name": "The Intercept",
        "url": "https://theintercept.com",
        "article_selector": ".post",
        "title_selector": "h3 a, .post-title a",
        "link_selector": "h3 a, .post-title a",
        "desc_selector": ".excerpt, .post-excerpt",
        "base_url": "https://theintercept.com"
    }
]

def fetch_site(site):
    try:
        r = requests.get(site["url"], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = []

        for art in soup.select(site["article_selector"])[:5]:  # 5 per site
            title_tag = art.select_one(site["title_selector"])
            link_tag = art.select_one(site["link_selector"])
            desc_tag = art.select_one(site["desc_selector"])

            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = urljoin(site["base_url"], link_tag['href'])
                desc = desc_tag.get_text(strip=True)[:300] + "..." if desc_tag else ""

                items.append({
                    "title": f"[{site['name']}] {title}",
                    "link": link,
                    "desc": desc,
                    "date": datetime.datetime.now().isoformat(),
                    "source": site["name"]
                })
        return items
    except:
        return []

def generate_rss(all_items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Merged News: Drop Site + Ground + Intercept"
    ET.SubElement(channel, "link").text = "https://github.com/your-username/merged-news-rss"
    ET.SubElement(channel, "description").text = "Auto-merged RSS for r/yourcommunity"
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Sort by date (newest first)
    for item in sorted(all_items, key=lambda x: x['date'], reverse=True):
        i = ET.SubElement(channel, "item")
        ET.SubElement(i, "title").text = item['title']
        ET.SubElement(i, "link").text = item['link']
        ET.SubElement(i, "description").text = f"<![CDATA[<strong>{item['source']}</strong><br>{item['desc']}]]>"
        ET.SubElement(i, "pubDate").text = item['date']
        ET.SubElement(i, "guid").text = item['link']

    rough = ET.tostring(rss, encoding='utf-8')
    return minidom.parseString(rough).toprettyxml(indent="  ")

def main():
    all_items = []
    for site in SITES:
        all_items.extend(fetch_site(site))
    
    rss_xml = generate_rss(all_items)
    os.makedirs("docs", exist_ok=True)
    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_xml)

if __name__ == "__main__":
    main()
