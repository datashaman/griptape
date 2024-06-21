import re
from typing import Optional
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver
from griptape.utils import import_optional_dependency


@define
class MarkdownifyWebScraperDriver(BaseWebScraperDriver):
    """Driver to scrape a webpage and return the content in markdown format.

    As a prerequisite to using MarkdownifyWebScraperDriver, you need to install the browsers used by
    playwright. You can do this by running: `poetry run playwright install`.
    For more details about playwright, see https://playwright.dev/python/docs/library.

    Attributes:
        include_links: If `True`, the driver will include link urls in the markdown output.
        exclude_tags: Optionally provide custom tags to exclude from the scraped content.
        exclude_classes: Optionally provide custom classes to exclude from the scraped content.
        exclude_ids: Optionally provide custom ids to exclude from the scraped content.
        timeout: Optionally provide a timeout in milliseconds for the page to continue loading after
            the browser has emitted the "load" event.
    """

    DEFAULT_EXCLUDE_TAGS = ["script", "style", "head"]

    include_links: bool = field(default=True, kw_only=True)
    exclude_tags: list[str] = field(
        default=Factory(lambda self: self.DEFAULT_EXCLUDE_TAGS, takes_self=True), kw_only=True
    )
    exclude_classes: list[str] = field(default=Factory(list), kw_only=True)
    exclude_ids: list[str] = field(default=Factory(list), kw_only=True)
    timeout: Optional[int] = field(default=None, kw_only=True)

    def scrape_url(self, url: str) -> TextArtifact:
        try:  # TODO: hack for graceful erroring
            # find a local file where the name is a hash of the url
            # if it exists, return the contents of the file
            # if it doesn't exist, scrape the url and save the contents to the file
            # return the contents of the file
            import os
            import hashlib

            hashed_name = hashlib.md5(url.encode()).hexdigest()
            if os.path.exists(f"cached_webscraper_output/{hashed_name}.txt"):
                with open(f"cached_webscraper_output/{hashed_name}.txt") as f:
                    return TextArtifact(f.read())

            sync_playwright = import_optional_dependency("playwright.sync_api").sync_playwright
            BeautifulSoup = import_optional_dependency("bs4").BeautifulSoup
            MarkdownConverter = import_optional_dependency("markdownify").MarkdownConverter

            include_links = self.include_links

            # Custom MarkdownConverter to optionally linked urls. If include_links is False only
            # the text of the link is returned.
            class OptionalLinksMarkdownConverter(MarkdownConverter):
                def convert_a(self, el, text, convert_as_inline):
                    if include_links:
                        return super().convert_a(el, text, convert_as_inline)
                    return text

            with sync_playwright() as p:
                with p.chromium.launch(headless=True) as browser:
                    page = browser.new_page()

                    def skip_loading_images(route):
                        if route.request.resource_type == "image":
                            return route.abort()
                        route.continue_()

                    page.route("**/*", skip_loading_images)

                    page.goto(url)

                    # Some websites require a delay before the content is fully loaded
                    # even after the browser has emitted "load" event.
                    if self.timeout:
                        page.wait_for_timeout(self.timeout)

                    content = page.content()

                    if not content:
                        raise Exception("can't access URL")

                    soup = BeautifulSoup(content, "html.parser")

                    # Remove unwanted elements
                    exclude_selector = ",".join(
                        self.exclude_tags
                        + [f".{c}" for c in self.exclude_classes]
                        + [f"#{i}" for i in self.exclude_ids]
                    )
                    if exclude_selector:
                        for s in soup.select(exclude_selector):
                            s.extract()

                    text = OptionalLinksMarkdownConverter().convert_soup(soup)

                    # Remove leading and trailing whitespace from the entire text
                    text = text.strip()

                    # Remove trailing whitespace from each line
                    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

                    # Indent using 2 spaces instead of tabs
                    text = re.sub(r"(\n?\s*?)\t", r"\1  ", text)

                    # Remove triple+ newlines (keep double newlines for paragraphs)
                    text = re.sub(r"\n\n+", "\n\n", text)

                    # Save the content to a file
                    with open(f"cached_webscraper_output/{hashed_name}.txt", "w") as f:
                        f.write(text)

                    return TextArtifact(text)
        except Exception:
            # TODO: hack for graceful erroring
            return TextArtifact(f"Error scraping URL: {url}")
