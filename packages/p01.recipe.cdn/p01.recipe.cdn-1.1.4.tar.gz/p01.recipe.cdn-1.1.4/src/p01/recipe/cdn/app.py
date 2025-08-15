###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Z3c development recipes
$Id:$
"""

import os
import os.path
import sys
import json
import io
import zc.buildout
import zc.recipe.egg

TRUE_VALUES = ('yes', 'true', 'True', '1', 'on')
FALSE_VALUES = ('no', 'false', 'False', '0', 'off')

json_dump_kwargs = {'ensure_ascii': False, 'sort_keys': True, 'indent': 4}

def ensure_unicode(obj):
    if isinstance(obj, dict):
        return {ensure_unicode(k): ensure_unicode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_unicode(i) for i in obj]
    elif isinstance(obj, str):
        if sys.version_info[0] < 3:
            return obj.decode('utf-8')
        return obj
    return obj



def getBoolean(v, default=False):
    if v in [True, 'True', 'true', 'on', '1']:
        return True
    elif v in [False, None, 'None', 'null', 'False', 'false', 'off', '0', '']:
        return False
    else:
        return default


zcml_template = """<configure
    xmlns='http://namespaces.zope.org/zope'
    xmlns:meta="http://namespaces.zope.org/meta">
  %s
</configure>
"""


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""


env_template = """os.environ['%s'] = %r
"""


def getRealPath(ws, dPath):
    """Get real path supporting [pkg]/relative/path"""
    dPath = dPath.strip()
    if dPath.startswith('#') or dPath.startswith(';'):
        # skip comments
        return None
    elif dPath.startswith('['):
        # get path for externals packages and eggs
        # [pkg.name] relative/path or
        # [pkg.name]/relative/path or
        # [pkg.name]relative/path
        pkgName, relPath = dPath.split(']')
        # remove leading [ from package name
        pkgName = pkgName[1:]
        # strip empty spaces from relative path
        relPath = relPath.strip()
        # remove leading slash
        if relPath.startswith('/'):
            relPath = relPath[1:]

        # get egg base path
        eggPath = ws.by_key[pkgName].location
        dPath = os.path.join(eggPath, relPath)
    return os.path.abspath(dPath)


# cdn extract
class CDNRecipeBase:
    """Content delivery resource extractor recipe.

    This recipe installes scripts for extract resources from a project based
    on a ZCML configuration file which contains the cdn configuration or
    includes cdn configuration files. See the package p01.cdn for more
    information about cdn resources.
    """

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.cdn'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']

        # setup parts dir
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        wd = options.get('working-directory', options['location'])

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # uri option 1
        # allows to setup an uri and use them in ResourceManager during
        # extraction. This will override the P01_CDN_URI environment variable.
        # NOTE: it's up to you if you use this option. But if so, you need to
        # implement a custom ResourceManger which is able to use the
        # P01_CDN_URI environment variable.
        uri = self.options.get('uri')
        if uri is not None:
            initialization += env_template % ('P01_CDN_URI', uri)

        # uri(s) option 2
        # allows to setup additional uris. Useable if you setup more then one
        # ResourceManager. This will override the P01_CDN_URI_* environment
        # variable.
        # NOTE: it's up to you if you use this option. But if so, you need to
        # implement a custom ResourceManger which is able to use the different
        # P01_CDN_URI_* environment variable.
        urisStr = self.options.get('uris')
        if urisStr is not None:
            uriLines = urisStr.split('\n')
            for line in uriLines:
                name, uri = line.strip().split(' ')
                key = 'P01_CDN_URI_%s' % name
                initialization += env_template % (key, uri)

        # ger base registry name if there is any
        registry = self.options.get('registry', None)

        # setup zcml configuration file
        zcml = self.options.get('zcml', None)
        if zcml is None:
            raise zc.buildout.UserError('No zcml configuration defined.')
        zcml = zcml_template % zcml
        zcmlPath = os.path.join(location, 'configure.zcml')
        with open(zcmlPath, 'w') as f:
            f.write(zcml)
        # append file to dest which will remove it on update
        dest.append(zcmlPath)
        # get output path
        output = self.options.get('output', None)
        if output is not None:
            # get absolut output path
            output = os.path.abspath(output)

        # get skip file names
        layer = self.options.get('layer', None)
        if layer is None:
            layers = []
        else:
            layers = [s.strip() for s in layer.splitlines()]

        # get skip file names
        skip = self.options.get('skip', None)
        if skip is None:
            skip = []
        else:
            skip = [s.strip() for s in skip.splitlines()]

        # get zrt-replace resource prefixes
        zrtPrefix = self.options.get('zrtPrefix')
        zrtDirPrefix = self.options.get('zrtDirPrefix')
        zrtPrefixes = {}
        for pStr in self.options.get('zrtPrefixes', '').splitlines():
            if pStr.startswith(('#', ';')):
                # skip comments
                continue
            if not ':' in pStr:
                raise zc.buildout.UserError(
                    "Bad string used in zrtPrefixes: You must use "
                    "<resource-name>:<prefix> as zrtPrefixes and not %s" % pStr)
            rName, prefix = pStr.split(':')
            zrtPrefixes[rName] = prefix

        # sleep and wait for less compiler after write the zrt-replace.less file
        sleepForCompileLessFallBack = 120
        sleepForCompileLess = self.options.get('sleepForCompileLess',
            sleepForCompileLessFallBack)
        try:
            sleepForCompileLess = int(sleepForCompileLess)
        except TypeError:
            sleepForCompileLess = sleepForCompileLessFallBack

        # create json data based configuration file
        data = {
            'registry': registry,
            'zcml': zcmlPath,
            'layers': layers,
            'skip': skip,
            'zrtPrefix': zrtPrefix,
            'zrtDirPrefix': zrtDirPrefix,
            'zrtPrefixes': zrtPrefixes,
            'sleepForCompileLess': sleepForCompileLess,
            'output': output,
        }
        cPath = os.path.join(location, 'cdn.json')
        # f = open(cPath, 'wb')
        # f.write(json.dumps(data, sort_keys=True, indent=4))
        # f.close()
        # with open(cPath, 'w', encoding='utf-8') as f:
        #     json.dump(data, f, sort_keys=True, indent=4)
        with io.open(cPath, 'w', encoding='utf-8') as f:
            if sys.version_info[0] < 3:
                data = ensure_unicode(data)
                json_str = json.dumps(data, **json_dump_kwargs)
                f.write(json_str)  # `json_str` ist Unicode
            else:
                json.dump(data, f, **json_dump_kwargs)
        dest.append(cPath)

        # do the relevant setup
        self.doSetup(dest, ws, extra_paths, initialization, cPath, output)
        return dest

    update = install


class CDNSetupRecipe(CDNRecipeBase):
    """Content delivery resource setup recipe (only for file based versioning).

    This recipe extracts the resource versions and stores them in a json file.
    The path to this file is given from the cdn resource manager and is called
    svnVersionSourcePath. This recipe also know how to write the zrt-replace
    directives used in css and js files and stores them in a file which can
    get included by other less files. The path to this file is given from the
    cdn resource manager and is called svnZRTReplacePath.

    Note: this recipe is only used once for all extraction and prepase the
    subversion and package based versioning. If you use hardcoded versions
    for all files together, you don't need to use this recipe because there
    is no need ot setup the version and the related zrt-replace.less file.
    """

    def doSetup(self, dest, ws, extra_paths, initialization, cPath, output):
        """Install scripts"""

        # generate setup script and return locations
        arguments = ['setup', '-c', cPath]
        dest.extend(zc.buildout.easy_install.scripts(
            [('cdn-setup', 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))


class CDNExtractRecipe(CDNRecipeBase):
    """Content delivery resource extractor recipe.

    This recipe installes scripts for extract resources from a project based
    on a ZCML configuration file which contains the cdn configuration or
    includes cdn configuration files. See the package p01.cdn for more
    information about cdn resources.

    You need to use this recipe for each cdn extraction e.g. dev, stage and
    production.

    """

    def doSetup(self, dest, ws, extra_paths, initialization, cPath, output):
        """Install scripts"""

        if self.name.startswith('-'):
            sName = self.name
        else:
            sName = '%s-' % self.name

        # generate extract script and return locations
        arguments = ['extract', '-c', cPath]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%sextract' % sName, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # generate uri listing script and return locations
        arguments = ['uris', '-c', cPath]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%suris' % sName, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # generate source path listing script and return locations
        arguments = ['paths', '-c', cPath]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%spaths' % sName, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # generate ouput path listing script and return locations
        arguments = ['output', '-c', cPath]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%soutput' % sName, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # get (optional) FTP config
        server = self.options.get('server', None)
        username = self.options.get('username', None)
        password = self.options.get('password', None)

        # currently we can't use the ftp server setup without an output.
        # TODO: implement explicit ftp server ``source`` argument where we can
        # find the extracted resources`. This is just an issue if you use
        # a custom ResourceManager and define a custom ResourceManager.output
        # concept
        if output is not None and server is not None:
            # generate deploy script and return locations
            # setup script arguments and generate extract script
            arguments = [output, server, username, password]
            dest.extend(zc.buildout.easy_install.scripts(
                [('%sdeploy' % sName, 'p01.recipe.cdn.deploy', 'main')],
                ws, self.buildout['buildout']['executable'],
                self.buildout['buildout']['bin-directory'],
                extra_paths = extra_paths,
                arguments = arguments,
                initialization = initialization,
                ))

## XXX: should we offer additional ftp deploy accounts?
##
##ftp
##  An additional list of ftp servers used for deploy the cdn resources. Each
##  line must provide a scriptname, username, password and ftp server url with
##  the following notation.
##
##  <name><username>:<password>@<ftp.domain.tld>
##
##  The domain must get used without the ftp:// protocol and the name
##  get used as a postfix for the deploy script e.g. <partsname>deploy-<name>
#
#        ftp = []
#        append = ftp.append
#        ftpStr = self.options.get('ftp')
#        if ftpStr is not None:
#            ftpLines = ftp.split('\n')
#            for line in ftpLines:
#                parts = line.strip().split('@')
#                if len(parts) != 3:
#                    raise ValueError("Not valid ftp value, must be " \
#                        "<scriptname><username>:<password>@<ftp.domain.tld>")
#                    username, password = parts[1].split(':')
#                    append(parts[0],username, password, domain)
#
#        for name, username, password, domain in ftp:
#            # generate deploy script and return locations
#            # setup script arguments and generate extract script
#            arguments = [output, domain, username, password]
#            dest.extend(zc.buildout.easy_install.scripts(
#                [('%sdeploy-%s' % (self.name, name),
#                  'p01.recipe.cdn.deploy', 'main')],
#                ws, self.buildout['buildout']['executable'],
#                self.buildout['buildout']['bin-directory'],
#                extra_paths = extra_paths,
#                arguments = arguments,
#                initialization = initialization,
#                ))

        return dest


# minify setup
def addMinifyLibrary(options, lib):
    """Inject the libary defined by it'sname"""
    # inject relevant minification library
    if lib == 'jsmin':
        options['eggs'] = options['eggs'] + '\n' + 'jsmin'
    elif lib == 'lpjsmin':
        options['eggs'] = options['eggs'] + '\n' + 'lpjsmin'
    elif lib == 'slimit':
        options['eggs'] = options['eggs'] + '\n' + 'slimit'
    elif lib == 'cssmin':
        options['eggs'] = options['eggs'] + '\n' + 'cssmin'
    else:
        raise zc.buildout.UserError('minify library "%s" is unknown' % lib)


