
class File():
    def __init__(self, file_path,mode,step=0):
        self.bufferFile = open(file=file_path, mode=mode)
        self.offset = 0
        self.step = step
    
    def read(self):
        self.bufferFile.seek(self.offset*self.step)
        self.offset += 1
        return self.bufferFile.read(self.step)

    def is_EOF(self):
        self.bufferFile.seek(self.offset*self.step)
        if (self.bufferFile.read(self.step) == ''):
            return True
        return False

    def write(self,data):
        self.bufferFile.write(data)

    def close(self):
        self.bufferFile.close()