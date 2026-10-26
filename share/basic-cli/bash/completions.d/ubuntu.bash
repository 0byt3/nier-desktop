if declare -F register_completion > /dev/null; then
register_completion \
         '[' addpart agetty awk b2sum base32 base64 basename \
         basenc bat bits blkdiscard blkid blkpr blkzone blockdev \
         bunzip2 bzcat bzdiff bzgrep bzip2 bzip2recover bzmore \
         cal cat cfdisk chage chcpu chfn chgpasswd chgrp \
         chmem chmod choom chown chpasswd chroot chrt chsh \
         cksum cmp col colcrt colrm column comm copyfilerange \
         coresched cp csplit ctrlaltdel cut date dconf dd \
         delpart depmod df diff diff3 dir dircolors dirname \
         dmesg docker du echo egrep eject enosys env \
         exch expand expr eza factor fadvise faillog fallocate \
         false fd fdisk fgrep fincore find findfs findmnt \
         flock fmt fold free fsck fsck.cramfs fsck.minix fsfreeze \
         fstrim gawk getino getopt getsubids gio git glow \
         gpasswd grep groupadd groupdel groupmod groups grpck grpconv \
         grpunconv gum gunzip gzexe gzip hardlink head hexdump \
         hostid hugetop hwclock i386 id insmod install ionice \
         ip ipcmk ipcrm ipcs irqtop isosize join kill \
         kmod last lastb lastlog2 ldattach ldc ldc2 less \
         lesskey link linux32 linux64 ln logger login logname \
         look losetup ls lsblk lsclocks lscpu lsfd lsipc \
         lsirq lslocks lslogins lsmem lsmod lsns lzcat lzcmp lzdiff \
         lzegrep lzfgrep lzgrep \
         lzless lzma lzmadec lzmainfo lzmore mcookie md5sum mesg \
         mkdir mkfifo mkfs mkfs.bfs mkfs.cramfs mkfs.minix mknod mkswap \
         mktemp modinfo modprobe more mount mountpoint mv namei \
         newgidmap newgrp newuidmap newusers nice nl nohup \
         nologin nproc nsenter numfmt od pandoc partx passwd paste \
         pathchk pg pgrep pidof pidwait pinky pipesz pivot_root \
         pkill pmap pr printenv printf prlimit ps ptx pwck \
         pwconv pwd pwdx pwunconv readlink readprofile realpath rename \
         renice resizepart rev rfkill rg rm rmdir rmmod \
         rtcwake runuser script scriptlive scriptreplay sdiff sed seq \
         setarch setpgid setpriv setsid setterm sfdisk sha1sum sha224sum \
         sha256sum sha384sum sha512sum shred shuf slabtop sleep sort \
         split ss stat stdbuf stty su sulogin sum \
         swaplabel swapoff swapon switch_root sync sysctl tac tail \
         tar taskset tee test timeout tldr tload top \
         touch tr true truncate tsort tty tunelp uclampset \
         udevadm udisksctl ul umount uname uname26 uncompress \
         unexpand uniq unlink unlzma unshare unxz uptime useradd \
         userdel usermod users utmpdump uuidd uuidgen uuidparse vdir \
         vigr vipw vmstat w waitpid wall \
         watch wc wdctl whereis which who whoami wipefs \
         write x86_64 xargs xz xzcat xzcmp xzdec xzdiff \
         xzegrep xzfgrep xzgrep xzless xzmore yes yq zcat \
         zcmp zdiff zegrep zfgrep zforce zgrep zless zmore \
         znew zoxide zramctl

if shopt -q nullglob; then
    nullglob_was_set=1
else
    nullglob_was_set=0
    shopt -s nullglob
fi
completion_paths=(
    /usr/share/bash-completion/completions/*ctl
    /usr/share/bash-completion/completions/systemd-*
)
if (( nullglob_was_set == 0 )); then
    shopt -u nullglob
fi
unset nullglob_was_set
completion_names=()
for completion_path in "${completion_paths[@]}"; do
    completion_names+=("${completion_path##*/}")
done
register_completion "${completion_names[@]}"
unset completion_paths completion_names

# The ldc completion file registers ldc2 only.
if [[ -r /usr/share/bash-completion/completions/ldc ]]; then
    source /usr/share/bash-completion/completions/ldc
    complete -o nospace -F _ldc ldc
    complete -o nospace -F _ldc ldc2
fi
fi
