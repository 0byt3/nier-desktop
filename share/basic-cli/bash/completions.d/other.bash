# Completions for tools that Ubuntu 26.04 does not package.
# basic-cli/setup.bash does not deploy this file.
if declare -F register_completion > /dev/null; then
    register_completion charm vhs yazi
fi
