#!/usr/bin/env python

import logging
import os
from os import path
import copy
import sys

import Config
import Includer
import Compiler
import subprocess

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    sourcePool = Config.System.JAVA_LIBS
    out = Config.Path.CREATOR
    if not os.path.exists(out):
        os.mkdir(out)

    imports = set()
    if  len(sys.argv) > 1 and os.path.isfile(Includer.absjoin(out, sys.argv[1].replace(".", "/")+".py")):
        logger.info("input pkg: {}".format(sys.argv[1]))
        os.remove(Includer.absjoin(out, sys.argv[1].replace(".", "/")+".py"))
        imports.add(sys.argv[1])
    else:
        files = Includer.absjoin(Config.Path.CUROUT, "Parcel_list")

        # load used creator files
        with open(files, "r") as ffd:
            pkgs = ffd.read().split("\n")
        for pkg in pkgs:
            if  pkg.find(".") > 0:
                imports.add(pkg)
            else:
                logger.warn("Ignoring error format:{}".format(pkg))

    # empty set
    solvedPkgs = set()
    while len(imports) > 0:
        logger.info("dependency: []".format(", ".join(imports)))
        toSolve = copy.copy(imports)

        for pkg in toSolve:
            solvedPkgs.add(pkg)
            imports.remove(pkg)

            # find built-in library but not find not solve
            if  pkg.split(".")[0] == "java":
                logger.info("builtin lib: {}".format(pkg))
                continue

            for source in sourcePool:
                pfile = Includer.pkg2path(source, pkg)
                if  os.path.isfile(pfile):
                    break
            else:
                source = Config.System.FRAMEWORK
                result = []
                stop = False
                tmp_pkg = pkg
                while tmp_pkg.find('.') > 0 and not stop:
                    f_basename = tmp_pkg.split('.')[-1]+".java"
                    f_root = "/".join(tmp_pkg.split('.')[:-1])
                    res = subprocess.check_output(["find", source, "-name", f_basename])
                    if res is not "":
                        f_list = res.split("\n")
                        for r in f_list:
                            if r.find(f_root) > 0:
                                result.append(r)
                                stop = True
                    tmp_pkg = ".".join(tmp_pkg.split('.')[:-1])

                if len(result) is 0:
                    logger.warn("Unknown file: {}".format(pkg))
                    continue
                elif len(result) is 1:
                    pfile = result.pop(0)
                    logger.warn("Find file: {}".format(pfile))
                else:
                    logger.warn("Multiple file: {}".format(result))
                    continue


            targetFile = path.join(out, path.relpath(pfile, source)).replace(".java", ".py")
            targetDir = path.dirname(targetFile)

            if  os.path.isfile(targetFile):
                continue

            logger.info("<<<NEW FILE>>> # {}".format(targetFile))

            compiler = Compiler.Compiler()
            try:
                result = compiler.compilePackage(source, pfile)
            except:
                logger.info(pfile)
                logger.info(sys.exc_info)
                raise

            newDiscover = compiler.imports - solvedPkgs
            if  len(newDiscover) > 0:
                logger.info("new discover: {}".format(", ".join(newDiscover)))
                imports = imports.union(newDiscover)


            if not os.path.exists(targetDir):
                os.makedirs(targetDir)

            with open(targetFile, "w") as targetFd:
                targetFd.write(result)

    for root, dirs, files in os.walk(out):
        init = path.join(root, "__init__.py")
        with open(init, 'w'):
            os.utime(init, None)
