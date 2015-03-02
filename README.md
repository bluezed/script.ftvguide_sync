FTV Guide Sync
==============

This Service will try to sync your FTV Guide database and settings with a WebDAV-compatible server that you can specify in the Service-Settings. This should allow you to have the same channels and settings across multiple devices.

**PLEASE NOTE:** This Service is still very much EXPERIMENTAL and there is still a risk that data might get lost!

For official support go to the forums on [tvaddons.ag](http://forums.tvaddons.ag/threads/22837-RELEASE-FTV-Guide)

Download the package from [HERE](https://github.com/bluezed/script.ftvguide_sync/releases/download/0.1.2/script.ftvguide_sync.zip)


Here are the basic steps to install the FTV Guide Sync service onto your Kodi box.

# Prerequisites
* XBMC 14 (Helix) or higher
* The downloaded Zip-file
* Place the file somewhere you can get to easily on your XBMC box

# Installation and configuration
1. Go to System -> Addons and select "Install from Zip-file"                                          
 ![](http://s19.postimg.org/hqhlmyf6r/step01.png)

2. Select the Zip file you downloaded earlier. This should install the FTV Guide Sync service on your box.

3. Now go to "Enabled Add-ons"                                                                     
 ![](http://s19.postimg.org/4cflbfvj7/sync_step1.png)

4. Select the "Services"                                                                     
 ![](http://s19.postimg.org/hfb7uplr7/sync_step2.png)

5. Go to entry for "FTV Guide Sync"                                                                              
![](http://s19.postimg.org/mo1neuesj/sync_step3.png)

6. Click on it and select "Configure"                                                                        
 ![](http://s19.postimg.org/ro3p0j9sz/sync_step4.png)

7. Enable the service, set the update interval and add your server details.                                    
 ![](http://s19.postimg.org/q1ehfaxr7/sync_step5.png)

 **Note:** After setting the service to enabled you have to restart Kodi for it to take effect!
Setting the service to disabled does not require a restart though.

8. After the service has started running you should see the "source.db" and "settings.xml" appearing on your server
 ![](http://s19.postimg.org/wdtmp50tf/sync_step6.png)

#Resources
This package bundles the [easywebdav](https://github.com/amnong/easywebdav) library.

