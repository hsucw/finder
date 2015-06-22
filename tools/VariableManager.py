import logging
import plyj.parser as plyj
import JavaLib
import json

import IAdaptor
import Helper

logger = logging.getLogger(__name__)

CALLABLE = "callable"
VARIABLE = "variable"

class VariableManager(object):
    def __init__(self):
        self.iAdaptor = IAdaptor.IncludeAdaptor()
        globalScope = self.Scope("__global__", "__global__")
        self.vTable = globalScope
        self.path = [globalScope]
        self.current = globalScope
        self.classPaths = {}
        self.reversedClassPaths = {}

        #member tabel
        self.members = {}
        self.reversedMember = {}


    def setIAdaptor(self, iAdaptor):
        self.iAdaptor = iAdaptor


    def newScope(self, body):
        unit = body.__class__.__name__
        if  (type(body) == plyj.ClassDeclaration or
        type(body) == plyj.InterfaceDeclaration or
        type(body) == plyj.MethodDeclaration or
        type(body) == plyj.ConstructorDeclaration):
            name = Helper.keywordReplace_helper(body.name)
            logger.debug(">>>>>> {}::{}".format(unit, name))
            localScope = self.current.getCallableVariable(name)
            if  not localScope:
                localScope = self.Scope(name, unit)
            self.current.newCallable(name, localScope)
            self.current = localScope
            self.path.append(localScope)

            if  type(body) == plyj.ClassDeclaration or type(body) == plyj.InterfaceDeclaration:
                if  name not in self.classPaths:
                    self.classPaths[name] = self.getPath()
                    self.reversedClassPaths[self.getPath()] = name

    def getPath(self):
        return ".".join(i.name for i in self.path[1:])

    def leaveScope(self, body):
        unit = body.__class__.__name__
        if  (type(body) == plyj.ClassDeclaration or
        type(body) == plyj.InterfaceDeclaration or
        type(body) == plyj.MethodDeclaration or
        type(body) == plyj.ConstructorDeclaration):
            name = body.name
            logger.debug("<<<<<< {}::{}".format(unit, name))
            del self.path[-1]
            self.current = self.path[-1]

    def addInherit(self, cls):
        self.iAdaptor.addInherit(cls)

    def newVariable(self, name, mtype, isMember=False):
        logger.debug(" {}: \033[1;31m{} \033[0m{}".format(" > ".join(str(i) for i in self.path), mtype, name))
        self.current.newVariable(name, mtype)
        if  isMember and name not in self.members:
            self.members[name] = self.getPath() + "." + name
            self.reversedMember[self.getPath() + "." + name] = name

    def isMember(self, name):
        preClass = None
        for scope in reversed(self.path):
            if  scope.vtype == "ClassDeclaration":
                preClass = scope
                break
        if  preClass is None:
            return False
        elif  self.current.isDeclared(name):
            return False
        elif  preClass.isDeclared(name):
            return True
        return False

    def findClass(self, clsName):
        if  clsName in self.classPaths:
            return self.classPaths[clsName]
        return None

    def getFullPathByName(self, cls):
        if  cls not in self.classPaths:
            raise Exception("Try to access a none self class: {}".format(cls))
        return self.classPaths[cls]

    def getPath(self):
        return ".".join(str(i) for i in self.path[1:])

    def dump(self):
        return self._dump(self.vTable)

    def _dump(self, scope, level=0, pattern="    "):
        result = ""
        indent = pattern * level
        level += 1
        for k, v in scope.variables.items():
            result += "{}{}:{}\n".format(indent, k, v)

        for k, v in scope.callables.items():
            result += "{}{}:[\n".format(indent, k)
            result += self._dump(v, level)
            result += "{}]\n".format(indent)
        return result


    ##################################################

    class Scope(object):
        """docstring for Scope"""
        def __init__(self, name, vtype):
            self.name = name
            self.vtype = vtype
            self.variables = {}
            self.callables = {}

        def isDeclared(self, name, type=None):
            if  type == CALLABLE and name in self.callables:
                return True
            elif type == VARIABLE and name in self.variables:
                return True
            elif  name in self.variables or name in self.callables:
                return True
            return False

        def newCallable(self, name, type):
            self.callables[name] = type

        def newVariable(self, name, type):
            self.variables[name] = type

        def getCallableVariable(self, name):
            if  name in self.callables:
                return self.callables[name]
            else:
                return None

        def __str__(self):
            return self.name

        def __repr__(self):
            return str(self.variables)

class NeedFixName(Exception):
    pass

