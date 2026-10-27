import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Keep confirmation inside the greeter window: Cage manages a single surface.
FocusScope {
    id: dialog
    property string action: "reboot"
    property var style
    signal accepted()
    signal rejected()
    visible: false

    function open() {
        visible = true;
        cancelButton.forceActiveFocus();
    }
    function reject() {
        visible = false;
        rejected();
    }
    Keys.onEscapePressed: function(event) { reject(); event.accepted = true; }

    Rectangle { anchors.fill: parent; color: "#99000000" }
    MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }
    Rectangle {
        anchors.centerIn: parent
        width: Math.min(460, dialog.width - 48)
        height: content.implicitHeight + 48
        radius: dialog.style.radius
        color: dialog.style.surface
        border.width: 1; border.color: dialog.style.outline
        ColumnLayout {
            id: content
            anchors.fill: parent; anchors.margins: 24
            spacing: 20
            Text {
                Layout.fillWidth: true
                text: dialog.action === "reboot" ? "Restart this computer?" : "Shut down this computer?"
                color: dialog.style.foreground
                wrapMode: Text.WordWrap
                font.family: dialog.style.fontFamily; font.pixelSize: 18; font.bold: true
            }
            Text {
                Layout.fillWidth: true
                text: "Any open sessions will be closed."
                color: dialog.style.muted
                wrapMode: Text.WordWrap
                font.family: dialog.style.fontFamily; font.pixelSize: dialog.style.fontSize
            }
            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: 12
                Button {
                    id: cancelButton
                    objectName: "cancelPower"
                    text: "Cancel"
                    palette.button: dialog.style.background; palette.buttonText: dialog.style.foreground
                    font.family: dialog.style.fontFamily
                    KeyNavigation.tab: confirmButton; KeyNavigation.backtab: confirmButton
                    onClicked: dialog.reject()
                }
                Button {
                    id: confirmButton
                    objectName: "confirmPower"
                    text: dialog.action === "reboot" ? "Restart" : "Shut down"
                    palette.button: dialog.style.accent; palette.buttonText: dialog.style.surface
                    font.family: dialog.style.fontFamily
                    KeyNavigation.tab: cancelButton; KeyNavigation.backtab: cancelButton
                    onClicked: { dialog.visible = false; dialog.accepted(); }
                }
            }
        }
    }
}
