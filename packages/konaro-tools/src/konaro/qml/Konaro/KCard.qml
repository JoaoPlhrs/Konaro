import QtQuick

// Bloco de superfície com contorno fino.
Rectangle {
    color: Theme.surface
    radius: Theme.radiusCard
    border.width: 1
    border.color: Theme.dark ? Theme.hairline : Qt.rgba(0, 0, 0, 0.06)
}
