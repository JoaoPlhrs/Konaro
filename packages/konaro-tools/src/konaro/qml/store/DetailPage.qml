// Loja Konaro — página de um app.
import QtQuick
import QtQuick.Layouts
import Konaro

KScrollPage {
    id: root
    property var ctl
    property var app: null
    property var permissions: []
    property bool permissionsLoaded: false

    Connections {
        target: store
        function onPermissionsReady(id, perms) {
            if (root.app && id === root.app.id) { root.permissions = perms; root.permissionsLoaded = true }
        }
    }
    onAppChanged: if (app && app.backend !== "flatpak") permissionsLoaded = false

    KButton {
        text: i18n.tr("Back")
        iconName: "go-previous-symbolic"
        kind: "ghost"
        compact: true
        onClicked: root.ctl.page = root.ctl.pageBeforeDetail
    }

    // ---------------------------------------------------- cabeçalho com a luz do ícone
    Rectangle {
        width: parent.width
        height: 196
        radius: Theme.radiusHero
        color: Theme.dark ? Theme.raised : Theme.surface
        border.width: 1
        border.color: Theme.dark ? Theme.hairline : Qt.rgba(0, 0, 0, 0.06)
        clip: true
        Image {
            source: root.app ? "image://glow/" + root.app.icon : ""
            width: 400; height: 400
            x: -110; anchors.verticalCenter: parent.verticalCenter
            opacity: Theme.dark ? 0.55 : 0.42
        }
        RowLayout {
            anchors { fill: parent; leftMargin: Theme.s6; rightMargin: Theme.s6 }
            spacing: Theme.s5
            KIcon { name: root.app ? root.app.icon : ""; Layout.preferredWidth: 104; Layout.preferredHeight: 104 }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Theme.s2
                KText { text: root.app ? root.app.name : ""; heading: true; font.pixelSize: Theme.sizeHero; font.letterSpacing: -0.7; Layout.fillWidth: true }
                KText { text: root.app ? root.app.summaryText : ""; secondary: true; font.pixelSize: 15; Layout.fillWidth: true }
                Row {
                    spacing: Theme.s2
                    KChip { text: root.app ? root.app.originText : "" }
                    KChip { text: root.app ? root.app.categoryText : "" }
                }
            }
            ColumnLayout {
                spacing: Theme.s2
                KButton {
                    Layout.preferredWidth: 150
                    kind: "primary"
                    text: root.ctl.actionLabel(root.app)
                    enabled: root.ctl.actionEnabled(root.app)
                    progress: root.ctl.progressFor(root.app)
                    onClicked: root.ctl.primaryAction(root.app)
                }
                KButton {
                    visible: root.app && root.app.state === "installed"
                    Layout.preferredWidth: 150
                    kind: "ghost"
                    text: i18n.tr("Remove")
                    enabled: store.busyId === ""
                    onClicked: root.ctl.askRemove(root.app)
                }
            }
        }
    }

    // ---------------------------------------------------- informações
    RowLayout {
        width: parent.width
        spacing: Theme.s5

        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignTop
            spacing: Theme.s3
            KText { text: i18n.tr("About this app"); heading: true; font.pixelSize: Theme.sizeHeading }
            KText {
                text: root.app ? root.app.summaryText : ""
                lineHeight: 1.3
                font.pixelSize: 15
                Layout.fillWidth: true
            }
            KText {
                text: root.app && root.app.backend === "flatpak"
                      ? i18n.tr("This app runs isolated from the rest of the system (Flatpak) and only reaches what its permissions allow.")
                      : i18n.tr("This app is a Debian package, installed and updated together with the system.")
                secondary: true
                lineHeight: 1.25
                Layout.fillWidth: true
            }
        }

        KCard {
            Layout.preferredWidth: 340
            Layout.alignment: Qt.AlignTop
            implicitHeight: info.implicitHeight + Theme.s5 * 2
            ColumnLayout {
                id: info
                anchors { fill: parent; margins: Theme.s5 }
                spacing: Theme.s3
                component Field: ColumnLayout {
                    property string label
                    property string value
                    spacing: 2
                    Layout.fillWidth: true
                    KText { text: parent.label; secondary: true; font.pixelSize: Theme.sizeSmall }
                    KText { text: parent.value; Layout.fillWidth: true }
                }
                Field { label: i18n.tr("Source"); value: root.app ? root.app.originText : "" }
                Field { label: i18n.tr("Format"); value: root.app ? root.app.formatText : "" }
                Field { label: i18n.tr("Category"); value: root.app ? root.app.categoryText : "" }
                Field {
                    label: i18n.tr("Permissions")
                    value: !root.app ? ""
                           : root.app.backend !== "flatpak" ? i18n.tr("Same as your user account")
                           : !root.permissionsLoaded ? i18n.tr("Loading permissions…")
                           : root.permissions.join("\n")
                }
            }
        }
    }
}
