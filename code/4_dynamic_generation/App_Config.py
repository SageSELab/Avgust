
class Etsy:
    def __init__(self):
        self.appname = 'etsy'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.etsy.android",
            "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
        }

class Abc:
    def __init__(self):
        self.appname = 'abc'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.abc.abcnews",
            "appActivity": "com.abc.abcnews.ui.StartActivity"
        }

class SixPM:
    def __init__(self):
        self.appname = '6pm'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.zappos.android.sixpmFlavor",
            "appActivity": "com.zappos.android.activities.HomeActivity"
        }

class NewsBreak:
    def __init__(self):
        self.appname = 'newsbreak'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 10000,
            "appPackage": "com.particlenews.newsbreak",
            "appActivity": "com.particlemedia.ui.guide.NetworkWarningActivity"
        }

class Zappos:
    def __init__(self):
        self.appname = 'zappos'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.zappos.android",
            "appActivity": "com.zappos.android.activities.HomeActivity"
        }


class Home:
    def __init__(self):
        self.appname = 'home'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.contextlogic.home",
            "appActivity": "com.contextlogic.wish.activity.browse.BrowseActivity"
        }

class FiveMiles:
    def __init__(self):
        self.appname = '5miles'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.thirdrock.fivemiles",
            "appActivity": "com.insthub.fivemiles.Activity.GuidePagerActivity"
        }

class AliExpress:
    def __init__(self):
        self.appname = 'aliexpress'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.alibaba.aliexpresshd",
            "appActivity": "com.alibaba.aliexpresshd.home.ui.MainActivity"
        }

class Ebay:
    def __init__(self):
        self.appname = 'ebay'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.ebay.mobile",
            "appActivity": "com.ebay.mobile.activities.MainActivity"
        }

class Geek:
    def __init__(self):
        self.appname = 'geek'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.contextlogic.geek",
            "appActivity": "com.contextlogic.wish.activity.browse.BrowseActivity"
        }
        
class GoogleShopping:
    def __init__(self):
        self.appname = 'googleshopping'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.google.android.apps.shopping.express",
            "appActivity": "com.google.android.apps.shopping.express.main.PreMainActivity"
        }

class Groupon:
    def __init__(self):
        self.appname = 'groupon'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.groupon",
            "appActivity": ".onboarding.main.activities.Onboarding"
        }

class Wish:
    def __init__(self):
        self.appname = 'wish'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.contextlogic.wish",
            "appActivity": "com.contextlogic.wish.activity.browse.BrowseActivity"
        }

class BBC:
    def __init__(self):
        self.appname = 'bbc'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "bbc.mobile.news.ww",
            "appActivity": "bbc.mobile.news.v3.app.TopLevelActivity"
        }

class Buzzfeed:
    def __init__(self):
        self.appname = 'buzzfeed'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.buzzfeed.android",
            "appActivity": "com.buzzfeed.android.activity.SplashActivity"
        }

class Fox:
    def __init__(self):
        self.appname = 'fox'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.foxnews.android",
            "appActivity": "com.foxnews.android.corenav.StartActivity"
        }

class Reuters:
    def __init__(self):
        self.appname = 'reuters'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.thomsonreuters.reuters",
            "appActivity": "com.thomsonreuters.reuters.activities.SplashActivity"
        }

class DailyHunt:
    def __init__(self):
        self.appname = 'Dailyhunt'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.eterno",
            "appActivity": "com.newshunt.appview.common.ui.activity.HomeActivity"
        }

class Guardian:
    def __init__(self):
        self.appname = 'guardian'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.guardian",
            "appActivity": "com.guardian.feature.stream.NewHomeActivity"
        }

class USAToday:
    def __init__(self):
        self.appname = 'usatoday'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.usatoday.android.news",
            "appActivity": "com.gannett.android.news.ActivityLoading"
        }

class DailyHunt:
    def __init__(self):
        self.appname = 'dailyhunt'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.eterno",
            "appActivity": "com.newshunt.onboarding.view.activity.OnBoardingActivity"
        }

class Zappos:
    def __init__(self):
        self.appname = 'zappos'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 100000,
            "appPackage": "com.zappos.android",
            "appActivity": "com.zappos.android.activities.HomeActivity"
        }