if command -v fzf > /dev/null 2>&1 && command -v bat > /dev/null 2>&1; then
    alias ff="fzf --preview 'bat --style=numbers --color=always {}'"
    alias eff='$EDITOR "$(ff)"'
fi
