if command -v zoxide > /dev/null 2>&1; then
    eval "$(zoxide init bash)"
    alias cd="zd"
    zd() {
        if (( $# == 0 )); then
            builtin cd ~ || return
        elif [[ -d $1 ]]; then
            builtin cd "$1" || return
        else
            if ! z "$@"; then
                echo "Error: Directory not found"
                return 1
            fi

            printf "\U000F17A9 "
            pwd
        fi
    }
fi
