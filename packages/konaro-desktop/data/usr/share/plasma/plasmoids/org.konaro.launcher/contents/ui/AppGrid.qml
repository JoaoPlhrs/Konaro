import QtQuick
import org.kde.kirigami as Kirigami

// Grade de apps do Iniciar: ícone grande com o nome embaixo, realce suave ao passar o
// mouse ou com o teclado. Não rola sozinha (a rolagem é da página inteira).
GridView {
    id: grid
    property int columns: 6
    property int cell: 118
    property int iconSize: 64
    property int maxRows: -1
    signal launch(var model, int index)

    width: columns * cell
    readonly property int rows: Math.ceil(count / columns)
    height: (maxRows > 0 ? Math.min(rows, maxRows) : rows) * cell
    cellWidth: cell
    cellHeight: cell
    interactive: false
    keyNavigationEnabled: true
    currentIndex: -1
    highlightFollowsCurrentItem: true
    highlight: Rectangle { radius: 18; color: Qt.rgba(1, 1, 1, 0.16); visible: grid.activeFocus }
    highlightMoveDuration: 0

    Keys.onReturnPressed: if (currentIndex >= 0) grid.launch(grid.model, currentIndex)
    Keys.onEnterPressed: if (currentIndex >= 0) grid.launch(grid.model, currentIndex)

    delegate: Item {
        width: grid.cell
        height: grid.cell
        Rectangle {
            anchors.fill: parent
            anchors.margins: 4
            radius: 18
            color: hover.hovered ? Qt.rgba(1, 1, 1, 0.12) : "transparent"
        }
        HoverHandler { id: hover }
        Kirigami.Icon {
            id: icon
            width: grid.iconSize
            height: width
            anchors.horizontalCenter: parent.horizontalCenter
            y: parent.height * 0.12
            source: model.decoration
            scale: tap.pressed ? 0.92 : 1
            Behavior on scale { NumberAnimation { duration: 90 } }
        }
        Text {
            anchors.top: icon.bottom
            anchors.topMargin: 8
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 12
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            maximumLineCount: 1
            text: model.display || ""
            color: "white"
            font.pixelSize: 13
            style: Text.Raised
            styleColor: Qt.rgba(0, 0, 0, 0.35)
        }
        MouseArea {
            id: tap
            anchors.fill: parent
            onClicked: grid.launch(grid.model, index)
        }
    }
}
