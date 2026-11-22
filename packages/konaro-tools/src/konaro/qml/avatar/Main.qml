// Meu Avatar — prévia grande à esquerda; à direita, as categorias e as opções de
// cada uma em miniaturas do próprio avatar (como um provador).
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 920
    height: 640
    minimumWidth: 760
    minimumHeight: 540
    visible: true
    color: Theme.paper
    title: i18n.tr("My Avatar")

    property string part: "skin"
    readonly property var current: avatar.parts.find(p => p.id === part)

    Connections {
        target: avatar
        function onSaved() { toast.show(i18n.tr("Saved! Your avatar is now your profile picture."), false, "") }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // ---------------------------------------------------- prévia
        Rectangle {
            Layout.preferredWidth: 360
            Layout.fillHeight: true
            color: Theme.surface
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.hairline }
            ColumnLayout {
                anchors.centerIn: parent
                spacing: Theme.s5
                Image {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 260
                    Layout.preferredHeight: 260
                    sourceSize: Qt.size(520, 520)
                    source: "image://avatar/" + avatar.key
                    cache: false
                    smooth: true
                }
                KText { text: i18n.tr("My Avatar"); heading: true; font.pixelSize: Theme.sizeTitle; Layout.alignment: Qt.AlignHCenter }
                KText {
                    text: i18n.tr("It appears on the login screen, in Start and in Settings.")
                    secondary: true; horizontalAlignment: Text.AlignHCenter
                    Layout.preferredWidth: 280; Layout.alignment: Qt.AlignHCenter
                }
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: Theme.s2
                    KButton { text: i18n.tr("Surprise me"); onClicked: avatar.randomize() }
                    KButton { text: i18n.tr("Use as my picture"); kind: "primary"; onClicked: avatar.save() }
                }
            }
        }

        // ------------------------------------------------- categorias e opções
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Theme.s5
            spacing: Theme.s4

            Flow {
                Layout.fillWidth: true
                spacing: Theme.s2
                Repeater {
                    model: avatar.parts
                    Rectangle {
                        readonly property bool on: win.part === modelData.id
                        width: lbl.implicitWidth + 26; height: 32; radius: 16
                        color: on ? Theme.ink : Theme.fill
                        KText { id: lbl; anchors.centerIn: parent; text: modelData.label; color: parent.on ? Theme.inverse : Theme.ink; font.weight: Font.DemiBold }
                        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.part = modelData.id }
                        Accessible.role: Accessible.PageTab
                        Accessible.name: modelData.label
                    }
                }
            }

            GridView {
                id: grid
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                cellWidth: Math.floor(width / Math.max(3, Math.floor(width / 120)))
                cellHeight: cellWidth
                model: win.current ? win.current.count : 0
                delegate: Item {
                    width: grid.cellWidth; height: grid.cellHeight
                    readonly property bool on: avatar.choice[win.part] === index
                    Rectangle {
                        anchors.fill: parent; anchors.margins: 6
                        radius: 18
                        color: Theme.surface
                        border.width: parent.on ? 3 : 1
                        border.color: parent.on ? Theme.ink : Theme.hairline
                        Image {
                            anchors.fill: parent; anchors.margins: 8
                            sourceSize: Qt.size(220, 220)
                            source: "image://avatar/" + avatar.variant(win.part, index)
                            asynchronous: true
                            smooth: true
                        }
                    }
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: avatar.set(win.part, index) }
                }
            }
        }
    }

    KToast { id: toast }
}
