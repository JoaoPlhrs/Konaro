// Restaurar o Konaro — três opções, da mais leve à mais forte, cada uma com confirmação.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 760
    height: 600
    minimumWidth: 620
    minimumHeight: 520
    visible: true
    color: Theme.paper
    title: i18n.tr("Restore Konaro")

    Connections {
        target: restore
        function onMessage(text, isError) { toast.show(text, isError, "") }
    }

    KScrollPage {
        anchors.fill: parent
        margin: 40

        KText { text: i18n.tr("Restore Konaro"); heading: true; font.pixelSize: Theme.sizeHero }
        KText {
            width: parent.width; secondary: true
            text: i18n.tr("Fix the system without losing your files. Start with the lightest option.")
        }

        Repeater {
            model: [
                { id: "settings", title: i18n.tr("Restore my settings"), icon: "edit-reset",
                  text: i18n.tr("Appearance, desktop, shortcuts and app settings go back to the default. Your current settings are saved in a folder, and your files are not touched. Logs you out."),
                  button: i18n.tr("Restore settings"), enabled: true },
                { id: "time", title: i18n.tr("Back in Time"), icon: "timeshift",
                  text: i18n.tr("Go back to how the system was on a recent day or before an update."),
                  button: i18n.tr("Open Back in Time"), enabled: true },
                { id: "factory", title: i18n.tr("Restore to factory state"), icon: "system-reboot",
                  text: restore.factoryAvailable
                        ? i18n.tr("The system goes back to how it was right after installation. Documents, photos and downloads stay; apps installed later are removed. Restarts the computer.")
                        : i18n.tr("Available on systems installed with Btrfs (the Konaro default), after the first restore point."),
                  button: i18n.tr("Restore to factory"), enabled: restore.factoryAvailable }
            ]
            KCard {
                width: parent.width
                height: row.implicitHeight + 36
                opacity: modelData.enabled ? 1 : 0.6
                RowLayout {
                    id: row
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: Theme.s4
                    KIcon { name: modelData.icon; Layout.preferredWidth: 40; Layout.preferredHeight: 40; Layout.alignment: Qt.AlignTop }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        KText { text: modelData.title; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeHeading; Layout.fillWidth: true }
                        KText { text: modelData.text; secondary: true; Layout.fillWidth: true }
                    }
                    KButton {
                        text: modelData.button
                        enabled: modelData.enabled
                        kind: modelData.id === "factory" ? "secondary" : "primary"
                        onClicked: {
                            if (modelData.id === "time") { restore.openTimeMachine(); return }
                            confirm.action = modelData.id
                            confirm.title = modelData.title + "?"
                            confirm.message = modelData.text
                            confirm.confirmText = modelData.button
                            confirm.open()
                        }
                    }
                }
            }
        }
    }

    KDialog {
        id: confirm
        property string action: ""
        onConfirmed: action === "settings" ? restore.resetSettings() : restore.factoryRestore()
    }
    KToast { id: toast }
}
