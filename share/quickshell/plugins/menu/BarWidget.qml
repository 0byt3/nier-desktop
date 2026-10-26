// Credit: Adapted from Omarchy
import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "nier.menu"

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: ""
    fontFamily: root.bar ? root.bar.fontFamily : "JetBrainsMono Nerd Font"
    horizontalMargin: 7.5
    onPressed: function(button) {
      if (!root.bar) return
      if (button === Qt.RightButton) root.bar.run("xdg-terminal-exec")
      else root.bar.run("nier-shell shell toggle nier.menu '{\"menu\":\"root\"}'")
    }
  }
}
