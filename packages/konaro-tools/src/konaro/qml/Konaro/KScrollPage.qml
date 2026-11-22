import QtQuick
import QtQuick.Controls

// Página rolável com margens padrão.
Flickable {
    id: root
    default property alias content: column.data
    property int margin: Theme.s6
    contentWidth: width
    contentHeight: column.implicitHeight + margin * 2
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
    Column {
        id: column
        x: root.margin
        y: root.margin
        width: root.width - root.margin * 2
        spacing: Theme.s5
    }
}
