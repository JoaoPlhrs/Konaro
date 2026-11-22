import QtQuick
import org.kde.kirigami as Kirigami

// Cartão dos widgets do Konaro: quadrado de cantos bem arredondados, sombra suave,
// claro ou escuro conforme o tema (a mesma base em todos os widgets).
Item {
    id: card
    default property alias content: inner.data
    readonly property bool dark: Kirigami.Theme.backgroundColor.hslLightness < 0.5
    readonly property color ink: dark ? "#F5F5F7" : "#1D1D1F"
    readonly property color muted: dark ? "#98989D" : "#6E6E73"
    readonly property color accent: "#FF3B30"
    readonly property real r: Math.min(width, height) * 0.13

    // sombra suave feita com camadas translúcidas (funciona com e sem aceleração 3D)
    Repeater {
        model: 4
        Rectangle {
            anchors.fill: shape
            anchors.margins: -index * 1.5
            anchors.topMargin: -index * 1.5 + 2 + index
            radius: shape.radius + index * 1.5
            color: "transparent"
            border.width: 1.5
            border.color: Qt.rgba(0, 0, 0, 0.07 - index * 0.015)
        }
    }
    Rectangle {
        id: shape
        anchors.fill: parent
        anchors.margins: 6
        radius: card.r
        color: card.dark ? Qt.rgba(0.11, 0.11, 0.12, 0.92) : Qt.rgba(1, 1, 1, 0.94)
        border.color: card.dark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(0, 0, 0, 0.06)
    }
    Item {
        id: inner
        anchors.fill: shape
        anchors.margins: shape.radius * 0.55
    }
}
