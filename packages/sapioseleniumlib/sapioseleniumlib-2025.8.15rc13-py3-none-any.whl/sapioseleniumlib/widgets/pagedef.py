from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Optional, Callable, Union, cast, List

import selenium.webdriver.support.expected_conditions as EC
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from sapioseleniumlib.util.driver import SapioSeleniumDriver


class PageElementSearchMethod(Enum):
    """
    Page element search method for all widgets elements declared in subclasses of a BasePage.
    """
    CSS = 'css', By.CSS_SELECTOR
    ID = 'id', By.ID
    NAME = 'name', By.NAME
    XPATH = 'xpath', By.XPATH
    LINK_TEXT = 'link_text', By.LINK_TEXT
    PARTIAL_LINK_TEXT = 'partial_link_text', By.PARTIAL_LINK_TEXT
    TAG_NAME = 'tag', By.TAG_NAME
    CLASS_NAME = 'class_name', By.CLASS_NAME

    _page_factory_key: str
    _driver_by: str

    def __init__(self, page_factory_key: str, driver_by: str):
        self._page_factory_key = page_factory_key
        self._driver_by = driver_by

    @property
    def page_factory_key(self):
        return self._page_factory_key

    @property
    def driver_by(self):
        return self._driver_by


class BasePage:
    """
    Base class for Page Object Models (POM)
    """
    _source: WebElement
    _sapio_driver: SapioSeleniumDriver
    _wait: WebDriverWait
    _timeout_seconds: float

    def _load_cached_element(self, element_key: str, by: str, query: str) -> WebElement:
        if hasattr(self, element_key):
            return getattr(self, element_key)
        ret = self.sapio_driver.wait_until_element_visible(self.main_element, by, query,
                                                           timeout_seconds=self.timeout_seconds)
        setattr(self, element_key, ret)
        return ret

    def rebase(self, ele: WebElement):
        """
        Rebase the current element as another element in DOM.
        """
        self._source = self.wait.until(EC.visibility_of(ele))

    def __init__(self, driver: SapioSeleniumDriver, timeout_seconds: float | None = None,
                 static_source: WebElement = None):
        """
        Define a new page.
        :param driver: The sapio driver object to retrieve the page.
        :param timeout_seconds: The page-level timeout settings.
        :param static_source: If the source is static and already retrieved, define it here.
        If the source isn't static, then the class's _get_source() method will be called immediately to obtain the
        main source element.
        """
        super().__init__()
        self._sapio_driver = driver
        self.driver: WebDriver = self._sapio_driver.selenium_driver

        if timeout_seconds is None:
            timeout_seconds = self._sapio_driver.default_timeout

        self.timeout_seconds = timeout_seconds
        if static_source is None:
            self._source = self._get_source()
        else:
            self._source = static_source

    @property
    def timeout_seconds(self):
        return self._timeout_seconds

    @timeout_seconds.setter
    def timeout_seconds(self, timeout_seconds: float):
        self._timeout_seconds = timeout_seconds
        self._wait = WebDriverWait(self._sapio_driver.selenium_driver, timeout_seconds,
                                   ignored_exceptions=[NoSuchElementException])

    @property
    def wait(self):
        """
        Get the wait object.
        """
        return self._wait

    def wait_for(self, element_finder: Callable[[WebDriver], Optional[WebElement]],
                 must_be_visible: bool = True) -> WebElement:
        """
        Wait until the function provided returns a non-null object.
        Exceptions may cause the method to blow up early.
        :param element_finder: The function to return an object or null. This method returns when it becomes non-null.
        :param must_be_visible: If true, will further check whether it's on viewport before returning from this method.
        :return: The element from the element finder on success.
        """
        return self.sapio_driver.wait_for(element_finder,
                                          timeout_seconds=self.timeout_seconds, must_be_visible=must_be_visible)

    def wait_for_many(self, element_finders: Callable[[WebDriver], Optional[List[WebElement]]]) -> List[WebElement]:
        """
        This is simliar to wait_for, but the function is expected to return a list of elements.
        :param element_finders: The function to return a list of elements or null.
        This method returns when the element_finders function returns a non-blank list..
        :return: The list of elements returned from element finder on success.
        """
        return self.sapio_driver.wait_for_many(element_finders, timeout_seconds=self.timeout_seconds)

    def click_element(self, element: WebElement):
        """
        Click in the middle of the web element.
        """
        return self.sapio_driver.click(element, self.timeout_seconds)

    @property
    def sapio_driver(self) -> SapioSeleniumDriver:
        """
        Get the sapio selenium driver object.
        """
        return self._sapio_driver

    @abstractmethod
    def _get_source(self) -> WebElement:
        """
        Provides the web element that serves as the search context of this POM.  This will be called by the constructor.
        """
        pass

    @property
    def page_source(self) -> WebElement:
        """
        The widgets web element.
        """
        try:
            # Test if the current element is stale. If it is stale we will recover by automatically re-obtain source.
            self._source.is_enabled()
            return self._source
        except StaleElementReferenceException as e:
            self.rebase(self._get_source())

    @property
    def main_element(self) -> WebElement:
        return self.page_source

    def find_by_xpath(self, xpath: str) -> WebElement:
        """
        Obtain a web element under a global x-path. This is a shortcut.
        """
        return self._sapio_driver.selenium_driver.find_element(By.XPATH, xpath)

    def wait_until_supplier_visible(self, supplier: Callable[[WebDriver], Optional[Union[BasePage, WebElement]]]):
        """
        Wait until the supplier function has evaluated to non-null value and is visible.
        """

        def inner_supplier(d: WebDriver) -> Optional[Union[BasePage, WebElement]]:
            fun_result: Optional[Union[BasePage, WebElement]] = supplier(d)
            if fun_result is None:
                return None
            element: WebElement
            if isinstance(fun_result, WebElement):
                element = fun_result
            else:
                fun_page: BasePage = cast(BasePage, fun_result)
                element = fun_page.main_element
            if not element.is_displayed():
                return None
            return fun_result

        return self.wait.until(inner_supplier)


