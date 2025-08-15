###############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import sys
import logging
import subprocess
from xml.etree import ElementTree

logger = logging.getLogger()


def do(cmd, cwd=None, captureOutput=True, skipError=False):
    logger.debug('Command: ' + cmd)
    if captureOutput:
        stdout = stderr = subprocess.PIPE
    else:
        stdout = stderr = None
    p = subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr,
        shell=True, cwd=cwd)
    stdout, stderr = p.communicate()
    if stdout is None:
        stdout = "See output above"
    if stderr is None:
        stderr = "See output above"
    if p.returncode != 0 and not skipError:
        logger.error(u'An error occurred while running command: %s' %cmd)
        logger.error('Error Output: \n%s' % stderr)
        sys.exit(p.returncode)
    logger.debug('Output: \n%s' % stdout)
    return stdout


class SVN(object):
    """Subversion command wrappper"""

    username = None
    password = None
    forceAuth = False
    active = True

    def __init__(self, username=None, password=None, forceAuth=False):
        self.username = username
        self.password = password
        self.forceAuth = forceAuth

    def _addAuth(self, command):
        auth = ''
        if self.username:
            auth = '--usernamename %s --password %s' % (self.username,
                self.password)
            if self.forceAuth:
                auth += ' --no-auth-cache'
        command = command.replace('##__auth__##', auth)
        return command

    def info(self, url, skipError=False):
        command = 'svn info --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command, skipError=skipError)

    def getRevision(self, resource):
        xml = self.info(resource.path, skipError=True)
        try:
            elem = ElementTree.fromstring(xml)
            revision = elem.find("entry").find("commit").get("revision")
            if not revision:
                return 0
            else:
                return int(revision)
        except (AttributeError, ElementTree.ParseError):
            # Ok, this resource is not part of the svn repository
            if not resource.pkgVersion:
                # new non versioned file
                return 0
            else:
                # fallback to package version for egg packages
                return resource.pkgVersion
