#!/usr/bin/env python

import argparse
import importlib
import os
import re
import lsst.pex.config as pexConfig
import lsst.pex.config.history as pexConfigHistory

class ConfigDoc(object):
    def __init__(self, writeCurrentValue=True, writeSourceLine=True,
            writeDoc=True, writeHistory=True):
        self.writeCurrentValue = writeCurrentValue
        self.writeSourceLine = writeSourceLine
        self.writeDoc = writeDoc
        self.writeHistory = writeHistory

    def docName(self, configName, overrides, configFiles):
        lastDot = configName.rfind('.')
        configModule = configName[0:lastDot]
        configClass = configName[lastDot+1:]
        ConfigClass = getattr(importlib.import_module(configModule),
                                    configClass)
        config = ConfigClass()
        if configFiles is not None:
            for f in configFiles:
                config.load(f)

        if overrides is not None:
            for override in overrides:
                name, sep, valueStr = override.partition("=")
                # see if setting the string value works; if not, try eval
                try:
                    setDottedAttr(config, name, valueStr)
                except Exception:
                    try:
                        value = eval(valueStr, {})
                    except Exception:
                        raise RuntimeError(
                                "Cannot parse %r as a value for %s" % (
                                    valueStr, name))
                    try:
                        setDottedAttr(config, name, value)
                    except Exception, e:
                        raise RuntimeError("Cannot set config.%s=%r: %s" % (
                            name, value, str(e))) 

        self.doc(config)


    def doc(self, config, prefix=""):
        m = re.search(r"'(.*)'>", str(type(config)))
        if prefix != "":
            line = "%s (%s):" % (prefix[0:-1], m.group(1))
        else:
            line = "Doc for %s:" % (m.group(1),)
        if self.writeSourceLine:
            line += " " + _sourceLine(config._source)
        print line
        # Need str() here because __doc__ is sometimes None
        if self.writeDoc:
            print _colorize('"""%s"""' % (str(config.__doc__),), 'TEXT')
        for k, v in config.iteritems():
            field = config._fields[k]
            if isinstance(v, pexConfig.Config):
                self.doc(v, prefix + k + ".")
            elif isinstance(v, pexConfig.configChoiceField.ConfigInstanceDict):
                attr = "name"
                if field.multi:
                    attr = "names"
                line = prefix + k + "." + attr
                if self.writeCurrentValue:
                    line += " = " + _colorize(str(getattr(v, attr)), 'VALUE')
                print line
                if self.writeHistory:
                    for val, tb, label in config.history[k]:
                        line = "\t" + _colorize(str(val), 'VALUE')
                        line += " " + label
                        if self.writeSourceLine:
                            line += " " + _sourceLine(tb[-1])
                        print line
                if isinstance(v, pexConfig.registry.RegistryInstanceDict):
                    iterable = field.typemap.registry
                elif hasattr(v.types, "__iter__"):
                    iterable = v.types
                else:
                    # No way to iterate through the typemap so have to
                    # iterate through the dictionary of values that have
                    # been set
                    print "[unable to show unset configs]"
                    iterable = v
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
                        self.doc(documentable, "%s%s['%s']." % (prefix, k, n))
            elif isinstance(v, pexConfig.configurableField.ConfigurableInstance):
                line = prefix + k + ".target"
                if self.writeCurrentValue:
                    line += " = " + _colorize(str(v.target), 'VALUE')
                print line
                if self.writeHistory:
                    for val, tb, label in config.history[k]:
                        line = "\t" + _colorize(str(val), 'VALUE')
                        line += " " + label
                        if self.writeSourceLine:
                            line += " " + _sourceLine(tb[-2])
                        print line
                self.doc(v.value, prefix + k + ".")
            else:
                line = prefix + k
                if self.writeCurrentValue:
                    line += " = " + _colorize(str(v), 'VALUE')
                if self.writeSourceLine and not self.writeHistory:
                    line += " " + _sourceLine(config.history[k][-1][1][-1])
                print line
                if self.writeDoc:
                    for l in field.doc.split('\n'):
                        print "\t" + _colorize(l, 'TEXT')
                    if hasattr(field, "dtype"):
                        if field.dtype == pexConfig.dictField.Dict:
                            print "\tDict: %s => %s" % (str(field.keytype),
                                str(field.itemtype))
                        elif field.dtype == pexConfig.listField.List:
                            print "\tList: %s" % (str(field.itemtype),)
                        else:
                            print "\t%s" % (str(field.dtype),)
                if self.writeHistory:
                    for v, tb, label in config.history[k]:
                        line = "\t" + _colorize(str(v), 'VALUE')
                        line += " " + label
                        if self.writeSourceLine:
                            line += " " + _sourceLine(tb[-1])
                        print line
    
def _colorize(value, color):
    return pexConfigHistory._colorize(value, color)

def _sourceLine(tbEntry):
    fileName = re.sub(r'.*/python/lsst/', "", tbEntry[0])
    return _colorize("(%s:%d)" % (fileName, tbEntry[1]), 'FILE')

def setDottedAttr(item, name, value):
    """Like setattr, but accepts hierarchical names, e.g. foo.bar.baz"""
    subitem = item
    subnameList = name.split(".")
    for subname in subnameList[:-1]:
        subitem = getattr(subitem, subname)
    subitem._fields[subnameList[-1]].__set__(subitem, value,
            label="command line")

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
    parser.add_argument('-c', '--config', nargs="*", dest="overrides",
            help="config override(s)")
    parser.add_argument('-C', '--configfile', nargs="*", dest="configFiles",
            help="config override file(s)")

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
    cd.docName(args.config[0], args.overrides, args.configFiles)
