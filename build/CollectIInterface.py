#!/usr/bin/env python2.7
"""
Collect IInterface java source in android framework
move from ANDROID TO _IINTERFACE directory
"""

import Config
import logging
import fnmatch
import shutil
import os
import re

logger = logging.getLogger(__name__)

def fileWalker(travelPath, excludePattern, includePattern):

    includes = r'|'.join( [fnmatch.translate(x) for x in includePattern ])
    excludes = r'|'.join( [fnmatch.translate(x) for x in excludePattern ]) or r'$.'

    result = []
    for root, dirs, files in os.walk(travelPath ):
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]    # filter excluded folders
        dirs[:] = [os.path.join(root, d) for d in dirs]

        files = [ f for f in files if re.match(includes, f)] # filter satisfied file
        files = [os.path.join(root, f) for f in files]

        result += files
    return result

def recursiveCopy(source, target, excludePattern, includePattern, matchPattern):
    for file in fileWalker(source, excludePattern, includePattern):
        with open(file, "r") as fd:
            buf = fd.read()
            if matchPattern(buf):
                t_file = file.split("/")[-1]
                shutil.copyfile(file, os.path.join(target, t_file))
                logger.info(">> {}".format(os.path.join(target, t_file)))


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    excludePattern = ['.git', 'vnc']

    logger.info("Collecting system level interface: ")
    framework = Config.System.FRAMEWORK
    interface = Config.Path._IINTERFACE
    if not os.path.exists(interface):
        os.makedirs(interface)
    interfacePattern = (lambda buf: re.search("extends (android.os.)?IInterface[^>]",buf)\
            and (buf.find("descriptor") > 0 or buf.find("Stub") > 0))
    recursiveCopy(framework, interface, excludePattern, ["I*.java"], interfacePattern)

    logger.info("Collecting AIDL interface: ")
    aidl      = Config.System.AIDL_CACHE
    recursiveCopy(aidl, interface, excludePattern, ["*.java"], interfacePattern)

    logger.info("Collecting Native interface: ")
    core      = Config.System.JAVA_POOL
    native    = Config.Path._NATIVE_STUB
    if not os.path.exists(native):
        os.makedirs(native)
    nativePattern = (lambda buf: buf.find("descriptor") > 0 )
    recursiveCopy(core, native, excludePattern, ["*Native.java"], nativePattern)

    logger.info("Collecting Hardware interface: ")
    hardware  = Config.Path._HARDWARE
    if not os.path.exists(hardware):
        os.makedirs(hardware)
    hardwarePattern = (lambda buf: buf.find("IMPLEMENT_META_INTERFACE") > 0 )
    recursiveCopy(framework, hardware, excludePattern, ["I*.cpp"], hardwarePattern)

