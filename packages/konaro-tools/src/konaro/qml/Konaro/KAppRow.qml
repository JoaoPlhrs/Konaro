import QtQuick
import QtQuick.Layouts

// Linha de app para listas e grades (categorias, busca, biblioteca).
Item {
    id: root
    property var app: ({})
    property string actionText: ""
    property real progress: -1
    property bool actionEnabled: true
    property string note: ""
    signal opened()
    signal action()
    implicitHeight: 84

    Rectangle {
        anchors.fill: parent
        radius: Theme.radiusCard
        color: mouse.containsMouse ? (Theme.dark ? Theme.raised : Theme.surface) : "transparent"
        border.width: mouse.containsMouse ? 1 : 0
        border.color: Theme.dark ? Theme.hairline : Qt.rgba(0, 0, 0, 0.06)
        Behavior on color { ColorAnimation { duration: Theme.quick } }
    }
    MouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.opened() }
    RowLayout {
        anchors { fill: parent; leftMargin: Theme.s3; rightMargin: Theme.s3 }
        spacing: Theme.s4
        KIcon { name: root.app.icon || ""; Layout.preferredWidth: 48; Layout.preferredHeight: 48 }
        ColumnLayout {
            spacing: 2
            Layout.fillWidth: true
            KText { text: root.app.name || ""; font.pixelSize: 15; font.weight: Font.DemiBold; elide: Text.ElideRight; maximumLineCount: 1; Layout.fillWidth: true }
            KText { text: root.app.summaryText || ""; secondary: true; font.pixelSize: Theme.sizeSmall; maximumLineCount: 1; elide: Text.ElideRight; Layout.fillWidth: true }
            KText { visible: text !== ""; text: root.note || root.app.originText || ""; secondary: true; font.pixelSize: Theme.sizeTiny; Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 1 }
        }
        KButton {
            text: root.actionText
            compact: true
            progress: root.progress
            enabled: root.actionEnabled
            onClicked: root.action()
        }
    }
}
