import asyncio
import logging
import os
import pkgutil
import types
import warnings
import zipfile
from abc import ABC, abstractmethod
from base64 import b64decode, urlsafe_b64encode
from contextlib import asynccontextmanager, suppress
from typing import Awaitable, Optional, Union

from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
    JavascriptException,
    NoSuchCookieException,
    NoSuchElementException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.common.timeouts import Timeouts
from selenium.webdriver.common.virtual_authenticator import (
    Credential,
    VirtualAuthenticatorOptions,
    required_virtual_authenticator,
)
from selenium.webdriver.remote import webdriver as remote_webdriver
from selenium.webdriver.remote.bidi_connection import BidiConnection
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.remote.file_detector import FileDetector, LocalFileDetector
from selenium.webdriver.remote.locator_converter import LocatorConverter
from selenium.webdriver.remote.script_key import ScriptKey
from selenium.webdriver.support.relative_locator import RelativeBy
from twisted.internet.error import DNSLookupError

from .proxy import ProxyConfig, generate_proxy_extension
from .remote_connection import ChromeRemoteConnection
from .shadowroot import AsyncShadowRoot
from .switch_to import AsyncSwitchTo
from .webelement import AsyncWebElement

logger = logging.getLogger(__name__)


class AbstractAsyncWebDriver(ABC):
    @abstractmethod
    async def get(self, url: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    async def current_url(self) -> Awaitable[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    async def page_source(self) -> Awaitable[str]:
        raise NotImplementedError

    @abstractmethod
    async def implicitly_wait(self, time_to_wait: float) -> None:
        raise NotImplementedError

    @abstractmethod
    async def quit(self) -> None:
        raise NotImplementedError


class AsyncSeleniumWebDriver(webdriver.Remote, AbstractAsyncWebDriver):
    """
    Controls a browser by sending commands to a remote server. This server
    is expected to be running the WebDriver wire protocol as defined at
    https://www.selenium.dev/documentation/legacy/json_wire_protocol/.

    :Attributes:
     - session_id - String ID of the browser session started and controlled by this WebDriver.
     - capabilities - Dictionary of effective capabilities of this browser session as returned by the remote server.
         See https://www.selenium.dev/documentation/legacy/desired_capabilities/
     - command_executor - remote_connection.RemoteConnection object used to execute commands.
     - error_handler - errorhandler.ErrorHandler object used to handle errors.
    """

    _web_element_cls = AsyncWebElement
    _shadowroot_cls = AsyncShadowRoot

    @classmethod
    async def create(
        cls,
        grid_remote_url: str = "http://127.0.0.1:4444",
        proxy: Optional[ProxyConfig] = None,
        options: Optional[webdriver.ChromeOptions] = None,
    ):
        """
        Create a new driver that will issue commands using the wire protocol.
        :param grid_remote_url: Either a string URL of the remote server or a custom RemoteConnection object. Defaults to 'http://127.0.0.1:4444/wd/hub'.
        :param proxy: Optional proxy configuration to use.
        :param options: instance of a driver options.Options class
        :return:
        """
        if not options:
            options = webdriver.ChromeOptions()

        if proxy:
            proxy_extension_path: str = generate_proxy_extension(
                host=proxy.host,
                port=proxy.port,
                username=proxy.username,
                password=proxy.password,
            )
            options.add_extension(extension=proxy_extension_path)

        command_executor = ChromeRemoteConnection(remote_server_addr=grid_remote_url)
        try:
            obj = cls(command_executor=command_executor)
            await obj.start_session(options=options)
        except Exception:
            await command_executor.close()
            raise
        return obj

    # noinspection PyMissingConstructor
    def __init__(
        self,
        command_executor: ChromeRemoteConnection,
        file_detector: Optional[FileDetector] = None,
        locator_converter: Optional[LocatorConverter] = None,
        web_element_cls: Optional[type] = None,
    ) -> None:
        self.command_executor = command_executor
        self._is_remote = True
        self.session_id = None
        self.caps = {}
        self.pinned_scripts = {}
        self.error_handler = ErrorHandler()
        self._switch_to = AsyncSwitchTo(self)
        self.file_detector = file_detector or LocalFileDetector()
        self.locator_converter = locator_converter or LocatorConverter()
        self._web_element_cls = web_element_cls or self._web_element_cls
        self._authenticator_id = None
        self._websocket_connection = None
        self._script = None

        self._proxy_extension = None

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ):
        await self.quit()

    async def start_session(self, options: Options) -> None:
        logger.info("Starting remote session")
        capabilities = (
            remote_webdriver.create_matches(options) if isinstance(options, list) else options.to_capabilities()
        )
        caps = remote_webdriver._create_caps(capabilities)

        response = (await self.execute(Command.NEW_SESSION, caps))["value"]

        self.session_id = response.get("sessionId")
        self.caps = response.get("capabilities")
        logger.info(f"Remote session was created with id {self.session_id}")

    async def execute(self, driver_command: str, params: dict = None) -> dict:
        """
        Sends a command to be executed by a command.CommandExecutor.
        :param driver_command: The name of the command to execute as a string.
        :param params: A dictionary of named parameters to send with the command.
        :return: The command's JSON response loaded into a dictionary object.
        """
        params = self._wrap_value(params)

        if self.session_id:
            if not params:
                params = {"sessionId": self.session_id}
            elif "sessionId" not in params:
                params["sessionId"] = self.session_id

        response = await self.command_executor.execute(driver_command, params)
        if response:
            self.error_handler.check_response(response)
            response["value"] = self._unwrap_value(response.get("value", None))
            return response
        # If the server doesn't send a response, assume the command was a success
        return {"success": 0, "value": None, "sessionId": self.session_id}

    async def get(self, url: str) -> None:
        try:
            logger.debug(f"Started downloading {url} (session #{self.session_id})")
            await self.execute(Command.GET, {"url": url})
            logger.debug(f"Finished downloading {url} (session #{self.session_id})")
        except WebDriverException as e:
            # handle DNS errors
            if "ERR_NAME_NOT_RESOLVED" in e.msg:
                raise DNSLookupError(url)
            # raise original exception for other errors
            raise

    @property
    async def title(self) -> str:
        return (await self.execute(Command.GET_TITLE)).get("value", "")

    async def execute_script(self, script, *args):
        if isinstance(script, ScriptKey):
            try:
                script = self.pinned_scripts[script.id]
            except KeyError:
                raise JavascriptException("Pinned script could not be found")

        converted_args = list(args)
        command = Command.W3C_EXECUTE_SCRIPT

        return (await self.execute(command, {"script": script, "args": converted_args}))["value"]

    async def execute_async_script(self, script: str, *args):
        converted_args = list(args)
        command = Command.W3C_EXECUTE_SCRIPT_ASYNC

        return (await self.execute(command, {"script": script, "args": converted_args}))["value"]

    @property
    async def current_url(self) -> Awaitable[str]:
        return (await self.execute(Command.GET_CURRENT_URL))["value"]

    @property
    async def page_source(self) -> Awaitable[str]:
        return (await self.execute(Command.GET_PAGE_SOURCE))["value"]

    @property
    def closed(self):
        return self.command_executor.closed

    async def close(self) -> None:
        await self.execute(Command.CLOSE)

    async def quit(self) -> None:
        """Quit the WebDriver session and close the connection."""
        try:
            await asyncio.wait_for(self.execute(Command.QUIT), timeout=5.0)  # wait for 5 seconds
        except Exception as e:
            logger.exception(f"Error sending QUIT command {self.session_id}: {e}")

        try:
            await self.command_executor.close()
        except Exception as e:
            logger.exception(f"Error closing connection {self.session_id}: {e}")

    @property
    async def current_window_handle(self) -> str:
        return (await self.execute(Command.W3C_GET_CURRENT_WINDOW_HANDLE))["value"]

    @property
    async def window_handles(self) -> list[str]:
        return (await self.execute(Command.W3C_GET_WINDOW_HANDLES))["value"]

    async def maximize_window(self) -> None:
        command = Command.W3C_MAXIMIZE_WINDOW
        await self.execute(command, None)

    async def fullscreen_window(self) -> None:
        await self.execute(Command.FULLSCREEN_WINDOW)

    async def minimize_window(self) -> None:
        await self.execute(Command.MINIMIZE_WINDOW)

    async def print_page(self, print_options: Optional[PrintOptions] = None) -> str:
        options = {}
        if print_options:
            options = print_options.to_dict()

        return (await self.execute(Command.PRINT_PAGE, options))["value"]

    # Navigation
    async def back(self) -> None:
        await self.execute(Command.GO_BACK)

    async def forward(self) -> None:
        await self.execute(Command.GO_FORWARD)

    async def refresh(self) -> None:
        await self.execute(Command.REFRESH)

    # Options
    async def get_cookies(self) -> list[dict]:
        return (await self.execute(Command.GET_ALL_COOKIES))["value"]

    async def get_cookie(self, name) -> Optional[dict]:
        with suppress(NoSuchCookieException):
            return (await self.execute(Command.GET_COOKIE, {"name": name}))["value"]
        return None

    async def delete_cookie(self, name) -> None:
        await self.execute(Command.DELETE_COOKIE, {"name": name})

    async def delete_all_cookies(self) -> None:
        await self.execute(Command.DELETE_ALL_COOKIES)

    async def add_cookie(self, cookie_dict) -> None:
        if "sameSite" in cookie_dict:
            assert cookie_dict["sameSite"] in ["Strict", "Lax", "None"]
            await self.execute(Command.ADD_COOKIE, {"cookie": cookie_dict})
        else:
            await self.execute(Command.ADD_COOKIE, {"cookie": cookie_dict})

    # Timeouts
    async def implicitly_wait(self, time_to_wait: float) -> None:
        await self.execute(Command.SET_TIMEOUTS, {"implicit": int(float(time_to_wait) * 1000)})

    async def set_script_timeout(self, time_to_wait: float) -> None:
        await self.execute(Command.SET_TIMEOUTS, {"script": int(float(time_to_wait) * 1000)})

    async def set_page_load_timeout(self, time_to_wait: float) -> None:
        try:
            await self.execute(Command.SET_TIMEOUTS, {"pageLoad": int(float(time_to_wait) * 1000)})
        except WebDriverException:
            await self.execute(
                Command.SET_TIMEOUTS,
                {"ms": float(time_to_wait) * 1000, "type": "page load"},
            )

    @property
    async def timeouts(self) -> Timeouts:
        timeouts = (await self.execute(Command.GET_TIMEOUTS))["value"]
        timeouts["implicit_wait"] = timeouts.pop("implicit") / 1000
        timeouts["page_load"] = timeouts.pop("pageLoad") / 1000
        timeouts["script"] = timeouts.pop("script") / 1000
        return Timeouts(**timeouts)

    @timeouts.setter
    async def timeouts(self, timeouts) -> None:
        _ = (await self.execute(Command.SET_TIMEOUTS, timeouts._to_json()))["value"]

    async def find_element(self, by=By.ID, value: Optional[str] = None) -> AsyncWebElement:
        if isinstance(by, RelativeBy):
            elements = await self.find_elements(by=by, value=value)
            if not elements:
                raise NoSuchElementException(f"Cannot locate relative element with: {by.root}")
            return elements[0]

        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        return (await self.execute(Command.FIND_ELEMENT, {"using": by, "value": value}))["value"]

    async def find_elements(self, by=By.ID, value: Optional[str] = None) -> list[AsyncWebElement]:
        if isinstance(by, RelativeBy):
            _pkg = ".".join(__name__.split(".")[:-1])
            raw_function = pkgutil.get_data(_pkg, "findElements.js").decode("utf8")
            find_element_js = f"/* findElements */return ({raw_function})" f".apply(null, arguments);"
            return await self.execute_script(find_element_js, by.to_dict())

        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        # Return empty list if driver returns null
        # See https://github.com/SeleniumHQ/selenium/issues/4555
        return (await self.execute(Command.FIND_ELEMENTS, {"using": by, "value": value}))["value"] or []

    async def get_screenshot_as_file(self, filename) -> bool:
        if not str(filename).lower().endswith(".png"):
            warnings.warn(
                "name used for saved screenshot does not match file type. " "It should end with a `.png` extension",
                UserWarning,
                stacklevel=2,
            )
        png: bytes = await self.get_screenshot_as_png()
        try:
            with open(filename, "wb") as f:
                f.write(png)
        except OSError:
            return False
        finally:
            del png
        return True

    async def save_screenshot(self, filename) -> bool:
        return await self.get_screenshot_as_file(filename)

    async def get_screenshot_as_png(self) -> bytes:
        return b64decode((await self.get_screenshot_as_base64()).encode("ascii"))

    async def get_screenshot_as_base64(self) -> str:
        return (await self.execute(Command.SCREENSHOT))["value"]

    async def set_window_size(self, width, height, windowHandle: str = "current") -> None:
        self._check_if_window_handle_is_current(windowHandle)
        await self.set_window_rect(width=int(width), height=int(height))

    async def get_window_size(self, windowHandle: str = "current") -> dict:
        self._check_if_window_handle_is_current(windowHandle)
        size = await self.get_window_rect()

        if size.get("value", None):
            size = size["value"]

        return {k: size[k] for k in ("width", "height")}

    async def set_window_position(self, x: float, y: float, windowHandle: str = "current") -> dict:
        self._check_if_window_handle_is_current(windowHandle)
        return await self.set_window_rect(x=int(x), y=int(y))

    async def get_window_position(self, windowHandle="current") -> dict:
        self._check_if_window_handle_is_current(windowHandle)
        position = await self.get_window_rect()

        return {k: position[k] for k in ("x", "y")}

    async def get_window_rect(self) -> dict:
        return (await self.execute(Command.GET_WINDOW_RECT))["value"]

    async def set_window_rect(self, x=None, y=None, width=None, height=None) -> dict:
        if (x is None and y is None) and (not height and not width):
            raise InvalidArgumentException("x and y or height and width need values")

        return (
            await self.execute(
                Command.SET_WINDOW_RECT,
                {"x": x, "y": y, "width": width, "height": height},
            )
        )["value"]

    @property
    async def orientation(self):
        return (await self.execute(Command.GET_SCREEN_ORIENTATION))["value"]

    @orientation.setter
    async def orientation(self, value) -> None:
        allowed_values = ["LANDSCAPE", "PORTRAIT"]
        if value.upper() in allowed_values:
            await self.execute(Command.SET_SCREEN_ORIENTATION, {"orientation": value})
        else:
            raise WebDriverException("You can only set the orientation to 'LANDSCAPE' and 'PORTRAIT'")

    @property
    async def log_types(self):
        return (await self.execute(Command.GET_AVAILABLE_LOG_TYPES))["value"]

    async def get_log(self, log_type):
        return (await self.execute(Command.GET_LOG, {"type": log_type}))["value"]

    @asynccontextmanager
    async def bidi_connection(self):
        remote_webdriver.import_cdp()
        if self.caps.get("se:cdp"):
            ws_url = self.caps.get("se:cdp")
            version = self.caps.get("se:cdpVersion").split(".")[0]
        else:
            version, ws_url = self._get_cdp_details()

        if not ws_url:
            raise WebDriverException("Unable to find url to connect to from capabilities")

        devtools = remote_webdriver.cdp.import_devtools(version)
        async with remote_webdriver.cdp.open_cdp(ws_url) as conn:
            targets = await conn.execute(devtools.target.get_targets())
            target_id = targets[0].target_id
            async with conn.open_session(target_id) as session:
                yield BidiConnection(session, remote_webdriver.cdp, devtools)

    # Virtual Authenticator Methods
    async def add_virtual_authenticator(self, options: VirtualAuthenticatorOptions) -> None:
        self._authenticator_id = (await self.execute(Command.ADD_VIRTUAL_AUTHENTICATOR, options.to_dict()))["value"]

    @required_virtual_authenticator
    async def remove_virtual_authenticator(self) -> None:
        """Removes a previously added virtual authenticator.

        The authenticator is no longer valid after removal, so no
        methods may be called.
        """
        await self.execute(
            Command.REMOVE_VIRTUAL_AUTHENTICATOR,
            {"authenticatorId": self._authenticator_id},
        )
        self._authenticator_id = None

    @required_virtual_authenticator
    async def add_credential(self, credential: Credential) -> None:
        await self.execute(
            Command.ADD_CREDENTIAL,
            {
                **credential.to_dict(),
                "authenticatorId": self._authenticator_id,
            },
        )

    @required_virtual_authenticator
    async def get_credentials(self) -> list[Credential]:
        credential_data = await self.execute(Command.GET_CREDENTIALS, {"authenticatorId": self._authenticator_id})
        return [Credential.from_dict(credential) for credential in credential_data["value"]]

    @required_virtual_authenticator
    async def remove_credential(self, credential_id: Union[str, bytearray]) -> None:
        if isinstance(credential_id, bytearray):
            credential_id = urlsafe_b64encode(credential_id).decode()

        await self.execute(
            Command.REMOVE_CREDENTIAL,
            {
                "credentialId": credential_id,
                "authenticatorId": self._authenticator_id,
            },
        )

    @required_virtual_authenticator
    async def remove_all_credentials(self) -> None:
        await self.execute(Command.REMOVE_ALL_CREDENTIALS, {"authenticatorId": self._authenticator_id})

    @required_virtual_authenticator
    async def set_user_verified(self, verified: bool) -> None:
        await self.execute(
            Command.SET_USER_VERIFIED,
            {
                "authenticatorId": self._authenticator_id,
                "isUserVerified": verified,
            },
        )

    async def get_downloadable_files(self) -> dict:
        if "se:downloadsEnabled" not in self.capabilities:
            raise WebDriverException("You must enable downloads in order to work with " "downloadable files.")

        return (await self.execute(Command.GET_DOWNLOADABLE_FILES))["value"]["names"]

    async def download_file(self, file_name: str, target_directory: str) -> None:
        if "se:downloadsEnabled" not in self.capabilities:
            raise WebDriverException("You must enable downloads in order to work with " "downloadable files.")

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        contents = (await self.execute(Command.DOWNLOAD_FILE, {"name": file_name}))["value"]["contents"]

        target_file = os.path.join(target_directory, file_name)
        with open(target_file, "wb") as file:
            file.write(b64decode(contents))

        with zipfile.ZipFile(target_file, "r") as zip_ref:
            zip_ref.extractall(target_directory)

    async def delete_downloadable_files(self) -> None:
        if "se:downloadsEnabled" not in self.capabilities:
            raise WebDriverException("You must enable downloads in order to work with " "downloadable files.")

        await self.execute(Command.DELETE_DOWNLOADABLE_FILES)
