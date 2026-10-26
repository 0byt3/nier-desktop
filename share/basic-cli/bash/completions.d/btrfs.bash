# btrfs completions. basic-cli/setup.bash deploys this file only when the
# btrfs-progs package is already installed.
if declare -F register_completion > /dev/null; then
    register_completion btrfs
fi
