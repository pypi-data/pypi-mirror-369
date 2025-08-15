# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys

from Loading import LoadingDot, LoadingPercentage, LoadingBar
import time




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # l = LoadingDot()
    # #l = LoadingBar(logMsg=False)
    l = LoadingPercentage(0, 10, fill= '   ', loadingMSG= 'My love is growing')
    print('inizio')
    l.StartAnimation()
    # time.sleep(1)
    for i in range(11):
        l.iteration = i
        l.suffix = 'Iterazione n: ' + str(i)
        time.sleep(1)
    l.done = True
    print('end')
