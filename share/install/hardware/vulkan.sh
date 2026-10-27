# Credit: Adapted from Omarchy
# Fedora's Mesa driver package covers AMD and Intel Vulkan implementations.
if lspci | grep -iE '(VGA|Display).*(Intel|AMD|ATI)' >/dev/null; then
  nier-pkg-add mesa-vulkan-drivers vulkan-loader
fi
