## run rpi-imager, bake raspberry pi image to both a usb drive and a sd card

Using rpi-imager, bake raspberry pi image to a USB drive /dev/sdX. Also, bake to a SD card for later use.  

Then, to avoid some usb issue, put the following command on cmdline.txt
```bash
mount /dev/sdX1 /mnt
nano /mnt/cmdline.txt
```
```
usb-storage.quirks=XXXX:YYYY:u
```
Please find the product/vendor id `XXXX:YYYY` corresponding to the usb device via `lsusb`.

Then, plug the usb drive (not SD card) to raspberry pi. It will restart several times for inital setup.  
(maybe its better to do a software update here)  
After initial setup, shutdown raspberry pi and deplug the usb drive, and plug it to another linux computer.

## in some linux computer, backup sdX
```bash
mount /dev/sdX1 /mnt
mount /dev/sdX2 /mnt1
mkdir /mntcopy/
rsync -av /mnt1/ /mntcopy/root/
rsync -av /mnt/ /mntcopy/firmware/
umount /mnt
umount /mnt1
```

## format disk again
```bash
fdisk /dev/sdX
```

initial disk info
```
Disk /dev/sdX: 931.51 GiB, 1000204886016 bytes, 1953525168 sectors
Disk model: 100T2B0B-00Y    
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x0a7a79b1

Device     Boot   Start        End    Sectors  Size Id Type
/dev/sdX1          8192    1056767    1048576  512M  c W95 FAT32 (LBA)
/dev/sdX2       1056768 1953525167 1952468400  931G 83 Linux
```

Delete two partitions, and expand /dev/sdX1 to at least 5G, starting from sector 8192. Then, create /dev/sdX2 again, placing after /dev/sdX1. Set BOTH to primary partitions. Do not forget to change partition type.

## make crypt partitons, copy backup data
```bash
mkfs.fat -F32 /dev/sdX1
mount /dev/sdX1 /mnt
rsync -av /mntcopy/firmware/ /mnt/
pvcreate /dev/sdX2
vgcreate CryptGroup /dev/sdX2
lvcreate -L200G -n cryptroot CryptGroup
lvcreate -L200G -n crypthome CryptGroup
lvcreate -L200G -n misc CryptGroup
cryptsetup luksFormat /dev/CryptGroup/crypthome 
cryptsetup luksFormat /dev/CryptGroup/cryptroot
cryptsetup open /dev/CryptGroup/crypthome home
cryptsetup open /dev/CryptGroup/cryptroot root
mkfs.ext4 /dev/mapper/root
mkfs.ext4 /dev/mapper/home
mkfs.ext4 /dev/mapper/CryptGroup-misc # for some unencrypted volume
mount /dev/mapper/root /mnt
mkdir /mnt/home
mount /dev/mapper/home /mnt/home
mkdir -p /mnt/boot/firmware
mount /dev/sdX1 /mnt/boot/firmware
rsync -av mntcopy/root/ /mnt/
rsync -av mntcopy/firmware/ /mnt/boot/firmware/
```

## clean up
```bash
umount /mnt/home
umount /mnt/boot/firmware
umount /mnt
cryptsetup close root
cryptsetup close home
vgchange -an CryptGroup
```


## next, launch raspberry pi os on the raspberry pi, using a SD card, which is created before. (do not boot the usb device)

in the shell...

```bash
apt update
apt upgrade
apt install cryptsetup lvm2
```

## mount drives and chroot into them
```bash
cryptsetup open /dev/mapper/CryptGroup-cryptroot root
cryptsetup open /dev/mapper/CryptGroup-crypthome home
mount /dev/mapper/root /mnt
mount /dev/mapper/home /mnt/home
mount /dev/sda1 /mnt/boot/firmware/ # this should be sda1, but might be otherwise
cd /mnt
mount -t proc /proc proc/
mount -t sysfs /sys sys/
mount --rbind /dev dev/
chroot /mnt /bin/bash
```

## inside chroot, prepare crypt devices
```bash
echo "nameserver 8.8.8.8" > /etc/resolv.conf # update nameserver to access the internet
apt update
apt upgrade
apt install vim cryptsetup cryptsetup-initramfs lvm2
vim /boot/firmware/cmdline.txt
```

## Edit cmdline.txt

Add `cryptdevice=UUID=<UUID of /dev/mapper/CryptGroup-cryptroot>:root root=/dev/mapper/root` to cmdline.txt.  
You can obtain UUID of the filesystem by `lsblk -o name,UUID | grep cryptroot`.
Also, remove `splash` from it to enable console.

```bash
nano /boot/firmware/cmdline.txt
```

## edit crypttab to add root and home. also, add a key file for home dir.
```bash
head -c 512 /dev/random > /etc/my-home-key
chmod 600 /etc/my-home-key
cryptsetup luksAddKey /dev/CryptGroup/crypthome /etc/my-home-key
echo -e 'root\t/dev/CryptGroup/cryptroot\tnone\tluks' > /etc/crypttab
echo -e 'home\t/dev/CryptGroup/crypthome\t/etc/my-home-key\tluks' >> /etc/crypttab
```

## rebuild initramfs to include crypttab settings
```bash
update-initramfs -k all -u
```

## make sure generated initramfs files contain necessary driver files
```bash
lsinitramfs /boot/firmware/initramfs_2712 | grep lvm
lsinitramfs /boot/firmware/initramfs_2712 | grep crypt
```

## exit chroot and reboot

```bash
exit
umount /mnt/home
umount /mnt/boot/firmware
umount /mnt
cryptsetup close root
cryptsetup close home
vgchange -an CryptGroup
reboot
```
