/*
 * Konaro OS — widget Sistema: três anéis (CPU, memória, disco), no estilo do widget
 * de baterias do macOS. Os dados vêm dos sensores do próprio Plasma.
 */
import QtQuick
import QtQuick.Shapes
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    switchWidth: 0; switchHeight: 0
    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0

    Sensors.Sensor { id: cpu; sensorId: "cpu/all/usage"; updateRateLimit: 2000 }
    Sensors.Sensor { id: mem; sensorId: "memory/physical/usedPercent"; updateRateLimit: 2000 }
    Sensors.Sensor { id: disk; sensorId: "disk/all/usedPercent"; updateRateLimit: 10000 }

    fullRepresentation: Card {
        id: card
        implicitWidth: 170; implicitHeight: 170

        Grid {
            anchors.centerIn: parent
            columns: 2
            spacing: card.width * 0.06
            Ring { label: "CPU"; value: cpu.value; tint: "#0A84FF" }
            Ring { label: root.pt ? "Memória" : "Memory"; value: mem.value; tint: "#30D158" }
            Ring { label: "Disco"; value: disk.value; tint: "#FF9F0A" }
            Item {
                width: card.width * 0.36; height: width
                Text {
                    anchors.centerIn: parent
                    text: root.pt ? "Sistema" : "System"
                    color: card.muted
                    font.pixelSize: card.height * 0.075
                    font.weight: Font.DemiBold
                }
            }
        }
    }

    component Ring: Item {
        id: ring
        property string label
        property real value: 0
        property color tint
        width: 170 * 0.36; height: width
        readonly property real v: Math.max(0, Math.min(100, isNaN(value) ? 0 : value)) / 100
        Shape {
            anchors.fill: parent
            layer.enabled: true; layer.samples: 4
            ShapePath {
                strokeColor: Qt.rgba(ring.tint.r, ring.tint.g, ring.tint.b, 0.2); strokeWidth: ring.width * 0.1
                fillColor: "transparent"; capStyle: ShapePath.RoundCap
                PathAngleArc { centerX: ring.width / 2; centerY: ring.height / 2; radiusX: ring.width * 0.42; radiusY: radiusX; startAngle: 0; sweepAngle: 360 }
            }
            ShapePath {
                strokeColor: ring.tint; strokeWidth: ring.width * 0.1
                fillColor: "transparent"; capStyle: ShapePath.RoundCap
                PathAngleArc { centerX: ring.width / 2; centerY: ring.height / 2; radiusX: ring.width * 0.42; radiusY: radiusX; startAngle: -90; sweepAngle: 360 * ring.v }
            }
        }
        Text {
            anchors.centerIn: parent
            text: Math.round(ring.v * 100) + "%"
            color: ring.tint
            font.pixelSize: ring.width * 0.24
            font.weight: Font.Bold
        }
        Text {
            anchors.top: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            text: ring.label
            font.pixelSize: ring.width * 0.17
            color: "#8E8E93"
        }
    }
}
