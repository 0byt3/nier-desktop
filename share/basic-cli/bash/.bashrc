# Interactive bash configuration.
[[ -r /usr/local/share/nier/default/bash/env-bootstrap ]] && . /usr/local/share/nier/default/bash/env-bootstrap
[[ $- != *i* ]] && return

shopt -s histappend
HISTCONTROL=ignoreboth
HISTSIZE=32768
HISTFILESIZE="${HISTSIZE}"

export EDITOR=nvim
export SSH_AUTH_SOCK="/run/user/${UID}/ssh-agent.socket"

if [[ -f ${BASH_SOURCE[0]%/*}/.inputrc ]]; then
    bind -f "${BASH_SOURCE[0]%/*}/.inputrc"
fi

basic_cli_root=${BASH_SOURCE[0]%/*}
if [[ ! -d ${basic_cli_root}/aliases.d && ! -d ${basic_cli_root}/completions.d ]]; then
    basic_cli_root=${XDG_CONFIG_HOME:-$HOME/.config}/basic-cli
fi

source_bash_directory() {
    local directory=$1
    local file
    local -a files=()
    local nullglob_was_set=0

    [[ -d $directory ]] || return 0
    if shopt -q nullglob; then
        nullglob_was_set=1
    fi
    shopt -s nullglob
    files=("$directory"/*.bash)
    if (( nullglob_was_set == 0 )); then
        shopt -u nullglob
    fi
    for file in "${files[@]}"; do
        # shellcheck disable=SC1090
        source "$file"
    done
}

if [[ ! -v BASH_COMPLETION_VERSINFO && -r /usr/share/bash-completion/bash_completion ]]; then
    source /usr/share/bash-completion/bash_completion
fi

source_bash_directory "${basic_cli_root}/completions.d"
unset -f register_completion
source_bash_directory "${basic_cli_root}/aliases.d"
unset -f source_bash_directory
source "${basic_cli_root}/prompt.bash"
source "${basic_cli_root}/blesh.bash"
unset basic_cli_root
