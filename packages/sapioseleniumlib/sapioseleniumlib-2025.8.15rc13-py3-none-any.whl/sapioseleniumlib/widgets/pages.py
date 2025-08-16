import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from sapioseleniumlib.util.driver import SapioSeleniumDriver
from sapioseleniumlib.widgets import panels, windowobj
from sapioseleniumlib.widgets import toolbars
from sapioseleniumlib.widgets.pagedef import BasePage
from sapioseleniumlib.widgets.panels import VeloxWestPanel, ProcessQueue
from selenium.webdriver.support.select import Select


class LoginPage(BasePage):
    """
    This is the main Sapio login page. Currently it doesn't handle SaaS Sapio homepage.
    If SSO is enabled such as SaaS then you should try to end with /localauth for the main Sapio URL.
    """
    def _get_source(self) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))

    _login_form: windowobj.LoginForm
    _login_web_form: windowobj.LoginWebForm

    def __init__(self, driver: SapioSeleniumDriver):
        super().__init__(driver)
        if not self.at_sapio_sciences_website():
            self._login_form = windowobj.LoginForm(self, self.main_element)
        # logging.info("Object created " + str(self.__class__))

    def login(self, username: str, password: str, lab_name: str | None):
        if self.logged_in:
            return
        if self.at_sapio_sciences_website():
            # Entering the email changes the form, so we need to create a new form after entering the email. Otherwise,
            # we get stale element exceptions when trying to use the lab and password fields.
            form = windowobj.LoginWebForm(self, self.main_element)
            form.user_name_field.send_keys(username + Keys.ENTER)
            form = windowobj.LoginWebForm(self, self.main_element)
            if lab_name is not None:
                Select(form.lab_field).select_by_visible_text(lab_name)
            form.password_field.send_keys(password + Keys.ENTER)
        else:
            self._login_form.do_login(username, password)

    @property
    def logged_in(self):
        return not self.sapio_driver.selenium_driver.title.startswith("Login - ") \
            and not self.at_sapio_sciences_website()

    def at_sapio_sciences_website(self) -> bool:
        return self.sapio_driver.selenium_driver.current_url.count("sapiosciences.com/seamless-eln-login") > 0


class MainPage(BasePage):
    """
    This is the main view (panel) of Sapio.
    The main view includes the west panel and the main panel.
    """
    CSS_SELECTOR: str = "[data-main-view]"

    def _get_source(self) -> WebElement:
        self.wait.until(EC.none_of(EC.url_contains("view=appManager")))
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, MainPage.CSS_SELECTOR)))

    @property
    def west_panel(self) -> VeloxWestPanel:
        return VeloxWestPanel(self, self.wait_for(
            lambda d: self.page_source.find_element(By.CSS_SELECTOR, VeloxWestPanel.BY_CSS)))

    @property
    def main_panel(self) -> WebElement:
        return self.wait_for(
            lambda d: self.page_source.find_element(
                By.XPATH, "./*[@data-panel and not(@data-main-east-panel) and not(@data-main-west-panel)]"))

    @property
    def home_page_tab_panel(self) -> windowobj.VeloxTabPanel:
        # go to home widgets first
        self.sapio_driver.click(self.west_panel.quick_access_toolbar.home_button)
        ele = self.wait.until(lambda d: self.main_panel.find_element(
            By.XPATH, ".//*[@data-tab-panel]"))
        return windowobj.VeloxTabPanel(self, ele)

    @property
    def integrated_data_view(self) -> panels.IntegratedDataView:
        return panels.IntegratedDataView(self, self.main_panel)

    @property
    def process_queue(self) -> panels.ProcessQueue:
        # return ProcessQueue(self, self.main_panel.find_element(
        #     By.XPATH,
        #     ".//*[@data-panel][@data-component-type][//*" + self.sapio_driver.x_path_ci_text_equals(
        #         "Process Queue") + "]"))
        # TODO the above ^ should work and would be better
        return ProcessQueue(self, self.main_panel.find_element(
            By.XPATH,
            ".//*[@data-panel][@data-component-type]"))


class AppSetupPage(BasePage):
    """
    This is the app setup page of Sapio. It includes the toolbar and the main panel.
    """
    XPATH_SELECTOR: str = "/html/body/div/table/tbody/tr/td/div/div"

    def _get_source(self) -> WebElement:
        self.wait.until(EC.url_contains("view=appManager"))
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, AppSetupPage.XPATH_SELECTOR)))

    def _get_main_element(self) -> WebElement:
        self.wait.until(EC.url_contains("view=appManager"))
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, self.XPATH_SELECTOR)))

    @property
    def app_setup_toolbar(self) -> toolbars.AppSetupToolbar:
        el = self.wait.until(
            lambda d: self.page_source.find_element(By.XPATH, ".//*" + self.sapio_driver.x_path_contains_class(
                windowobj.VeloxToolbar.CSS_CLASS)))
        return toolbars.AppSetupToolbar(self, el)


class ConfigurationManager(BasePage):
    """
    This is the configuration manager screen of the app setup page.
    It has header text, west panel (of menus of configs to choose), and the main panel.
    """

    def _get_source(self) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located((
            By.XPATH, AppSetupPage.XPATH_SELECTOR + "//*[@data-panel]//*[@data-panel]//*[@data-panel]")))

    @property
    def panel(self) -> windowobj.VeloxPanel:
        return windowobj.VeloxPanel(self, self.main_element)

    @property
    def header_text(self) -> str:
        return self.panel.main_element.text

    @property
    def west_panel(self) -> windowobj.VeloxPanel:
        return windowobj.VeloxPanel(self, self.wait.until(
            lambda d: self.panel.body.find_element(By.XPATH, "./div/div/div/div[1]")
        ))

    def filter_west_panel(self, filter_text: str) -> None:
        editor = self.wait_for(
            lambda d: self.west_panel.main_element.find_element(By.XPATH, ".//input")
        )
        actions = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(editor)
        actions.click()
        actions.send_keys(Keys.CONTROL + "a" + Keys.CONTROL + Keys.BACKSPACE)
        actions.pause(.25)
        actions.send_keys(filter_text)
        actions.pause(.25)
        actions.perform()

    def select_config(self, config_name: str) -> None:
        self.filter_west_panel(config_name)
        list_view = panels.ListView(self, self.wait.until(
            lambda d: self.west_panel.main_element.find_element(By.CSS_SELECTOR, panels.ListView.CSS_SELECTOR)
        ))
        list_view.select_item(config_name)

    @property
    def form(self) -> windowobj.VeloxForm:
        panel = self.panel
        return windowobj.VeloxForm(panel, panel.body)
