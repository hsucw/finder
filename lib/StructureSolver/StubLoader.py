import logging
import sys
import os
import pkgutil
import json

logger = logging.getLogger(__name__)

class StubLoader(object):
    """docstring for TransactionLoader"""
    def __init__(self, stubFolderName, loadOnly = None):
        self.stubFolderName = stubFolderName
        self.package = stubFolderName
        self.stubs = {}
        count = 0
        sys.path.append(stubFolderName)

        for module_loader, name, ispkg in pkgutil.iter_modules([stubFolderName]):
            if loadOnly is not None:
                if name not in loadOnly:
                    next

            module = module_loader.find_module(name).load_module(name)
            instance = module.OnTransact()
            try:
                descriptor = instance.descriptor if hasattr(instance, "descriptor") else instance.DESCRIPTOR
            except AttributeError:
                logger.warn("Cannot Find Descriptor in {}".format(name))
                next
            self.stubs[descriptor] = instance
            logger.debug("Load stub: [{}] = {}".format( descriptor, name))
            count += 1
        logger.info("Total load in {} modules".format(count))


class Property(object):
    pass

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    sloader = StubLoader(sys.argv[1])


