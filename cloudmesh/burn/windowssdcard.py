from cloudmesh.burn.util import os_is_windows

import string
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import writefile as common_writefile
from cloudmesh.common.util import readfile as common_readfile
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import path_expand
import os
import ascii
import sys
import string
import subprocess

# we need to deal with that imports of windos libraries are conditional

if os_is_windows():
    from ctypes import windll
    import win32api
    import win32wnet
    import win32netcon


# see mountvol
# see diskpart

# https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-vista/cc766465(v=ws.10)?redirectedfrom=MSDN



class USB:
    @staticmethod
    def info():
        print("Prints the table of information about devices on the  usb info")


'''
    diskpart commands - 
    https://www.windowscentral.com/how-mount-drive-windows-10#:~:text=Unmount%20drive%20with%20DiskPart&text=using%20these%20steps%3A-,Open%20Start.,Run%20as%20administrator**%20option.&text=Confirm%20the%20volume%20you%20want%20to%20unmount.&text=volume%20VOLUME%2DNUMBER-,In%20the%20command%2C%20replace%20VOLUME%2DNUMBER%20with%20the%20number%20of,volume)%20you%20want%20to%20mount.
    https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-xp/bb490893(v=technet.10)?redirectedfrom=MSDN
'''


class WindowsSDCard:

    # device will be likely of form Z:/path we need to use Path from new python 3

    # see https://superuser.com/questions/704870/mount-and-dismount-hard-drive-through-a-script-software#:~:text=Tutorial,open%20Command%20Prompt%20as%20Administrator.&text=To%20mount%20a%20drive%2C%20type,you%20noted%20in%20Step%202.

    def __init__(self, drive=None):
        self.drive = drive

    def readfile(self, filename=None):
        content = common_readfile(filename, mode='rb')
        # this may need to be changed to just "r"
        return content

    def writefile(self, filename=None, content=None):
        with open(path_expand(filename), 'w') as outfile:
            outfile.write(content)
            outfile.truncate() # may not be needed, but is better
            os.fsync(outfile)

    def get_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1

        return drives

    def find_free_drive_letter(self):
        """
        returns the first free driveletter
        :return: returns a free drive letter
        :rtype:
        """
        drives = self.get_drives()
        for drive in ascii.charlist()[10:]:
            if drive not in drives:
                return drive
        return ValueError("no free drive found")

    def unmount(self, drive=None):
        """
        unmounts the drive

        :param drive:
        :type drive:
        :return:
        :rtype:
        """
        os.system(f"mountvol {drive} /p")

    def mount(self, drive=None):
        """
        mounts the drive

        :param drive:
        :type drive:
        :return:
        :rtype:
        """
        # this will use mountvol
        raise NotImplementedError

    def format_drive(self, drive=None, unmount=True):
        """
        formats the drive
        :param drive: is a drive latte in Windows
        :type drive: str
        :return:
        :rtype:
        """
        # see https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/format
        if unmount:
            set_unmount = "/x"
        else:
            set_unmount = ""
        command = f"format {drive} /fs:FAT32 /v:UNTITLED /q {set_unmount}".strip()
        Console.info(command)
        # os.system(command)  ## this must be checked to prevent disaster
        raise NotImplementedError

    def info(self):

        """
        Prints information about the USB and sdcard if it is available

        :return:
        :rtype:
        """
        Console.info("Disk info")
        common_writefile(SdCard.tmp, "list volume")
        b = Shell.run(f"diskpart /s {SdCard.tmp}").splitlines()[8:]
        Windows.clean()
        return b

        # command = f"mountvol {self.drive} /L"
        # r = Shell.run(command)
        # print (r)
        # see also gregos implementation for mac, osx, and raspberry,
        # that just may work

        # diskpart list disk
        # diskpart detail disk
        # diskpart detail volume

        # diskpart /s <script_file>

        #os.system("diskpart list disk")

        # Path pathlib
        # filename = Path("/tmp/list-disk.txt")

        # common_writefile(filename, "list disk\n\exit")
        # os.system(f"diskpart /s {filename}")

    @staticmethod
    def guess_drive():
        return None
        raise NotImplementedError

    @staticmethod
    def clean():
        raise NotImplementedError
        # rm SDCard.tmp

    # @staticmethod
    # def list_file_systems():

