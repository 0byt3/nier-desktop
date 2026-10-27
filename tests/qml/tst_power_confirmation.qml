import QtQuick
import QtTest
import "../../share/greeter"

TestCase {
    id: test
    name: "PowerConfirmation"
    when: windowShown
    visible: true
    width: 800; height: 600
    PowerConfirmation {
        id: dialog
        anchors.fill: parent
        style: ({background: "#1e1e2e", surface: "#161622", foreground: "#cdd6f4",
                 muted: "#9197b1", accent: "#89b4fa", outline: "#45475a",
                 fontFamily: "monospace", fontSize: 12, radius: 4})
    }
    SignalSpy { id: accepted; target: dialog; signalName: "accepted" }
    SignalSpy { id: rejected; target: dialog; signalName: "rejected" }
    function init() { dialog.visible = false; accepted.clear(); rejected.clear(); }
    function test_cancel_does_not_accept_power_action() {
        dialog.action = "reboot";
        dialog.open();
        tryCompare(dialog, "visible", true);
        mouseClick(findChild(dialog, "cancelPower"));
        compare(dialog.visible, false);
        compare(accepted.count, 0);
        compare(rejected.count, 1);
    }
    function test_escape_cancels_and_defaults_to_cancel() {
        dialog.open();
        var cancel = findChild(dialog, "cancelPower");
        tryCompare(cancel, "activeFocus", true);
        keyClick(Qt.Key_Escape);
        compare(dialog.visible, false);
        compare(accepted.count, 0);
        compare(rejected.count, 1);
    }
    function test_confirm_shutdown_emits_only_a_signal() {
        // This component has no power command: accepting cannot affect the host.
        dialog.action = "poweroff";
        dialog.open();
        var confirm = findChild(dialog, "confirmPower");
        compare(confirm.text, "Shut down");
        mouseClick(confirm);
        compare(dialog.visible, false);
        compare(accepted.count, 1);
        compare(rejected.count, 0);
    }
    function test_restart_label_and_keyboard_focus_cycle() {
        dialog.action = "reboot";
        dialog.open();
        var cancel = findChild(dialog, "cancelPower");
        var confirm = findChild(dialog, "confirmPower");
        compare(confirm.text, "Restart");
        keyClick(Qt.Key_Tab);
        tryCompare(confirm, "activeFocus", true);
        keyClick(Qt.Key_Tab);
        tryCompare(cancel, "activeFocus", true);
        compare(accepted.count, 0);
    }
}
