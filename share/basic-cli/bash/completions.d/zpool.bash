# zpool completions. basic-cli/setup.bash deploys this file only when the
# zpool command is already present.
if declare -F register_completion > /dev/null; then
    register_completion zpool
fi
