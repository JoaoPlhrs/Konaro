import QtQuick
import QtQuick.Layouts

// Cartão vertical de app, usado nas fileiras da página inicial.
Item {
    id: root
    property var app: ({})
    property string actionText: ""
    property real progress: -1
    property bool actionEnabled: true
    signal opened()
    signal action()
    implicitWidth: 196
    implicitHeight: 232

    KCard {
        id: card
        anchors.fill: parent
        radius: Theme.radiusBlock
        color: mouse.containsMouse ? (Theme.dark ? Theme.raised : Theme.surface) : Theme.surface
        border.color: mouse.containsMouse ? Theme.hairline : (Theme.dark ? Theme.hairline : Qt.rgba(0, 0, 0, 0.06))
    }
    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.opened()
    }
    ColumnLayout {
        anchors { fill: parent; margins: Theme.s4 }
        spacing: Theme.s1
        KIcon { name: root.app.icon || ""; Layout.preferredWidth: 60; Layout.preferredHeight: 60 }
        Item { Layout.preferredHeight: Theme.s2 }
        KText {
            text: root.app.name || ""
            font.pixelSize: 15
            font.weight: Font.DemiBold
            elide: Text.ElideRight
            maximumLineCount: 1
            Layout.fillWidth: true
        }
        KText {
            text: root.app.summaryText || ""
            secondary: true
            font.pixelSize: Theme.sizeSmall
            maximumLineCount: 2
            elide: Text.ElideRight
            lineHeight: 1.15
            Layout.fillWidth: true
        }
        Item { Layout.fillHeight: true }
        KButton {
            text: root.actionText
            kind: "secondary"
            compact: true
            progress: root.progress
            enabled: root.actionEnabled
            onClicked: root.action()
        }
    }
}
