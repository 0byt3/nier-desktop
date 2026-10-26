# zfs completions. basic-cli/setup.bash deploys this file only when the
# zfs command is already present.
if declare -F register_completion > /dev/null; then
    register_completion zfs
fi
