# netplan completions. basic-cli/setup.bash deploys this file only when the
# netplan.io package is already installed.
if declare -F register_completion > /dev/null; then
    register_completion netplan
fi
