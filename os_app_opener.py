import subprocess
import os.path
import abc

# Example usage:
# app_opener = MacOSAppOpener()
# if app_opener.app_exists('Safari'):
#     app_opener.open_app('Safari')
# else:
#     print('Safari is not installed.')
class AppOpener(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def app_exists(self, app_name):
        pass

    @abc.abstractmethod
    def open_app(self, app_name):
        pass

    @abc.abstractmethod
    def close_app(self, app_name):
        pass

class MacOSAppOpener(AppOpener):
    def app_exists(self, app_name):
        app_path = '/Applications/{}.app'.format(app_name)
        return os.path.exists(app_path)

    def open_app(self, app_name):
        if not self.app_exists(app_name):
            print('Error: Application "{}" not found.'.format(app_name))
            return False
        return subprocess.run(['open', '-a', app_name])

    def close_app(self, app_name):
        if not self.app_exists(app_name):
            print('Error: Application "{}" not found.'.format(app_name))
            return False
        print('Closing application "{}"...'.format(app_name))
        return subprocess.run(['osascript', '-e', 'quit app "{}"'.format(app_name)])

class WindowsAppOpener(AppOpener):
    def app_exists(self, app_name):
        app_path = r'C:\Program Files\{}.exe'.format(app_name)
        return os.path.exists(app_path)

    def open_app(self, app_name):
        if not self.app_exists(app_name):
            print('Error: Application "{}" not found.'.format(app_name))
            return
        subprocess.Popen(['start', '', app_name], shell=True)

class LinuxAppOpener(AppOpener):
    def app_exists(self, app_name):
        app_path = '/usr/bin/{}'.format(app_name)
        return os.path.exists(app_path)

    def open_app(self, app_name):
        if not self.app_exists(app_name):
            print('Error: Application "{}" not found.'.format(app_name))
            return
        subprocess.Popen([app_name])
