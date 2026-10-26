# Bash prompt. Sourced by basic-cli bashrc and by the Omarchy bashrc after
# Omarchy's own startup. Starship redraws PS1 from PROMPT_COMMAND, so that
# hook is removed before this prompt is set.
if [[ ${PROMPT_COMMAND-} == *starship_precmd* ]]; then
    if [[ -n ${STARSHIP_PROMPT_COMMAND-} ]]; then
        PROMPT_COMMAND=$STARSHIP_PROMPT_COMMAND
    else
        unset PROMPT_COMMAND
    fi
    unset STARSHIP_PROMPT_COMMAND
    PS2='> '
fi

prompt_color_count=0
if [[ -t 2 && ${TERM:-dumb} != dumb ]] && command -v tput > /dev/null 2>&1; then
    prompt_color_count=$(tput colors 2> /dev/null || printf '%s' 0)
fi

PS1='╭─| \u@\h: \w\n╰─ bash$ '
if [[ -t 2 && ${TERM:-dumb} != dumb ]]; then
    if [[ ${COLORTERM:-} == truecolor || ${COLORTERM:-} == 24bit || ${TERM:-} == *direct* ]]; then
        PS1='╭─| \[\e[38;2;157;206;212m\]\u@\h\[\e[39m\]: \[\e[38;2;232;196;160m\]\w\[\e[39m\]\n╰─ \[\e[38;2;201;177;224m\]bash\[\e[39m\]$ '
    elif [[ ${TERM:-} == *256color* || ( $prompt_color_count =~ ^[0-9]+$ && $prompt_color_count -ge 256 ) ]]; then
        PS1='╭─| \[\e[38;5;152m\]\u@\h\[\e[39m\]: \[\e[38;5;223m\]\w\[\e[39m\]\n╰─ \[\e[38;5;183m\]bash\[\e[39m\]$ '
    fi
fi
unset prompt_color_count
