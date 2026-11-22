import QtQuick
import QtQuick.Layouts

// Título de seção com ação opcional à direita ("Ver tudo").
RowLayout {
    property alias text: title.text
    property string actionText: ""
    signal action()
    spacing: Theme.s3
    KText {
        id: title
        heading: true
        font.pixelSize: Theme.sizeHeading
        Layout.fillWidth: true
    }
    KButton {
        visible: parent.actionText !== ""
        text: parent.actionText
        kind: "ghost"
        compact: true
        onClicked: parent.action()
    }
}
