import QtQuick
import QtQuick.Layouts

// Destaque principal: o ícone do app vira uma luz desfocada atrás do título.
// É o único elemento com cor forte na interface — e a cor vem do próprio app.
Rectangle {
    id: root
    property var app: ({})
    property string body: ""
    property string actionText: ""
    property string detailsText: ""
    property real progress: -1
    property bool actionEnabled: true
    signal action()
    signal opened()

    implicitHeight: 300
    radius: Theme.radiusHero
    color: Theme.dark ? Theme.raised : Theme.surface
    border.width: 1
    border.color: Theme.dark ? Theme.hairline : Qt.rgba(0, 0, 0, 0.06)
    clip: true

    Image {
        id: glow
        source: root.app.icon ? "image://glow/" + root.app.icon : ""
        width: 520; height: 520
        anchors { right: parent.right; rightMargin: -60; verticalCenter: parent.verticalCenter }
        opacity: Theme.dark ? 0.6 : 0.5
        smooth: true
        cache: true
    }
    KIcon {
        name: root.app.icon || ""
        width: 136; height: 136
        anchors.centerIn: glow
    }

    ColumnLayout {
        anchors { left: parent.left; leftMargin: Theme.s6 + 8; verticalCenter: parent.verticalCenter }
        width: Math.min(440, root.width * 0.5)
        spacing: Theme.s3
        KText {
            text: root.app.name || ""
            heading: true
            font.pixelSize: 40
            font.letterSpacing: -0.8
            Layout.fillWidth: true
        }
        KText {
            text: root.body
            font.pixelSize: 15
            lineHeight: 1.25
            color: Theme.dark ? Qt.rgba(0.96, 0.96, 0.97, 0.82) : Qt.rgba(0.11, 0.11, 0.12, 0.78)
            Layout.fillWidth: true
        }
        Item { Layout.preferredHeight: Theme.s2 }
        RowLayout {
            spacing: Theme.s2
            KButton { text: root.actionText; kind: "primary"; progress: root.progress; enabled: root.actionEnabled; onClicked: root.action() }
            KButton { text: root.detailsText; kind: "ghost"; onClicked: root.opened() }
        }
    }
}
