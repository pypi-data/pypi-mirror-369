import logging
from typing import List

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from sapioseleniumlib.util.driver import SapioSeleniumDriver
from sapioseleniumlib.widgets import eln, windowobj
from sapioseleniumlib.widgets import pages
from sapioseleniumlib.widgets.pages import LoginPage


class Do:
    """
    Includes popular actions to perform.
    """
    _sapio_driver: SapioSeleniumDriver
    _wait: WebDriverWait
    _username: str
    _password: str
    _lab_name: str | None
    _wait_timeout_seconds: float

    def __init__(self, sapio_driver: SapioSeleniumDriver, wait_timeout_seconds: float, username: str, password: str,
                 lab_name: str | None = None):
        self._sapio_driver = sapio_driver
        self._username = username
        self._password = password
        self._lab_name = lab_name
        self._wait = sapio_driver.wait(wait_timeout_seconds)
        self._wait_timeout_seconds = wait_timeout_seconds

    def _load(self) -> None:
        """
        Check to see if the app has loaded. If not we wait for it to finish
        """
        title = self._sapio_driver.selenium_driver.title
        if not title or "Sapio" not in title:
            body = self._sapio_driver.selenium_driver.find_element(By.TAG_NAME, "body")
            if body.text and "Compiling" in body.text:
                try:
                    logging.info("waiting for refresh...")
                    self._wait.until(EC.staleness_of(body))
                    logging.info("done! (super dev mode refreshed)")
                except Exception as e:
                    pass
        self._wait.until(EC.title_contains("Sapio"))

    def login(self) -> None:
        """
        Log in with the provided username and password.
        """
        self._load()
        login_page = LoginPage(self._sapio_driver)
        login_page.login(self._username, self._password, self._lab_name)

        current_title = ""
        current_url = ""
        anti_title = "Login - "
        anti_url = "sapiosciences.com/seamless-eln-login"

        def ready_condition(d: WebDriver) -> bool:
            nonlocal current_title
            nonlocal current_url
            nonlocal anti_title
            nonlocal anti_url
            current_title = self._sapio_driver.selenium_driver.title
            current_url = self._sapio_driver.selenium_driver.current_url
            # It's not finished logging in if it's still on log in widgets.
            is_login_title = current_title and current_title.startswith(anti_title)
            is_login_page = current_url and current_url.count(anti_url) > 0
            if is_login_title or is_login_page:
                return False
            return self._sapio_driver.exists(By.XPATH, "/html/body/div/table/tbody/tr/td/div")

        self._wait.until(ready_condition)
        # wait to see if there are any guided help
        if self._sapio_driver.exists(By.CSS_SELECTOR, ".vgh-close", timeout_seconds=2):
            # click the close button on guided help if there is any.
            self._sapio_driver.selenium_driver.find_element(By.CSS_SELECTOR, ".vgh-close").click()

    def logout(self) -> None:
        self.main_view()
        main_page = pages.MainPage(self._sapio_driver)
        west_panel = main_page.west_panel
        west_panel.expand()
        west_panel.quick_access_toolbar.user_button.click()
        top_most_menu = windowobj.VeloxMenu.get_top_most_menu(self._sapio_driver)
        top_most_menu.get_menu_item_containing_text("Logout").click()

        current_title = ""
        current_url = ""
        login_title = "Login - "
        login_url = "sapiosciences.com/seamless-eln-login"
        sso_logout_title = " - Logout"

        def ready_condition(d: WebDriver) -> bool:
            nonlocal current_title
            nonlocal current_url
            nonlocal login_title
            nonlocal login_url
            nonlocal sso_logout_title
            current_title = self._sapio_driver.selenium_driver.title
            current_url = self._sapio_driver.selenium_driver.current_url
            # It's not finished logging out if it's not on the login page yet.
            is_login_title = current_title and current_title.startswith(login_title)
            is_login_page = current_url and current_url.count(login_url) > 0
            is_sso_logout = current_url and current_title.casefold().endswith(sso_logout_title.casefold())
            return is_login_title or is_login_page or is_sso_logout

        self._wait.until(ready_condition)

    def app_setup(self) -> None:
        """
        Go to the App Setup screen.
        """
        self._load()
        self.login()
        if self._sapio_driver.exists(By.XPATH, pages.AppSetupPage.XPATH_SELECTOR, .5):
            main_page = pages.MainPage(self._sapio_driver)
            main_page.west_panel.quick_access_toolbar.user_button.click()
            top_most_menu = windowobj.VeloxMenu.get_top_most_menu(self._sapio_driver)
            top_most_menu.get_menu_item_containing_text("App Setup").click()

    def main_view(self) -> None:
        """
        Ensure we are currently in the main Sapio view when the method exists.
        If we are currently in app setup we close the app setup screen.
        """
        self._load()
        self.login()
        if self._sapio_driver.exists_by_supplier(
                lambda d: pages.MainPage(self._sapio_driver).page_source, .5):
            # we are already inside main view. don't need to close app setup.
            return
        # we are in app setup widgets, close the app setup widgets to return to main widgets.
        app_setup_page = pages.AppSetupPage(self._sapio_driver)
        app_setup_page.app_setup_toolbar.close_button_or_menu_item.click()

    def create_ad_hoc_experiment(self) -> eln.ElnExperimentPage:
        """
        Create a new ad-hoc eln experiment.
        """
        self.main_view()
        main_page = pages.MainPage(self._sapio_driver)
        west_panel = main_page.west_panel
        west_panel.expand()
        west_panel.notebook_explorer_menu_item.click()
        notebook_explorer = eln.NotebookExplorer(self._sapio_driver)
        notebook_explorer.add_experiment()
        self._sapio_driver.wait_seconds(.5)
        return eln.ElnExperimentPage(self._sapio_driver)

    def create_template_experiment(self, template_filter_text: str) -> eln.ElnExperimentPage:
        """
        Create a new experiment from a template experiment, provided by its name.
        """
        self.main_view()
        main_page = pages.MainPage(self._sapio_driver)
        west_panel = main_page.west_panel
        west_panel.expand()
        west_panel.notebook_explorer_menu_item.click()
        notebook_explorer = eln.NotebookExplorer(self._sapio_driver)
        notebook_explorer.add_experiment_from_template(template_filter_text)
        self._sapio_driver.wait_seconds(.5)
        return eln.ElnExperimentPage(self._sapio_driver)

    def config_manager(self, config_name: str) -> pages.ConfigurationManager:
        """
        Go to App Setup => Configuration Manager.
        """
        self.app_setup()
        app_setup_page = pages.AppSetupPage(self._sapio_driver)
        app_setup_page.app_setup_toolbar.config_manager.click()
        config_manager = pages.ConfigurationManager(self._sapio_driver)
        config_manager.select_config(config_name)
        return config_manager

    def main_menu(self, texts: List[str]) -> None:
        """
        Click the nested menu items provided in the main menu.
        """
        self.main_view()
        pages.MainPage(self._sapio_driver).west_panel.click_menu_items(texts)

    def home_page(self) -> None:
        """
        Navigate to Sapio home page
        """
        self.main_view()
        self._sapio_driver.click(pages.MainPage(self._sapio_driver).west_panel.quick_access_toolbar.home_button)

    def switch_group(self, group_name: str) -> None:
        """
        Switch group to the provided group name
        :param group_name: The group to switch to
        """
        self.main_view()
        pages.MainPage(self._sapio_driver).west_panel.quick_access_toolbar.change_group(group_name)
        self._sapio_driver.wait_seconds(1)
        self.main_view()

    def navigate_to(self, relative_url_after_app_guid: str):
        """
        Navigate to a new widgets URL.
        The existing objects should all be considered stale.
        """
        current_url = self._sapio_driver.selenium_driver.current_url
        if "#" in current_url:
            current_url = current_url[0: current_url.index("#")]
        if not relative_url_after_app_guid.startswith("#"):
            raise ValueError("navigation url should start with #")
        target_url = current_url + relative_url_after_app_guid
        self._sapio_driver.selenium_driver.get(target_url)
