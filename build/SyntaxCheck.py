import py_compile
import os
from os import path
import logging

import Config

logger = logging.getLogger(__name__)

def absjoin(*args):
    return path.abspath( path.join(*args))

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    #checkDirs = [Config.Path.STUB, Config.Path.CREATOR]
    checkDirs = [Config.Path.STUB]
    log = absjoin(Config.Path.CUROUT, "syntax_error.log")
    logFd = open(log, "w")

    logger.info(checkDirs)
    total = 0
    counter = 0

    for chkDir in checkDirs:
        for root, dir, files in os.walk(chkDir):
            logger.info("Solving dir: {}".format(root))
            for file in files:
                if  file != "__init__.py" and file.endswith(".py"):
                    total += 1
                    logger.info("    o {} ".format(file))
                    try:
                        py_compile.compile( absjoin(root, file) , doraise=True)
                    except py_compile.PyCompileError as e:
                        counter += 1
                        logFd.write("="*10 + "\n")
                        logFd.write("filename: {}\n".format(absjoin(root, file)))
                        logFd.write(str(e))
                        logFd.write("\n" + "="*10 + "\n")



    logger.info("="*10)
    logger.info("Parse complete!")
    logger.info("Total parsed: {}, syntax error: {}".format(total, counter))
