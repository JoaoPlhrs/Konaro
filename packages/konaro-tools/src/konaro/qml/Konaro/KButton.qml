import QtQuick

// Botão em pílula. kind: "primary" (grafite), "secondary" (preenchido suave),
// "ghost" (sem fundo). `progress` (0..1) mostra o andamento dentro do botão.
Item {
    id: root
    property string text: ""
    property string iconName: ""
    property string kind: "secondary"
    property bool compact: false
    property real progress: -1
    property bool enabled: true
    signal clicked()

    implicitHeight: compact ? 30 : 36
    implicitWidth: Math.max(compact ? 72 : 96, row.implicitWidth + (compact ? 28 : 36))
    opacity: enabled ? 1 : 0.45
    activeFocusOnTab: enabled

    Accessible.role: Accessible.Button
    Accessible.name: text
    Accessible.onPressAction: if (enabled) root.clicked()
    Keys.onSpacePressed: if (enabled) root.clicked()
    Keys.onReturnPressed: if (enabled) root.clicked()

    readonly property color base: kind === "primary" ? Theme.ink
                                 : kind === "secondary" ? Theme.fill : "transparent"
    readonly property color fg: kind === "primary" ? Theme.inverse : Theme.ink

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: height / 2
        color: root.base
        border.width: root.activeFocus ? 2 : 0
        border.color: Theme.stone
        clip: true

        // camada de hover/pressão
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: root.kind === "primary" ? Theme.inverse : Theme.ink
            opacity: mouse.pressed ? 0.16 : mouse.containsMouse ? 0.08 : 0
            Behavior on opacity { NumberAnimation { duration: Theme.quick } }
        }
        // andamento da operação
        Rectangle {
            visible: root.progress >= 0
            anchors { left: parent.left; top: parent.top; bottom: parent.bottom }
            width: parent.width * Math.max(0.04, Math.min(1, root.progress))
            color: root.kind === "primary" ? Theme.inverse : Theme.ink
            opacity: 0.18
            Behavior on width { NumberAnimation { duration: Theme.smooth; easing.type: Easing.OutCubic } }
        }
    }

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 6
        KIcon {
            visible: root.iconName !== ""
            name: root.iconName
            tinted: true
            color: root.fg
            width: 16; height: 16
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: root.text
            color: root.fg
            font.family: Theme.body
            font.pixelSize: root.compact ? Theme.sizeSmall : 13
            font.weight: Font.DemiBold
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    scale: mouse.pressed ? 0.97 : 1
    Behavior on scale { NumberAnimation { duration: Theme.quick } }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.enabled
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
