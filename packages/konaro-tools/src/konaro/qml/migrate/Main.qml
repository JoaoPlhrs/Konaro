// Migração do Windows — escolhe o que trazer, copia com progresso e mostra onde ficou.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 860
    height: 640
    minimumWidth: 680
    minimumHeight: 520
    visible: true
    color: Theme.paper
    title: i18n.tr("Bring from Windows")

    property var unchecked: ({})
    function chosen() { return migrate.items.map(i => i.id).filter(id => !unchecked[id]) }

    KScrollPage {
        anchors { fill: parent; bottomMargin: bar.height }
        margin: 48

        RowLayout {
            width: parent.width
            spacing: Theme.s5
            Rectangle {
                Layout.preferredWidth: 72; Layout.preferredHeight: 72; radius: 20
                color: Theme.surface; border.color: Theme.hairline
                KIcon { anchors.centerIn: parent; width: 40; height: 40; name: "folder-windows" ; fallback: "drive-harddisk" }
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                KText {
                    heading: true; font.pixelSize: Theme.sizeTitle; Layout.fillWidth: true
                    text: migrate.state === "done" ? i18n.tr("All done!")
                          : migrate.state === "copying" ? i18n.tr("Copying your files…")
                          : migrate.state === "none" ? i18n.tr("No Windows found")
                          : migrate.state === "error" ? i18n.tr("Something went wrong")
                          : migrate.state === "scanning" ? i18n.tr("Looking for Windows…")
                          : i18n.tr("Bring your things from Windows")
                }
                KText {
                    secondary: true; Layout.fillWidth: true
                    text: migrate.state === "choose" ? i18n.tr("Choose what to copy. Windows itself is opened read-only: nothing there is changed or deleted.")
                          : migrate.state === "none" ? i18n.tr("We did not find a Windows installation on this computer. If Windows is on another drive, connect it and try again.")
                          : migrate.state === "error" ? migrate.message
                          : migrate.state === "done" ? i18n.tr("Your files are in a “Do Windows” folder inside Documents, Pictures, Music and the other folders. Bookmarks are in Documents, ready to import in your browser.")
                          : migrate.state === "copying" ? migrate.status
                          : i18n.tr("This takes only a moment.")
                }
            }
        }

        // lista do que dá para trazer
        Repeater {
            model: migrate.state === "choose" ? migrate.items : []
            KCard {
                width: parent.width
                height: 68
                readonly property bool on: !win.unchecked[modelData.id]
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16; anchors.rightMargin: 16
                    spacing: Theme.s4
                    KIcon { Layout.preferredWidth: 36; Layout.preferredHeight: 36; name: modelData.icon }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0
                        KText { text: modelData.name; font.weight: Font.DemiBold }
                        KText { text: modelData.detail; secondary: true; font.pixelSize: Theme.sizeSmall }
                    }
                    KSwitch {
                        checked: parent.parent.on
                        onToggled: (value) => { const u = Object.assign({}, win.unchecked); u[modelData.id] = !value; win.unchecked = u }
                    }
                }
            }
        }

        // progresso
        Rectangle {
            visible: migrate.state === "copying" || migrate.state === "scanning"
            width: parent.width; height: 8; radius: 4
            color: Theme.fill
            Rectangle {
                width: migrate.state === "copying" ? parent.width * Math.max(0.02, migrate.progress / 100) : parent.width * 0.3
                height: parent.height; radius: 4; color: Theme.ink
                Behavior on width { NumberAnimation { duration: Theme.smooth } }
            }
        }

        KCard {
            visible: migrate.state === "done"
            width: parent.width
            height: 80
            RowLayout {
                anchors.fill: parent; anchors.margins: 16
                KIcon { Layout.preferredWidth: 36; Layout.preferredHeight: 36; name: "emblem-ok-symbolic"; tinted: true }
                KText {
                    Layout.fillWidth: true
                    text: i18n.tr("{n} files copied.").replace("{n}", migrate.result.copied || 0)
                          + (migrate.result.skipped ? " " + i18n.tr("{n} could not be read and were skipped.").replace("{n}", migrate.result.skipped) : "")
                }
            }
        }
    }

    // barra inferior
    Rectangle {
        id: bar
        anchors.bottom: parent.bottom
        width: parent.width
        height: 72
        color: Theme.surface
        Rectangle { width: parent.width; height: 1; color: Theme.hairline }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 48; anchors.rightMargin: 48
            KText {
                Layout.fillWidth: true
                secondary: true
                text: migrate.state === "choose" && migrate.users.length ? i18n.tr("Windows user") + ": " + migrate.users[0] : ""
            }
            KButton {
                visible: migrate.state === "none" || migrate.state === "error"
                text: i18n.tr("Try again")
                onClicked: migrate.scan()
            }
            KButton {
                visible: migrate.state === "done"
                text: i18n.tr("Open my files")
                onClicked: migrate.openFiles()
            }
            KButton {
                visible: migrate.state === "choose"
                kind: "primary"
                text: i18n.tr("Copy")
                enabled: win.chosen().length > 0
                onClicked: migrate.start(win.chosen())
            }
            KButton {
                visible: migrate.state === "done"
                kind: "primary"
                text: i18n.tr("Close")
                onClicked: Qt.quit()
            }
        }
    }
}