"""
class WindowsSDCard:
    
    tmp = "tmp.txt"

    @staticmethod
    def clean():
        raise NotImplementedError
        # rm SDCard.tmp

    # Take a look at Gregor's SDCard init method
    @staticmethod
    def format_card(volume_number, disk_number):

        '''
        # see https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/format
        if unmount:
            set_unmount = "/x"
        else:
            set_unmount = ""
        command = f"format {device} /fs:FAT32 /v:UNTITLED /q {set_unmount}".strip()
        print(command)
        '''

        print(f"format :{volume_number}")

        common_writefile(SdCard.tmp, f"select disk {disk_number} \n exit")
        
        a = Shell.run(f"diskpart /s {SdCard.tmp}")

        print(a)

        common_writefile(SdCard.tmp, f"select volume {volume_number}")
        a = Shell.run(f"diskpart /s {SdCard.tmp}")
        print(SdCard.tmp)
        print(a)

        common_writefile(SdCard.tmp, "format fs=fat32 quick")
        print(SdCard.tmp)
        a = Shell.run(f"diskpart /s {SdCard.tmp}")

    @staticmethod
    def mount(volume_number, volume_letter=None):
        if volume_letter == None:
            volume_letter = SdCard.get_free_drive()
        common_writefile(SdCard.tmp, f"select volume {volume_number}")
        a = Shell.run(f"diskpart /s {SdCard.tmp}")

        common_writefile(SdCard.tmp, f"assign letter={volume_letter}")
        a = Shell.run(f"diskpart /s {SdCard.tmp}")
        return volume_letter

    @staticmethod
    def unmount(volume_letter):
        common_writefile(SdCard.tmp, f"remove letter={volume_letter}")
        b = Shell.run(f"diskpart /s {SdCard.tmp}").splitlines()[8:]

        # os.system(f"mountvol {device} /p")

        print(b)

    @staticmethod
    def write(volume_number, volume_letter):
        pass

    @staticmethod
    def info():
        print("Disk info")
        common_writefile(SdCard.tmp, "list volume")
        b = Shell.run(f"diskpart /s {SdCard.tmp}").splitlines()[8:]
        return b

    @staticmethod
    def get_free_drive():
        drives = set(string.ascii_uppercase[2:])
        for d in win32api.GetLogicalDriveStrings().split(':\\\x00'):
            drives.discard(d)
        # Discard persistent network drives, even if not connected.
        henum = win32wnet.WNetOpenEnum(win32netcon.RESOURCE_REMEMBERED,
                                       win32netcon.RESOURCETYPE_DISK, 0, None)
        while True:
            result = win32wnet.WNetEnumResource(henum)
            if not result:
                break
            for r in result:
                if len(r.lpLocalName) == 2 and r.lpLocalName[1] == ':':
                    drives.discard(r.lpLocalName[0])
        if drives:
            return sorted(drives)[-1] + ':'

    @staticmethod
    def guess_volume_number():
        r = SdCard.info()
        print(r)
        for line in r:
            line = line.strip()
            if "*" not in line:
                line = line.replace("No Media", "NoMedia")
                line = line.replace("Disk ", "")
                line = ' '.join(line.split())
                num, kind, size, unit, unused1, unused2 = line.split(" ")
                size = int(size)

                if unit == "GB" and (size > 7 and size < 128):
                    return num
        raise ValueError("No SD card found")


SdCard.format_card(5, 3)
"""


'''
DO NOT DELETE THIS COMMENT - WORKING CODE HERE. 

r = SdCard.info()
print(r)
volume_number = SdCard.guess_volume_number()

if not yn_choice (f"Would you like to contine burning on disk {volume_number}"):
    sys.exit(0)

volume_letter = SdCard.mount(volume_number)

from glob import glob

files = glob(f"{volume_letter}:")

print(files)

SdCard.unmount(volume_letter)
'''




# TASK 1 explre sdcard that has raspberry os on it.
'''
1. plug in card with raspberry os burned on it
2. see hw the card registers
3. prg : cms burn info
4. prg : w = Windows()
         r = w.info()
         print(r)
5. find the drive letter
6. prg: drive = device = "Z:"
7: prg: ... mount the drive
8: prg: look if you can find the boot partition on the drive
10: prg: can you list and write things in the boot partition?
11: prg: unmount the drive

12: First task won

TASK 2: do the same as task 1 but with ubuntu on it


TASK 3: FORMAT SD CARD form commandline

9: prg: format the sdcard
'''