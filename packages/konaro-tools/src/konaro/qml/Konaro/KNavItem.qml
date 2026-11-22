import QtQuick

// Item do trilho lateral: ícone + nome; o selecionado ganha fundo e uma barra à esquerda.
Item {
    id: root
    property string text: ""
    property string iconName: ""
    property bool selected: false
    property string badge: ""
    signal clicked()
    implicitHeight: 38
    implicitWidth: 200
    activeFocusOnTab: true
    Accessible.role: Accessible.PageTab
    Accessible.name: text
    Accessible.selected: selected
    Keys.onSpacePressed: root.clicked()
    Keys.onReturnPressed: root.clicked()

    Rectangle {
        anchors.fill: parent
        radius: Theme.radiusControl
        color: root.selected ? (Theme.dark ? Theme.raised : Theme.surface)
                             : (mouse.containsMouse ? Theme.fill : "transparent")
        border.width: root.activeFocus ? 2 : 0
        border.color: Theme.stone
        Behavior on color { ColorAnimation { duration: Theme.quick } }
    }
    Rectangle {
        visible: root.selected
        width: 3; height: 16; radius: 2
        color: Theme.ink
        anchors { left: parent.left; leftMargin: 4; verticalCenter: parent.verticalCenter }
    }
    KIcon {
        id: icon
        name: root.iconName
        tinted: true
        width: 18; height: 18
        anchors { left: parent.left; leftMargin: 16; verticalCenter: parent.verticalCenter }
    }
    KText {
        text: root.text
        anchors { left: icon.right; leftMargin: 12; right: badgeText.left; verticalCenter: parent.verticalCenter }
        font.weight: root.selected ? Font.DemiBold : Font.Normal
        elide: Text.ElideRight
        wrapMode: Text.NoWrap
    }
    KText {
        id: badgeText
        text: root.badge
        secondary: true
        font.pixelSize: Theme.sizeSmall
        anchors { right: parent.right; rightMargin: 12; verticalCenter: parent.verticalCenter }
    }
    MouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.clicked() }
}
