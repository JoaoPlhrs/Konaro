// Por que está lento? — resumo do computador e achados com botão para resolver.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 820
    height: 620
    minimumWidth: 640
    minimumHeight: 480
    visible: true
    color: Theme.paper
    title: i18n.tr("Why is it slow?")

    KScrollPage {
        anchors.fill: parent
        margin: 40

        RowLayout {
            width: parent.width
            KText { text: i18n.tr("Why is it slow?"); heading: true; font.pixelSize: Theme.sizeHero; Layout.fillWidth: true }
            KButton {
                text: diag.state === "checking" ? i18n.tr("Checking…") : i18n.tr("Check again")
                enabled: diag.state !== "checking"
                onClicked: diag.check()
            }
        }
        KText {
            width: parent.width
            secondary: true
            text: i18n.tr("Konaro looks at memory, disk, processor, temperature and startup apps, and explains what to do.")
        }

        // resumo em quatro números
        Row {
            width: parent.width
            spacing: Theme.s3
            Repeater {
                model: [{ k: i18n.tr("Memory"), v: diag.summary.memory || "…" },
                        { k: i18n.tr("Disk"), v: diag.summary.disk || "…" },
                        { k: i18n.tr("Temperature"), v: diag.summary.temp || "…" },
                        { k: i18n.tr("Busiest now"), v: diag.summary.cpu || "…" }]
                KCard {
                    width: (parent.width - Theme.s3 * 3) / 4
                    height: 78
                    Column {
                        anchors.fill: parent; anchors.margins: 14
                        spacing: 4
                        KText { text: modelData.k; secondary: true; font.pixelSize: Theme.sizeSmall }
                        KText { text: modelData.v; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeHeading; elide: Text.ElideRight; width: parent.width }
                    }
                }
            }
        }

        Repeater {
            model: diag.findings
            KCard {
                width: parent.width
                height: row.implicitHeight + 32
                RowLayout {
                    id: row
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: Theme.s4
                    Rectangle {
                        Layout.preferredWidth: 12; Layout.preferredHeight: 12; radius: 6
                        Layout.alignment: Qt.AlignTop
                        Layout.topMargin: 6
                        color: modelData.level === "bad" ? Theme.danger : modelData.level === "warn" ? "#E8A317" : Theme.success
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        KText { text: modelData.title; font.weight: Font.DemiBold; font.pixelSize: Theme.sizeHeading; Layout.fillWidth: true }
                        KText { text: modelData.text; secondary: true; Layout.fillWidth: true }
                    }
                    KButton {
                        visible: modelData.action !== ""
                        text: modelData.actionText
                        kind: modelData.level === "bad" ? "primary" : "secondary"
                        onClicked: diag.act(modelData.action)
                    }
                }
            }
        }
    }
}
