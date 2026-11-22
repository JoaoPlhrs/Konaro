/*
 * Konaro OS — Central de controle (barra superior).
 *
 * Organização inspirada na Central de Controle do macOS: um bloco grande com
 * Wi-Fi / Bluetooth / Modo avião, ao lado Não perturbe e Modo escuro, o modo de
 * energia, e embaixo os controles deslizantes de Tela e Som e a Bateria.
 * Os ícones são do tema do sistema e a fonte é a do sistema (Inter por padrão).
 *
 * As ações usam as ferramentas padrão do sistema (nmcli, bluetoothctl, wpctl,
 * powerprofilesctl, upower) via o motor "executable" do Plasma: nada de serviço
 * extra rodando em segundo plano. Itens sem hardware (bateria, brilho) somem.
 * Licença: pendente (ver docs/LICENSES.md).
 */
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0
    function t(a, b) { return pt ? a : b }

    // ------------------------------------------------------------- estado
    property bool wifiOn: false
    property string wifiName: ""
    property bool btOn: false
    property bool btAvailable: false
    property bool airplane: false
    property bool dnd: false
    property bool dark: Kirigami.Theme.backgroundColor.hslLightness < 0.5
    property string profile: ""          // power-saver | balanced | performance
    property real volume: 0.5
    property bool muted: false
    property real brightness: -1         // -1 = sem controle de brilho
    property real brightnessMax: 1
    property int battery: -1             // -1 = sem bateria
    property string batteryState: ""
    property int batteryHealth: -1

    Plasmoid.icon: "configure"
    toolTipMainText: t("Central de controle", "Control Center")
    toolTipSubText: (wifiOn && wifiName ? "Wi-Fi: " + wifiName : "") + (battery >= 0 ? (wifiName ? " · " : "") + t("Bateria ", "Battery ") + battery + "%" : "")

    // ---------------------------------------------- execução de comandos
    P5Support.DataSource {
        id: exec
        engine: "executable"
        connectedSources: []
        property var handlers: ({})
        property int serial: 0
        onNewData: (source, data) => {
            const cb = handlers[source]
            delete handlers[source]
            disconnectSource(source)
            if (cb) cb((data["stdout"] || "").trim(), data["exit code"])
        }
        function run(cmd, cb) {
            serial += 1
            const src = cmd + " #" + serial          // fonte única por chamada
            handlers[src] = cb
            connectSource(src)
        }
    }
    function sh(cmd, cb) { exec.run(cmd, cb || function() {}) }

    function refresh() {
        sh("nmcli -t -f WIFI,WWAN radio", out => {
            const parts = out.split(":")
            wifiOn = parts[0] === "enabled"
        })
        sh("nmcli -t -f ACTIVE,SSID dev wifi 2>/dev/null | grep '^yes:' | head -1 | cut -d: -f2", out => wifiName = out)
        sh("nmcli -t -f WIFI,WWAN radio; nmcli networking", out => {
            airplane = out.split("\n").pop() === "disabled"
        })
        sh("bluetoothctl show 2>/dev/null", out => {
            btAvailable = out.indexOf("Controller") !== -1
            btOn = out.indexOf("Powered: yes") !== -1
        })
        sh("kreadconfig6 --file plasmanotifyrc --group DoNotDisturb --key Until", out => {
            dnd = out.length > 0 && new Date(out) > new Date()
        })
        sh("powerprofilesctl get 2>/dev/null", out => profile = out)
        sh("wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null", out => {
            const m = out.match(/Volume:\s*([0-9.]+)/)
            if (m) volume = Math.min(1, parseFloat(m[1]))
            muted = out.indexOf("MUTED") !== -1
        })
        sh("qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightnessMax 2>/dev/null; "
           + "qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightness 2>/dev/null", out => {
            const v = out.split("\n").map(Number)
            if (v.length === 2 && v[0] > 0) { brightnessMax = v[0]; brightness = v[1] / v[0] } else brightness = -1
        })
        sh("upower -i $(upower -e | grep -m1 BAT) 2>/dev/null", out => {
            const p = out.match(/percentage:\s*([0-9]+)/)
            battery = p ? parseInt(p[1]) : -1
            const s = out.match(/state:\s*(\S+)/)
            batteryState = s ? s[1] : ""
            const c = out.match(/capacity:\s*([0-9.]+)/)
            batteryHealth = c ? Math.round(parseFloat(c[1])) : -1
        })
    }

    Timer { interval: 4000; repeat: true; running: root.expanded; triggeredOnStart: true; onTriggered: root.refresh() }
    Timer { interval: 60000; repeat: true; running: true; triggeredOnStart: true; onTriggered: root.refresh() }

    // ------------------------------------------------------------- ações
    function setWifi(on) { wifiOn = on; sh("nmcli radio wifi " + (on ? "on" : "off"), refresh) }
    function setBt(on) { btOn = on; sh("bluetoothctl power " + (on ? "on" : "off"), refresh) }
    function setAirplane(on) { airplane = on; sh("nmcli networking " + (on ? "off" : "on") + "; bluetoothctl power " + (on ? "off" : "on"), refresh) }
    function setDnd(on) {
        dnd = on
        sh("kwriteconfig6 --notify --file plasmanotifyrc --group DoNotDisturb --key Until "
           + (on ? "'2099-12-31T23:59:59'" : "--delete"))
    }
    function setDark(on) { dark = on; sh("konaro-theme " + (on ? "dark" : "light")) }
    function setProfile(p) { profile = p; sh("powerprofilesctl set " + p, refresh) }
    function setVolume(v) { volume = v; sh("wpctl set-volume @DEFAULT_AUDIO_SINK@ " + v.toFixed(2)) }
    function toggleMute() { muted = !muted; sh("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle") }
    function setBrightness(v) {
        brightness = v
        sh("qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl setBrightness " + Math.round(v * brightnessMax))
    }
    function open(cmd) { sh(cmd); root.expanded = false }

    // ---------------------------------------------------- ícone na barra
    compactRepresentation: MouseArea {
        Layout.minimumWidth: Kirigami.Units.iconSizes.small * 1.4
        onClicked: root.expanded = !root.expanded
        // duas "chaves" sobrepostas, como o ícone da Central de Controle
        Item {
            anchors.centerIn: parent
            width: Kirigami.Units.iconSizes.small; height: width
            Repeater {
                model: 2
                Item {
                    width: parent.width; height: parent.height * 0.36
                    y: index === 0 ? parent.height * 0.08 : parent.height * 0.56
                    Rectangle {
                        anchors.fill: parent
                        radius: height / 2
                        color: "transparent"
                        border.width: Math.max(1, parent.height * 0.16)
                        border.color: Kirigami.Theme.textColor
                    }
                    Rectangle {
                        width: parent.height * 0.62; height: width; radius: width / 2
                        anchors.verticalCenter: parent.verticalCenter
                        x: index === 0 ? parent.width - width - parent.height * 0.19 : parent.height * 0.19
                        color: Kirigami.Theme.textColor
                    }
                }
            }
        }
    }

    // ------------------------------------------------------- painel aberto
    fullRepresentation: Item {
        id: panel
        Layout.preferredWidth: 372
        Layout.minimumWidth: 372
        Layout.preferredHeight: col.implicitHeight + 24
        Layout.minimumHeight: col.implicitHeight + 24

        readonly property color tileColor: root.dark ? Qt.rgba(1, 1, 1, 0.10) : Qt.rgba(1, 1, 1, 0.62)
        readonly property color ink: Kirigami.Theme.textColor
        readonly property color muted: Qt.rgba(ink.r, ink.g, ink.b, 0.6)
        readonly property color accent: "#0A84FF"

        component Tile: Rectangle {
            radius: 14
            color: panel.tileColor
            border.color: root.dark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(0, 0, 0, 0.06)
        }
        // botão redondo com ícone (azul quando ligado), como na Central do macOS
        component RoundToggle: Rectangle {
            property bool on: false
            property string icon: ""
            signal toggled()
            width: 30; height: 30; radius: 15
            color: on ? panel.accent : (root.dark ? Qt.rgba(1, 1, 1, 0.14) : Qt.rgba(0, 0, 0, 0.08))
            Kirigami.Icon {
                anchors.centerIn: parent; width: 16; height: 16
                source: parent.icon; isMask: true
                color: parent.on ? "white" : panel.ink
            }
            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: parent.toggled() }
        }
        component Row2: RowLayout {
            id: r2
            property alias icon: rt.icon
            property alias on: rt.on
            property string title
            property string sub
            signal toggled()
            spacing: 10
            RoundToggle { id: rt; onToggled: r2.toggled() }
            ColumnLayout {
                spacing: 0
                Layout.fillWidth: true
                QQC2.Label { text: r2.title; font.weight: Font.DemiBold; font.pixelSize: 13; color: panel.ink; elide: Text.ElideRight; Layout.fillWidth: true }
                QQC2.Label { text: r2.sub; font.pixelSize: 11; color: panel.muted; elide: Text.ElideRight; Layout.fillWidth: true; visible: text.length > 0 }
            }
        }
        component SliderTile: Tile {
            id: st
            property string title
            property string icon
            property real value: 0
            signal moved(real v)
            signal iconClicked()
            Layout.fillWidth: true
            implicitHeight: 64
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 10
                spacing: 6
                QQC2.Label { text: st.title; font.weight: Font.DemiBold; font.pixelSize: 13; color: panel.ink }
                // trilho grosso e arredondado, com o ícone dentro (estilo macOS)
                Rectangle {
                    id: track
                    Layout.fillWidth: true
                    height: 22; radius: 11
                    color: root.dark ? Qt.rgba(1, 1, 1, 0.14) : Qt.rgba(0, 0, 0, 0.10)
                    Rectangle {
                        width: Math.max(height, track.width * st.value)
                        height: parent.height; radius: 11
                        color: root.dark ? "#F2F2F7" : "white"
                        border.color: Qt.rgba(0, 0, 0, 0.08)
                    }
                    Kirigami.Icon {
                        x: 5; anchors.verticalCenter: parent.verticalCenter
                        width: 13; height: 13; source: st.icon
                        isMask: true; color: "#6E6E73"
                        MouseArea { anchors.fill: parent; anchors.margins: -4; onClicked: st.iconClicked() }
                    }
                    MouseArea {
                        anchors.fill: parent; anchors.leftMargin: 22
                        function apply(x) { st.moved(Math.max(0, Math.min(1, (x + 22) / track.width))) }
                        onPressed: (m) => apply(m.x)
                        onPositionChanged: (m) => { if (pressed) apply(m.x) }
                    }
                }
            }
        }

        ColumnLayout {
            id: col
            anchors.fill: parent
            anchors.margins: 12
            spacing: 10

            RowLayout {
                spacing: 10
                Layout.fillWidth: true
                // bloco de conexões
                Tile {
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 150
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 12
                        spacing: 8
                        Row2 {
                            icon: "network-wireless-symbolic"; title: "Wi-Fi"; on: root.wifiOn
                            sub: root.wifiOn ? (root.wifiName || root.t("Ligado", "On")) : root.t("Desligado", "Off")
                            onToggled: root.setWifi(!root.wifiOn)
                        }
                        Row2 {
                            icon: "network-bluetooth-symbolic"; title: "Bluetooth"; on: root.btOn
                            sub: !root.btAvailable ? root.t("Indisponível", "Unavailable") : root.btOn ? root.t("Ligado", "On") : root.t("Desligado", "Off")
                            onToggled: if (root.btAvailable) root.setBt(!root.btOn)
                        }
                        Row2 {
                            icon: "network-flightmode-on"; title: root.t("Modo avião", "Airplane"); on: root.airplane
                            sub: root.airplane ? root.t("Ligado", "On") : root.t("Desligado", "Off")
                            onToggled: root.setAirplane(!root.airplane)
                        }
                    }
                }
                ColumnLayout {
                    spacing: 10
                    Layout.fillWidth: true
                    Tile {
                        Layout.fillWidth: true; Layout.preferredHeight: 70
                        Row2 {
                            anchors.fill: parent; anchors.margins: 12
                            icon: "notifications-disabled"; on: root.dnd
                            title: root.t("Não perturbe", "Do Not Disturb")
                            sub: root.dnd ? root.t("Ligado", "On") : ""
                            onToggled: root.setDnd(!root.dnd)
                        }
                    }
                    Tile {
                        Layout.fillWidth: true; Layout.preferredHeight: 70
                        Row2 {
                            anchors.fill: parent; anchors.margins: 12
                            icon: "contrast"; on: root.dark
                            title: root.t("Modo escuro", "Dark Mode")
                            sub: root.dark ? root.t("Ligado", "On") : root.t("Desligado", "Off")
                            onToggled: root.setDark(!root.dark)
                        }
                    }
                }
            }

            // modo de energia (perfis de bateria)
            Tile {
                Layout.fillWidth: true
                implicitHeight: 64
                visible: root.profile.length > 0
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 10
                    spacing: 6
                    QQC2.Label { text: root.t("Modo de energia", "Power Mode"); font.weight: Font.DemiBold; font.pixelSize: 13; color: panel.ink }
                    RowLayout {
                        spacing: 6
                        Repeater {
                            model: [{ id: "power-saver", label: root.t("Economia", "Low Power") },
                                    { id: "balanced", label: root.t("Equilibrado", "Automatic") },
                                    { id: "performance", label: root.t("Desempenho", "High Power") }]
                            Rectangle {
                                Layout.fillWidth: true; height: 24; radius: 12
                                readonly property bool sel: root.profile === modelData.id
                                color: sel ? panel.accent : (root.dark ? Qt.rgba(1, 1, 1, 0.10) : Qt.rgba(0, 0, 0, 0.06))
                                QQC2.Label { anchors.centerIn: parent; text: modelData.label; font.pixelSize: 11; color: parent.sel ? "white" : panel.ink }
                                MouseArea { anchors.fill: parent; onClicked: root.setProfile(modelData.id) }
                            }
                        }
                    }
                }
            }

            SliderTile {
                visible: root.brightness >= 0
                title: root.t("Tela", "Display"); icon: "brightness-high"; value: Math.max(0, root.brightness)
                onMoved: (v) => root.setBrightness(Math.max(0.05, v))
            }
            SliderTile {
                title: root.t("Som", "Sound"); icon: root.muted ? "audio-volume-muted" : "audio-volume-high"; value: root.muted ? 0 : root.volume
                onMoved: (v) => root.setVolume(v)
                onIconClicked: root.toggleMute()
            }

            // bateria
            Tile {
                Layout.fillWidth: true
                implicitHeight: 56
                visible: root.battery >= 0
                RowLayout {
                    anchors.fill: parent; anchors.margins: 12
                    Kirigami.Icon {
                        source: root.batteryState === "charging" ? "battery-charging" : "battery-good"
                        Layout.preferredWidth: 22; Layout.preferredHeight: 22
                    }
                    ColumnLayout {
                        spacing: 0
                        Layout.fillWidth: true
                        QQC2.Label {
                            text: root.t("Bateria", "Battery") + " · " + root.battery + "%"
                                  + (root.batteryState === "charging" ? root.t(" · carregando", " · charging") : "")
                            font.weight: Font.DemiBold; font.pixelSize: 13; color: panel.ink
                        }
                        QQC2.Label {
                            visible: root.batteryHealth > 0
                            text: root.t("Saúde da bateria: ", "Battery health: ") + root.batteryHealth + "%"
                                  + (root.batteryHealth < 80 ? root.t(" (considere trocar)", " (consider replacing)") : "")
                            font.pixelSize: 11; color: panel.muted
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                QQC2.Label {
                    text: root.t("Configurações…", "Settings…")
                    color: panel.accent; font.pixelSize: 12
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.open("systemsettings") }
                }
                Item { Layout.fillWidth: true }
                QQC2.Label {
                    text: root.t("Energia…", "Power…")
                    color: panel.accent; font.pixelSize: 12
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.open("systemsettings kcm_powerdevilprofilesconfig") }
                }
            }
        }
    }
}
