/*
 * Konaro OS — Iniciar (tecla Super / Windows).
 *
 * Em vez do menu pequeno no canto, abre uma tela cheia de vidro, centralizada,
 * que mistura o Launchpad do macOS e o Iniciar do Windows 11:
 *   - busca em pílula no alto (apps, configurações, calculadora…);
 *   - "Fixados": os apps favoritos, em grade;
 *   - "Todos os apps": grade em ordem alfabética, rolagem vertical;
 *   - embaixo: o usuário à esquerda e Bloquear / Sair / Reiniciar / Desligar à direita.
 * Usa os modelos de apps do próprio Plasma (org.kde.plasma.private.kicker).
 * Licença: pendente (ver docs/LICENSES.md).
 */
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasmoid
import org.kde.plasma.private.kicker as Kicker
import org.kde.coreaddons as KCoreAddons

PlasmoidItem {
    id: launcher

    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0
    function t(ptText, enText) { return pt ? ptText : enText }

    preferredRepresentation: compactRepresentation
    compactRepresentation: compactComponent
    fullRepresentation: compactComponent
    Plasmoid.icon: Plasmoid.configuration.icon

    property QtObject favorites: rootModel.favoritesModel
    property QtObject systemActions: rootModel.systemFavoritesModel

    Kicker.RootModel {
        id: rootModel
        autoPopulate: false
        appletInterface: launcher
        flat: true
        sorted: true
        showSeparators: false
        showAllApps: true
        showAllAppsCategorized: false
        showTopLevelItems: false
        showRecentApps: false
        showRecentDocs: false

        Component.onCompleted: {
            favoritesModel.initForClient("org.konaro.launcher.favorites.instance-" + Plasmoid.id)
            if (!Plasmoid.configuration.favoritesPorted) {
                if (favoritesModel.count < 1)
                    favoritesModel.portOldFavorites(Plasmoid.configuration.favoriteApps)
                Plasmoid.configuration.favoritesPorted = true
            }
        }
    }

    onSystemActionsChanged: {
        if (systemActions)
            systemActions.favorites = ["lock-screen", "logout", "reboot", "shutdown"]
    }

    Kicker.RunnerModel {
        id: runnerModel
        appletInterface: launcher
        favoritesModel: rootModel.favoritesModel
        mergeResults: true
        runners: ["krunner_services", "krunner_systemsettings", "calculator", "unitconverter",
                  "krunner_sessions", "krunner_powerdevil", "baloosearch", "locations"]
    }

    Kicker.WindowSystem { id: windowSystem }
    KCoreAddons.KUser { id: kuser }

    Component {
        id: compactComponent
        Item {
            id: button
            Layout.minimumWidth: Kirigami.Units.iconSizes.small
            Layout.minimumHeight: Kirigami.Units.iconSizes.small
            Kirigami.Icon {
                anchors.fill: parent
                source: Plasmoid.icon
                active: mouse.containsMouse || (dash.visible === true)
            }
            MouseArea {
                id: mouse
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.LeftButton
                onClicked: dash.toggle()
            }
        }
    }

    Connections {
        target: Plasmoid
        function onActivated() { dash.toggle() }
    }

    Component.onCompleted: rootModel.refresh()

    // ======================================================== janela em tela cheia
    Kicker.DashboardWindow {
        id: dash
        visualParent: launcher
        backgroundColor: Qt.rgba(0.06, 0.06, 0.08, 0.62)
        keyEventProxy: search

        readonly property real s: Math.max(0.8, Math.min(width / 1440, height / 900))
        readonly property int iconSize: Math.round(64 * s)
        readonly property int cell: Math.round(118 * s)
        readonly property int columns: Math.max(4, Math.min(8, Math.floor((width * 0.72) / cell)))
        readonly property bool searching: search.text.length > 0

        onKeyEscapePressed: {
            if (searching) search.text = ""
            else dash.toggle()
        }
        onVisibleChanged: {
            search.text = ""
            if (visible) {
                rootModel.refresh()
                allGrid.model = rootModel.modelForRow(0)
                scroller.contentY = 0
                search.forceActiveFocus()
            }
        }

        function launch(model, index) {
            if (model && "trigger" in model) model.trigger(index, "", null)
            if (dash.visible) dash.toggle()
        }

        mainItem: MouseArea {
            id: content
            anchors.fill: parent
            // clicar no vazio fecha, como no Launchpad
            onClicked: dash.toggle()

            // --------------------------------------------------------- busca
            Rectangle {
                id: searchPill
                width: Math.min(620 * dash.s, parent.width * 0.8)
                height: 44 * dash.s
                radius: height / 2
                anchors.horizontalCenter: parent.horizontalCenter
                y: parent.height * 0.07
                color: Qt.rgba(1, 1, 1, search.activeFocus ? 0.20 : 0.15)
                border.color: Qt.rgba(1, 1, 1, 0.22)
                Kirigami.Icon {
                    id: lens
                    source: "search"
                    width: 18 * dash.s; height: width
                    anchors.verticalCenter: parent.verticalCenter
                    x: 16 * dash.s
                    color: "white"
                    isMask: true
                    opacity: 0.8
                }
                QQC2.TextField {
                    id: search
                    anchors.fill: parent
                    leftPadding: 44 * dash.s
                    rightPadding: 16 * dash.s
                    background: Item {}
                    color: "white"
                    placeholderText: launcher.t("Pesquisar apps, configurações e arquivos", "Search apps, settings and files")
                    placeholderTextColor: Qt.rgba(1, 1, 1, 0.6)
                    font.pixelSize: 16 * dash.s
                    onTextChanged: runnerModel.query = text
                    Keys.onDownPressed: (dash.searching ? resultsGrid : (favGrid.count ? favGrid : allGrid)).forceActiveFocus()
                    onAccepted: {
                        if (dash.searching && runnerModel.count > 0) {
                            var m = runnerModel.modelForRow(0)
                            if (m && m.count > 0) dash.launch(m, 0)
                        }
                    }
                }
            }

            // ------------------------------------------------ apps (sem busca)
            Flickable {
                id: scroller
                visible: !dash.searching
                anchors.top: searchPill.bottom
                anchors.topMargin: 34 * dash.s
                anchors.bottom: footer.top
                anchors.bottomMargin: 16 * dash.s
                width: dash.columns * dash.cell
                anchors.horizontalCenter: parent.horizontalCenter
                contentHeight: column.implicitHeight
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                Column {
                    id: column
                    width: parent.width
                    spacing: 14 * dash.s
                    SectionTitle { text: launcher.t("Fixados", "Pinned"); visible: favGrid.count > 0 }
                    AppGrid { id: favGrid; model: rootModel.favoritesModel; columns: dash.columns; cell: dash.cell; iconSize: dash.iconSize; onLaunch: (m, i) => dash.launch(m, i) }
                    Item { width: 1; height: 8 * dash.s }
                    SectionTitle { text: launcher.t("Todos os apps", "All apps") }
                    AppGrid { id: allGrid; columns: dash.columns; cell: dash.cell; iconSize: dash.iconSize; onLaunch: (m, i) => dash.launch(m, i) }
                }
            }

            // --------------------------------------------- resultados da busca
            Column {
                visible: dash.searching
                anchors.top: searchPill.bottom
                anchors.topMargin: 34 * dash.s
                width: dash.columns * dash.cell
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 14 * dash.s
                SectionTitle { text: launcher.t("Melhores resultados", "Best matches") }
                AppGrid {
                    id: resultsGrid
                    model: dash.searching && runnerModel.count > 0 ? runnerModel.modelForRow(0) : null
                    columns: dash.columns; cell: dash.cell; iconSize: dash.iconSize
                    maxRows: 3
                    onLaunch: (m, i) => dash.launch(m, i)
                }
                Text {
                    visible: !resultsGrid.count
                    text: launcher.t("Nada encontrado", "No results")
                    color: Qt.rgba(1, 1, 1, 0.7)
                    font.pixelSize: 15 * dash.s
                }
            }

            // ------------------------------------------- rodapé: usuário e energia
            Rectangle {
                id: footer
                width: Math.min(dash.columns * dash.cell + 32 * dash.s, parent.width * 0.9)
                height: 60 * dash.s
                radius: 16 * dash.s
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height * 0.05
                color: Qt.rgba(1, 1, 1, 0.08)
                border.color: Qt.rgba(1, 1, 1, 0.12)

                MouseArea { anchors.fill: parent }   // não fecha ao clicar no rodapé

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 18 * dash.s
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 12 * dash.s
                    Rectangle {
                        width: 34 * dash.s; height: width; radius: width / 2
                        color: "#8E8E93"
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            anchors.centerIn: parent
                            text: (kuser.fullName || kuser.loginName || "?").charAt(0).toUpperCase()
                            color: "white"; font.pixelSize: 15 * dash.s; font.bold: true
                        }
                        Kirigami.Icon {
                            anchors.fill: parent
                            source: kuser.faceIconUrl
                            visible: kuser.faceIconUrl.toString().length > 0 && valid
                        }
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: kuser.fullName || kuser.loginName
                        color: "white"
                        font.pixelSize: 15 * dash.s
                        font.weight: Font.DemiBold
                    }
                }
                Row {
                    anchors.right: parent.right
                    anchors.rightMargin: 12 * dash.s
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6 * dash.s
                    Repeater {
                        model: launcher.systemActions
                        delegate: Rectangle {
                            width: 40 * dash.s; height: width; radius: width / 2
                            color: hov.hovered ? Qt.rgba(1, 1, 1, 0.18) : "transparent"
                            HoverHandler { id: hov }
                            Kirigami.Icon {
                                anchors.centerIn: parent
                                width: 20 * dash.s; height: width
                                source: model.decoration
                                color: "white"; isMask: true
                            }
                            QQC2.ToolTip.visible: hov.hovered
                            QQC2.ToolTip.text: model.display
                            MouseArea { anchors.fill: parent; onClicked: dash.launch(launcher.systemActions, index) }
                        }
                    }
                }
            }
        }
    }
}
