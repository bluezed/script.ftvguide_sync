#
#   FTV Guide Sync
#   Copyright (C) 2015 Thomas Geppert
#   [bluezed] - bluezed.apps@gmail.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import xbmc
import xbmcaddon
import xbmcgui
import os
import datetime

from resources.lib import easywebdav

ADDON = xbmcaddon.Addon(id='script.ftvguide_sync')
  
    
class SyncException(Exception):
    def __init__(self, e):
        msg = str(e)
        xbmcgui.Dialog().ok('FTV Guide Sync', 'Error trying to connect to the WebDav-Server!\n\n{0}'.format(msg))
        super(SyncException, self).__init__(msg)

        
class Sync():

    webdav = None
    localFolder = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ftvguide'))
    db = 'source.db'
    settings = 'settings.xml'
    lastMod = 0

    protocol = ADDON.getSetting('webdav.protocol')
    url = ADDON.getSetting('webdav.url')
    user = ADDON.getSetting('webdav.user')
    password = ADDON.getSetting('webdav.password')
    remoteFolder = ADDON.getSetting('webdav.folder')

    NO_CHANGE = 0
    REMOTE_NEWER = 1
    LOCAL_NEWER = 2

    def __init__(self):
        xbmc.log('[script.ftvguide_sync] Started...', level=xbmc.LOGNOTICE)
        xbmcgui.Dialog().notification('FTV Guide Sync', 'Started...')
        try:
            self.webdav = easywebdav.connect(self.url,
                                        username=self.user,
                                        password=self.password,
                                        protocol=self.protocol)

            if not self.webdav.exists(self.remoteFolder):
                self.webdav.mkdir(self.remoteFolder)
                xbmc.log('[script.ftvguide_sync] Folder created', level=xbmc.LOGNOTICE)
            else:
                xbmc.log('[script.ftvguide_sync] Folder exists', level=xbmc.LOGNOTICE)

            self.doSync()
        except Exception as e:
            raise SyncException(e)

    def doSync(self):
        xbmc.log('[script.ftvguide_sync] Sync called', level=xbmc.LOGNOTICE)
        try:
            ret = self.checkFile(self.settings)
            if ret == self.LOCAL_NEWER:
                self.uploadFile(self.settings)
            elif ret == self.REMOTE_NEWER:
                self.downloadFile(self.settings)

            ret = self.checkFile(self.db)
            if ret == self.LOCAL_NEWER:
                self.uploadFile(self.db)
            elif ret == self.REMOTE_NEWER:
                self.downloadFile(self.db)
        except Exception as e:
            raise SyncException(e)

    def checkFile(self, fName):
        ret = self.NO_CHANGE
        fPath = os.path.join(self.localFolder, fName)
        localMod = datetime.datetime.utcfromtimestamp(os.path.getmtime(fPath))
        xbmc.log('[script.ftvguide_sync] Local file "'+fName+'":  ' + str(localMod), level=xbmc.LOGNOTICE)
        remoteMod = self.getRemoteMod(fName)
        xbmc.log('[script.ftvguide_sync] Remote file "'+fName+'": ' + str(remoteMod), level=xbmc.LOGNOTICE)
        if remoteMod is None or localMod > remoteMod:
            ret = self.LOCAL_NEWER
            xbmc.log('[script.ftvguide_sync] Local file "'+fName+'" is newer', level=xbmc.LOGDEBUG)
        elif localMod < remoteMod:
            ret = self.REMOTE_NEWER
            xbmc.log('[script.ftvguide_sync] Remote file "'+fName+'" is newer', level=xbmc.LOGDEBUG)
        else:
            xbmc.log('[script.ftvguide_sync] Files "'+fName+'" appear the same', level=xbmc.LOGDEBUG)
        return ret

    def getRemoteMod(self, fName):
        mTime = None
        remFile = self.remoteFolder + '/' + fName
        try:
            # returned data looks like this:
            # [ File(name='/FTVGuideSync', size=0, mtime='Sat, 28 Feb 2015 11:23:22 GMT', ctime='2015-02-28T11:23:22Z', contenttype='httpd/unix-directory'),
            #   File(name='/FTVGuideSync/source.db', size=5121024, mtime='Sat, 28 Feb 2015 11:29:30 GMT', ctime='2015-02-28T11:23:23Z', contenttype='application/octetstream') ]
            for fItem in self.webdav.ls(self.remoteFolder):
                if fItem.contenttype != 'httpd/unix-directory' and fItem.name == remFile:
                    # 'Sat, 28 Feb 2015 11:29:30 GMT'
                    mTime = datetime.datetime.strptime(fItem.mtime, '%a, %d %b %Y %H:%M:%S %Z')
                    break
        except Exception as e:
            raise SyncException(e)
        return mTime

    def uploadFile(self, fName):
        localPath = os.path.join(self.localFolder, fName)
        remotePath = self.remoteFolder + '/' + fName
        try:
            self.webdav.upload(localPath, remotePath)
            self.updateModTime(fName)
            xbmc.log('[script.ftvguide_sync] File "'+fName+'" uploaded', level=xbmc.LOGNOTICE)
        except Exception as e:
            raise SyncException(e)

    def downloadFile(self, fName):
        localPath = os.path.join(self.localFolder, fName)
        remotePath = self.remoteFolder + '/' + fName
        try:
            self.webdav.download(remotePath, localPath)
            self.updateModTime(fName)
            xbmc.log('[script.ftvguide_sync] File "'+fName+'" downloaded', level=xbmc.LOGNOTICE)
        except Exception as e:
            raise SyncException(e)

    def updateModTime(self, fName):
        localPath = os.path.join(self.localFolder, fName)
        remoteMod = self.getRemoteMod(fName)
        td = remoteMod - datetime.datetime(1970,1,1)
        # need to do it this way cause Android doesn't support .total_seconds() :(
        self.lastMod = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6

        os.utime(localPath, (self.lastMod, self.lastMod))
        xbmc.log('[script.ftvguide_sync] Local file "'+fName+'" mod-time set to: ' + str(remoteMod), level=xbmc.LOGDEBUG)


if __name__ == '__main__':
    if ADDON.getSetting('service.enabled') == 'true':
        sync = Sync()
        monitor = xbmc.Monitor()
        while True:
            # Sleep/wait for abort for the interval
            interval = int(ADDON.getSetting('service.interval')) * 60
            if monitor.waitForAbort(interval):
                # Abort was requested while waiting. We should exit
                break
            if ADDON.getSetting('service.enabled') == 'true':
                sync.doSync()
            else:
                xbmc.log('[script.ftvguide_sync] Has been stopped, exiting', level=xbmc.LOGNOTICE)
                break
    else:
        xbmc.log('[script.ftvguide_sync] Not enabled, exiting', level=xbmc.LOGNOTICE)