#!/usr/bin/env python

import argparse
import importlib
import os
import re
import lsst.pex.config as pexConfig



class ConfigDoc(object):
    def __init__(self, writeCurrentValue=True, writeSourceLine=True,
            writeDoc=True, writeHistory=True):
        self.writeCurrentValue = writeCurrentValue
        self.writeSourceLine = writeSourceLine
        self.writeDoc = writeDoc
        self.writeHistory = writeHistory
        self.colors = dict(no="", di="", ex="", pi="")
        if "LS_COLORS" not in os.environ:
            return
        for pair in os.environ["LS_COLORS"].split(':'):
            name, eq, color = pair.partition('=')
            self.colors[name] = '\033[' + color + 'm'

    def doc(self, configName):
        lastDot = configName.rfind('.')
        configModule = configName[0:lastDot]
        configClass = configName[lastDot+1:]
        ConfigClass = getattr(importlib.import_module(configModule),
                                    configClass)
        self._doc(ConfigClass())

    def _colorize(self, value, color):
        return "%s%s%s" % (self.colors[color], value, self.colors['no'])

    def _sourceLine(self, tbEntry):
        fileName = re.sub(r'.*/python/lsst/', "", tbEntry[0])
        return self._colorize("(%s:%d)" % (fileName, tbEntry[1]), 'ex')

    def _doc(self, config, prefix=""):
        m = re.search(r"'(.*)'>", str(type(config)))
        if prefix != "":
            line = "%s (%s):" % (prefix[0:-1], m.group(1))
        else:
            line = "Doc for %s:" % (m.group(1),)
        if self.writeSourceLine:
            line += " " + self._sourceLine(config._source)
        print line
        # Need str() here because __doc__ is sometimes None
        if self.writeDoc:
            print self._colorize('"""%s"""' % (str(config.__doc__),), 'di')
        for k, v in config.iteritems():
            if isinstance(v, pexConfig.Config):
                self._doc(v, prefix + k + ".")
            elif isinstance(v, pexConfig.registry.RegistryInstanceDict) \
                    or isinstance(v, pexConfig.config.ConfigInstanceDict):
                attr = "name"
                if config._fields[k].multi:
                    attr = "names"
                line = prefix + k + "." + attr
                if self.writeCurrentValue:
                    line += " = " + self._colorize(str(getattr(v, attr)), 'pi')
                print line
                if isinstance(v, pexConfig.config.ConfigInstanceDict):
                    if hasattr(v.type, "__iter__"):
                        iterable = v.type
                    else:
                        # No way to iterate through the typemap so have to
                        # iterate through the dictionary of values that have
                        # been set
                        iterable = v
                else:
                    iterable = config._fields[k].typemap.registry
                for n, c in iterable.iteritems():
                    documentable = None
                    if n in v:
                        # Document the actual value
                        documentable = v[n]
                    elif isinstance(c, pexConfig.Config):
                        documentable = c
                    elif hasattr(c, "ConfigClass"):
                        # We just have a potential value, so construct it to
                        # document it
                        documentable = c.ConfigClass()
    
                    if documentable is not None:
                        self._doc(documentable, "%s%s['%s']." % (prefix, k, n))
            else:
                line = prefix + k
                if self.writeCurrentValue:
                    line += " = " + self._colorize(str(v), 'pi')
                if self.writeSourceLine and not self.writeHistory:
                    line += " " + self._sourceLine(config.history[k][-1][1][-1])
                print line
                if self.writeDoc:
                    for l in config._fields[k].__doc__.split('\n'):
                        print "\t" + self._colorize(l, 'di')
                if self.writeHistory:
                    for v, tb in config.history[k]:
                        line = "\t" + self._colorize(str(v), 'pi')
                        if self.writeSourceLine:
                            line += " " + self._sourceLine(tb[-1])
                        print line
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Describe an lsst.pex.config.Config.')
    parser.add_argument('-a', '--all', action='store_true',
            help="write all available information")
    parser.add_argument('-d', '--doc', action='store_true',
            help="write docstrings")
    parser.add_argument('-l', '--line', action='store_true',
            help="write source file and line number")
    parser.add_argument('-H', '--history', action='store_true',
            help="write value history")
    parser.add_argument('-v', '--value', action='store_true',
            help="write current value")
    parser.add_argument('config', type=str, nargs=1,
            help="fully-qualified name of Config class (package must be setup)")
    args = parser.parse_args()

    if args.all:
        args.doc = True
        args.line = True
        args.history = True
        args.value = True
    cd = ConfigDoc(writeCurrentValue=args.value, writeSourceLine=args.line,
            writeDoc=args.doc, writeHistory=args.history)
    cd.doc(args.config[0])