class MinifyRecipe:
    """Minify recipe.

    This recipe installes scripts for minify resources.

    """

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.cdn'

        # get library name
        self.lib = self.options.get('lib', None)
        if self.lib is None:
            raise zc.buildout.UserError('No lib configuration defined.')

        # inject default minification library
        addMinifyLibrary(self.options, self.lib)

        self.libs = {}
        lines = self.options.get('libs', '').splitlines()
        for item in lines:
            if ' ' in item.strip():
                # load explicit defined minify libraries
                fName, lib = item.split()
                addMinifyLibrary(self.options, lib)
                # add filename, libarary tuple as libs option
                # self.libs.append((fName, lib))
                self.libs[fName] = lib

        # setup egg
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']

        # setup parts dir
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup additional egg path and working set
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        wd = options.get('working-directory', options['location'])

        # get header and header include file paths
        header = []
        header_includes = []
        _header = self.options.get('header', '')
        if ':${' in _header:
            raise zc.buildout.UserError(
                "You must prefix the $ in header with an additional $")
        for hStr in _header.splitlines():
            if hStr.startswith('['):
                hPath = getRealPath(ws, hStr)
                header_includes.append(hPath)
            else:
                header.append(hStr)
        # use header include before header option
        header_includes_first = self.options.get('header_includes_first', True)
        header_includes_first = getBoolean(header_includes_first, True)

        # get output path
        output = self.options.get('output', None)
        if output is None:
            raise zc.buildout.UserError('No output configuration defined.')
        # get real absolut output path
        output = getRealPath(ws, output)

        # get source files, order matters
        sources = []
        files = self.options.get('files', None)
        if files is None:
            raise zc.buildout.UserError('No input configuration defined.')

        for fPath in files.splitlines():
            # find real path
            fPath = getRealPath(ws, fPath)
            if fPath is None:
                # skip comments
                continue

            fName = os.path.basename(fPath)
            fPath = os.path.abspath(fPath)
            # check the given paths
            if not os.path.exists(fPath):
                raise zc.buildout.UserError(
                    'Given file path "%s" does not exist.' % fPath)
            sources.append({'filename': fName, 'path': fPath})

        # get skip file names
        skips = self.options.get('skip', None) or None
        if skips is None:
            skip = ''
        else:
            skip = [s.strip() for s in skips.splitlines()]

        # additional minify options replated to the relevant minify libs
        # slimit
        slimit_mangle = self.options.get('slimit_mangle', '')
        slimit_mangle_toplevel = self.options.get('slimit_mangle_toplevel', '')

        # cssmin
        cssmin_wrap = self.options.get('cssmin_wrap', '')

        # create json data based configuration file
        data = {
            'header': header,
            'header_includes': header_includes,
            'header_includes_first': header_includes_first,
            'sources': sources,
            'skip': skip,
            'lib': self.lib,
            'libs': self.libs,
            'slimit_mangle': slimit_mangle,
            'slimit_mangle_toplevel': slimit_mangle_toplevel,
            'cssmin_wrap': cssmin_wrap,
            'output': output,
        }
        cPath = os.path.join(location, 'minify.json')
        # f = open(cPath, 'wb')
        # f.write(json.dumps(data, sort_keys=True, indent=4))
        # f.close()
        # with open(cPath, 'w', encoding='utf-8') as f:
        #     json.dump(data, f, sort_keys=True, indent=4)
        cPath = os.path.join(location, 'minify.json')
        with io.open(cPath, 'w', encoding='utf-8') as f:
            if sys.version_info[0] < 3:
                data = ensure_unicode(data)
                json_str = json.dumps(data, **json_dump_kwargs)
                f.write(json_str)  # `json_str` ist Unicode
            else:
                json.dump(data, f, **json_dump_kwargs)

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # generate minify script and return script location
        # arguments = [self.lib, header, output, fPaths, self.libs, skip,
        #             # slimit options
        #             slimit_mangle, slimit_mangle_toplevel,
        #             # cssmin options
        #             cssmin_wrap,
        #             ]
        arguments = ['-c', cPath]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.cdn.minify', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        return dest

    update = install


