// Ajuda Konaro — "Onde está…?": o nome que a pessoa conhece do Windows e onde fica no
// Konaro, com botão para abrir. Também atalhos de teclado e perguntas frequentes.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 980
    height: 700
    minimumWidth: 720
    minimumHeight: 520
    visible: true
    color: Theme.paper
    title: i18n.tr("Konaro Help")

    property string tab: "where"
    readonly property string query: search.text.trim().toLowerCase()
    function matches(item) {
        if (!query) return true
        const hay = (item.known + " " + item.konaro + " " + item.how).toLowerCase()
        return query.split(/\s+/).every(w => hay.indexOf(w) !== -1)
    }
    readonly property var places: helpApp.places.filter(matches)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0

        // ------------------------------------------------------------ cabeçalho
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: header.implicitHeight + 56
            color: Theme.surface
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.hairline }
            ColumnLayout {
                id: header
                anchors.centerIn: parent
                width: Math.min(parent.width - 64, 720)
                spacing: Theme.s3
                KText { text: i18n.tr("Where is…?"); heading: true; font.pixelSize: Theme.sizeHero; Layout.alignment: Qt.AlignHCenter }
                KText {
                    text: i18n.tr("Type the name you know from Windows and see where it is in Konaro.")
                    secondary: true; Layout.alignment: Qt.AlignHCenter
                }
                KSearchField {
                    id: search
                    Layout.fillWidth: true
                    Layout.preferredHeight: 44
                    placeholder: i18n.tr("e.g. Control Panel, Task Manager, Notepad…")
                    text: initialSearch
                    Component.onCompleted: focusField()
                }
                Row {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: Theme.s2
                    Repeater {
                        model: [{ id: "where", label: i18n.tr("Where is it") },
                                { id: "keys", label: i18n.tr("Keyboard shortcuts") },
                                { id: "faq", label: i18n.tr("Questions") }]
                        Rectangle {
                            readonly property bool on: win.tab === modelData.id
                            width: label.implicitWidth + 28; height: 32; radius: 16
                            color: on ? Theme.ink : Theme.fill
                            KText { id: label; anchors.centerIn: parent; text: modelData.label; color: parent.on ? Theme.inverse : Theme.ink; font.weight: Font.DemiBold }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.tab = modelData.id }
                            Accessible.role: Accessible.PageTab
                            Accessible.name: modelData.label
                        }
                    }
                }
            }
        }

        // ------------------------------------------------------------- conteúdo
        KScrollPage {
            Layout.fillWidth: true
            Layout.fillHeight: true
            margin: 32

            // Onde está…?
            Repeater {
                model: win.tab === "where" ? win.places : []
                KCard {
                    width: parent.width
                    height: row.implicitHeight + 32
                    RowLayout {
                        id: row
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: Theme.s4
                        Rectangle {
                            Layout.preferredWidth: 52; Layout.preferredHeight: 52; radius: 14
                            color: Theme.fill
                            KIcon { anchors.centerIn: parent; width: 32; height: 32; name: modelData.icon }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            KText { text: modelData.known; secondary: true; font.pixelSize: Theme.sizeSmall }
                            KText { text: "→ " + modelData.konaro; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeHeading; Layout.fillWidth: true }
                            KText { text: modelData.how; secondary: true; Layout.fillWidth: true }
                        }
                        KButton {
                            visible: modelData.action !== ""
                            text: i18n.tr("Open")
                            kind: "primary"
                            compact: true
                            onClicked: helpApp.open(modelData.action)
                        }
                    }
                }
            }
            KText {
                visible: win.tab === "where" && win.places.length === 0
                text: i18n.tr("Nothing found. Try another word, or search in Start (Windows key).")
                secondary: true
            }

            // Atalhos
            KCard {
                visible: win.tab === "keys"
                width: parent.width
                height: keys.implicitHeight + 24
                Column {
                    id: keys
                    anchors.fill: parent
                    anchors.margins: 12
                    Repeater {
                        model: helpApp.shortcuts
                        RowLayout {
                            width: keys.width
                            height: 44
                            Rectangle {
                                Layout.preferredWidth: keyText.implicitWidth + 20; Layout.preferredHeight: 28; radius: 7
                                color: Theme.fill; border.color: Theme.hairline
                                KText { id: keyText; anchors.centerIn: parent; text: modelData.keys; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeSmall }
                            }
                            KText { text: modelData.what; Layout.fillWidth: true; Layout.leftMargin: Theme.s3 }
                        }
                    }
                }
            }

            // Perguntas frequentes
            Repeater {
                model: win.tab === "faq" ? helpApp.faq : []
                KCard {
                    width: parent.width
                    height: qa.implicitHeight + 32
                    Column {
                        id: qa
                        x: 16; y: 16
                        width: parent.width - 32
                        spacing: Theme.s2
                        KText { text: modelData.q; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeHeading; width: parent.width }
                        KText { text: modelData.a; secondary: true; width: parent.width }
                    }
                }
            }
        }
    }
}
