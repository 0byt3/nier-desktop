# Credit: Adapted from Omarchy
# Set default XCompose that is triggered with CapsLock
tee ~/.XCompose >/dev/null <<EOF
# Run nier-restart-xcompose to apply changes

# Include fast emoji access
include "/usr/local/share/nier/default/xcompose"

# Identification
<Multi_key> <space> <n> : "$NIER_USER_NAME"
<Multi_key> <space> <e> : "$NIER_USER_EMAIL"
EOF
