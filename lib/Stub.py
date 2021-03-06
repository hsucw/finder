import logging
import sys

import build.Config as Config
sys.path.append(Config.Path.CREATOR)
from android.os.StrictMode import StrictMode

logger = logging.getLogger(__name__)

class Stub(object):
    def __init__(self):
        pass

    def creatorResolver(self, name, *args):
        """ function call to require creator constructor for reconstruct \
        java object from parcel raw data
        from
        _arg0 = android.media.AudioAttributes.CREATOR.createFromParcel(data);
        to
        _arg0 = self.creatorResolver("android.media.AudioAttributes", data)
        """

        className = name.split(".")[-1]
        try:
            creator = __import__(name, globals(), locals(), className)
            result = getattr(creator, className).CREATOR.createFromParcel(*args)
        except ImportError:
            name = ".".join(name.split(".")[:-1])
            creator = __import__(name, globals(), locals(), className)
            result = getattr(creator, className).CREATOR.createFromParcel(*args)

        return "creator of [{}]".format(creator)

    def interfaceResolver(self, name, strongBinder):
        """ function call of 'asInterface', ex:
        from:
        _arg3 = android.media.IAudioFocusDispatcher.Stub.asInterface(data.readStrongBinder());
        to:
        _arg3 = self.interfaceResolver("android.media.IAudioFocusDispatcher", data.readStrongBinder())
        """
        return "solved interface of [{}]".format(name)

    def newInstance(self, name, *args):
        """
            Do not know this
        """
        if  len(args) == 0:
            return object()
        if  name == "StrictMode.ViolationInfo":
            return StrictMode.ViolationInfo(*args)
        raise CallCreator("new instance with name: {}({})".format(name, [str(type(i)) for i in args]))

    def callFunction(self, funName, *args, **kargs):
        result = list(args)
        result.insert(0, funName)
        return result

class CallCreator(Exception):
    pass
