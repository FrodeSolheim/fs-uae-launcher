class DriverTestHelper:
    def __init__(self, driver):
        self.driver = driver

    def install(self, installdir):
        print("Installing into", installdir)
        self.driver.prepare()
        self.driver.install()
