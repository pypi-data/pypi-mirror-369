======
README
======

This buildout recipe package offers 3 different concepts. This 3 concept allows
you to reduce the resources size and offload the resources from your
application server. The nice thing is, that you can start your application with
different configurations if you like to server the minified and static or the
local non monified resource versions. The p01.cdn package also offers a version
manager which allows to use different resource versioning concepts.

Since version 1.0.0 this package is offering versiong per file and doesn't
require to use one version for all resources. The optinal p01.recipe.cdn:setup
recipe creates a script which is able to generate a version map and the related
zrt-replace directives and stores them in a json data map and a less file
which can get included in your related less files.


sprites
-------

The first concept allows to generate sprite images and the relevant css styles
pointing to the right sprite background position. This recipe uses the
spritemapper python package


minify
------

The second concept allows to minify javascript or CSS files. The recipe supports
the following python minify libraries.

  jsmin: http://pypi.python.org/pypi/jsmin
  lpjsmin: http://pypi.python.org/pypi/lpjsmin
  slimit: http://pypi.python.org/pypi/slimit
  cssmin: http://pypi.python.org/pypi/cssmin


content delivery network
------------------------

The third concept allows to extract CDN (content delivery network) resources
based on p01.cdn into a folder structure.
