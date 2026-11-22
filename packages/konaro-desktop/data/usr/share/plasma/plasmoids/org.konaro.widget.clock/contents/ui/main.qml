/*
 * Konaro OS — widget Relógio: mostrador analógico branco com os 12 números,
 * ponteiros pretos e ponteiro de segundos laranja, num cartão arredondado.
 */
import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    switchWidth: 0; switchHeight: 0

    property date now: new Date()
    Timer { interval: 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.now = new Date() }

    fullRepresentation: Card {
        id: card
        implicitWidth: 170; implicitHeight: 170

        Item {
            id: face
            anchors.centerIn: parent
            width: Math.min(parent.width, parent.height)
            height: width

            Rectangle {
                anchors.fill: parent
                radius: width / 2
                color: card.dark ? "#1C1C1E" : "#FFFFFF"
                border.color: card.dark ? "#3A3A3C" : "#E5E5EA"
                border.width: 1
            }
            Repeater {   // marcas dos minutos
                model: 60
                Rectangle {
                    readonly property bool hour: index % 5 === 0
                    width: hour ? 0 : 1; height: face.height * 0.03
                    color: card.muted; antialiasing: true
                    x: face.width / 2 - width / 2; y: face.height * 0.03
                    transform: Rotation { origin.x: width / 2; origin.y: face.height / 2 - face.height * 0.03; angle: index * 6 }
                }
            }
            Repeater {   // números 1–12
                model: 12
                Text {
                    readonly property real a: (index + 1) * Math.PI / 6
                    readonly property real rr: face.width * 0.37
                    text: index + 1
                    color: card.ink
                    font.pixelSize: face.width * 0.115
                    font.weight: Font.Medium
                    x: face.width / 2 + Math.sin(a) * rr - width / 2
                    y: face.height / 2 - Math.cos(a) * rr - height / 2
                }
            }
            Hand { length: 0.27; thick: 0.045; handAngle: (root.now.getHours() % 12 + root.now.getMinutes() / 60) * 30; color: card.ink }
            Hand { length: 0.39; thick: 0.032; handAngle: (root.now.getMinutes() + root.now.getSeconds() / 60) * 6; color: card.ink }
            Hand { length: 0.42; thick: 0.012; tail: 0.1; handAngle: root.now.getSeconds() * 6; color: "#FF9500" }
            Rectangle { width: face.width * 0.05; height: width; radius: width / 2; anchors.centerIn: parent; color: "#FF9500" }
            Rectangle { width: face.width * 0.02; height: width; radius: width / 2; anchors.centerIn: parent; color: card.dark ? "#1C1C1E" : "white" }
        }
    }

    component Hand: Rectangle {
        property real length: 0.3
        property real thick: 0.03
        property real tail: 0
        property real handAngle: 0
        width: parent.width * thick
        height: parent.width * (length + tail)
        radius: width / 2
        antialiasing: true
        x: parent.width / 2 - width / 2
        y: parent.height / 2 - parent.width * length
        transform: Rotation { origin.x: width / 2; origin.y: parent.width * length; angle: handAngle }
    }
}
