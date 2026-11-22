// Drivers do Konaro — detecta o hardware, explica e instala só com permissão.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 820
    height: 680
    minimumWidth: 680
    minimumHeight: 520
    visible: true
    color: Theme.paper
    title: i18n.tr("Konaro Drivers")

    KScrollPage {
        anchors { fill: parent; bottomMargin: bar.height }
        margin: 48

        RowLayout {
            width: parent.width
            spacing: Theme.s5
            KIcon { name: "konaro-drivers"; Layout.preferredWidth: 64; Layout.preferredHeight: 64 }
            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true
                KText {
                    heading: true; font.pixelSize: 30; font.letterSpacing: -0.6; Layout.fillWidth: true
                    text: drivers.state === "scanning" ? i18n.tr("Scanning your hardware…")
                          : drivers.recommendations.length === 0 ? i18n.tr("Everything is working.")
                          : i18n.plural(drivers.recommendations.length, "{n} recommended driver", "{n} recommended drivers")
                }
                KText { text: i18n.tr("Drivers are only installed with your permission."); secondary: true; Layout.fillWidth: true }
            }
        }

        // ---- recomendações
        Repeater {
            model: drivers.recommendations
            KCard {
                width: parent.width
                implicitHeight: rec.implicitHeight + Theme.s5 * 2
                ColumnLayout {
                    id: rec
                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: Theme.s5 }
                    spacing: Theme.s2
                    RowLayout {
                        spacing: Theme.s2
                        KText { text: modelData.title; font.pixelSize: 17; font.weight: Font.DemiBold; Layout.fillWidth: true }
                        KChip { visible: modelData.restart; text: i18n.tr("May require a restart") }
                    }
                    KText { text: modelData.reason; lineHeight: 1.25; Layout.fillWidth: true }
                    GridLayout {
                        columns: 2
                        columnSpacing: Theme.s4
                        rowSpacing: 2
                        Layout.topMargin: Theme.s1
                        KText { text: i18n.tr("Source"); secondary: true; font.pixelSize: Theme.sizeSmall }
                        KText { text: modelData.origin; font.pixelSize: Theme.sizeSmall; Layout.fillWidth: true }
                        KText { text: i18n.tr("Packages"); secondary: true; font.pixelSize: Theme.sizeSmall }
                        KText { text: modelData.packagesText; font.pixelSize: Theme.sizeSmall; font.family: "monospace"; Layout.fillWidth: true }
                    }
                    KButton {
                        Layout.alignment: Qt.AlignRight
                        kind: "primary"
                        text: drivers.busyIndex === index ? i18n.tr("Installing…") : i18n.tr("Install")
                        enabled: drivers.state === "ready"
                        progress: drivers.busyIndex === index ? drivers.progress : -1
                        onClicked: { confirm.index = index; confirm.title = modelData.title
                                     confirm.message = modelData.reason + "\n\n" + i18n.tr("Your password may be requested."); confirm.open() }
                    }
                }
            }
        }

        // ---- dispositivos
        KText { text: i18n.tr("Your devices"); heading: true; font.pixelSize: Theme.sizeHeading; visible: drivers.devices.length > 0 }
        KCard {
            visible: drivers.devices.length > 0
            width: parent.width
            implicitHeight: devs.implicitHeight + Theme.s3 * 2
            Column {
                id: devs
                anchors { left: parent.left; right: parent.right; top: parent.top; margins: Theme.s3 }
                Repeater {
                    model: drivers.devices
                    RowLayout {
                        width: parent.width
                        height: 60
                        spacing: Theme.s4
                        KIcon { name: modelData.icon; Layout.preferredWidth: 32; Layout.preferredHeight: 32; Layout.leftMargin: Theme.s2 }
                        ColumnLayout {
                            spacing: 2
                            Layout.fillWidth: true
                            KText { text: modelData.name; font.weight: Font.DemiBold; elide: Text.ElideRight; wrapMode: Text.NoWrap; Layout.fillWidth: true }
                            KText { text: modelData.kind + ". " + modelData.status; secondary: true; font.pixelSize: Theme.sizeSmall; Layout.fillWidth: true }
                        }
                        Rectangle { width: 8; height: 8; radius: 4; color: modelData.ok ? Theme.success : Theme.stone; Layout.rightMargin: Theme.s3 }
                    }
                }
            }
        }
    }

    Rectangle {
        id: bar
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 80
        color: Theme.paper
        Rectangle { anchors { left: parent.left; right: parent.right; top: parent.top } height: 1; color: Theme.hairline }
        RowLayout {
            anchors { fill: parent; leftMargin: 48; rightMargin: 48 }
            KButton { text: i18n.tr("Scan again"); iconName: "view-refresh-symbolic"; enabled: drivers.state === "ready"; onClicked: drivers.scan() }
            Item { Layout.fillWidth: true }
        }
    }

    KDialog {
        id: confirm
        property int index: -1
        iconName: "konaro-drivers"
        cancelText: i18n.tr("Cancel")
        confirmText: i18n.tr("Install")
        onConfirmed: drivers.install(index)
    }
    KDialog {
        id: restartDialog
        iconName: "system-reboot"
        title: i18n.tr("Restart required")
        message: i18n.tr("The driver was installed. Restart the computer to start using it.")
        cancelText: i18n.tr("Later")
        confirmText: i18n.tr("Restart now")
        onConfirmed: drivers.reboot()
    }
    KDialog { id: errorDialog; iconName: "dialog-warning"; title: i18n.tr("Something went wrong"); confirmText: i18n.tr("Close") }
    Connections {
        target: drivers
        function onRestartNeeded() { restartDialog.open() }
        function onFailed(message, details) { errorDialog.message = message; errorDialog.details = details; errorDialog.open() }
    }
}
