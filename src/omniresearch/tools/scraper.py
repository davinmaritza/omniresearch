"""Web scraper utility for extracting clean article text from target URLs."""

import httpx
from bs4 import BeautifulSoup


def scrape_url_content(url: str, timeout: float = 10.0, max_chars: int = 5000) -> str | None:
    """Fetch and extract cleaned text content from an HTTP(S) URL."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove non-content tags
            for tag in soup(
                ["script", "style", "nav", "footer", "header", "noscript", "aside", "svg"]
            ):
                tag.decompose()

            # Extract text from paragraphs and headings
            blocks = []
            for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
                txt = elem.get_text().strip()
                if len(txt) > 20:
                    blocks.append(txt)

            text = "\n\n".join(blocks).strip()
            if text:
                return text[:max_chars]
    except Exception as exc:
        print(f"[OmniResearch Scraper Warning] Failed to scrape {url}: {exc}")
    return None
