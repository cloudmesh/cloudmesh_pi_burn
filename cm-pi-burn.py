#!/usr/bin/env python3

"""\
Cloudmesh Raspberry Pi Image Burner.
Usage:
  cm-pi-burn create [--image=IMAGE] [--device=DEVICE]
                    [--hostname=HOSTNAME] [--ipaddr=IP] [--sshkey=KEY]
  cm-pi-burn burn [IMAGE] [DEVICE]
  cm-pi-burn mount [DEVICE] [MOUNTPOINT]
  cm-pi-burn set-hostname [HOSTNAME] [MOUNTPOINT]
  cm-pi-burn set-ip [IP] [MOUNTPOINT]
  cm-pi-burn set-key [KEY] [MOUNTPOINT]
  cm-pi-burn enable-ssh [MOUNTPOINT]
  cm-pi-burn unmount [DEVICE]
  cm-pi-burn image-get-latest # TODO
  cm-pi-burn image-ls # TODO
  cm-pi-burn image-delete [IMAGE] # TODO
  cm-pi-burn (-h | --help)
  cm-pi-burn --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --image=IMAGE       The image filename, e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE     The device, e.g. /dev/mmcblk0
  --hostname=HOSTNAME The hostname
  --ipaddr=IP         The IP address
  --key=KEY           The name of the SSH key file [default: id_rsa]

Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
    Location where the images will be stored for reuse

Description:
  cm-pi-burn

Example:
  cm-pi-burn create --image=2019-09-26-raspbian-buster.img --device=/dev/mmcblk0
                    --hostname=red1 --ipaddr=192.168.1.1 --key=id_rsa
  cm-pi-burn create-many --image=2019-09-26-raspbian-buster.img --device=/dev/mmcblk0
                         --hostname=red --ipaddr=192.168.1. --key=id_rsa
                         --hostnamerange=5-7 --ipaddrrange=5-7
"""

import os
import wget
import hostlist
from docopt import docopt
from pprint import pprint
import requests
from pathlib import Path
import sys

debug = True

# noinspection PyPep8Naming
def WARNING(*args, **kwargs):
    print("WARNING:", *args, file=sys.stderr, **kwargs)

class Image(object): # TODO
    def __init__(self, name):
        self.directory = '~/.cloudmesh/images'
        os.system('mkdir -p ' + self.directory)

        if name == "latest":
            self.image_name = 'raspbian-buster-lite.img'
            self.url = 'https://downloads.raspberrypi.org/raspbian_lite_latest'
        else:
            self.image_name = name
            self.url = 'https://downloads.raspberrypi.org/' + self.image_name.replace('.img', '')


    def fetch(self):
        # if image is already there skip
        # else downlod from url using python requests
        # see cmburn.py you can copy form there
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if os.path.isfile(Path(self.directory / self.image_name)):
            return
        source = requests.head(self.url, allow_redirects=True).url
        size = requests.get(self.url, stream=True).headers['Content-length']
        destination = os.path.basename(source)
        if debug:
            print(self.url)
            print(destination)
        download = True
        if os.path.exists(destination):
            if int(os.path.getsize(destination)) == int(size):
                WARNING("file already downloaded. Found at:", Path(self.directory / destination))
                download = False
        if download:
            wget.download(self.url)

        # uncompressing
        image_name = destination.replace(".zip", "") + ".img"
        image_file = Path(self.directory / image_name)
        if not os.path.exists(image_file):
            self.unzip_image(image_name)
        else:
            WARNING("file already downloaded. Found at:", Path(self.directory / image_name))
        self.image = Path(self.directory / image_name)
        return self.image

    def unzip_image(self, source):
        tmp = Path(self.directory) / "."
        os.chdir(tmp)
        image_zip = str(Path(self.directory / source)).replace(".img", ".zip")
        print("unzip image", image_zip)
        # BUG zipfile not defined
        zipfile.ZipFile(image_zip).extractall()

    def verify(self):
        # verify if the image is ok, use SHA
        raise NotImplementedError

    def rm(self):
        # remove the downloaded image
        Path(self.directory / self.image_name).unlink()

    def ls(self):
        #Path(self.directory)
        raise NotImplementedError

