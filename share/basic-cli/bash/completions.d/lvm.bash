# LVM completions. basic-cli/setup.bash deploys this file only when the
# lvm2 package is already installed.
if declare -F register_completion > /dev/null; then
    register_completion \
        lvchange lvcreate lvdisplay lvextend lvm lvmdiskscan lvreduce lvremove \
        lvrename lvresize lvs lvscan \
        pvchange pvcreate pvdisplay pvmove pvremove pvs pvscan \
        vgcfgbackup vgcfgrestore vgchange vgck vgconvert vgcreate vgdisplay \
        vgexport vgextend vgimport vgmerge vgmknodes vgreduce vgremove \
        vgrename vgs vgscan vgsplit
fi
