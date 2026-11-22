// Boas-vindas do Konaro — primeiro uso, em passos.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 1000
    height: 700
    minimumWidth: 860
    minimumHeight: 620
    visible: true
    color: Theme.paper
    title: t("Welcome to Konaro")

    // tradução reativa: reavalia os textos quando o idioma muda
    function t(s) { return welcome.lang.length >= 0 ? i18n.tr(s) : s }

    property int step: Math.min(startPage, pages.count - 1)
    property bool darkChosen: welcome.dark
    property string fontChosen: welcome.font
    readonly property int total: pages.count

    // ---------------------------------------------------------------- componentes de página
    component Page: ColumnLayout {
        property string title
        property string subtitle
        default property alias body: content.data
        spacing: Theme.s3
        KText { text: parent.title; heading: true; font.pixelSize: 34; font.letterSpacing: -0.8; Layout.fillWidth: true }
        KText { visible: text !== ""; text: parent.subtitle; secondary: true; font.pixelSize: 15; lineHeight: 1.25; Layout.fillWidth: true; Layout.maximumWidth: 640 }
        ColumnLayout { id: content; spacing: Theme.s4; Layout.topMargin: Theme.s5; Layout.fillWidth: true }
        Item { Layout.fillHeight: true }
    }
    component ActionCard: KCard {
        id: card
        property string iconName
        property string title
        property string text
        property string buttonText
        signal activated()
        Layout.fillWidth: true
        implicitHeight: 92
        RowLayout {
            anchors { fill: parent; leftMargin: Theme.s5; rightMargin: Theme.s5 }
            spacing: Theme.s4
            KIcon { name: card.iconName; Layout.preferredWidth: 40; Layout.preferredHeight: 40 }
            ColumnLayout {
                spacing: 2
                Layout.fillWidth: true
                KText { text: card.title; font.pixelSize: 15; font.weight: Font.DemiBold; Layout.fillWidth: true }
                KText { text: card.text; secondary: true; font.pixelSize: Theme.sizeSmall; Layout.fillWidth: true }
            }
            KButton { text: card.buttonText; onClicked: card.activated() }
        }
    }

    // ---------------------------------------------------------------- páginas
    StackLayout {
        id: pages
        currentIndex: win.step
        anchors { left: parent.left; right: parent.right; top: parent.top; bottom: bar.top
                  leftMargin: 72; rightMargin: 72; topMargin: 56 }

        // 1. boas-vindas + idioma
        ColumnLayout {
            spacing: Theme.s3
            KIcon { name: "konaro"; Layout.preferredWidth: 88; Layout.preferredHeight: 88; Layout.bottomMargin: Theme.s4 }
            KText { text: t("Welcome to Konaro"); heading: true; font.pixelSize: 46; font.letterSpacing: -1.2; Layout.fillWidth: true }
            KText {
                text: t("Let's get your computer ready in a few steps. You can change everything later in Settings.")
                secondary: true; font.pixelSize: 16; lineHeight: 1.25; Layout.maximumWidth: 600; Layout.fillWidth: true
            }
            KText { text: t("Language"); font.weight: Font.DemiBold; Layout.topMargin: Theme.s6 }
            Row {
                spacing: Theme.s2
                Repeater {
                    model: [{ code: "pt", label: "Português (Brasil)" }, { code: "en", label: "English" }]
                    KButton {
                        text: modelData.label
                        kind: welcome.lang === modelData.code ? "primary" : "secondary"
                        onClicked: welcome.setLanguage(modelData.code)
                    }
                }
            }
            KText { text: t("The system language is applied the next time you log in."); secondary: true; font.pixelSize: Theme.sizeSmall }
            KCard {
                visible: welcome.live
                Layout.topMargin: Theme.s5
                Layout.fillWidth: true
                Layout.maximumWidth: 640
                implicitHeight: 84
                RowLayout {
                    anchors { fill: parent; leftMargin: Theme.s5; rightMargin: Theme.s5 }
                    spacing: Theme.s4
                    KText { text: t("You are trying Konaro OS without installing it. Nothing is changed on your computer until you install."); secondary: true; Layout.fillWidth: true }
                    KButton { text: t("Install Konaro OS"); kind: "primary"; onClicked: welcome.install() }
                }
            }
            Item { Layout.fillHeight: true }
        }

        // 2. aparência
        Page {
            title: t("Appearance")
            subtitle: t("Choose how Konaro looks. You can switch at any time.")
            RowLayout {
                spacing: Theme.s5
                Repeater {
                    model: [{ dark: false, label: t("Light"), image: welcome.lightPreview },
                            { dark: true, label: t("Dark"), image: welcome.darkPreview }]
                    ColumnLayout {
                        spacing: Theme.s2
                        readonly property bool chosen: modelData.dark === win.darkChosen
                        Rectangle {
                            Layout.preferredWidth: 300
                            Layout.preferredHeight: 186
                            radius: Theme.radiusBlock + 4
                            color: "transparent"
                            border.width: parent.chosen ? 3 : 1
                            border.color: parent.chosen ? Theme.ink : Theme.hairline
                            Image {
                                anchors { fill: parent; margins: 6 }
                                source: "file://" + modelData.image
                                fillMode: Image.PreserveAspectCrop
                                layer.enabled: false
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: { win.darkChosen = modelData.dark; welcome.setDark(modelData.dark) }
                            }
                            Accessible.role: Accessible.RadioButton
                            Accessible.name: modelData.label
                        }
                        KText { text: modelData.label; font.weight: parent.chosen ? Font.DemiBold : Font.Normal; Layout.alignment: Qt.AlignHCenter }
                    }
                }
            }
            // fonte do sistema: cada opção aparece escrita na própria fonte
            KText { text: t("System font"); font.weight: Font.DemiBold; Layout.topMargin: Theme.s4 }
            Flow {
                Layout.fillWidth: true
                spacing: Theme.s2
                Repeater {
                    model: welcome.fonts
                    Rectangle {
                        readonly property bool chosen: modelData.id === win.fontChosen
                        width: fontLabel.implicitWidth + 32
                        height: 40
                        radius: height / 2
                        color: chosen ? Theme.ink : Theme.fill
                        Text {
                            id: fontLabel
                            anchors.centerIn: parent
                            text: modelData.name
                            font.family: modelData.family
                            font.pixelSize: 15
                            color: parent.chosen ? Theme.inverse : Theme.ink
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: { win.fontChosen = modelData.id; welcome.setFont(modelData.id) }
                        }
                        Accessible.role: Accessible.RadioButton
                        Accessible.name: modelData.name
                    }
                }
            }
            RowLayout {
                Layout.topMargin: Theme.s4
                spacing: Theme.s3
                KSwitch { onToggled: (on) => welcome.setReducedAnimations(on) }
                ColumnLayout {
                    spacing: 2
                    KText { text: t("Reduce animations"); font.weight: Font.DemiBold }
                    KText { text: t("Makes the interface faster on modest computers and more comfortable if motion bothers you."); secondary: true; font.pixelSize: Theme.sizeSmall }
                }
            }
        }

        // 3. widgets
        Page {
            title: t("Widgets")
            subtitle: t("Glance at the time, your calendar and notes right on the desktop. Turn on the ones you want — you can move or remove them later.")
            GridLayout {
                columns: 2
                columnSpacing: Theme.s3
                rowSpacing: Theme.s3
                Layout.fillWidth: true
                Repeater {
                    model: welcome.widgets
                    KCard {
                        Layout.fillWidth: true
                        implicitHeight: 84
                        RowLayout {
                            anchors { fill: parent; leftMargin: Theme.s4; rightMargin: Theme.s4 }
                            spacing: Theme.s3
                            KIcon { name: modelData.icon; Layout.preferredWidth: 36; Layout.preferredHeight: 36 }
                            ColumnLayout {
                                spacing: 2
                                Layout.fillWidth: true
                                KText { text: modelData.name; font.weight: Font.DemiBold; Layout.fillWidth: true }
                                KText { text: modelData.description; secondary: true; font.pixelSize: Theme.sizeSmall; Layout.fillWidth: true; maximumLineCount: 2; elide: Text.ElideRight }
                            }
                            KSwitch {
                                checked: modelData.enabled
                                enabled: modelData.available
                                onToggled: (on) => welcome.setWidget(modelData.id, on)
                            }
                        }
                    }
                }
            }
        }

        // 4. internet
        Page {
            title: t("Internet")
            subtitle: welcome.online ? t("You are connected to the internet.")
                                     : t("You are not connected to the internet yet. Connect to install apps and receive updates.")
            ActionCard {
                iconName: welcome.online ? "network-wireless-connected-100" : "network-wireless-disconnected"
                title: t("Network settings")
                text: t("Wi-Fi, cable and mobile connections.")
                buttonText: t("Open")
                onActivated: welcome.openNetwork()
            }
        }

        // 5. privacidade
        Page {
            title: t("Privacy")
            subtitle: t("Konaro OS does not collect any data about you or your computer. There is no account to create.")
            RowLayout {
                spacing: Theme.s3
                KSwitch { onToggled: (on) => welcome.setFeedback(on) }
                KText { text: t("Share anonymous usage statistics with KDE (optional)"); Layout.fillWidth: true }
            }
        }

        // 6. atualizações e drivers
        Page {
            title: t("Updates and drivers")
            subtitle: t("Konaro tells you when updates are available — you choose when to install them.")
            ActionCard {
                iconName: "konaro-updater"; title: t("Konaro Updates"); text: t("Security fixes and improvements for the system and your apps.")
                buttonText: t("Check for updates"); onActivated: welcome.openTool("konaro-updater")
            }
            ActionCard {
                iconName: "konaro-drivers"; title: t("Konaro Drivers"); text: t("Extra drivers for graphics cards, Wi-Fi and other devices.")
                buttonText: t("Check drivers"); onActivated: welcome.openTool("konaro-drivers")
            }
        }

        // 7. jogos e Windows
        Page {
            title: t("Games and Windows apps")
            subtitle: t("Steam with Proton runs thousands of Windows games. Lutris and Bottles help with other launchers and Windows programs. Wine is already installed: double-click a .exe file to run it.")
            Row {
                spacing: Theme.s4
                Repeater {
                    model: ["/usr/share/konaro/store/icons/com.valvesoftware.Steam.png", "/usr/share/konaro/store/icons/lutris.png",
                            "/usr/share/konaro/store/icons/com.usebottles.bottles.png", "/usr/share/konaro/store/icons/wine.png"]
                    KIcon { name: modelData; width: 64; height: 64 }
                }
            }
            KText { text: t("Not every game or program works: anti-cheat systems and some DRM can block them."); secondary: true; font.pixelSize: Theme.sizeSmall; Layout.fillWidth: true }
            KButton { text: t("Open the Games section of the Store"); kind: "primary"; onClicked: welcome.openTool("store:games") }
        }

        // 8. como usar
        Page {
            title: t("Getting around")
            GridLayout {
                columns: 2
                columnSpacing: Theme.s3
                rowSpacing: Theme.s3
                Layout.fillWidth: true
                Repeater {
                    model: [
                        { icon: "view-app-grid-symbolic", text: t("The dock at the bottom opens your apps. Running apps show a dot.") },
                        { icon: "konaro-start", text: t("The Konaro logo at the top left opens all apps and search. You can also press the Meta (Windows) key.") },
                        { icon: "preferences-system-notifications", text: t("The top right shows network, sound, battery, notifications and the clock.") },
                        { icon: "window-symbolic", text: t("Meta + W shows all open windows.") }
                    ]
                    KCard {
                        Layout.fillWidth: true
                        implicitHeight: 96
                        RowLayout {
                            anchors { fill: parent; margins: Theme.s4 }
                            spacing: Theme.s3
                            KIcon { name: modelData.icon; tinted: true; Layout.preferredWidth: 28; Layout.preferredHeight: 28; Layout.alignment: Qt.AlignTop }
                            KText { text: modelData.text; lineHeight: 1.2; Layout.fillWidth: true }
                        }
                    }
                }
            }
        }

        // 9. pronto
        Page {
            title: t("All set!")
            subtitle: t("Enjoy Konaro OS. You can open this welcome again from the app menu.")
            KButton { text: t("Open the Store"); onClicked: welcome.openTool("store") }
            RowLayout {
                spacing: Theme.s3
                KSwitch { id: again }
                KText { text: t("Show this welcome at every login") }
            }
        }
    }

    // ---------------------------------------------------------------- barra inferior
    Rectangle {
        id: bar
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 84
        color: Theme.paper
        Rectangle { anchors { left: parent.left; right: parent.right; top: parent.top } height: 1; color: Theme.hairline }
        RowLayout {
            anchors { fill: parent; leftMargin: 72; rightMargin: 72 }
            spacing: Theme.s3
            ColumnLayout {
                spacing: 6
                KText { text: t("Step {n} of {total}").replace("{n}", win.step + 1).replace("{total}", win.total); secondary: true; font.pixelSize: Theme.sizeSmall }
                Rectangle {
                    Layout.preferredWidth: 180; Layout.preferredHeight: 4; radius: 2; color: Theme.fill
                    Rectangle {
                        width: parent.width * (win.step + 1) / win.total; height: parent.height; radius: 2; color: Theme.ink
                        Behavior on width { NumberAnimation { duration: Theme.smooth; easing.type: Easing.OutCubic } }
                    }
                }
            }
            Item { Layout.fillWidth: true }
            KButton { visible: win.step > 0; text: t("Back"); kind: "ghost"; onClicked: win.step -= 1 }
            KButton {
                kind: "primary"
                text: win.step === win.total - 1 ? t("Start using Konaro") : t("Next")
                onClicked: {
                    if (win.step === win.total - 1) { welcome.finish(again.checked); Qt.quit() }
                    else win.step += 1
                    if (win.step === 3) welcome.refreshOnline()
                }
            }
        }
    }
}
