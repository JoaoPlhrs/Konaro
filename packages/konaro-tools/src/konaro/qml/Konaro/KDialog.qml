import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Diálogo de confirmação (modal, centralizado).
Popup {
    id: root
    property string title: ""
    property string message: ""
    property string details: ""
    property string iconName: ""
    property string confirmText: ""
    property string cancelText: ""
    property bool showDetails: false
    signal confirmed()

    anchors.centerIn: Overlay.overlay
    width: Math.min(460, parent ? parent.width - 64 : 460)
    modal: true
    focus: true
    padding: Theme.s5 + 4
    closePolicy: Popup.CloseOnEscape
    Overlay.modal: Rectangle { color: Theme.scrim }
    enter: Transition { NumberAnimation { property: "opacity"; from: 0; to: 1; duration: Theme.quick } }
    exit: Transition { NumberAnimation { property: "opacity"; from: 1; to: 0; duration: Theme.quick } }

    background: Rectangle {
        radius: Theme.radiusBlock + 2
        color: Theme.raised
        border.width: 1
        border.color: Theme.hairline
    }
    contentItem: ColumnLayout {
        spacing: Theme.s3
        KIcon { visible: root.iconName !== ""; name: root.iconName; Layout.preferredWidth: 56; Layout.preferredHeight: 56 }
        KText { text: root.title; heading: true; font.pixelSize: 20; Layout.fillWidth: true }
        KText { text: root.message; secondary: true; lineHeight: 1.2; Layout.fillWidth: true }
        KText {
            visible: root.details !== ""
            text: root.showDetails ? root.details : ""
            secondary: true
            font.pixelSize: Theme.sizeTiny
            font.family: "monospace"
            Layout.fillWidth: true
            Layout.maximumHeight: 160
            clip: true
        }
        RowLayout {
            Layout.topMargin: Theme.s3
            spacing: Theme.s2
            KButton {
                visible: root.details !== ""
                kind: "ghost"; compact: true
                text: i18n.tr(root.showDetails ? "Hide details" : "Technical details")
                onClicked: root.showDetails = !root.showDetails
            }
            Item { Layout.fillWidth: true }
            KButton { visible: root.cancelText !== ""; text: root.cancelText; onClicked: root.close() }
            KButton { text: root.confirmText; kind: "primary"; onClicked: { root.close(); root.confirmed() } }
        }
    }
}
