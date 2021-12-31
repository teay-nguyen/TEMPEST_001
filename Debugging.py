
class Debug:
    def __init__(self):
        self.DebugLog = []

    def ResetLog(self):
        self.DebugLog = []

    def AppendLog(self, log):
        self.DebugLog.append(log)

    def PrintFormatted(self):
        for i, log in enumerate(self.DebugLog):
            print()
            print('------------------------')
            print(f'Log No. {i}: {log}')
            print('------------------------\n')
