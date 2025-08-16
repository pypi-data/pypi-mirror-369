from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.shadowroot import ShadowRoot


class AsyncShadowRoot(ShadowRoot):
    async def find_element(self, by: str = By.ID, value: str = None):
        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        return await self._execute(Command.FIND_ELEMENT_FROM_SHADOW_ROOT, {"using": by, "value": value})["value"]

    async def find_elements(self, by: str = By.ID, value: str = None):
        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        return await self._execute(Command.FIND_ELEMENTS_FROM_SHADOW_ROOT, {"using": by, "value": value})["value"]

    # Private Methods
    async def _execute(self, command, params=None):
        """Executes a command against the underlying HTML element.

        Args:
          command: The name of the command to _execute as a string.
          params: A dictionary of named parameters to send with the command.

        Returns:
          The command's JSON response loaded into a dictionary object.
        """
        if not params:
            params = {}
        params["shadowId"] = self._id
        return await self.session.execute(command, params)
