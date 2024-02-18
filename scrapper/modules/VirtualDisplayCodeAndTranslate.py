import os
import time
from selenium.webdriver import ActionChains


class SmartDisplayWithTranslate:
    """ Code enable to use builtin chrome translate
        *******************************************

        ...
        Requirement to setup pyvirtual display
        --------
        sudo apt-get install python3-tk python3-dev
        sudo apt-get install xvfb
        pip install xlib pyvirtualdisplay pyautogui
        pip install python-xlib

        ...
        Reference
        --------
        https://stackoverflow.com/questions/32173839/easyprocess-easyprocesscheckinstallederror-cmd-xvfb-help-oserror-errno
        http://fredtantini.free.fr/blog/index.php?article58/automatiser-des-actions-avec-selenium-pyautogui-et-xvfb
        https://stackoverflow.com/questions/35798478/how-i-can-attach-the-mouse-movement-pyautogui-to-pyvirtualdisplay-with-seleniu
        https://github.com/asweigart/pyautogui/issues/133

    """

    def __init__(self):
        print("In Init")
        import Xlib.display
        from pyvirtualdisplay.smartdisplay import SmartDisplay
        self.display = SmartDisplay(visible=0, size=(1080, 720))
        self.display.start()
        import pyautogui
        pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])

    def doTranslate(self, driver):
        import pyautogui
        print("In Do Translate Function")
        self.your_link = driver.find_element_by_xpath('//div')
        self.actionChains = ActionChains(driver)
        self.actionChains.context_click(self.your_link).perform()
        time.sleep(6)
        pyautogui.press("up")
        pyautogui.press("up")
        pyautogui.press("up")
        pyautogui.press("enter")

    def stopSmartDisplay(self):
        print("Stop Smart Display")
        self.display.stop()