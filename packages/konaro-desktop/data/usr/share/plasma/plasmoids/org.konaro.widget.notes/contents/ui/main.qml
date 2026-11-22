/*
 * Konaro OS — widget Notas: título em amarelo e uma nota que se edita direto no
 * cartão. O texto fica salvo na configuração do widget.
 */
import QtQuick
import QtQuick.Controls as QQC2
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    switchWidth: 0; switchHeight: 0
    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0

    fullRepresentation: Card {
        id: card
        implicitWidth: 170; implicitHeight: 170

        Row {
            id: head
            spacing: 6
            Rectangle { width: 4; height: title.height; radius: 2; color: "#FFCC00" }
            Text {
                id: title
                text: root.pt ? "Notas" : "Notes"
                color: "#E5A800"
                font.pixelSize: Math.max(11, card.height * 0.085)
                font.weight: Font.Bold
            }
        }
        QQC2.TextArea {
            anchors.top: head.bottom
            anchors.topMargin: 6
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            padding: 0
            background: Item {}
            wrapMode: TextEdit.Wrap
            color: card.ink
            placeholderText: root.pt ? "Escreva um lembrete…" : "Write a reminder…"
            placeholderTextColor: card.muted
            font.pixelSize: Math.max(11, card.height * 0.08)
            text: Plasmoid.configuration.text
            onTextChanged: if (text !== Plasmoid.configuration.text) Plasmoid.configuration.text = text
        }
    }
}
