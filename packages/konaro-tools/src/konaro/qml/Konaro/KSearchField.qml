import QtQuick
import QtQuick.Controls

// Campo de busca arredondado.
Rectangle {
    id: root
    property alias text: input.text
    property alias placeholder: hint.text
    signal accepted()
    implicitHeight: 38
    implicitWidth: 420
    radius: height / 2
    color: Theme.dark ? Theme.surface : Theme.fill
    border.width: input.activeFocus ? 2 : 1
    border.color: input.activeFocus ? Theme.stone : (Theme.dark ? Theme.hairline : "transparent")

    function focusField() { input.forceActiveFocus() }

    KIcon {
        id: glass
        name: "search"
        tinted: true
        color: Theme.stone
        width: 16; height: 16
        anchors { left: parent.left; leftMargin: 14; verticalCenter: parent.verticalCenter }
    }
    TextField {
        id: input
        anchors { left: glass.right; leftMargin: 8; right: clear.left; rightMargin: 4; verticalCenter: parent.verticalCenter }
        background: null
        color: Theme.ink
        font.family: Theme.body
        font.pixelSize: Theme.sizeBody
        selectByMouse: true
        selectionColor: Theme.ink
        selectedTextColor: Theme.inverse
        padding: 0
        onAccepted: root.accepted()
        Accessible.name: hint.text
        Text {
            id: hint
            visible: input.text === ""
            color: Theme.stone
            font: input.font
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    MouseArea {
        id: clear
        visible: input.text !== ""
        width: visible ? 28 : 0; height: 28
        anchors { right: parent.right; rightMargin: 6; verticalCenter: parent.verticalCenter }
        cursorShape: Qt.PointingHandCursor
        onClicked: input.text = ""
        KIcon { anchors.centerIn: parent; name: "edit-clear"; tinted: true; color: Theme.stone; width: 14; height: 14 }
    }
}
