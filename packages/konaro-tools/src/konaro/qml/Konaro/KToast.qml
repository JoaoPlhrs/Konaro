import QtQuick
import QtQuick.Layouts

// Aviso flutuante na parte de baixo da janela.
Rectangle {
    id: root
    property string text: ""
    property string actionText: ""
    property bool error: false
    signal action()
    function show(message, isError, actionLabel) {
        text = message; error = !!isError; actionText = actionLabel || ""
        opacity = 1; hideTimer.restart()
    }
    implicitHeight: 48
    implicitWidth: Math.min(560, row.implicitWidth + 40)
    radius: height / 2
    color: Theme.dark ? "#F5F5F7" : "#1D1D1F"
    opacity: 0
    visible: opacity > 0
    Behavior on opacity { NumberAnimation { duration: Theme.smooth } }
    Accessible.role: Accessible.AlertMessage
    Accessible.name: text
    Timer { id: hideTimer; interval: root.error ? 9000 : 4500; onTriggered: root.opacity = 0 }
    RowLayout {
        id: row
        anchors.centerIn: parent
        spacing: Theme.s3
        Rectangle { width: 8; height: 8; radius: 4; color: root.error ? Theme.danger : Theme.success }
        Text {
            text: root.text
            color: Theme.dark ? "#161618" : "#FFFFFF"
            font.family: Theme.body
            font.pixelSize: 13
            font.weight: Font.Medium
            elide: Text.ElideRight
            Layout.maximumWidth: 400
        }
        Text {
            visible: root.actionText !== ""
            text: root.actionText
            color: Theme.dark ? "#161618" : "#FFFFFF"
            font.family: Theme.body
            font.pixelSize: 13
            font.weight: Font.Bold
            font.underline: true
            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.action() }
        }
    }
}