# glue setup
class GlueRecipe:
    """CSS and sprite generation recipe based on glue python package

    See: http://pypi.python.org/pypi/glue

    """

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.cdn'

        # optional inject Pillow (PIL fork)
        # NOTE: non of the PIL libraries does work with buildout or easy_install
        # because of a bad top level path setup. Pillow is a PIL fork which
        # installs PIL. But since glue defines PIL as a dependency we will
        # provide a copy of glue.py and skip the PIL install_requires defined
        # in glue/setup.py
        pil = self.options.get('pil')
        if pil == 'pillow':
            # use Pillow
            self.options['eggs'] = self.options['eggs'] + '\n' + 'Pillow'
        elif pil not in ['skip', 'no', 'false', 'False', '0']:
            # skip PIL and Pillow at all, your eggs must define PIL or a PIL
            # replacement egg. We support the following imports
            self.options['eggs'] = self.options['eggs'] + '\n' + 'PIL'

        # setup egg
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']

        # setup parts dir
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup additional egg path and working set
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        wd = options.get('working-directory', options['location'])

        # source
        source = self.options.get('source', None)
        if source is None:
            raise zc.buildout.UserError('No source configuration defined.')
        source = getRealPath(ws, source)

        # css
        css = self.options.get('css', None)
        if css is None:
            raise zc.buildout.UserError('No css configuration defined.')
        css = getRealPath(ws, css)

        # img
        img = self.options.get('img', None)
        if img is None:
            raise zc.buildout.UserError('No img configuration defined.')
        img = getRealPath(ws, img)

        # url
        url = self.options.get('url', None)
        if url is None:
            url = ''

        # project
        project = self.options.get('project', None)
        if project is None:
            project = 'false'
        else:
            project = 'true'

        # less
        less = self.options.get('less', None)
        if less is None:
            less = 'false'
        else:
            less = 'true'

        # html
        html = self.options.get('html', None)
        if html is None:
            html = 'false'
        else:
            html = 'true'

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # generate minify script and return script location
        arguments = [source, css, img, url, project, less, html]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.cdn.sprites', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        return dest

    update = install
