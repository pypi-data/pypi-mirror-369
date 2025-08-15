import binascii
import time

import pyotp
from quantplay.exception.exceptions import (
    BrokerException,
    InvalidArgumentException,
    RetryableException,
)
from quantplay.utils.constant import Constants
from quantplay.utils.selenium_utils import Selenium
from retrying import retry  # type: ignore
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = Constants.logger


class AliceblueLogin:
    """Handles automated login for Aliceblue broker platform."""

    @staticmethod
    def check_error(page_source: str) -> None:
        """Check for error messages in the page source and raise appropriate exceptions."""
        error_messages = [
            "User profile not found",
            "Invalid username or password",
            "Invalid TOTP",
        ]

        for error_message in error_messages:
            if error_message in page_source:
                raise InvalidArgumentException(error_message)

        if "Invalid" in page_source and "api_key" in page_source:
            raise InvalidArgumentException("Invalid API Key")

    @staticmethod
    def _click_button_by_id(driver: Chrome, button_id: str, timeout: int = 5) -> bool:
        """Click a button by ID using JavaScript execution for reliability."""
        try:
            wait = WebDriverWait(driver, timeout)
            button = wait.until(EC.presence_of_element_located((By.ID, button_id)))

            if button.is_displayed() and button.is_enabled():
                driver.execute_script("arguments[0].click();", button)
                return True
            return False
        except (TimeoutException, NoSuchElementException):
            return False

    @staticmethod
    def click_on_next(driver: Chrome) -> None:
        """Click the Next button on the login form."""
        if not AliceblueLogin._click_button_by_id(driver, "buttonLabel_Next"):
            raise BrokerException("Next button not found or not clickable")

    @staticmethod
    def enter_user_id(driver: Chrome, user_id: str) -> None:
        """Enter user ID in the login form."""
        wait = WebDriverWait(driver, 10)
        user_id_element = wait.until(
            EC.presence_of_element_located((By.ID, "new_login_userId"))
        )
        user_id_element.clear()
        user_id_element.send_keys(user_id)
        time.sleep(0.5)

    @staticmethod
    def enter_password(driver: Chrome, password: str) -> None:
        """Enter password in the login form."""
        wait = WebDriverWait(driver, 10)
        password_element = wait.until(
            EC.presence_of_element_located((By.ID, "new_login_password"))
        )
        password_element.clear()
        password_element.send_keys(password)
        time.sleep(0.5)

    @staticmethod
    def enter_totp(driver: Chrome, totp: str) -> None:
        """Enter TOTP code in the login form."""
        wait = WebDriverWait(driver, 15)
        totp_element = wait.until(
            EC.presence_of_element_located((By.ID, "new_login_otp"))
        )
        totp_element.clear()
        totp_element.send_keys(totp)
        time.sleep(0.5)

    @staticmethod
    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def login(user_id: str, password: str, totp: str) -> None:
        """
        Perform automated login to Aliceblue platform.

        Args:
            user_id: Aliceblue user ID
            password: Account password
            totp: TOTP secret key for 2FA

        Raises:
            InvalidArgumentException: Invalid credentials or TOTP key
            BrokerException: Login failed due to page issues
            RetryableException: Temporary failures that can be retried
        """
        driver = None
        try:
            driver = Selenium().get_browser(headless=True)
            driver.get("https://ant.aliceblueonline.com/")

            # Wait for login form to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "new_login_userId")))

            # Step 1: Enter credentials and proceed
            AliceblueLogin.enter_user_id(driver, user_id)
            AliceblueLogin.enter_password(driver, password)
            AliceblueLogin.click_on_next(driver)

            # Step 2: Enter TOTP and complete login
            totp_code = pyotp.TOTP(str(totp)).now()
            AliceblueLogin.enter_totp(driver, totp_code)

            # Try to click Next button, but it might auto-submit
            time.sleep(1)  # Allow page to process TOTP
            AliceblueLogin._click_button_by_id(driver, "buttonLabel_Next", timeout=3)

            # Wait for successful login (dashboard loads)
            time.sleep(2)
            logger.info(f"Aliceblue Login successfull for {user_id}")

        except binascii.Error:
            raise InvalidArgumentException("Invalid TOTP key provided")
        except InvalidArgumentException:
            raise
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Aliceblue login failed: {str(e)}")
            raise BrokerException(
                "Login to Aliceblue failed. Please log in manually to generate a new token"
            )
        except WebDriverException as e:
            logger.error(f"Selenium WebDriver error: {str(e)}")
            raise RetryableException("Selenium setup needs to be fixed")
        except Exception as e:
            logger.error(f"Unexpected error during Aliceblue login: {str(e)}")
            raise RetryableException(str(e))
        finally:
            if driver:
                driver.quit()
