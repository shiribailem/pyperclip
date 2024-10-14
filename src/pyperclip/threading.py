import pyperclip
import threading
from subprocess import TimeoutExpired
from time import time

# If it's running in a thread then more patience is already expected
pyperclip.paste_timeout = 10


class ClipboardThread(threading.Thread):
    def __init__(self, callback=None):
        self.clipboard = None
        self.__old_clipboard = None
        # Optionally accept a callback function
        self.callback = None
        threading.Thread.__init__(self)
        # Identify as daemon so it doesn't hold up program exit
        self.daemon = True

    def run(self):
        # Looping without sleeping is safe as pyperclip calling Popen is a blocking call
        while True:
            try:
                # Cache the old result to identify if the result has changed
                self.__old_clipboard = self.clipboard

                # Use a basic timer, in at least xsel and xclip there can occasionally be significant lag in
                # getting results based on the application that holds the clipboard.
                # If encountered, resfresh the clipboard manually to clear that ownership so the next call is
                # faster.
                timestamp = time()
                self.clipboard = pyperclip.paste()
                if time() - timestamp > 1:
                    pyperclip.copy(self.clipboard)

                if self.callback and self.clipboard != self.__old_clipboard:
                    self.callback(self.clipboard)
            except TimeoutExpired:
                # If it does take 10 seconds it's better to just go ahead and try again.
                self.clipboard = None
