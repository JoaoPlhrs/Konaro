// Loja Konaro — página inicial: destaque, fileiras curadas e programas do Windows.
import QtQuick
import QtQuick.Layouts
import Konaro

KScrollPage {
    id: root
    property var ctl
    property int spot: 0
    readonly property var featured: ["com.valvesoftware.Steam", "com.usebottles.bottles", "libreoffice", "com.spotify.Client"]
        .map(id => ctl.appById(id)).filter(a => a !== null)
    readonly property var spotApp: featured.length ? featured[spot % featured.length] : null

    function pick(ids) { return ids.map(id => ctl.appById(id)).filter(a => a !== null) }

    // ------------------------------------------------ destaque
    Item {
        width: parent.width
        height: 300
        visible: root.spotApp !== null
        KSpotlight {
            anchors.fill: parent
            app: root.spotApp || ({})
            body: root.spotApp ? root.spotApp.summaryText : ""
            actionText: root.ctl.actionLabel(root.spotApp)
            actionEnabled: root.ctl.actionEnabled(root.spotApp)
            progress: root.ctl.progressFor(root.spotApp)
            detailsText: i18n.tr("Details")
            onAction: root.ctl.primaryAction(root.spotApp)
            onOpened: root.ctl.showApp(root.spotApp)
        }
        // seletor do destaque (manual; nada muda sozinho)
        Row {
            anchors { left: parent.left; leftMargin: Theme.s6 + 8; bottom: parent.bottom; bottomMargin: Theme.s5 }
            spacing: 8
            Repeater {
                model: root.featured.length
                Rectangle {
                    width: index === root.spot ? 22 : 8
                    height: 8
                    radius: 4
                    color: Theme.ink
                    opacity: index === root.spot ? 0.9 : 0.25
                    Behavior on width { NumberAnimation { duration: Theme.quick } }
                    MouseArea { anchors.fill: parent; anchors.margins: -6; cursorShape: Qt.PointingHandCursor; onClicked: root.spot = index }
                    Accessible.role: Accessible.Button
                    Accessible.name: root.featured[index].name
                }
            }
        }
    }

    // ------------------------------------------------ fileiras
    component Shelf: Column {
        property string title
        property var items: []
        property string target: ""
        width: root.width - root.margin * 2
        spacing: Theme.s3
        KSectionTitle {
            width: parent.width
            text: parent.title
            actionText: parent.target !== "" ? i18n.tr("See all") : ""
            onAction: root.ctl.go(parent.target)
        }
        Row {
            id: line
            spacing: Theme.s4
            readonly property int fit: Math.max(1, Math.floor((parent.width + spacing) / (184 + spacing)))
            readonly property real tileWidth: (parent.width - spacing * (fit - 1)) / fit
            Repeater {
                model: parent.parent.items.slice(0, line.fit)
                KAppTile {
                    width: line.tileWidth
                    app: modelData
                    actionText: root.ctl.actionLabel(modelData)
                    actionEnabled: root.ctl.actionEnabled(modelData)
                    progress: root.ctl.progressFor(modelData)
                    onOpened: root.ctl.showApp(modelData)
                    onAction: root.ctl.primaryAction(modelData)
                }
            }
        }
    }

    Shelf {
        title: i18n.tr("Get started")
        items: root.pick(["firefox-esr", "libreoffice", "vlc", "thunderbird", "com.spotify.Client",
                          "keepassxc", "brave-browser", "io.github.ungoogled_software.ungoogled_chromium"])
    }
    Shelf {
        title: i18n.tr("Play")
        target: "games"
        items: root.ctl.appsIn("games")
    }

    // ------------------------------------------------ programas do Windows
    KCard {
        width: parent.width
        height: 168
        radius: Theme.radiusBlock
        RowLayout {
            anchors { fill: parent; margins: Theme.s5; leftMargin: Theme.s6 }
            spacing: Theme.s6
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Theme.s2
                KText { text: i18n.tr("Windows programs on Konaro"); heading: true; font.pixelSize: Theme.sizeTitle; Layout.fillWidth: true }
                KText {
                    text: i18n.tr("Double-click a .exe file to open it with Wine. For more demanding programs, Bottles creates a separate, tidy environment for each one.")
                    secondary: true
                    lineHeight: 1.25
                    Layout.fillWidth: true
                    Layout.maximumWidth: 620
                }
                RowLayout {
                    Layout.topMargin: Theme.s2
                    spacing: Theme.s2
                    readonly property var bottles: root.ctl.appById("com.usebottles.bottles")
                    KButton {
                        visible: parent.bottles !== null
                        kind: "primary"
                        text: parent.bottles ? (parent.bottles.state === "installed" ? i18n.tr("Open Bottles") : i18n.tr("Install Bottles")) : ""
                        enabled: parent.bottles !== null && root.ctl.actionEnabled(parent.bottles)
                        progress: root.ctl.progressFor(parent.bottles)
                        onClicked: root.ctl.primaryAction(parent.bottles)
                    }
                    KButton { text: i18n.tr("See Windows apps"); kind: "ghost"; onClicked: root.ctl.go("windows") }
                }
            }
            Row {
                spacing: -18
                Layout.alignment: Qt.AlignVCenter
                KIcon { name: "wine"; width: 84; height: 84 }
                KIcon { name: "com.usebottles.bottles"; width: 84; height: 84 }
            }
        }
    }

    Shelf {
        title: i18n.tr("Create and edit")
        items: root.pick(["gimp", "krita", "kdenlive", "com.obsproject.Studio", "org.blender.Blender", "inkscape", "audacity"])
    }
    Shelf {
        title: i18n.tr("Talk with friends")
        items: root.pick(["com.discordapp.Discord", "org.telegram.desktop", "org.signal.Signal", "us.zoom.Zoom", "kdeconnect"])
    }
    Item { width: 1; height: Theme.s5 }
}