class Burner(object):

    @staticmethod
    def burn(image, device):
        """
        burns the SD Card
        :param image: name of the image
        """
        os.system('sudo cat ' + image + ' >' + device)

    @staticmethod
    def set_hostname(hostname, mountpoint):
        """
        sets the hostname on the sd card
        :param hostname:
        """
        # write the new hostname to /etc/hostname
        with open(mountpoint + '/etc/hostname', 'w') as f:
            f.write(hostname + '\n')

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        with open(mountpoint + '/etc/hosts', 'r') as f: # read /etc/hosts
            lines = [l for l in f.readlines()][:-1] # ignore the last line
            newlastline = '127.0.1.1 ' + hostname + '\n'

        with open(mountpoint + '/etc/hosts', 'w') as f: # and write the modified version
            for line in lines:
                f.write(line)
            f.write(newlastline)

    @staticmethod
    def set_static_ip(ip, mountpoint):
        """
        Sets the static ip on the sd card
        :param ip:
        """
        with open(mountpoint + '/etc/hosts') as f:
            lines = [l for l in f.readlines()]
        with open(mountpoint + '/etc/hosts', 'w') as f:
            for line in lines:
                f.write(line)
            f.write('interface eth0\n')
            f.write('static ip_address=' + ip + '/24')

    @staticmethod
    def set_key(name, mountpoint):
        """
        copies the public key into the .ssh/authorized_keys file on the sd card
        """
        # name should be something like 'id_rsa'
        os.system('cp ~/.ssh/' + name + '.pub ' + mountpoint + '/home/pi/.ssh/authorized_keys')

    @staticmethod
    def mount(device, mountpoint):
        """
        mounts the current SD card
        """
        os.system('sudo rmdir ' + mountpoint)
        os.system('sudo mkdir ' + mountpoint)
        os.system('sudo mount ' + device + 'p2 ' + mountpoint)
        os.system('sudo mount ' + device + 'p1 ' + mountpoint + '/boot')

    @staticmethod
    def unmount(device):
        """
        unmounts the current SD card
        """
        os.system('sudo umount ' + device + 'p1')
        try:
            os.system('sudo umount ' + device + 'p1')
        except:
            pass
        os.system('sudo umount ' + device + 'p2')

    @staticmethod
    def enable_ssh(mountpoint):
        """
        Enables ssh on next boot of sd card
        """
        # touch /media/pi/boot/ssh
        os.system('sudo touch ' + mountpoint + '/boot/ssh')


def analyse(arguments):
    if arguments['burn']:
        image = arguments['IMAGE']
        device = arguments['DEVICE']
        Burner.burn(image, device)
    elif arguments['mount']:
        device = arguments['DEVICE']
        mp = arguments['MOUNTPOINT']
        Burner.mount(device, mp)
    elif arguments['set-hostname']:
        hostname = arguments['HOSTNAME']
        mp = arguments['MOUNTPOINT']
        Burner.set_hostname(hostname, mp)
    elif arguments['set-ip']:
        ip = arguments['IP']
        mp = arguments['MOUNTPOINT']
        Burner.set_static_ip(ip, mp)
    elif arguments['set-key']:
        key = arguments['KEY']
        mp = arguments['MOUNTPOINT']
        Burner.set_key(key, mp)
    elif arguments['enable-ssh']:
        mp = arguments['MOUNTPOINT']
        Burner.enable_ssh(mp)
    elif arguments['unmount']:
        device = arguments['DEVICE']
        Burner.unmount(device)
    elif arguments['create']:
        image = arguments['--image']
        device = arguments['--device']
        hostnames = hostlist.expand_hostlist(arguments['--hostname'])
        ips = hostlist.expand_hostlist(arguments['--ipaddr'])
        key = arguments['--sshkey']
        mp = '/mount/pi'

        for hostname, ip in zip(hostnames, ips):
            Burner.burn(image, device)
            Burner.mount(device, mp)
            Burner.enable_ssh(mp)
            Burner.set_hostname(hostname, mp)
            Burner.set_key(key, mp)
            Burner.set_static_ip(ip, mp)
            Burner.unmount(device)
            input('Insert next card and press enter...')


def main():
    """main entrypoint for setup.py"""
    VERSION = 1.0
    arguments = docopt(__doc__, version=VERSION)
    analyse(arguments)

if __name__ == '__main__':
    main()
