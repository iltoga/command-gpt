import unittest
import subprocess
from  os_app_opener import MacOSAppOpener

class TestAppOpener(unittest.TestCase):
    def setUp(self):
        self.app_opener = MacOSAppOpener()

    def test_app_exists(self):
        self.assertTrue(self.app_opener.app_exists('Safari'))
        self.assertFalse(self.app_opener.app_exists('NonexistentApp'))

    def test_open_app(self):
        # Test opening an existing application
        self.assertIsInstance(self.app_opener.open_app('Safari'), subprocess.CompletedProcess)
        subprocess.run(['sleep', '1'])
        # Close the application
        subprocess.run(['osascript', '-e', 'quit app "Safari"'])
        subprocess.run(['sleep', '1'])

        # Test opening a nonexistent application
        self.assertFalse(self.app_opener.open_app('NonexistentApp'))

    def test_close_app(self):
        subprocess.run(['open', '-a', 'Safari'])
        subprocess.run(['sleep', '1'])
        # Test closing an existing application
        self.assertIsInstance(self.app_opener.close_app('Safari'), subprocess.CompletedProcess)
        subprocess.run(['sleep', '1'])

if __name__ == '__main__':
    unittest.main()
