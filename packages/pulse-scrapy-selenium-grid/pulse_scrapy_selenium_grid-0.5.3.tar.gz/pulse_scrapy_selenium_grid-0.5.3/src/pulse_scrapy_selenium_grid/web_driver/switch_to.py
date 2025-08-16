from typing import Awaitable, Optional, Union

from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.switch_to import SwitchTo

from .alert import AsyncAlert
from .webelement import AsyncWebElement


class AsyncSwitchTo(SwitchTo):
    @property
    async def active_element(self) -> Awaitable[AsyncWebElement]:
        return await self._driver.execute(Command.W3C_GET_ACTIVE_ELEMENT)["value"]

    @property
    async def alert(self) -> AsyncAlert:
        alert = AsyncAlert(self._driver)
        _ = await alert.text
        return alert

    async def default_content(self) -> None:
        await self._driver.execute(Command.SWITCH_TO_FRAME, {"id": None})

    async def frame(self, frame_reference: Union[str, int, AsyncWebElement]) -> None:
        if isinstance(frame_reference, str):
            try:
                frame_reference = await self._driver.find_element(By.ID, frame_reference)
            except NoSuchElementException:
                try:
                    frame_reference = await self._driver.find_element(By.NAME, frame_reference)
                except NoSuchElementException as exc:
                    raise NoSuchFrameException(frame_reference) from exc

        await self._driver.execute(Command.SWITCH_TO_FRAME, {"id": frame_reference})

    async def new_window(self, type_hint: Optional[str] = None) -> None:
        value = await self._driver.execute(Command.NEW_WINDOW, {"type": type_hint})["value"]
        await self._w3c_window(value["handle"])

    async def parent_frame(self) -> None:
        await self._driver.execute(Command.SWITCH_TO_PARENT_FRAME)

    async def window(self, window_name: str) -> None:
        await self._w3c_window(window_name)

    async def _w3c_window(self, window_name: str) -> None:
        async def send_handle(h):
            await self._driver.execute(Command.SWITCH_TO_WINDOW, {"handle": h})

        try:
            # Try using it as a handle first.
            await send_handle(window_name)
        except NoSuchWindowException:
            # Check every window to try to find the given window name.
            original_handle = await self._driver.current_window_handle
            handles = await self._driver.window_handles
            for handle in handles:
                await send_handle(handle)
                current_name = await self._driver.execute_script("return window.name")
                if window_name == current_name:
                    return
            await send_handle(original_handle)
            raise
