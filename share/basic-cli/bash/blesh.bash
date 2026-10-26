# Load ble.sh only when the terminal can show a colored history suggestion
# and Ubuntu's ble.sh package is installed.
blesh_color_count=0
if [[ -t 2 && ${TERM:-dumb} != dumb ]] && command -v tput > /dev/null 2>&1; then
    blesh_color_count=$(tput colors 2> /dev/null || printf '%s' 0)
fi

blesh_color_mode=
if [[ -t 2 && ${TERM:-dumb} != dumb ]]; then
    if [[ ${COLORTERM:-} == truecolor || ${COLORTERM:-} == 24bit || ${TERM:-} == *direct* ]]; then
        blesh_color_mode=truecolor
    elif [[ ${TERM:-} == *256color* || ( $blesh_color_count =~ ^[0-9]+$ && $blesh_color_count -ge 256 ) ]]; then
        blesh_color_mode=256
    fi
fi
unset blesh_color_count

blesh_config_root=${basic_cli_root:-${XDG_CONFIG_HOME:-$HOME/.config}/basic-cli}
if [[ -n $blesh_color_mode && -r /usr/share/blesh/ble.sh && -r ${blesh_config_root}/blerc ]]; then
    # shellcheck disable=SC1091
    source -- /usr/share/blesh/ble.sh --attach=none --rcfile "${blesh_config_root}/blerc"
    [[ ${BLE_VERSION-} ]] && ble-attach
fi
unset blesh_color_mode blesh_config_root
