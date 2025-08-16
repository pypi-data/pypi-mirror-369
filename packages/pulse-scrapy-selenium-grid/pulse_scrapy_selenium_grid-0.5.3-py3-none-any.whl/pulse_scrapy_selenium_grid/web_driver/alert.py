from typing import Awaitable

from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.remote.command import Command


class AsyncAlert:
    """Allows to work with alerts.

    Use this class to interact with alert prompts.  It contains methods for dismissing,
    accepting, inputting, and getting text from alert prompts.

    Accepting / Dismissing alert prompts::

        Alert(driver).accept()
        Alert(driver).dismiss()

    Inputting a value into an alert prompt::

        name_prompt = Alert(driver)
        name_prompt.send_keys("Willian Shakesphere")
        name_prompt.accept()


    Reading a the text of a prompt for verification::

        alert_text = Alert(driver).text
        self.assertEqual("Do you wish to quit?", alert_text)
    """

    def __init__(self, driver) -> None:
        """Creates a new Alert.

        :Args:
         - driver: The WebDriver instance which performs user actions.
        """
        self.driver = driver

    @property
    async def text(self) -> Awaitable[str]:
        """Gets the text of the Alert."""
        return await self.driver.execute(Command.W3C_GET_ALERT_TEXT)["value"]

    async def dismiss(self) -> Awaitable[None]:
        """Dismisses the alert available."""
        await self.driver.execute(Command.W3C_DISMISS_ALERT)

    async def accept(self) -> Awaitable[None]:
        """Accepts the alert available.

        :Usage:
            ::

                Alert(driver).accept() # Confirm a alert dialog.
        """
        await self.driver.execute(Command.W3C_ACCEPT_ALERT)

    async def send_keys(self, keysToSend: str) -> Awaitable[None]:
        """Send Keys to the Alert.

        :Args:
         - keysToSend: The text to be sent to Alert.
        """
        await self.driver.execute(
            Command.W3C_SET_ALERT_VALUE, {"value": keys_to_typing(keysToSend), "text": keysToSend}
        )
