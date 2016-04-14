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

    # The common exclude file pattern
    excludePattern = ['.git', 'vnc']

    # The source and destination directory path
    framework = Config.System.FRAMEWORK
    interface = Config.Path._IINTERFACE
    aidl      = Config.System.AIDL_CACHE
    core      = Config.System.JAVA_POOL
    native    = Config.Path._NATIVE_STUB
    hardware  = Config.Path._HARDWARE

    # Check the out fold existence
    if not os.path.exists(interface):
        os.makedirs(interface)
    if not os.path.exists(native):
        os.makedirs(native)
    if not os.path.exists(hardware):
        os.makedirs(hardware)

    # The pattern for matching, using lambda function
    interfacePattern = (lambda buf: re.search("extends (android.os.)?IInterface[^>]",buf)\
            and (buf.find("descriptor") > 0 or buf.find("Stub") > 0))
    nativePattern = (lambda buf: buf.find("descriptor") > 0 )
    hardwarePattern = (lambda buf: buf.find("IMPLEMENT_META_INTERFACE") > 0 )

    # Start to Collection
    logger.info("Collecting system level interface: ")
    recursiveCopy(framework, interface, excludePattern, ["I*.java"], interfacePattern)

    logger.info("Collecting AIDL interface: ")
    recursiveCopy(aidl, interface, excludePattern, ["*.java"], interfacePattern)

    logger.info("Collecting Native interface: ")
    recursiveCopy(core, native, excludePattern, ["*Native.java"], nativePattern)

    logger.info("Collecting Hardware interface: ")
    recursiveCopy(framework, hardware, excludePattern, ["I*.cpp"], hardwarePattern)