class BasePageObject(BasePage):
    """
    A re-usable object element inside a widgets. Such as a form, a button, a dialog, a table in Sapio.
    """

    _parent_page_obj: Optional[BasePage]
    _main_element: WebElement

    def test_staleness(self):
        # A quick test for staleness and if it is stale it will raise StaleElementReferenceException immediately.
        self.main_element.is_enabled()

    def rebase(self, ele: WebElement):
        self._main_element = ele

    def __init__(self, parent_page: BasePage | None = None, main_element: WebElement = None,
                 relative_to_parent: bool = True,
                 driver: Optional[SapioSeleniumDriver] = None, timeout_seconds: Optional[float] = None):
        """
        Create a new reusable object inside a widgets.
        :param parent_page: The parent widgets POM object. If not specified, then driver and timeout must be specified.
        """
        page_source: WebElement
        if parent_page is not None:
            driver = parent_page._sapio_driver
            if timeout_seconds is None:
                timeout_seconds = parent_page.timeout_seconds
            page_source = parent_page.page_source
        else:
            relative_to_parent = False
            page_source = main_element
            if timeout_seconds is None:
                if driver is not None:
                    timeout_seconds = driver.default_timeout
                else:
                    timeout_seconds = 60
        super().__init__(driver, timeout_seconds, page_source)
        self._relative_to_parent = relative_to_parent
        self._parent_page_obj = parent_page
        if main_element is None:
            main_element = parent_page.page_source
        self._main_element = main_element
        if not isinstance(self._main_element, WebElement):
            raise ValueError("Type error for main element")

    def _get_source(self) -> WebElement:
        if hasattr(self, "_parent_page_obj"):
            page: BasePage = self._parent_page_obj
            return page.page_source
        else:
            return self.main_element

    @property
    def main_element(self) -> WebElement:
        return self._main_element

    @property
    def parent(self) -> WebElement:
        """
        Get the parent element that encapsulates the object.
        """
        return self._main_element

    @property
    def text(self):
        """
        If this element contains inner text, then
        :return:
        """
        return self.main_element.text

    def click(self):
        """
        Click in the middle of this object.
        """
        return self.sapio_driver.click(self.main_element, self.timeout_seconds)

    def _get_main_element(self) -> WebElement:
        return self.parent
