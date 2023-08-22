from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List, Optional, Union
import json
import requests
import feedparser


class Post:
    def __init__(self, title: str, link: str, description: str) -> None:
        self.title = title
        self.link = link
        self.description = description

    def __repr__(self) -> str:
        return f"{self.title}, {self.link}, {self.description}"

    def __str__(self) -> str:
        return f"{self.title}, {self.link}, {self.description}"

    def truncate_description(self, max_words=150) -> None:
        """Truncate summary to a maximum number of words"""
        if not self.description:
            self.description = "No description available"
            return

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
        if description == "":
            self.generate_summary_from_website()
        else:
            self.description = description
        self.posts = self.get_latest_posts()

    def __str__(self) -> str:
        return f"title: {self.title}, website_link: {self.website_link}, \
        feed_link: {self.feed_link}, description: {self.description}, {len(self.posts)} posts"

    def get_latest_posts(self, num_posts=10) -> List[Post]:
        """Retrieve the latest posts from the feed"""
        try:
            feed = feedparser.parse(self.feed_link)
            posts = []

            for entry in feed.entries[:num_posts]:
                post = Post(
                    title=entry.title, link=entry.link, description=entry.description
                )
                posts.append(post)

            return posts
        except Exception as e:
            print(f"Error fetching posts for feed {self.feed_link}: {e}")
            return []

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
    def extract_rss_feed_from_website(website_url: str) -> list[str]:
        """Discover the RSS feed URL from a website's main page."""
        response = requests.get(website_url)
        soup = BeautifulSoup(response.content, "html.parser")
        link: Optional[Union[Tag, NavigableString]] = soup.find(
            "link", {"type": "application/rss+xml"}
        )
        if isinstance(link, Tag):
            href_value = link["href"]
            if isinstance(href_value, list):
                return href_value
            else:
                return [href_value]
        else:
            return []

    @staticmethod
    def search_rss_feeds(keywords):
        """Search for RSS feeds based on keywords."""
        api_url = f"https://cloud.feedly.com/v3/search/feeds?query={keywords}"
        response = requests.get(api_url)
        feeds = response.json().get("results", [])
        return feeds

    @classmethod
    def discover_feeds(cls, query: str) -> List[Feed]:
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

    @classmethod
    def load_feeds_from_file(cls, file_path: str) -> List[Feed]:
        """Load feeds from a specified source file"""
        with open(file_path, "r") as file:
            data = json.load(file)
            sources = data.get("sources", [])

            feed_objects = []
            for source in sources:
                feed = Feed(
                    title=source.get("title"),
                    website_link=source.get("website_link", ""),
                    feed_link=source.get("feedId"),
                    description=source.get("description", ""),
                )
                feed_objects.append(feed)

        return feed_objects
