##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re
import unittest
import doctest

import zc.buildout.testing
from zope.testing import renormalizing



def test_start_error():
    """The start script will setup a egg based start hook for a Zope 3 setup.
    Let's create a buildout that installs it as an ordinary script:

    >>> write('buildout.cfg',
    ... '''
    ... [cdn]
    ... recipe = p01.recipe.cdn:cdn
    ... ''')

    >>> print(system(join('bin', 'buildout')))

    """


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('p01.recipe.cdn', test)
    zc.buildout.testing.install_develop('jsmin', test)
    zc.buildout.testing.install_develop('lpjsmin', test)
    zc.buildout.testing.install_develop('slimit', test)
    zc.buildout.testing.install_develop('cssmin', test)
    zc.buildout.testing.install_develop('argparse', test)
    zc.buildout.testing.install_develop('ply', test)
    zc.buildout.testing.install_develop('Pillow', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('zc.buildout', test)


# checker = renormalizing.RENormalizing([
#     zc.buildout.testing.normalize_path,
#     # note sure if misspelled?) has \n at the end on linux?
#     (re.compile("Couldn't find index page for '[a-zA-Z0-9.]+' "
#      "\(maybe misspelled\?\)\n"), ''),
#     # windows doesn't have \n at the end of misspelled?)
#     (re.compile("Couldn't find index page for '[a-zA-Z0-9.]+' "
#      "\(maybe misspelled\?\)"), ''),
#     (re.compile("""['"][^\n"']+p01.recipe.cdn[^\n"']*['"],"""),
#      "'/p01.recipe.cdn',"),
#     (re.compile('#![^\n]+\n'), ''),
#     (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'), '-pyN.N.egg'),
#     (re.compile('[a-zA-Z0-9:\\\]+site-packages'), '/sample-pyN.N.egg'),
#     # the following are for compatibility with Windows
#     (re.compile('-  .*\.exe\n'), ''),
#     (re.compile('RuntimeWarning[a-zA-Z0-9:.,_ ]*'), ''),
#     (re.compile('-script.py'), ''),
#     # update buildout version
#     (re.compile('restarting.'), ''),
#     (re.compile('Upgraded:'), ''),
#     (re.compile('zc.buildout version 1.4.3;'), ''),
#     (re.compile('Not found:[a-zA-Z0-9_:/\\\. ]*'), ''),
#     (re.compile("Generated script '/sample-buildout/bin/buildout'."), ''),
#     ])
checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(r"Couldn't find index page for '[\w.]+' \(maybe misspelled\?\)\n?"), ''),
    (re.compile(r"""['"][^\n"']+p01\.recipe\.cdn[^\n"']*['"],"""), "'/p01.recipe.cdn',"),
    (re.compile(r'#![^\n]+\n'), ''),
    (re.compile(r'-\S+-py\d\.\d(-\S+)?\.egg'), '-pyN.N.egg'),
    (re.compile(r'[/\\\w:.]+site-packages'), '/sample-pyN.N.egg'),
    (re.compile(r'-  .*\.exe\n'), ''),
    (re.compile(r'RuntimeWarning[:\w\d., _\-\'"\\/\(\)]+'), ''),
    (re.compile(r'-script\.py'), ''),
    (re.compile(r'restarting\.'), ''),
    (re.compile(r'Upgraded:'), ''),
    (re.compile(r'zc\.buildout version [\d.]+;'), ''),
    (re.compile(r'Not found:[\w_:/\\\. ]*'), ''),
    (re.compile(r"Generated script '.*?/bin/buildout'."), ''),
    # optional: unicode prefix remover
    (re.compile(r"u'(.*?)'"), r"'\1'"),
    (re.compile(r'u"(.*?)"'), r'"\1"'),
])


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt'),
        doctest.DocFileSuite('../cdn.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('../minify.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('../sprites.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
