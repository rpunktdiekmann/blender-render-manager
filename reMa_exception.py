class BlenderVersionException(Exception):
    def __init__(self):
        self.message = 'Versions below 2.8 are not supported'

class OSNotSupportedException(Exception):
    def __init__(self):
        self.message = 'Your OS is not supported \n Supported are: Windows, Linux or MacOS'

class NoCameraException(Exception):
    def __init__(self):
        self.message = 'Blend file has no camera'

class IOException(Exception):
    def __init__(self):
        self.message = 'Error while reading/writing to file'