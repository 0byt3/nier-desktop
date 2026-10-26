// Credit: Adapted from Omarchy
import QtQuick
import Quickshell.Hyprland
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "nier.workspaces"

  readonly property int pageSize: 20
  readonly property int staticCount: 20

  property bool popupOpen: false
  property int pageIndex: 0
  readonly property bool opened: popupOpen

  readonly property int activeId: {
    var workspace = Hyprland.focusedWorkspace
    return workspace && workspace.id > 0 ? workspace.id : 0
  }

  readonly property string activeLabel: activeId > 0 ? String(activeId) : "—"

  readonly property var ids: root.collectIds(Hyprland.workspaces.values, root.staticCount)
  readonly property int pageCount: Math.max(1, Math.ceil(root.ids.length / root.pageSize))
  readonly property bool paged: root.ids.length > root.pageSize
  readonly property var pageIds: root.pageSlice(root.ids, root.pageIndex, root.pageSize)

  readonly property real openPanelIndicatorWidth: button.labelWidth
  readonly property real openPanelIndicatorHeight: Math.max(Style.space(10), Math.round(Style.bar.iconSlot * 0.55))

  function collectIds(values, staticCount) {
    var list = []
    var i
    for (i = 1; i <= staticCount; i++) list.push(i)
    for (i = 0; i < values.length; i++) {
      var id = values[i].id
      if (id > 0 && list.indexOf(id) === -1) list.push(id)
    }
    list.sort(function(left, right) { return left - right })
    return list
  }

  function pageSlice(ids, pageIndex, pageSize) {
    var start = pageIndex * pageSize
    return ids.slice(start, start + pageSize)
  }

  function pageForId(ids, id, pageSize) {
    var index = ids.indexOf(id)
    if (index < 0) return 0
    return Math.floor(index / pageSize)
  }

  function clampIndex(index, count) {
    if (count <= 0) return 0
    if (index < 0) return 0
    if (index > count - 1) return count - 1
    return index
  }

  function workspaceById(id) {
    var values = Hyprland.workspaces.values
    for (var i = 0; i < values.length; i++) {
      if (values[i].id === id) return values[i]
    }

    return null
  }

  function workspaceOccupied(id) {
    var workspace = workspaceById(id)
    return workspace !== null && workspace.toplevels.values.length > 0
  }

  function focusWorkspace(id) {
    if (!root.bar) return
    root.bar.run("hyprctl dispatch " + Util.shellQuote("hl.dsp.focus({ workspace = \"" + id + "\" })"))
  }

  function showActivePage() {
    pageIndex = root.pageForId(root.ids, root.activeId, root.pageSize)
  }

  function open() {
    root.showActivePage()
    popupOpen = true
  }

  function close() { popupOpen = false }

  function togglePanel() {
    if (popupOpen) root.close()
    else root.open()
  }

  function nextPage() {
    pageIndex = root.clampIndex(pageIndex + 1, root.pageCount)
  }

  function prevPage() {
    pageIndex = root.clampIndex(pageIndex - 1, root.pageCount)
  }

  onIdsChanged: pageIndex = root.clampIndex(pageIndex, root.pageCount)

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.activeLabel
    horizontalMargin: 8
    verticalPadding: 6
    tooltipText: "Workspaces"
    onPressed: function() { root.togglePanel() }
  }

  PopupCard {
    id: popup
    anchorItem: button
    bar: root.bar
    owner: root
    open: root.popupOpen
    contentWidth: popup.fittedContentWidth(Style.space(132))
    contentHeight: popup.fittedContentHeight(list.implicitHeight)

    Item {
      anchors.fill: parent
      clip: true

      WheelHandler {
        enabled: root.paged && root.popupOpen
        onWheel: function(event) {
          if (event.angleDelta.y < 0) root.nextPage()
          else root.prevPage()
          event.accepted = true
        }
      }

      Column {
        id: list
        anchors.fill: parent
        spacing: Style.space(2)

        Repeater {
          model: root.pageIds

          Button {
            required property int modelData

            readonly property bool focused: root.activeId === modelData
            readonly property bool occupied: root.workspaceOccupied(modelData)

            width: list.width
            height: Style.spacing.popupRowHeight
            text: String(modelData)
            selected: focused
            leftAlign: true
            foreground: root.bar ? root.bar.foreground : Color.foreground
            fontFamily: root.bar ? root.bar.fontFamily : Style.font.family
            fontSize: Style.font.body
            verticalPadding: Style.spacing.xxs
            opacity: occupied || focused ? 1 : 0.5
            onClicked: {
              root.focusWorkspace(modelData)
              root.close()
            }
          }
        }

        Item {
          visible: root.paged
          width: list.width
          height: visible ? Math.max(prevPageButton.height, pageLabel.height, nextPageButton.height) : 0

          MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
          }

          Button {
            id: prevPageButton
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            width: Style.space(36)
            text: "‹"
            fontFamily: root.bar ? root.bar.fontFamily : Style.font.family
            foreground: root.bar ? root.bar.foreground : Color.foreground
            opacity: root.pageIndex > 0 ? 1 : 0.35
            onClicked: if (root.pageIndex > 0) root.prevPage()
          }

          Text {
            id: pageLabel
            anchors.centerIn: parent
            textFormat: Text.PlainText
            text: (root.pageIndex + 1) + " / " + root.pageCount
            color: root.bar ? root.bar.foreground : Color.foreground
            font.family: root.bar ? root.bar.fontFamily : Style.font.family
            font.pixelSize: Style.font.caption
          }

          Button {
            id: nextPageButton
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            width: Style.space(36)
            text: "›"
            fontFamily: root.bar ? root.bar.fontFamily : Style.font.family
            foreground: root.bar ? root.bar.foreground : Color.foreground
            opacity: root.pageIndex < root.pageCount - 1 ? 1 : 0.35
            onClicked: if (root.pageIndex < root.pageCount - 1) root.nextPage()
          }
        }
      }
    }
  }
}
