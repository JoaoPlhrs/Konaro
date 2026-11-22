// Meu Avatar — o palco com o personagem à esquerda; à direita, as abas (Pele, Cabelo,
// Olhos…) e as opções de cada uma. Cores aparecem como amostras redondas; formatos
// aparecem como miniaturas ampliadas só da parte que muda (os olhos, a boca…).
// A escolhida tem anel escuro e um visto. As imagens são desenhadas em segundo plano.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 1000
    height: 660
    minimumWidth: 820
    minimumHeight: 560
    visible: true
    color: Theme.paper
    title: i18n.tr("My Avatar")

    property string tabId: startTab || "skin"
    readonly property var tab: avatar.tabs.find(t => t.id === tabId) || avatar.tabs[0]

    Connections {
        target: avatar
        function onSaved() { toast.show(i18n.tr("Saved. Your avatar is now your profile picture."), false, "") }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // ------------------------------------------------------------- palco
        Rectangle {
            Layout.preferredWidth: 380
            Layout.fillHeight: true
            color: Theme.surface
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.hairline }

            ColumnLayout {
                anchors.centerIn: parent
                width: parent.width - 64
                spacing: Theme.s4

                Item {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 280
                    Layout.preferredHeight: 280
                    Image {
                        id: stage
                        width: 280; height: 280
                        sourceSize: Qt.size(560, 560)
                        source: "image://avatar/full/" + avatar.key
                        asynchronous: true
                        retainWhileLoading: true
                        smooth: true
                        mipmap: true
                    }
                }
                KText {
                    text: i18n.tr("My Avatar"); heading: true; font.pixelSize: Theme.sizeTitle
                    Layout.alignment: Qt.AlignHCenter
                }
                KText {
                    text: i18n.tr("It appears on the login screen, in Start and in Settings.")
                    secondary: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: Theme.s2
                    KButton { text: i18n.tr("Surprise me"); onClicked: avatar.randomize() }
                    KButton { text: i18n.tr("Use as my picture"); kind: "primary"; onClicked: avatar.save() }
                }
            }
        }

        // ----------------------------------------------------------- opções
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // abas
            Flow {
                Layout.fillWidth: true
                Layout.margins: Theme.s5
                Layout.bottomMargin: Theme.s3
                spacing: Theme.s2
                Repeater {
                    model: avatar.tabs
                    Rectangle {
                        readonly property bool on: win.tabId === modelData.id
                        width: lbl.implicitWidth + 28; height: 34; radius: 17
                        color: on ? Theme.ink : (hover.hovered ? Theme.hairline : Theme.fill)
                        HoverHandler { id: hover }
                        KText {
                            id: lbl; anchors.centerIn: parent; text: modelData.label
                            color: parent.on ? Theme.inverse : Theme.ink; font.weight: Font.DemiBold
                        }
                        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.tabId = modelData.id }
                        Accessible.role: Accessible.PageTab
                        Accessible.name: modelData.label
                        Accessible.selected: on
                    }
                }
            }
            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.hairline }

            // seções da aba (formato e/ou cor)
            Flickable {
                id: page
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentHeight: sections.implicitHeight + 48
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                Column {
                    id: sections
                    x: Theme.s5; y: Theme.s5
                    width: page.width - Theme.s5 * 2
                    spacing: Theme.s5

                    Repeater {
                        model: win.tab.sections
                        Column {
                            id: section
                            readonly property var info: modelData
                            width: sections.width
                            spacing: Theme.s3

                            KText { text: section.info.label; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeHeading }

                            // amostras de cor
                            Flow {
                                visible: section.info.kind === "color"
                                width: parent.width
                                spacing: Theme.s3
                                Repeater {
                                    model: section.info.kind === "color" ? section.info.colors : []
                                    Item {
                                        readonly property bool on: avatar.choice[section.info.part] === index
                                        width: 52; height: 52
                                        Rectangle {   // anel de seleção
                                            anchors.fill: parent
                                            radius: width / 2
                                            color: "transparent"
                                            border.width: 3
                                            border.color: parent.on ? Theme.ink : "transparent"
                                        }
                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: 40; height: 40; radius: 20
                                            color: modelData
                                            border.width: 1
                                            border.color: Qt.rgba(0, 0, 0, 0.12)
                                            scale: swatchHover.hovered && !parent.on ? 1.06 : 1
                                            Behavior on scale { NumberAnimation { duration: Theme.quick } }
                                        }
                                        HoverHandler { id: swatchHover }
                                        MouseArea {
                                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                            onClicked: avatar.set(section.info.part, index)
                                        }
                                        Accessible.role: Accessible.RadioButton
                                        Accessible.name: section.info.label + " " + (index + 1)
                                        Accessible.checked: on
                                    }
                                }
                            }

                            // miniaturas de formato (recorte ampliado da parte)
                            Grid {
                                visible: section.info.kind === "shape"
                                width: parent.width
                                readonly property int cols: Math.max(3, Math.floor(width / 128))
                                readonly property real cell: (width - (cols - 1) * Theme.s3) / cols
                                columns: cols
                                spacing: Theme.s3
                                Repeater {
                                    model: section.info.kind === "shape" ? section.info.count : 0
                                    Item {
                                        readonly property bool on: avatar.choice[section.info.part] === index
                                        width: parent.cell; height: parent.cell
                                        Rectangle {
                                            anchors.fill: parent
                                            radius: 22
                                            color: Theme.surface
                                            border.width: parent.on ? 3 : 1
                                            border.color: parent.on ? Theme.ink : (thumbHover.hovered ? Theme.stone : Theme.hairline)
                                        }
                                        Image {
                                            anchors.fill: parent
                                            anchors.margins: 3
                                            sourceSize: Qt.size(200, 200)
                                            source: "image://avatar/" + section.info.crop + "/" + avatar.variant(section.info.part, index)
                                            asynchronous: true
                                            retainWhileLoading: true
                                            smooth: true
                                        }
                                        Rectangle {   // visto na opção escolhida
                                            visible: parent.on
                                            anchors.right: parent.right; anchors.top: parent.top
                                            anchors.margins: 8
                                            width: 24; height: 24; radius: 12
                                            color: Theme.ink
                                            KIcon { anchors.centerIn: parent; width: 14; height: 14; name: "checkmark"; tinted: true; color: Theme.inverse }
                                        }
                                        HoverHandler { id: thumbHover }
                                        MouseArea {
                                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                            onClicked: avatar.set(section.info.part, index)
                                        }
                                        Accessible.role: Accessible.RadioButton
                                        Accessible.name: section.info.label + " " + (index + 1)
                                        Accessible.checked: on
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    KToast { id: toast }
}
