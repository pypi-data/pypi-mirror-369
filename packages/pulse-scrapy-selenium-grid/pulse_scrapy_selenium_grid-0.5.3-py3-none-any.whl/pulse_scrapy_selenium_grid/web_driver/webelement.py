import os
import warnings
import zipfile
from base64 import b64decode, encodebytes
from hashlib import md5 as md5_hash
from io import BytesIO
from typing import Awaitable, List, Self

from selenium.common.exceptions import JavascriptException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.remote import webelement
from selenium.webdriver.remote.command import Command


class AsyncWebElement(webelement.WebElement):
    @property
    async def tag_name(self) -> Awaitable[str]:
        return (await self._execute(Command.GET_ELEMENT_TAG_NAME))["value"]

    @property
    async def text(self) -> Awaitable[str]:
        return (await self._execute(Command.GET_ELEMENT_TEXT))["value"]

    async def click(self) -> None:
        await self._execute(Command.CLICK_ELEMENT)

    async def submit(self) -> None:
        script = (
            "/* submitForm */var form = arguments[0];\n"
            'while (form.nodeName != "FORM" && form.parentNode) {\n'
            "  form = form.parentNode;\n"
            "}\n"
            "if (!form) { throw Error('Unable to find containing form element'); }\n"
            "if (!form.ownerDocument) { throw Error('Unable to find owning document'); }\n"
            "var e = form.ownerDocument.createEvent('Event');\n"
            "e.initEvent('submit', true, true);\n"
            "if (form.dispatchEvent(e)) { HTMLFormElement.prototype.submit.call(form) }\n"
        )

        try:
            await self._parent.execute_script(script, self)
        except JavascriptException as exc:
            raise WebDriverException("To submit an element, it must be nested inside a form " "element") from exc

    async def clear(self) -> None:
        await self._execute(Command.CLEAR_ELEMENT)

    async def get_property(self, name) -> Awaitable[str | bool | Self | dict]:
        try:
            return (await self._execute(Command.GET_ELEMENT_PROPERTY, {"name": name}))["value"]
        except WebDriverException:
            # if we hit an end point that doesn't understand getElementProperty
            # lets fake it
            return await self.parent.execute_script("return arguments[0][arguments[1]]", self, name)

    async def get_dom_attribute(self, name) -> Awaitable[str]:
        return (await self._execute(Command.GET_ELEMENT_ATTRIBUTE, {"name": name}))["value"]

    async def get_attribute(self, name) -> Awaitable[str | None]:
        if webelement.getAttribute_js is None:
            webelement._load_js()
        script = "/* getAttribute */return " f"({webelement.getAttribute_js}).apply(null, arguments);"
        attribute_value = await self.parent.execute_script(script, self, name)
        return attribute_value

    async def is_selected(self) -> Awaitable[bool]:
        return (await self._execute(Command.IS_ELEMENT_SELECTED))["value"]

    async def is_enabled(self) -> Awaitable[bool]:
        return (await self._execute(Command.IS_ELEMENT_ENABLED))["value"]

    async def send_keys(self, *value: str) -> None:
        # transfer file to another machine only if remote driver is used
        # the same behaviour as for java binding
        if self.parent._is_remote:
            local_files = list(
                map(
                    lambda keys_to_send: self.parent.file_detector.is_local_file(str(keys_to_send)),
                    "".join(map(str, value)).split("\n"),
                )
            )
            if None not in local_files:
                remote_files = []
                for file in local_files:
                    remote_files.append(await self._upload(file))
                value = "\n".join(remote_files)

        await self._execute(
            Command.SEND_KEYS_TO_ELEMENT,
            {
                "text": "".join(keys_to_typing(value)),
                "value": keys_to_typing(value),
            },
        )

    @property
    async def shadow_root(self):
        return (await self._execute(Command.GET_SHADOW_ROOT))["value"]

    # RenderedWebElement Items
    async def is_displayed(self) -> Awaitable[bool]:
        # Only go into this conditional for browsers that don't use the atom
        # themselves
        if webelement.isDisplayed_js is None:
            webelement._load_js()
        script = "/* isDisplayed */return " f"({webelement.isDisplayed_js}).apply(null, arguments);"
        return await self.parent.execute_script(script, self)

    @property
    async def location_once_scrolled_into_view(self) -> Awaitable[dict]:
        script = "arguments[0].scrollIntoView(true); return " "arguments[0].getBoundingClientRect()"
        old_loc = (
            await self._execute(
                Command.W3C_EXECUTE_SCRIPT,
                {
                    "script": script,
                    "args": [self],
                },
            )
        )["value"]
        return {"x": round(old_loc["x"]), "y": round(old_loc["y"])}

    @property
    async def size(self) -> Awaitable[dict]:
        size = (await self._execute(Command.GET_ELEMENT_RECT))["value"]
        new_size = {"height": size["height"], "width": size["width"]}
        return new_size

    async def value_of_css_property(self, property_name) -> Awaitable[str]:
        return (await self._execute(Command.GET_ELEMENT_VALUE_OF_CSS_PROPERTY, {"propertyName": property_name}))[
            "value"
        ]

    @property
    async def location(self) -> Awaitable[dict]:
        old_loc = (await self._execute(Command.GET_ELEMENT_RECT))["value"]
        new_loc = {"x": round(old_loc["x"]), "y": round(old_loc["y"])}
        return new_loc

    @property
    async def rect(self) -> Awaitable[dict]:
        return (await self._execute(Command.GET_ELEMENT_RECT))["value"]

    @property
    async def aria_role(self) -> Awaitable[str]:
        return (await self._execute(Command.GET_ELEMENT_ARIA_ROLE))["value"]

    @property
    async def accessible_name(self) -> Awaitable[str]:
        return (await self._execute(Command.GET_ELEMENT_ARIA_LABEL))["value"]

    @property
    async def screenshot_as_base64(self) -> Awaitable[str]:
        return (await self._execute(Command.ELEMENT_SCREENSHOT))["value"]

    @property
    async def screenshot_as_png(self) -> Awaitable[bytes]:
        return b64decode((await self.screenshot_as_base64).encode("ascii"))

    async def screenshot(self, filename) -> Awaitable[bool]:
        if not filename.lower().endswith(".png"):
            warnings.warn(
                "name used for saved screenshot does not match file type. It " "should end with a `.png` extension",
                UserWarning,
            )
        png = await self.screenshot_as_png
        try:
            with open(filename, "wb") as f:
                f.write(png)
        except OSError:
            return False
        finally:
            del png
        return True

    @property
    def parent(self):
        return self._parent

    @property
    def id(self) -> str:
        return self._id

    def __eq__(self, element):
        return hasattr(element, "id") and self._id == element.id

    def __ne__(self, element):
        return not self.__eq__(element)

    # Private Methods
    async def _execute(self, command, params=None):
        if not params:
            params = {}
        params["id"] = self._id
        return await self._parent.execute(command, params)

    async def find_element(self, by=By.ID, value=None) -> Awaitable[Self]:
        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        return (await self._execute(Command.FIND_CHILD_ELEMENT, {"using": by, "value": value}))["value"]

    async def find_elements(self, by=By.ID, value=None) -> Awaitable[List[Self]]:
        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        return (await self._execute(Command.FIND_CHILD_ELEMENTS, {"using": by, "value": value}))["value"]

    def __hash__(self) -> int:
        return int(md5_hash(self._id.encode("utf-8")).hexdigest(), 16)

    async def _upload(self, filename):
        fp = BytesIO()
        zipped = zipfile.ZipFile(fp, "w", zipfile.ZIP_DEFLATED)
        zipped.write(filename, os.path.split(filename)[1])
        zipped.close()
        content = encodebytes(fp.getvalue())
        if not isinstance(content, str):
            content = content.decode("utf-8")
        try:
            return (await self._execute(Command.UPLOAD_FILE, {"file": content}))["value"]
        except WebDriverException as e:
            if "Unrecognized command: POST" in str(e):
                return filename
            if "Command not found: POST " in str(e):
                return filename
            if '{"status":405,"value":["GET","HEAD","DELETE"]}' in str(e):
                return filename
            raise
