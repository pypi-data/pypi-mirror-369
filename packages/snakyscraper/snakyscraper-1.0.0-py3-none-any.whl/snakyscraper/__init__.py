import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class SnakyScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None

        if not url or not isinstance(url, str) or not self._is_valid_url(url):
            return

        try:
            response = requests.get(url, timeout=10)
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except Exception:
            self.soup = None

    def _is_valid_url(self, url):
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])

    def title(self):
        return getattr(self.soup.title, 'string', None) if self.soup else None

    def charset(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', charset=True)
        return tag['charset'] if tag else None

    def viewport(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'viewport'})
        return tag['content'].split(",") if tag else None

    def viewport_string(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'viewport'})
        return tag['content'] if tag else None

    def canonical(self):
        if not self.soup:
            return None
        tag = self.soup.find('link', attrs={'rel': 'canonical'})
        return tag['href'] if tag else None

    def content_type(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'http-equiv': 'Content-Type'})
        return tag['content'] if tag else None

    def csrf_token(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'csrf-token'})
        if not tag:
            tag = self.soup.find('input', attrs={'name': 'csrf-token'})
            return tag.get('value') if tag else None
        return tag.get('content')

    def author(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'author'})
        return tag['content'] if tag else None

    def description(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'description'})
        return tag['content'] if tag else None

    def image(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'property': 'og:image'})
        return tag['content'] if tag else None

    def keywords(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'keywords'})
        return tag['content'].split(",") if tag else None

    def keyword_string(self):
        if not self.soup:
            return None
        tag = self.soup.find('meta', attrs={'name': 'keywords'})
        return tag['content'] if tag else None

    def open_graph(self, prop=None):
        if not self.soup:
            return None
        if prop:
            tag = self.soup.find('meta', attrs={'property': prop})
            return tag['content'] if tag else None

        props = ['og:site_name', 'og:type', 'og:title', 'og:description', 'og:url', 'og:image']
        return {p: (self.soup.find('meta', attrs={'property': p}) or {}).get('content') for p in props}

    def twitter_card(self, prop=None):
        if not self.soup:
            return None
        if prop:
            tag = self.soup.find('meta', attrs={'name': prop})
            return tag['content'] if tag else None

        props = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:url', 'twitter:image']
        return {p: (self.soup.find('meta', attrs={'name': p}) or {}).get('content') for p in props}

    def _tag_list(self, tag_name):
        if not self.soup:
            return None
        return [tag.text.strip() for tag in self.soup.find_all(tag_name)]

    def h1(self): return self._tag_list('h1')
    def h2(self): return self._tag_list('h2')
    def h3(self): return self._tag_list('h3')
    def h4(self): return self._tag_list('h4')
    def h5(self): return self._tag_list('h5')
    def h6(self): return self._tag_list('h6')
    def p(self): return self._tag_list('p')

    def ul(self):
        if not self.soup:
            return None
        items = []
        for ul in self.soup.find_all("ul"):
            items.extend([li.text.strip() for li in ul.find_all("li")])
        return items

    def ol(self):
        if not self.soup:
            return None
        items = []
        for ol in self.soup.find_all("ol"):
            items.extend([li.text.strip() for li in ol.find_all("li")])
        return items

    def images(self):
        if not self.soup:
            return None
        return [img.get("src") for img in self.soup.find_all("img")]

    def image_details(self):
        if not self.soup:
            return None
        return [{
            "url": img.get("src"),
            "alt_text": img.get("alt"),
            "title": img.get("title")
        } for img in self.soup.find_all("img")]

    def links(self):
        if not self.soup:
            return None
        return [a.get("href") for a in self.soup.find_all("a") if a.get("href")]

    def link_details(self):
        if not self.soup:
            return None
        result = []
        for a in self.soup.find_all("a"):
            href = a.get("href")
            rel = a.get("rel", [])
            result.append({
                "url": href,
                "protocol": href.split(':')[0] if href and ':' in href else '',
                "text": a.text.strip(),
                "title": a.get("title", ''),
                "target": a.get("target", ''),
                "rel": rel,
                "is_nofollow": 'nofollow' in rel,
                "is_ugc": 'ugc' in rel,
                "is_noopener": 'noopener' in rel,
                "is_noreferrer": 'noreferrer' in rel
            })
        return result

    def filter(self, element, attributes, multiple=False, extract=None, return_html=True):
        if not self.soup or not isinstance(attributes, dict):
            return None

        def extract_content_from_tag(tag, selectors):
            result = {}
            for sel in selectors:
                if sel.startswith('.'):
                    key = f'class__{sel[1:]}'
                    found = tag.find(attrs={"class": sel[1:]})
                elif sel.startswith('#'):
                    key = f'id__{sel[1:]}'
                    found = tag.find(attrs={"id": sel[1:]})
                else:
                    key = sel
                    found = tag.find(sel)
                result[key] = found.get_text(strip=True) if found else None
            return result

        try:
            if multiple:
                tags = self.soup.find_all(element, attributes)
                results = []
                for tag in tags:
                    if extract and isinstance(extract, list):
                        results.append(extract_content_from_tag(tag, extract))
                    else:
                        results.append(tag.get_text(strip=True) if not return_html else str(tag))
                return results
            else:
                tag = self.soup.find(element, attributes)
                if tag and extract and isinstance(extract, list):
                    return extract_content_from_tag(tag, extract)
                return tag.get_text(strip=True) if tag and not return_html else str(tag)
        except:
            return None
