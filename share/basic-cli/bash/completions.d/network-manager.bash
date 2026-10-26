# NetworkManager completions. Ubuntu server uses systemd-networkd, so
# basic-cli/setup.bash does not deploy this file. Another distribution's
# installer can deploy it when NetworkManager is the network service.
if declare -F register_completion > /dev/null; then
    register_completion nmcli nmtui
fi
