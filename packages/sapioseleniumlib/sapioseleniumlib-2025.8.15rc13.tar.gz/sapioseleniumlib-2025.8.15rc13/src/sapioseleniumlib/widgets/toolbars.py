from typing import Optional

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from sapioseleniumlib.widgets import windowobj
from sapioseleniumlib.widgets.pagedef import BasePageObject
from sapioseleniumlib.widgets.windowobj import DialogExistsSearchType


class QuickAccessToolbar(windowobj.VeloxToolbar):
    @property
    def history_button(self) -> windowobj.VeloxButton:
        return self.get_history_button()

    @property
    def user_button(self) -> windowobj.VeloxButton:
        return self.get_user_button()

    @property
    def current_group(self) -> Optional[str]:
        return self.get_current_group()

    def get_history_button(self) -> windowobj.VeloxButton:
        """
        Get recent history menu.
        """
        return self.get_button_with_icon("history")

    def get_user_button(self) -> windowobj.VeloxButton:
        """
        Get the user profile icon in the top menu.
        """
        ele = self.main_element.find_element(By.XPATH, windowobj.VeloxButton.XPATH + "[1]")
        return windowobj.VeloxButton(self, ele)

    def get_current_group(self) -> Optional[str]:
        """
        Return the group name of the current log in session.
        It can be None if user do not have a group.
        """
        self.get_user_button().click()
        windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver).click_menu_items(["Profile Settings"])
        menu_items = windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver).menu_items
        change_group = None
        for menu_item in menu_items:
            # This user don't have a group if change group is not visible.
            if "Change Group".lower() == menu_item.text.lower():
                change_group = menu_item
        if not change_group:
            return None
        change_group.click()
        # We found the change group menu, now get all groups and find the one with highlight.
        groups = windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver).menu_items
        for group in groups:
            if group.has_icon("svg-native-checkboxmarkedcircleoutline"):
                group_name = group.text.strip()
                # Click the group that's the same group as the one we are on now, to make the menu go away.
                group.click()
                return group_name
        return None

    def change_group(self, group_name: str):
        """
        Change current session to another group.
        """
        self.get_user_button().click()
        windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver).click_menu_items(["Profile Settings", "Change Group",
                                                                                   group_name])

    @property
    def home_button(self) -> WebElement:
        return self.main_element.find_element(By.XPATH, windowobj.VeloxButton.XPATH + "[2]")


class ElnToolbar(windowobj.VeloxToolbar):
    experiment_display_name: str = "Experiment"
    """Some buttons on the ELN toolbar change with the experiment display name."""

    def click_refresh(self):
        """
        Click Refresh on ELN toolbar.
        """
        self.sapio_driver.wait_seconds(2)
        self.get_button_with_icon("refresh").click()
        self.sapio_driver.wait_seconds(1)

    def set_experiment_display_name(self, name: str) -> None:
        self.experiment_display_name = name

    def exists_complete_experiment_button(self) -> bool:
        """
        Whether there is Complete experiments button.
        """
        button = self.get_button_contains_text("Complete " + self.experiment_display_name)
        return button is not None

    def complete_experiment(self) -> None:
        button = self.get_button_contains_text("Complete " + self.experiment_display_name)
        self.sapio_driver.wait_until_clickable(lambda d: button.main_element, self.timeout_seconds)
        button.click()
        if windowobj.VeloxDialog.dialog_exists(
                "Confirmation Required", DialogExistsSearchType.EXACT, self.sapio_driver, timeout_seconds=5):
            windowobj.VeloxDialog.get_dialog_with_title(
                "Confirmation Required", self.sapio_driver).click_bottom_dialog_button("Yes")

    def cancel_experiment(self) -> None:
        self.sapio_driver.wait_seconds(2)
        self.sapio_driver.click(self.get_button_contains_text("Cancel " + self.experiment_display_name))
        if windowobj.VeloxDialog.dialog_exists(
                "Confirm Cancellation", DialogExistsSearchType.EXACT, self.sapio_driver, timeout_seconds=5):
            windowobj.VeloxDialog.get_dialog_with_title(
                "Confirm Cancellation", self.sapio_driver).click_bottom_dialog_button("Yes")

    def e_sign_experiment(self, username: str, password: str, reason: str = "Automation testing.") -> None:
        button = self.get_button_contains_text("E-Sign")
        self.sapio_driver.wait_until_clickable(lambda d: button.main_element)
        button.click()
        if windowobj.VeloxDialog.dialog_exists(
                "Authentication Required", DialogExistsSearchType.EXACT, self.sapio_driver, timeout_seconds=3):
            e_sign_dialog = windowobj.VeloxDialog.get_dialog_with_title("Authentication Required", self.sapio_driver)
            e_sign_form = e_sign_dialog.get_form()
            e_sign_form.set_string_field("Username", username)
            e_sign_form.set_string_field("Password", password)
            e_sign_form.set_string_field("Meaning of Action", reason)
            e_sign_dialog.click_bottom_dialog_button("OK")


class AppSetupToolbar(windowobj.VeloxToolbar):
    @property
    def close_button(self):
        return self.get_button_contains_text("Close Manager")

    @property
    def close_button_or_menu_item(self):
        return self.get_button_or_menu_item_containing_text("Close Manager")

    @property
    def config_manager(self):
        return self.get_button_or_menu_item_containing_text("Configuration Manager")


class WestMainPanel(BasePageObject):
    BY_CSS: str = "[data-main-west-panel]"

    def get_quick_access_toolbar(self):
        self.expand()
        element = self.wait_for_many(lambda d: self.main_element.find_elements(By.CSS_SELECTOR, self.BY_CSS))[1]
        return QuickAccessToolbar(self, element)

    @property
    def collapsed(self) -> bool:
        return "primaryWestPanel".lower() != self.main_element.get_attribute("id")

    def collapse(self) -> None:
        buttons = self.get_quick_access_toolbar().get_buttons()
        buttons[-1].click()

    def expand(self):
        if not self.collapsed:
            return
        parent = self.wait.until(lambda d: self.main_element.find_element(By.XPATH, "./.."))
        self.sapio_driver.click(self.main_element.find_element(By.XPATH, windowobj.VeloxButton.XPATH))
        visibility_cond = EC.visibility_of(parent.find_element(By.CSS_SELECTOR, self.BY_CSS))
        self.rebase(self.wait.until(visibility_cond))

    @property
    def tab_panel(self) -> windowobj.VeloxTabPanel:
        ele = self.wait.until(self, lambda d: self.main_element.find_element(
            By.XPATH, "./div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]"))
        return windowobj.VeloxTabPanel(ele)

    @property
    def notebook_explorer_menu_item(self) -> windowobj.VeloxMenuItem:
        return self.get_menu_item("notebook explorer")

    @property
    def _menu(self):
        element = self.wait.until(
            lambda d: self.tab_panel.active_tab_contents.find_element(By.XPATH, ".//" + windowobj.VeloxMenu.X_PATH)
        )
        return windowobj.VeloxMenu(self, element)

    def get_menu_item(self, text: str) -> windowobj.VeloxMenuItem:
        return self._menu.get_menu_item_containing_text(text)
