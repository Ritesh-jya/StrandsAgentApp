from dataclasses import dataclass
import re
from typing import List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from ..config import settings

ProductReview = tuple[str, str]


@dataclass
class ProductFeedback:
    product_name: str
    product_url: str
    asin: str
    reviews: List[ProductReview]


class AmazonFeedbackTool:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": settings.AMAZON_USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Referer": f"https://www.amazon.{settings.AMAZON_COUNTRY_CODE}/",
                "DNT": "1",
            }
        )
        self.base_url = f"https://www.amazon.{settings.AMAZON_COUNTRY_CODE}"

    def _get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=settings.AMAZON_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response

    def _extract_asin(self, url: str) -> Optional[str]:
        match = re.search(r"/(?:dp|gp/product|gp/aw/d|gp/offer-listing)/([A-Z0-9]{10})(?:[/?]|$)", url)
        if match:
            return match.group(1)

        try:
            response = self._get(url)
            text = response.text
            match = re.search(r"data-asin=\"([A-Z0-9]{10})\"", text)
            if match:
                return match.group(1)
            match = re.search(r"\"ASIN\"\s*[:=]\s*\"([A-Z0-9]{10})\"", text)
            if match:
                return match.group(1)
        except requests.RequestException:
            return None

        return None

    def _resolve_product_url(self, url: str) -> Optional[str]:
        try:
            response = self._get(url)
            if response.url and response.url != url:
                return response.url
        except requests.RequestException:
            return None
        return url

    def _format_review(self, review_element: BeautifulSoup) -> Optional[ProductReview]:
        body_element = review_element.select_one("span[data-hook='review-body']")
        if body_element is None:
            body_element = review_element.select_one("span.a-size-base.review-text.review-text-content")
        
        rating_element = review_element.select_one("i[data-hook='review-star-rating'] span")
        if rating_element is None:
            rating_element = review_element.select_one("i.a-icon.a-icon-star span")
        if rating_element is None:
            rating_element = review_element.select_one("span.a-icon-alt")
        
        if body_element is None or rating_element is None:
            return None

        body_text = " ".join(body_element.stripped_strings)
        if not body_text:
            return None
        
        rating_text = rating_element.get_text(strip=True)
        return rating_text, body_text

    def _search_first_product(self, product_name: str) -> Optional[str]:
        search_url = f"{self.base_url}/s?k={quote_plus(product_name)}"
        response = self._get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        for selector in [
            "a.a-link-normal.a-text-normal",
            "a.a-link-normal.s-no-outline",
            "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal",
        ]:
            result_link = soup.select_one(selector)
            if result_link is not None and result_link.get("href"):
                href = result_link.get("href", "").split("?")[0]
                product_url = urljoin(self.base_url, href)
                resolved = self._resolve_product_url(product_url)
                if resolved:
                    return resolved

        result_item = soup.select_one("div[data-asin]")
        if result_item is not None:
            asin = result_item.get("data-asin")
            if asin:
                link = result_item.select_one("a.a-link-normal.a-text-normal") or result_item.select_one("a.a-link-normal[href*='/dp/']")
                if link is not None and link.get("href"):
                    href = link.get("href", "").split("?")[0]
                    product_url = urljoin(self.base_url, href)
                    resolved = self._resolve_product_url(product_url)
                    if resolved:
                        return resolved
                return f"{self.base_url}/dp/{asin}"

        for item in soup.select("div[data-component-type='s-search-result']"):
            anchor = item.select_one('a[href*="/dp/"]') or item.select_one('a[href*="/gp/product/"]') or item.select_one('a[href*="/gp/aw/d/"]')
            if anchor is not None and anchor.get("href"):
                href = anchor.get("href", "").split("?")[0]
                product_url = urljoin(self.base_url, href)
                resolved = self._resolve_product_url(product_url)
                if resolved:
                    return resolved

        for anchor in soup.select('a[href*="/dp/"]') + soup.select('a[href*="/gp/product/"]') + soup.select('a[href*="/gp/aw/d/"]'):
            href = anchor.get("href", "").split("?")[0]
            if "/dp/" in href or "/gp/product/" in href or "/gp/aw/d/" in href:
                product_url = urljoin(self.base_url, href)
                resolved = self._resolve_product_url(product_url)
                if resolved:
                    return resolved

        pattern = re.compile(r"/(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})")
        match = pattern.search(response.text)
        if match:
            return f"{self.base_url}/dp/{match.group(1)}"

        return None

    def _load_reviews_for_asin(self, asin: str) -> List[ProductReview]:
        product_page = f"{self.base_url}/gp/product/{asin}/"
        response = self._get(product_page)
        soup = BeautifulSoup(response.text, "html.parser")
        raw_reviews: List[ProductReview] = []

        review_elements = soup.select("div[data-hook='review']")
        if not review_elements:
            review_elements = soup.select("div.a-section.a-spacing-none.a-spacing-top-mini.a-row")

        for review_element in review_elements[:5]:
            formatted_review = self._format_review(review_element)
            if formatted_review:
                raw_reviews.append(formatted_review)

        return raw_reviews

    def fetch_feedback(self, product_name: str) -> ProductFeedback:
        product_url = self._search_first_product(product_name)
        if not product_url:
            raise ValueError("Unable to locate a product page for this name on Amazon.in.")

        asin = self._extract_asin(product_url)
        if not asin:
            raise ValueError(f"Found product page but could not identify ASIN from {product_url}.")

        reviews = self._load_reviews_for_asin(asin)
        if not reviews:
            raise ValueError(f"Unable to extract review snippets from Amazon.in for ASIN {asin}.")

        return ProductFeedback(
            product_name=product_name,
            product_url=product_url,
            asin=asin,
            reviews=reviews,
        )
