import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Services.Greetd
import "Auth.js" as Auth

ShellRoot {
    id: root
    property var style: ({ background: "#1e1e2e", surface: "#161622", foreground: "#cdd6f4",
        muted: "#9197b1", accent: "#89b4fa", error: "#f38ba8", outline: "#45475a",
        fontFamily: "monospace", fontSize: 12, radius: 4 })
    property var users: []
    property var ui: ({ busy: false, active: false, waiting: false, canceling: false,
        prompt: "Password", echo: false, message: "", error: false })
    property var auth
    property date now: new Date()
    property string powerAction: ""
    property string powerError: ""

    function submit() {
        if (!Greetd.available || !auth || ui.busy) return;
        var response = password.text;
        password.clear();
        auth.submit(username.editText, response);
    }

    Component.onCompleted: {
        auth = Auth.create({
            createSession: function(user) { Greetd.createSession(user); },
            respond: function(response) { Greetd.respond(response); },
            cancelSession: function() { Greetd.cancelSession(); },
            launch: function() {
                Greetd.launch(["/usr/local/share/nier/bin/nier-session"],
                    ["XDG_SESSION_TYPE=wayland", "XDG_CURRENT_DESKTOP=Nier:Hyprland", "XDG_SESSION_DESKTOP=Hyprland"]);
            }
        }, function(state) {
            root.ui = state;
            if (!state.busy) Qt.callLater(function() { password.forceActiveFocus(); });
        });
    }

    FileView {
        path: Quickshell.env("NIER_GREETER_STYLE") || "/etc/nier/greeter.json"
        printErrors: false
        onLoaded: {
            try { root.style = Object.assign({}, root.style, JSON.parse(text())); }
            catch (error) { console.warn("Invalid greeter appearance file; using defaults"); }
        }
    }
    Process {
        id: powerProcess
        command: ["systemctl", "--no-ask-password", root.powerAction]
        stderr: StdioCollector { onStreamFinished: { if (text.trim()) console.warn("Greeter power action: " + text.trim()); } }
        onExited: function(exitCode, exitStatus) {
            if (exitCode !== 0) root.powerError = "Unable to " + (root.powerAction === "reboot" ? "restart" : "shut down") + ". Sign in and try again.";
        }
    }
    Process {
        command: ["/usr/local/share/nier/bin/nier-greeter-users"]
        running: true
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.users = JSON.parse(text); } catch (error) { root.users = []; }
            }
        }
    }
    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }
    Connections {
        target: Greetd
        function onAuthMessage(message, error, responseRequired, echoResponse) {
            root.auth.message(message, error, responseRequired, echoResponse);
        }
        function onAuthFailure(message) { password.clear(); root.auth.failure("Authentication failed. Try again."); }
        function onError(error) { password.clear(); root.auth.failure("Unable to sign in. Please try again."); }
        function onReadyToLaunch() { root.auth.ready(); }
        function onStateChanged() { if (Greetd.state === GreetdState.Inactive && root.auth) root.auth.inactive(); }
    }

    FloatingWindow {
        id: window
        title: "Nier Desktop — Sign in"
        color: root.style.background
        implicitWidth: 1280
        implicitHeight: 800
        visible: true
        Shortcut { sequence: "Escape"; onActivated: { if (powerDialog.visible) powerDialog.reject(); else { password.clear(); root.auth.cancel(); } } }

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0; color: root.style.background }
                GradientStop { position: 1; color: root.style.surface }
            }
        }
        Row {
            anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 36
            spacing: 12
            Rectangle {
                width: 28; height: 28; radius: root.style.radius
                color: root.style.accent
                Text { anchors.centerIn: parent; text: "N"; color: root.style.surface; font.family: root.style.fontFamily; font.bold: true; font.pixelSize: 18 }
            }
            Text {
                text: "NIER DESKTOP"; anchors.verticalCenter: parent.verticalCenter
                color: root.style.foreground; font.family: root.style.fontFamily
                font.pixelSize: root.style.fontSize; font.letterSpacing: 3
            }
        }
        Column {
            anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 36
            spacing: 4
            Text { anchors.right: parent.right; text: Qt.formatTime(root.now, "HH:mm"); color: root.style.foreground; font.family: root.style.fontFamily; font.pixelSize: 28 }
            Text { text: Qt.formatDate(root.now, "dddd, MMMM d"); color: root.style.muted; font.family: root.style.fontFamily; font.pixelSize: root.style.fontSize }
        }

        Rectangle {
            id: card
            anchors.centerIn: parent
            width: Math.min(440, window.width - 48)
            height: form.implicitHeight + 64
            radius: root.style.radius
            color: root.style.surface
            border.width: 1
            border.color: root.style.outline
            ColumnLayout {
                id: form
                anchors.fill: parent; anchors.margins: 32
                spacing: 16
                Rectangle { width: 32; height: 3; color: root.style.accent }
                Text { text: "Welcome back."; color: root.style.foreground; font.family: root.style.fontFamily; font.pixelSize: 24; font.bold: true }
                Text { text: "Sign in to your Nier desktop"; color: root.style.muted; font.family: root.style.fontFamily; font.pixelSize: root.style.fontSize; Layout.bottomMargin: 8 }
                Text { text: "USERNAME"; color: root.style.muted; font.family: root.style.fontFamily; font.pixelSize: 10; font.letterSpacing: 2 }
                ComboBox {
                    id: username
                    Layout.fillWidth: true
                    implicitHeight: 44
                    model: root.users
                    editable: true
                    enabled: !root.ui.active && !root.ui.busy
                    font.family: root.style.fontFamily; font.pixelSize: root.style.fontSize
                    palette.text: root.style.foreground; palette.base: root.style.background
                    palette.buttonText: root.style.foreground; palette.button: root.style.background
                    palette.highlight: root.style.accent; palette.highlightedText: root.style.surface
                    background: Rectangle { radius: root.style.radius; color: root.style.background; border.width: 1; border.color: username.activeFocus ? root.style.accent : root.style.outline }
                    onAccepted: password.forceActiveFocus()
                    Keys.onReturnPressed: password.forceActiveFocus()
                }
                Text { text: root.ui.prompt.replace(/:\s*$/, "").toUpperCase(); color: root.style.muted; font.family: root.style.fontFamily; font.pixelSize: 10; font.letterSpacing: 2 }
                TextField {
                    id: password
                    Layout.fillWidth: true
                    implicitHeight: 48
                    enabled: !root.ui.busy
                    placeholderText: root.ui.echo ? "Enter response" : "Enter password"
                    echoMode: root.ui.echo ? TextInput.Normal : TextInput.Password
                    passwordMaskDelay: 0
                    inputMethodHints: Qt.ImhSensitiveData | Qt.ImhNoPredictiveText
                    color: root.style.foreground
                    placeholderTextColor: root.style.muted
                    selectionColor: root.style.accent
                    selectedTextColor: root.style.surface
                    leftPadding: 14; rightPadding: 14
                    font.family: root.style.fontFamily; font.pixelSize: 14
                    background: Rectangle {
                        radius: root.style.radius; color: root.style.background; border.width: 2
                        border.color: root.ui.error ? root.style.error : (password.activeFocus ? root.style.accent : root.style.outline)
                    }
                    onAccepted: root.submit()
                    Component.onCompleted: forceActiveFocus()
                }
                Text {
                    Layout.fillWidth: true
                    Layout.minimumHeight: 28
                    text: !Greetd.available ? "Preview — authentication is unavailable" : root.ui.message
                    color: root.ui.error ? root.style.error : root.style.muted
                    wrapMode: Text.WordWrap
                    font.family: root.style.fontFamily; font.pixelSize: root.style.fontSize
                }
                Button {
                    id: signIn
                    Layout.fillWidth: true
                    implicitHeight: 44
                    enabled: Greetd.available && !root.ui.busy && username.editText.trim().length > 0
                    text: root.ui.busy ? "Please wait…" : (root.ui.waiting ? "Continue" : "Sign in  →")
                    onClicked: root.submit()
                    background: Rectangle { radius: root.style.radius; color: signIn.down ? Qt.darker(root.style.accent, 1.15) : root.style.accent; opacity: signIn.enabled ? 1 : 0.45 }
                    contentItem: Text { text: signIn.text; color: root.style.surface; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.family: root.style.fontFamily; font.pixelSize: root.style.fontSize; font.bold: true }
                }
                Button {
                    visible: root.ui.active
                    text: "Cancel / change user"
                    flat: true
                    Layout.alignment: Qt.AlignHCenter
                    palette.buttonText: root.style.muted
                    onClicked: { password.clear(); root.auth.cancel(); }
                }
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: card.bottom; anchors.topMargin: 20
            text: "HYPRLAND  ·  UWSM"; color: root.style.muted
            font.family: root.style.fontFamily; font.pixelSize: 10; font.letterSpacing: 2
        }
        Row {
            id: powerButtons
            anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 28
            spacing: 12
            enabled: !root.ui.busy && !powerProcess.running
            Button { id: restartButton; text: "Restart"; flat: true; palette.buttonText: root.style.muted; font.family: root.style.fontFamily; onClicked: { root.powerAction = "reboot"; root.powerError = ""; powerDialog.open(); } }
            Button { id: shutdownButton; text: "Shut down"; flat: true; palette.buttonText: root.style.muted; font.family: root.style.fontFamily; onClicked: { root.powerAction = "poweroff"; root.powerError = ""; powerDialog.open(); } }
        }
        Text {
            anchors.right: powerButtons.right; anchors.bottom: powerButtons.top
            width: Math.min(420, window.width - 56)
            text: root.powerError; visible: text.length > 0
            color: root.style.error; wrapMode: Text.WordWrap
            font.family: root.style.fontFamily; font.pixelSize: root.style.fontSize
        }
        PowerConfirmation {
            id: powerDialog
            anchors.fill: parent
            z: 100
            action: root.powerAction
            style: root.style
            onRejected: password.forceActiveFocus()
            onAccepted: powerProcess.running = true
        }
    }
}
