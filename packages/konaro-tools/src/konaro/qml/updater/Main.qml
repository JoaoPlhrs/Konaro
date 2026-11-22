// Atualizações do Konaro — mostra o que há para atualizar e instala só quando o usuário pede.
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
    title: i18n.tr("Konaro Updates")

    property var unchecked: ({})       // grupos desmarcados pelo usuário
    readonly property bool busy: updater.state !== "ready"

    function chosenKeys() { return updater.groups.map(g => g.key).filter(k => !unchecked[k]) }

    KScrollPage {
        anchors { fill: parent; bottomMargin: bar.height }
        margin: 48

        // ---- estado geral
        RowLayout {
            width: parent.width
            spacing: Theme.s5
            Rectangle {
                Layout.preferredWidth: 72; Layout.preferredHeight: 72; radius: 36
                color: Theme.dark ? Theme.raised : Theme.surface
                border.width: 1; border.color: Theme.hairline
                KIcon {
                    anchors.centerIn: parent
                    width: 34; height: 34
                    tinted: true
                    name: updater.state === "checking" ? "view-refresh-symbolic"
                          : updater.total === 0 ? "emblem-ok-symbolic" : "system-software-update-symbolic"
                    RotationAnimation on rotation {
                        running: updater.state === "checking" && !Theme.reducedMotion
                        from: 0; to: 360; duration: 1400; loops: Animation.Infinite
                    }
                }
            }
            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true
                KText {
                    heading: true
                    font.pixelSize: 30
                    font.letterSpacing: -0.6
                    Layout.fillWidth: true
                    text: updater.state === "checking" ? i18n.tr("Checking for updates…")
                          : updater.state === "installing" ? i18n.tr("Installing updates…")
                          : updater.total === 0 ? i18n.tr("Your system is up to date.")
                          : i18n.plural(updater.total, "{n} update available", "{n} updates available")
                }
                KText {
                    secondary: true
                    Layout.fillWidth: true
                    text: i18n.tr("Updates are never installed without your permission.")
                          + (updater.lastCheck !== "" ? " " + i18n.tr("Last check: {when}.").replace("{when}", updater.lastCheck) : "")
                }
            }
        }

        // ---- barra de andamento da instalação
        Rectangle {
            visible: updater.state === "installing"
            width: parent.width; height: 6; radius: 3; color: Theme.fill
            Rectangle {
                width: parent.width * Math.max(0.03, updater.progress); height: parent.height; radius: 3; color: Theme.ink
                Behavior on width { NumberAnimation { duration: Theme.smooth } }
            }
        }

        // ---- grupos
        Repeater {
            model: updater.groups
            KCard {
                id: card
                width: parent.width
                implicitHeight: col.implicitHeight + Theme.s5 * 2
                property bool open: false
                ColumnLayout {
                    id: col
                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: Theme.s5 }
                    spacing: Theme.s3
                    RowLayout {
                        spacing: Theme.s4
                        Layout.fillWidth: true
                        KIcon { name: modelData.icon; Layout.preferredWidth: 36; Layout.preferredHeight: 36 }
                        ColumnLayout {
                            spacing: 2
                            Layout.fillWidth: true
                            RowLayout {
                                spacing: Theme.s2
                                KText { text: modelData.title; font.pixelSize: 16; font.weight: Font.DemiBold }
                                KChip { text: i18n.plural(modelData.count, "{n} update", "{n} updates") }
                                KChip { visible: modelData.restart; text: i18n.tr("May require a restart") }
                            }
                            KText { text: modelData.description; secondary: true; font.pixelSize: 13; Layout.fillWidth: true }
                        }
                        KButton { text: card.open ? i18n.tr("Hide") : i18n.tr("Details"); kind: "ghost"; compact: true; onClicked: card.open = !card.open }
                        KSwitch {
                            checked: !win.unchecked[modelData.key]
                            enabled: !win.busy
                            onToggled: (on) => { const u = Object.assign({}, win.unchecked); u[modelData.key] = !on; win.unchecked = u }
                        }
                    }
                    Column {
                        visible: card.open
                        Layout.fillWidth: true
                        Layout.leftMargin: 52
                        spacing: 4
                        Repeater {
                            model: modelData.items
                            KText { text: modelData; secondary: true; font.pixelSize: Theme.sizeSmall; font.family: "monospace"; width: parent.width; elide: Text.ElideRight; wrapMode: Text.NoWrap }
                        }
                    }
                }
            }
        }
    }

    // ---------------------------------------------------------------- ações
    Rectangle {
        id: bar
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 80
        color: Theme.paper
        Rectangle { anchors { left: parent.left; right: parent.right; top: parent.top } height: 1; color: Theme.hairline }
        RowLayout {
            anchors { fill: parent; leftMargin: 48; rightMargin: 48 }
            spacing: Theme.s2
            KButton { text: i18n.tr("Check again"); iconName: "view-refresh-symbolic"; enabled: !win.busy; onClicked: updater.check() }
            Item { Layout.fillWidth: true }
            KButton {
                kind: "primary"
                text: updater.state === "installing" ? i18n.tr("Installing…") : i18n.tr("Install updates")
                enabled: !win.busy && updater.total > 0 && win.chosenKeys().length > 0
                progress: updater.state === "installing" ? updater.progress : -1
                onClicked: updater.install(win.chosenKeys())
            }
        }
    }

    KDialog {
        id: restartDialog
        iconName: "system-reboot"
        title: i18n.tr("Restart required")
        message: i18n.tr("Restart the computer to finish.")
        cancelText: i18n.tr("Later")
        confirmText: i18n.tr("Restart now")
        onConfirmed: updater.reboot()
    }
    KDialog {
        id: errorDialog
        iconName: "dialog-warning"
        title: i18n.tr("Something went wrong")
        confirmText: i18n.tr("Close")
    }
    Connections {
        target: updater
        function onRestartNeeded() { restartDialog.open() }
        function onFailed(message, details) { errorDialog.message = message; errorDialog.details = details; errorDialog.open() }
    }
}
