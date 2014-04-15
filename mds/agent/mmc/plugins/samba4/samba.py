# -*- coding: utf-8; -*-g
#
# (c) 2014 Zentyal S.L., http://www.zentyal.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import sys
from mmc.plugins.samba4.smb_conf import SambaConf
from mmc.support.mmctools import shlaunch


logger = logging.getLogger()

try:
    samba4_site_packages = os.path.join(SambaConf.PREFIX,
                                        'lib64/python2.7/site-packages')
    sys.path.insert(0, samba4_site_packages)

    from samba.samdb import SamDB
    from samba.param import LoadParm
    from samba.auth import system_session

except ImportError:
    logger.error("Python module ldb.so not found...\n"
                 "Samba4 package must be installed\n")
    raise


class SambaToolException(Exception):
    pass


class SambaAD:
    """
    Handle sam.ldb: users and computers
    """
    def __init__(self):
        smb_conf = SambaConf()
        self.sam_ldb_path = os.path.join(smb_conf.PRIVATE_DIR, 'sam.ldb')
        self.ldb = SamDB(url=self.sam_ldb_path, session_info=system_session(),
                         lp=LoadParm())

    def isUserEnabled(self, username):
        return True  # FIXME use self.ldb to search user

    def existsUser(self, username):
        return username in self._samba_tool("user list")

    def updateUserPassword(self, username, password):
        self._samba_tool("user setpassword %s --newpassword='%s'" %
                         (username, password))

    def createUser(self, username, password):
        self._samba_tool("user create %s '%s'" % (username, password))

    def enableUser(self, username):
        self._samba_tool("user enable %s" % username)

    def disableUser(self, username):
        self._samba_tool("user disable %s" % username)

    def deleteUser(self, username):
        self._samba_tool("user delete %s" % username)

    def _samba_tool(self, cmd):
        exit_code, std_out, std_err = shlaunch(cmd)
        if exit_code != 0:
            error_msg = "Error processing `%s`:\n" % cmd
            if std_err:
                error_msg += "\n".join(std_err)
            if std_out:
                error_msg += "\n".join(std_out)
            raise SambaToolException(error_msg)
        return std_out