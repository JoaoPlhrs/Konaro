import QtQuick

// Interruptor liga/desliga.
Item {
    id: root
    property bool checked: false
    signal toggled(bool checked)
    implicitWidth: 42
    implicitHeight: 24
    opacity: enabled ? 1 : 0.4
    activeFocusOnTab: true
    Accessible.role: Accessible.CheckBox
    Accessible.checkable: true
    Accessible.checked: checked
    Keys.onSpacePressed: flip()
    function flip() { checked = !checked; toggled(checked) }

    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: root.checked ? Theme.ink : Theme.fill
        border.width: root.activeFocus ? 2 : (root.checked ? 0 : 1)
        border.color: root.activeFocus ? Theme.stone : Theme.hairline
        Behavior on color { ColorAnimation { duration: Theme.quick } }
        Rectangle {
            width: 18; height: 18; radius: 9
            y: 3
            x: root.checked ? parent.width - width - 3 : 3
            color: root.checked ? Theme.inverse : Theme.surface
            border.width: root.checked ? 0 : 1
            border.color: Theme.hairline
            Behavior on x { NumberAnimation { duration: Theme.quick; easing.type: Easing.OutCubic } }
        }
    }
    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.flip() }
}
