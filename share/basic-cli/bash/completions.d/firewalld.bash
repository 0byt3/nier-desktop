# firewalld completions. basic-cli/setup.bash deploys this file only when
# the firewalld package is already installed.
if declare -F register_completion > /dev/null; then
    register_completion firewall-cmd
fi
