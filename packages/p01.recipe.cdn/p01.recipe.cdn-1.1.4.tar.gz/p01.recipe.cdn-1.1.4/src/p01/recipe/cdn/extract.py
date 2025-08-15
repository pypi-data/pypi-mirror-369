###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import json
import optparse
import os
import sys
import time
import logging
import traceback
import zope.interface
import zope.component
import zope.component.interfaces
from zope.security.proxy import removeSecurityProxy
from zope.configuration import xmlconfig
from zope.publisher.interfaces.http import IResult
from zope.publisher.browser import TestRequest
from p01.cdn import interfaces
from p01.cdn.resource import I18nCDNResource
from p01.cdn.resource import ZRTCDNResource
from p01.cdn.resource import CDNResourceDirectory

import p01.recipe.cdn.cmder


logger = logging.getLogger()
formatter = logging.Formatter('%(levelname)s - %(message)s')

EXCLUDED_NAMES = ('.svn',)


################################################################################
#
# helper

def getResources(layerPaths, url='http://localhost/'):
    resources = ()
    for layerPath in layerPaths:
        print "doing:", layerPath
        # get the layer interface
        moduleName, layerName = layerPath.rsplit('.', 1)
        module = __import__(moduleName, {}, {}, ['None'])
        layer = getattr(module, layerName)
        # now we create a test request with that layer and our custom base URL.
        # Note: we use a zope.publisher TestRequest. In some project we use
        # the p01.publisher TestRequest and a custom locale/langauge setup
        # concept. Which means put custom negotiator is not able to lookup the
        # language from the TestRequest. Bt this is not a problem since we don't
        # negotiate the request locale.
        request = TestRequest(environ={'SERVER_URL': url})
        zope.interface.alsoProvides(request, layer)
        # next we look up all the resources
        resources += tuple(
            zope.component.getAdapters((request,), interfaces.ICDNResource))
    return resources


################################################################################
#
# setup versions

def setUpVersion(name, resource, options):
    """Get output file name (inlcude svn version if enabled)"""
    try:
        fName = resource.manager.addVersion(name, resource, options)
        return '%s:%s' % (resource.rName, fName)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise e


def setUpVersions(name, resource, outNames=[], options=None):
    """Setup resource version and zrt-include file"""
    if isinstance(resource, I18nCDNResource):
        # we collect all resources for each language
        # setup resource per available locale
        for resource in resource.getExtractableResources():
            outName = setUpVersion(resource.rName, resource, options)
            if outName is not None:
                outNames.append(outName)
    elif isinstance(resource, CDNResourceDirectory):
        # we create the directory and walk through the children.
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name)
                setUpVersions(name, subResource, outNames, options)
    elif isinstance(resource, ZRTCDNResource):
        outName = setUpVersion(name, resource, options)
        if outName is not None:
            outNames.append(outName)
    else:
        # simply store the file
        outName = setUpVersion(name, resource, options)
        if outName is not None:
            outNames.append(outName)


################################################################################
#
# extract resources

def doAddFile(name, resource, output, data):
    """Add file (remove existing first)"""
    # ensure output directory
    if not os.path.exists(output):
        os.makedirs(output)
    # setup file path
    rName = resource.manager.getExtractFileName(name, resource)
    fName = os.path.abspath(os.path.join(output, rName))
    # remove existing file
    if os.path.exists(fName) and os.path.isfile(fName):
        os.remove(fName)
    # write file
    outFile = open(fName, 'wb')
    outFile.write(data)
    outFile.close()
    return fName


def saveResource(name, resource, output, data=None):
    if data is None:
        inFile = open(resource.path, 'rb')
        data = inFile.read()
        inFile.close()
    if IResult.providedBy(data):
        data = ''.join(data)
    return doAddFile(name, resource, output, data)


def storeResource(name, resource, output=None, outNames=[]):
    if output is None:
        output = resource.manager.output
    if '%(version)s' in output:
        output = output % {'version': resource.manager.version}
    if not os.path.exists(output):
        os.makedirs(output)
    if isinstance(resource, I18nCDNResource):
        # we collect all files for each language
        # setup resource per available locale
        for resource in resource.getExtractableResources():
            outName = saveResource(resource.rName, resource, output)
            if outName is not None:
                outNames.append(outName)
    elif isinstance(resource, CDNResourceDirectory):
        # we create the directory and walk through the children.
        output = os.path.join(output, resource.__name__)
        if not os.path.exists(output):
            os.makedirs(output)
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name)
                storeResource(name, subResource, output, outNames)
    elif isinstance(resource, ZRTCDNResource):
        data = resource.GET()
        outName = saveResource(name, resource, output, data)
        outNames.append(outName)
    else:
        # simply store the file
        outName = saveResource(name, resource, output)
        outNames.append(outName)


################################################################################
#
# resource uris

def getResourceURIs(uris, resource):
    if isinstance(resource, I18nCDNResource):
        # we collect all uris for each language
        for uri in resource.getURIs():
            if uri not in uris:
                uris.append(uri)
    elif isinstance(resource, CDNResourceDirectory):
        # get recursive resources and call this method again
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name)
                getResourceURIs(uris, subResource)
    else:
        # simply get the uri
        if resource.uri not in uris:
            uris.append(resource.uri)


################################################################################
#
# resource paths

def getSourcePaths(paths, resource):
    if isinstance(resource, I18nCDNResource):
        # we collect all path for each language
        for path in resource.getPaths():
            if path not in paths:
                paths.append(path)
    elif isinstance(resource, CDNResourceDirectory):
        # get recursive resources and call this method again
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name)
                getSourcePaths(paths, subResource)
    else:
        # simply get the path
        if resource.path not in paths:
            paths.append(resource.path)


