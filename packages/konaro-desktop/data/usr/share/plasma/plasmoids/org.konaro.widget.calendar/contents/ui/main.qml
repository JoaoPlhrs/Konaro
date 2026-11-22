/*
 * Konaro OS — widget Calendário (tamanho médio): à esquerda o dia da semana em
 * vermelho e o número do dia grande; à direita o mês, com o dia de hoje marcado.
 */
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    switchWidth: 0; switchHeight: 0

    property date today: new Date()
    Timer { interval: 60000; running: true; repeat: true; onTriggered: root.today = new Date() }

    readonly property var loc: Qt.locale()
    // segunda-feira primeiro em pt_BR? O Brasil usa domingo; seguimos o idioma do sistema.
    readonly property int firstDay: loc.firstDayOfWeek % 7

    function cells() {
        var y = today.getFullYear(), m = today.getMonth()
        var first = new Date(y, m, 1)
        var offset = (first.getDay() - firstDay + 7) % 7
        var days = new Date(y, m + 1, 0).getDate()
        var out = []
        for (var i = 0; i < offset; i++) out.push(0)
        for (var d = 1; d <= days; d++) out.push(d)
        while (out.length % 7) out.push(0)
        return out
    }

    fullRepresentation: Card {
        id: card
        implicitWidth: 360; implicitHeight: 170

        RowLayout {
            anchors.fill: parent
            spacing: parent.width * 0.06

            ColumnLayout {
                Layout.preferredWidth: parent.width * 0.34
                Layout.fillHeight: true
                spacing: 0
                Text {
                    text: root.loc.toString(root.today, "dddd").toUpperCase()
                    color: card.accent
                    font.pixelSize: card.height * 0.085
                    font.weight: Font.Bold
                    font.letterSpacing: 0.5
                }
                Text {
                    text: root.today.getDate()
                    color: card.ink
                    font.family: "Inter Display"
                    font.pixelSize: card.height * 0.36
                    font.weight: Font.Normal
                    Layout.topMargin: -card.height * 0.03
                }
                Item { Layout.fillHeight: true }
                Text {
                    text: Qt.locale().name.indexOf("pt") === 0 ? "Sem eventos hoje" : "No events today"
                    color: card.muted
                    font.pixelSize: card.height * 0.072
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: card.height * 0.01
                Text {
                    text: root.loc.toString(root.today, "MMMM").toUpperCase()
                    color: card.accent
                    font.pixelSize: card.height * 0.075
                    font.weight: Font.Bold
                }
                Grid {
                    id: grid
                    columns: 7
                    Layout.fillWidth: true
                    readonly property real cw: width / 7
                    Repeater {
                        model: 7
                        Text {
                            width: grid.cw
                            horizontalAlignment: Text.AlignHCenter
                            text: root.loc.dayName((index + root.firstDay) % 7, Locale.NarrowFormat).toUpperCase()
                            color: card.muted
                            font.pixelSize: card.height * 0.062
                            font.weight: Font.DemiBold
                        }
                    }
                    Repeater {
                        model: root.cells()
                        Item {
                            width: grid.cw
                            height: card.height * 0.105
                            readonly property bool isToday: modelData === root.today.getDate()
                            Rectangle {
                                anchors.centerIn: parent
                                width: Math.min(parent.width, parent.height) * 1.05
                                height: width; radius: width / 2
                                color: card.accent
                                visible: parent.isToday
                            }
                            Text {
                                anchors.centerIn: parent
                                text: modelData > 0 ? modelData : ""
                                color: parent.isToday ? "white" : card.ink
                                font.pixelSize: card.height * 0.066
                                font.weight: parent.isToday ? Font.Bold : Font.Medium
                            }
                        }
                    }
                }
                Item { Layout.fillHeight: true }
            }
        }
    }
}
