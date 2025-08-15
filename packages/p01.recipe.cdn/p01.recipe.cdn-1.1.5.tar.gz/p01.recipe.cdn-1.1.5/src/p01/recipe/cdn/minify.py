###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: minify.py 5546 2025-07-18 12:27:08Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import json
import gzip
import optparse
import os
import os.path
import sys
import traceback
from cStringIO import StringIO


TRUE_VALUES = ['1', 'true', 'True', 'ok', 'yes', True]

def isTrue(value):
    return value in TRUE_VALUES


class Options(object):
    """Options"""

    def __init__(self, data):
        self.__data = data

    def __getattr__(self, name):
        try:
            return self.__data[name]
        except KeyError:
            raise AttributeError(name)

    def getHeaderIncludes(self):
        res = ''
        for path in self.__data['header_includes']:
            f = open(path)
            res += f.read()
            f.close()
        return res

    def getHeaders(self):
        res = ''
        header = self.__data['header']
        for hStr in header:
            res += '%s\n' % hStr.replace('$$', '$').strip()
        return res

    @property
    def header(self):
        res = ''
        includes = self.getHeaderIncludes()
        headers = self.getHeaders()
        header_includes_first = self.__data['header_includes_first']
        if header_includes_first:
            res += includes
        res += headers
        if not header_includes_first:
            res += includes
        return res

    @property
    def sources(self):
        """Returns sorted sources"""
        sources = self.__data['sources']
        for data in sources:
            yield data['filename'], data['path']


def minifySource(fName, source, options):
    """Minify source file with given library"""
    # get an explicit defined lib or the default lib option
    lib = options.libs.get(fName, options.lib)
    if lib == 'jsmin':
        import jsmin
        return jsmin.jsmin(source)
    elif lib == 'lpjsmin':
        import lpjsmin.jsmin
        return lpjsmin.jsmin.jsmin(source)
    elif lib == 'slimit':
        mangle = False
        mangle_toplevel = False
        if isTrue(options.slimit_mangle):
            mangle = True
        if isTrue(options.slimit_mangle_toplevel):
            mangle_toplevel = True
        import slimit.minifier
        return slimit.minifier.minify(source, mangle, mangle_toplevel)
    elif lib == 'cssmin':
        wrap = False
        if isTrue(options.cssmin_wrap):
            # wrap_css_lines
            wrap = True
        import cssmin
        return cssmin.cssmin(source, wrap)
    else:
        raise Exception('minify library "%s" is unknown' % lib)


def minify(options):
    # minify each file in given order
    minified = []
    for fName, fPath in options.sources:
        f = open(fPath, 'r')
        source = f.read()
        f.close()
        if fName not in options.skip:
            minified.append((fName, minifySource(fName, source, options)))
        else:
            minified.append((fName, source))

    if os.path.exists(options.output):
        os.remove(options.output)
    out = open(options.output, 'wb')
    # add header if given and an additonal space
    first = True
    header = options.header.replace('$$', '$').strip()
    if header:
        out.write(header)
        first = False
    # bundle minified source
    for fName, source in minified:
        if not first:
            # an additional space
            out.write('\n')
        # and write library name as comment
        out.write('/* %s */' % fName)
        # write source
        if not source.startswith('\n'):
            out.write('\n')
        out.write(source)
        first = False
    out.close()
    # calculate and print gzip size
    full = open(options.output)
    fullSource = full.read()
    full.close()
    sio = StringIO()
    gzipFile = gzip.GzipFile(options.output, mode='wb', fileobj=sio)
    gzipFile.writelines(fullSource)
    gzipFile.close()
    gzs = sio.getvalue()
    sio.close()
    gzip_size = len(gzs)
    print "Minified file generated at %s with %sKB" % (options.output,
        os.path.getsize(options.output)/1024)
    print "Serving this file with gzip compresion will have a size of %sKB" % (
        gzip_size/1024)


def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser("%prog [options] output")
    parser.add_option("-c", "--config", dest="config",
        help="json formatted config file path", metavar="FILE")
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    f = open(options.config, 'rb')
    data = json.loads(f.read())
    f.close()
    return Options(data)


def main(args=None):
    options = get_options(args)
    try:
        minify(options)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)