################################################################################
#
# resource output

def getOutputPath(name, resource, output):
    """Add file (remove existing first)"""
    # setup file path
    rName = resource.manager.getExtractFileName(name, resource)
    return os.path.abspath(os.path.join(output, rName))


def getSourceOutputPaths(name, resource, output=None, outNames=[]):
    if output is None:
        output = resource.manager.output
    if '%(version)s' in output:
        output = output % {'version': resource.manager.version}
    if isinstance(resource, I18nCDNResource):
        # we collect all files for each language
        # setup resource per available locale
        for resource in resource.getExtractableResources():
            outName = getOutputPath(resource.rName, resource, output)
            if outName is not None:
                outNames.append(outName)
    elif isinstance(resource, CDNResourceDirectory):
        # we create the directory and walk through the children.
        output = os.path.join(output, resource.__name__)
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name)
                getSourceOutputPaths(name, subResource, output, outNames)
    elif isinstance(resource, ZRTCDNResource):
        outName = getOutputPath(name, resource, output)
        outNames.append(outName)
    else:
        # simply store the file
        outName = getOutputPath(name, resource, output)
        outNames.append(outName)


################################################################################
#
# skip names

def printSkipNames(options, skipped):
    missing = []
    if options.skip:
        print "Skipped resources"
        for name in options.skip:
            if name in skipped:
                print 'SKIP: %s' % name
            else:
                missing.append(name)
    if missing:
        print "Resources listed in skip option but not seen"
        for name in missing:
            print name


################################################################################
#
# process cdn methods

def process(options):
    """Process command"""

    # run the configuration
    xmlconfig.file(options.zcml)
    if options.registry is not None:
        # apply base ``registry`` name if given
        sm = zope.component.getSiteManager()
        sm = removeSecurityProxy(sm)
        base = zope.component.queryUtility(
            zope.component.interfaces.IComponents, name=options.registry)
        bases = (removeSecurityProxy(base),)
        sm.__bases__ = bases + sm.__bases__

    skipped = []
    # extract the resources
    # get resource list
    resources = getResources(options.layers)
    if options.command == 'setup':
        # setup versions and zrt-replace.less file
        managers = set()
        outNames = []
        print 'SETUP'
        for name, resource in resources:
            if name not in options.skip:
                managers.add(resource.manager)
                try:
                    setUpVersions(name, resource, outNames, options)
                except KeyboardInterrupt as e:
                    raise e
                except Exception:
                    traceback.print_exc()
                    print '====================='
                    print 'SETUP FAILED: %s %r %r' % (
                        name, resource, resource.manager)
                    print '====================='
                    sys.exit(1)
            else:
                skipped.append(name)
        print '\n'.join(outNames)
        print "Save versions and zrt files"
        changed = False
        for manager in managers:
            print "CDN Manager: %s" % manager
            print "Versions:    %s" % manager.svnVersionSourcePath
            print "ZRT Replace: %s" % manager.svnZRTReplacePath
            if not manager.checkVersions():
                manager.saveVersions()
                manager.saveZRTReplace()
                changed = True
        if changed:
            print "Sleep %s seconds, give less compiler some time to compile" % \
                options.sleepForCompileLess
        else:
            print "No versions changed, no need to sleep for less compiler"
        time.sleep(options.sleepForCompileLess)
    if options.command == 'extract':
        # now we can dump our resources to the output location given from the
        # recipe or if None, to the resource manager output location
        outNames = []
        output = options.output
        print 'EXTRACT'
        for name, resource in resources:
            if name not in options.skip:
                try:
                    storeResource(name, resource, output, outNames)
                except KeyboardInterrupt as e:
                    raise e
                except Exception:
                    traceback.print_exc()
                    print '====================='
                    print 'EXTRACT FAILED: %s %r %r' % (
                        name, resource, resource.manager)
                    print '====================='
                    sys.exit(1)
            else:
                skipped.append(name)
        print '\n'.join(outNames)
    elif options.command == 'uris':
        # if we only want to list the paths
        print 'URIS'
        uris = []
        for name, resource in resources:
            getResourceURIs(uris, resource)
        print '\n'.join(uris)
    elif options.command == 'paths':
        # if we only want to list the source paths
        print 'PATHS'
        paths = []
        for name, resource in resources:
            if name not in options.skip:
                getSourcePaths(paths, resource)
            else:
                skipped.append(name)
        print '\n'.join(paths)
    elif options.command == 'output':
        # if we only want to list the ouput paths
        print 'OUTPUT'
        outNames = []
        output = options.output
        for name, resource in resources:
            if name not in options.skip:
                getSourceOutputPaths(name, resource, output, outNames)
            else:
                skipped.append(name)
        print '\n'.join(outNames)
    # print skip names
    printSkipNames(options, skipped)


###############################################################################
# command-line

class Options(object):
    """Options

    TThe option class provides the following attributes:

    - svn
    - command
    - registry
    - layers
    - skip
    - zrtPrefix
    - zrtDirPrefix
    - zrtPrefixes
    - sleepForCompileLess
    - output

    """

    def __init__(self, data):
        self.__data = data
        self.svn = p01.recipe.cdn.cmder.SVN()

    def __getattr__(self, name):
        try:
            return self.__data[name]
        except KeyError:
            raise AttributeError(name)


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
    data['command'] = positional[0]
    return Options(data)


def main(args=None):
    # set up logger handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    options = get_options(args)
    os.environ['P01_CDN_RECIPE_PROCESS'] = '%s' % options.command
    try:
        process(options)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
    # Remove the handler again.
    logger.removeHandler(handler)
    sys.exit(0)
