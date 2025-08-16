import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional

from scrapy import Spider, signals
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from scrapy.crawler import Crawler
from scrapy.http import Request, TextResponse
from scrapy.settings import Settings
from scrapy.utils.defer import deferred_from_coro
from scrapy.utils.reactor import verify_installed_reactor
from twisted.internet.defer import Deferred

from pulse_scrapy_selenium_grid.web_driver.proxy import ProxyConfig
from pulse_scrapy_selenium_grid.web_driver.webdriver import AsyncSeleniumWebDriver

MAX_CONCURRENT_REQUESTS = 4  # limit of concurrent requests/sessions per spider

logger = logging.getLogger(__name__)


@dataclass
class Config:
    grid_remote_url: str = "http://127.0.0.1:4444"
    implicit_wait_in_sec: int = 0
    shutdown_timeout_sec: int = 30  # Maximum time to wait for all drivers to close

    @classmethod
    def from_settings(cls, settings: Settings) -> "Config":
        cfg = cls(
            grid_remote_url=settings.get("SELENIUM_GRID_REMOTE_URL", cls.grid_remote_url),
            implicit_wait_in_sec=settings.get("SELENIUM_GRID_IMPLICIT_WAIT_IN_SEC", cls.implicit_wait_in_sec),
            shutdown_timeout_sec=settings.get("SELENIUM_GRID_SHUTDOWN_TIMEOUT_SEC", cls.shutdown_timeout_sec),
        )
        return cfg


@dataclass
class DriverContext:
    """
    @summary: Holds a driver instance and an associated lock.
    """

    driver: AsyncSeleniumWebDriver
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def close(self):
        """Close the WebDriver session with timeout protection."""
        try:
            await asyncio.wait_for(self.driver.quit(), timeout=10.0)
        except Exception as e:
            logger.error(f"Error closing WebDriver session {self.driver.session_id}: {e}")


class ScrapyDownloadHandler(HTTPDownloadHandler):
    config: Config
    proxy_config: Optional[ProxyConfig] = None
    driver: AsyncSeleniumWebDriver = None

    def __init__(self, crawler: Crawler) -> None:
        super().__init__(settings=crawler.settings, crawler=crawler)
        verify_installed_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
        crawler.signals.connect(self.on_engine_stop, signals.engine_stopped)

        self.config: Config = Config.from_settings(settings=crawler.settings)
        self.proxy_config: ProxyConfig | None = ProxyConfig.from_settings(settings=crawler.settings)

        self.concurrent_requests: int = crawler.settings.get("CONCURRENT_REQUESTS")
        if self.concurrent_requests > MAX_CONCURRENT_REQUESTS:
            raise AttributeError(
                f"Too many concurrent requests: {self.concurrent_requests} (max allowed: {MAX_CONCURRENT_REQUESTS}). "
                f"Selenium uses separate nodes for concurrency, therefore can make too many pods."
            )

        # Lock to ensure the driver pool is only created once.
        self._driver_pool_lock = asyncio.Lock()
        # Holds a list of DriverContext objects (each has its own driver and lock).
        self._drivers: list[DriverContext] = []
        # Round-robin index for selecting which driver to use.
        self._driver_index: int = 0

    @classmethod
    def from_crawler(cls: type["ScrapyDownloadHandler"], crawler: Crawler) -> "ScrapyDownloadHandler":
        return cls(crawler)

    def download_request(self, request: Request, spider: Spider) -> Deferred:
        # Use selenium grid only if optional meta use_selenium_grid != False
        if request.meta.get("use_selenium_grid") is not False:
            return deferred_from_coro(self._download_request(request))
        return super().download_request(request, spider)

    async def _download_request(self, request: Request) -> TextResponse:
        """
        @summary: Asynchronous download request using Selenium.
        @param request: The Scrapy Request to download.
        @return: A TextResponse with the rendered page source.
        """
        await self._ensure_driver_pool_initialized()

        # Round-robin selection of a driver
        driver_context: DriverContext = self._drivers[self._driver_index]
        self._driver_index = (self._driver_index + 1) % len(self._drivers)

        # Lock per driver to ensure only one request at a time uses this driver.
        async with driver_context.lock:
            driver = driver_context.driver
            request.meta["selenium_grid_driver"] = driver

            # Navigate to the requested URL
            await driver.get(request.url)

            # Apply implicit wait if specified
            implicit_wait_in_sec = request.meta.get(
                "selenium_grid_implicit_wait_in_sec", self.config.implicit_wait_in_sec
            )
            if implicit_wait_in_sec:
                await driver.implicitly_wait(implicit_wait_in_sec)

            current_url = await driver.current_url
            page_source = await driver.page_source

            return TextResponse(
                url=current_url,
                body=page_source,
                request=request,
                encoding="utf-8",
                flags=["selenium_grid"],
            )

    async def _ensure_driver_pool_initialized(self) -> None:
        """
        @summary: Initializes a pool of drivers if not already done, one for each concurrent request.
        """
        # If the pool is already created, do nothing.
        if self._drivers:
            return

        async with self._driver_pool_lock:
            # Double-check inside the lock to avoid race conditions.
            if not self._drivers:
                logger.info(f"Creating a pool of drivers for concurrency={self.concurrent_requests}")
                self._drivers: list[DriverContext] = await asyncio.gather(
                    *[self._create_webdriver() for _ in range(self.concurrent_requests)]
                )

    async def _create_webdriver(self) -> DriverContext:
        """
        @summary: Creates a single driver instance based on the config.
        @return: A driver context with  WebDriver object.
        """
        if self.config is None:
            raise RuntimeError("Cannot create a WebDriver without a valid config.")

        # We can create asyncio webdriver in future
        driver: AsyncSeleniumWebDriver = await self._create_selenium_webdriver()
        return DriverContext(driver=driver)

    async def _create_selenium_webdriver(self) -> AsyncSeleniumWebDriver:
        """
        @summary: Creates and returns an AsyncSeleniumWebDriver.
        @return: An AsyncSeleniumWebDriver instance.
        """
        from pulse_scrapy_selenium_grid.web_driver.webdriver import AsyncSeleniumWebDriver

        return await AsyncSeleniumWebDriver.create(grid_remote_url=self.config.grid_remote_url, proxy=self.proxy_config)

    async def on_engine_stop(self) -> None:
        """
        @summary: Called when the Scrapy engine is stopped; clean up driver resources here.
        """
        if not self._drivers:
            return

        logger.info(f"Shutting down {len(self._drivers)} WebDriver instances.")

        # Close all drivers concurrently with overall timeout
        tasks = [driver_context.close() for driver_context in self._drivers]
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=self.config.shutdown_timeout_sec)
        except asyncio.TimeoutError:
            logger.error("Timeout reached while shutting down WebDriver instances.")

        self._drivers.clear()
