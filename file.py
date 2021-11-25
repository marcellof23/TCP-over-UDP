import os


class File():
    def __init__(self, file_path, mode, step=0):
        self.bufferFile = open(file=file_path, mode=mode)
        self.filePath = file_path
        self.offset = 0
        self.step = step

    def read(self):
        self.bufferFile.seek(self.offset)
        self.offset += self.step
        return self.bufferFile.read(self.step)

    def is_EOF(self):
        self.bufferFile.seek(self.offset)
        return not (self.bufferFile.read(self.step))

    def write(self, data):
        data = data.rstrip(b'\x00')
        self.bufferFile.write(data)

    def writeMetadata(self, fileName, fileExt):
        os.setxattr(self.filePath, 'user.originalFileName',
                    str.encode(fileName))
        os.setxattr(self.filePath, 'user.originalFileExt',
                    str.encode(fileExt))

    def close(self):
        self.bufferFile.close()
