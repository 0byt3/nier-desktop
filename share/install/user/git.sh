# Credit: Adapted from Omarchy
# Set identification from install inputs
if [[ -n ${NIER_USER_NAME//[[:space:]]/} ]]; then
  git config --global user.name "$NIER_USER_NAME"
fi

if [[ -n ${NIER_USER_EMAIL//[[:space:]]/} ]]; then
  git config --global user.email "$NIER_USER_EMAIL"
fi
