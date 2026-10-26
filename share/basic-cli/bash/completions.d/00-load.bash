if declare -F _comp_complete_load > /dev/null; then
    register_completion() {
        local cmd
        for cmd in "$@"; do
            [[ -n $cmd ]] || continue
            complete -p -- "$cmd" > /dev/null 2>&1 && continue
            if [[ -e /usr/share/bash-completion/completions/$cmd || -e /usr/share/bash-completion/completions/$cmd.bash || -e /usr/share/bash-completion/completions-core/$cmd.bash ]]; then
                complete -F _comp_complete_load -- "$cmd"
            fi
        done
    }
fi
