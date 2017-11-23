from time import sleep
import sys
from datetime import datetime

"""
sys.stdout.write(
    "\nstart - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
sys.stdout.flush()
for i in range(21):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-20s] %d%% \t (%d / 20)" %
                     ('='*i, 5*i, i))
    sys.stdout.flush()
    sleep(0.25)
    
sys.stdout.write("\n")
"""

class StatusBar:
    def __init__(self, num):
        self.start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.num = num
        self.done = 0
        # Write the start time
        sys.stdout.write("\nstart - " + self.start + "\n")
        
    def next(self):
        string = ("[%-20s] %d%% \t (%d / %d)" %
               ("="*self.done, 5*self.done, self.done, self.num))
        self.done += 1
        sys.stdout.write("\r")
        sys.stdout.write(string)
        sys.stdout.flush()
        
