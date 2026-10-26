# Credit: Adapted from Omarchy
# Setup user theme folder and seed the default only when no theme exists yet.
mkdir -p ~/.config/nier/themes

  if [[ ! -s $HOME/.local/state/nier/current/theme.name ]]; then
    NIER_THEME_HEADLESS=1 nier-theme-set "Tokyo Night"
    rm -f ~/.config/chromium/SingletonLock
  fi

mkdir -p ~/.config/btop/themes
ln -snf "$HOME/.local/state/nier/current/theme/btop.theme" ~/.config/btop/themes/current.theme
