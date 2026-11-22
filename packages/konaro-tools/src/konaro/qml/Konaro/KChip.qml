import QtQuick

// Etiqueta pequena (origem, formato).
Rectangle {
    property alias text: label.text
    implicitHeight: 22
    implicitWidth: label.implicitWidth + 16
    radius: height / 2
    color: "transparent"
    border.width: 1
    border.color: Theme.hairline
    Text {
        id: label
        anchors.centerIn: parent
        color: Theme.stone
        font.family: Theme.body
        font.pixelSize: Theme.sizeTiny
        font.weight: Font.Medium
    }
}
