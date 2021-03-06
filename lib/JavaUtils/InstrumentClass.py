class InstrumentClass(object):
    def __init__(self):
        pass
    
    def __str__(self):
        return self.dump()

    def __repr__(self):
        return self.dump()

    def dump(self):
        line = "Class name : " + self.__class__.__name__
        for mem in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
            if  mem == "dump":
                continue
            line += "{0:>12} {1}".format(mem, getattr(self, mem))
        return line

