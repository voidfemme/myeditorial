from bs4 import BeautifulSoup
from typing import List
import requests
import feedparser


class Post:
    def __init__(self, title: str, link: str, description: str) -> None:
        self.title = title
        self.link = link
        self.description = description

    def truncate_description(self, max_words=150) -> None:
        """Truncate summary to a maximum number of words"""
        words = self.description.split()
        if len(words) > max_words:
            self.description = " ".join(words[:max_words]) + "..."

    def generate_summary_from_website(self) -> None:
        """Generate a summary from the website's content"""
        try:
            response = requests.get(self.link)
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            summary = " ".join(p.text for p in paragraphs[:3])
            self.description = summary
        except requests.RequestException:
            self.description = "Unable to fetch summary from website"


class Feed:
    def __init__(
        self, title: str, website_link: str, feed_link: str, description: str
    ) -> None:
        self.title = title
        self.website_link = website_link
        self.feed_link = feed_link
        self.description = description
        self.posts = self.get_latest_posts()

    def get_latest_posts(self, num_posts=10) -> List[Post]:
        """Retrieve the latest posts from the feed"""
        feed = feedparser.parse(self.feed_link)
        posts = []

        for entry in feed.entries[:num_posts]:
            post = Post(
                title=entry.title, link=entry.link, description=entry.description
            )
            posts.append(post)

        return posts

    def generate_summary_from_website(self) -> None:
        """Generate a summary from the website's content"""
        try:
            response = requests.get(self.website_link)
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            summary = " ".join(p.text for p in paragraphs[:3])
            self.description = summary
        except requests.RequestException:
            self.description = "Unable to fetch summary from website"


class FeedParser:
    @staticmethod
    def extract_rss_feed_from_website(website_url: str) -> str:
        """Discover the RSS feed URL from a website's main page."""
        response = requests.get(website_url)
        soup = BeautifulSoup(response.content, "html.parser")
        link = soup.find("link", {"type": "application/rss+xml"})
        return link["href"] if link else ""

    @staticmethod
    def search_rss_feeds(keywords):
        """Search for RSS feeds based on keywords."""
        api_url = f"https://cloud.feedly.com/v3/search/feeds?query={keywords}"
        response = requests.get(api_url)
        feeds = response.json().get("results", [])
        return feeds

    @classmethod
    def create_feeds_from_search(cls, query: str) -> List[Feed]:
        feeds_data = cls.search_rss_feeds(query)
        feed_objects = []
        for feed_data in feeds_data:
            feed = Feed(
                title=feed_data.get("title"),
                website_link=feed_data.get("website"),
                feed_link=feed_data.get("feedId").replace("feed/", ""),
                description=feed_data.get("description", ""),
            )
            if not feed.description:
                feed.generate_summary_from_website()
            feed_objects.append(feed)

        return feed_objects
