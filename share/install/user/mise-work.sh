# Credit: Adapted from Omarchy
# Setup default work directory (and tries)
mkdir -p "$HOME/Work"
mkdir -p "$HOME/Work/tries"

mise use -g node@latest || echo "Warning: Node.js install deferred" >&2
