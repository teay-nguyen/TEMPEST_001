
class Debug:
    def __init__(self):
        self.DebugLog = []

    def ResetLog(self):
        self.DebugLog = []

    def AppendLog(self, log):
        self.DebugLog.append(log)

    def PrintFormatted(self):
        for i in range(len(self.DebugLog)):
            log = self.DebugLog[i]
            print('\n------------------------')
            print(f'LOG {i}: {log}')
            print('------------------------')
