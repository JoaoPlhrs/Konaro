// Loja Konaro — janela principal.
// Navegação familiar para quem vem do Windows: trilho lateral com ícone e nome,
// busca no topo, página do app dentro da janela com "Voltar".
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Konaro

ApplicationWindow {
    id: win
    width: 1200
    height: 780
    minimumWidth: 920
    minimumHeight: 600
    visible: true
    title: i18n.tr("Konaro Store")
    color: Theme.paper

    property string page: "home"
    property string pageBeforeDetail: "home"
    property var currentApp: null
    readonly property var apps: store.apps

    readonly property var categories: [
        { id: "home", label: i18n.tr("Home"), icon: "go-home-symbolic" },
        { id: "games", label: i18n.tr("Games"), icon: "applications-games-symbolic" },
        { id: "windows", label: i18n.tr("Windows apps"), icon: "window-symbolic" },
        { id: "internet", label: i18n.tr("Internet"), icon: "applications-internet-symbolic" },
        { id: "productivity", label: i18n.tr("Productivity"), icon: "applications-office-symbolic" },
        { id: "multimedia", label: i18n.tr("Multimedia"), icon: "applications-multimedia-symbolic" },
        { id: "graphics", label: i18n.tr("Graphics"), icon: "applications-graphics-symbolic" },
        { id: "development", label: i18n.tr("Development"), icon: "applications-development-symbolic" },
        { id: "utilities", label: i18n.tr("Utilities"), icon: "applications-utilities-symbolic" },
        { id: "desktops", label: i18n.tr("Desktop environments"), icon: "preferences-desktop-theme-global" }
    ]

    // ---------------------------------------------------------------- ajudantes
    function appById(id) {
        for (let i = 0; i < apps.length; ++i) if (apps[i].id === id) return apps[i]
        return null
    }
    function appsIn(category) { return apps.filter(a => a.category === category) }
    function busy(app) { return store.busyId !== "" && store.busyId === app.id }
    function actionLabel(app) {
        if (!app) return ""
        if (busy(app)) return app.state === "installed" ? i18n.tr("Removing…") : i18n.tr("Installing…")
        if (app.state === "unknown") return "…"
        return app.state === "installed" ? i18n.tr("Open") : i18n.tr("Install")
    }
    function actionEnabled(app) {
        if (!app || app.state === "unknown") return false
        if (store.busyId !== "") return false
        return app.state !== "installed" || app.canOpen
    }
    function progressFor(app) { return app && busy(app) ? store.progress : -1 }
    function primaryAction(app) {
        if (app.state === "installed") store.open(app.id)
        else askInstall(app)
    }
    function askInstall(app) {
        confirm.app = app
        confirm.removing = false
        confirm.title = i18n.tr("Install {name}?").replace("{name}", app.name)
        confirm.message = i18n.tr("Source") + ": " + app.originText + "\n" + i18n.tr("Format") + ": " + app.formatText
                          + "\n\n" + i18n.tr("Your password may be requested.")
        confirm.confirmText = i18n.tr("Install")
        confirm.iconName = app.icon
        confirm.open()
    }
    function askRemove(app) {
        confirm.app = app
        confirm.removing = true
        confirm.title = i18n.tr("Remove {name}?").replace("{name}", app.name)
        confirm.message = i18n.tr("Your password may be requested.")
        confirm.confirmText = i18n.tr("Remove")
        confirm.iconName = app.icon
        confirm.open()
    }
    function showApp(app) {
        if (page !== "detail") pageBeforeDetail = page
        currentApp = app
        page = "detail"
        store.loadPermissions(app.id)
    }
    function go(target) { search.text = ""; page = target }

    onAppsChanged: if (currentApp) currentApp = appById(currentApp.id)
    // categorias: além dos apps curados, mostra o catálogo completo daquela categoria
    onPageChanged: if (categories.some(c => c.id === page && c.id !== "home" && c.id !== "windows" && c.id !== "desktops")) store.browseCategory(page)

    Component.onCompleted: {
        if (startup.app && appById(startup.app)) showApp(appById(startup.app))
        else if (startup.category) page = startup.category === "featured" ? "home" : startup.category
        if (startup.search) search.text = startup.search
    }

    // ---------------------------------------------------------------- layout
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // trilho lateral
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 248
            color: Theme.rail

            ColumnLayout {
                anchors { fill: parent; margins: Theme.s3; topMargin: Theme.s5 }
                spacing: 2

                RowLayout {
                    Layout.leftMargin: Theme.s3
                    Layout.bottomMargin: Theme.s5
                    spacing: Theme.s3
                    KIcon { name: "konaro-store"; Layout.preferredWidth: 30; Layout.preferredHeight: 30 }
                    KText { text: i18n.tr("Store"); heading: true; font.pixelSize: 20 }
                }

                Repeater {
                    model: win.categories
                    KNavItem {
                        Layout.fillWidth: true
                        text: modelData.label
                        iconName: modelData.icon
                        selected: search.text === "" && (win.page === modelData.id
                                  || (win.page === "detail" && win.pageBeforeDetail === modelData.id))
                        onClicked: win.go(modelData.id)
                    }
                }

                Item { Layout.fillHeight: true }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: Theme.hairline; Layout.margins: Theme.s2 }

                KNavItem {
                    Layout.fillWidth: true
                    text: i18n.tr("Library")
                    iconName: "folder-download-symbolic"
                    badge: {
                        const n = win.apps.filter(a => a.state === "installed").length
                        return n > 0 ? String(n) : ""
                    }
                    selected: search.text === "" && (win.page === "installed"
                              || (win.page === "detail" && win.pageBeforeDetail === "installed"))
                    onClicked: win.go("installed")
                }
                KNavItem {
                    Layout.fillWidth: true
                    text: i18n.tr("Updates")
                    iconName: "system-software-update-symbolic"
                    onClicked: store.openUpdater()
                }
                KNavItem {
                    Layout.fillWidth: true
                    text: i18n.tr("Install from a file")
                    iconName: "document-open-symbolic"
                    onClicked: store.installFromFile()
                }
            }
        }
        Rectangle { Layout.fillHeight: true; Layout.preferredWidth: 1; color: Theme.hairline }

        // conteúdo
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 68
                KSearchField {
                    id: search
                    anchors.centerIn: parent
                    width: Math.min(560, parent.width - 96)
                    placeholder: i18n.tr("Search apps and games")
                    onTextChanged: { if (text !== "") win.currentApp = null; fullSearch.restart() }
                }
                // busca no catálogo completo (Debian + Flathub) depois que a pessoa para de digitar
                Timer { id: fullSearch; interval: 350; onTriggered: if (search.text.trim().length >= 2) store.searchAll(search.text) }
                Shortcut { sequences: [StandardKey.Find]; onActivated: search.focusField() }
            }

            Loader {
                Layout.fillWidth: true
                Layout.fillHeight: true
                sourceComponent: search.text !== "" ? listPage
                                : win.page === "home" ? homePage
                                : win.page === "detail" ? detailPage : listPage
            }
        }
    }

    Component { id: homePage; HomePage { ctl: win } }
    Component {
        id: listPage
        ListPage {
            ctl: win
            query: search.text
            category: search.text !== "" ? "search" : win.page
        }
    }
    Component { id: detailPage; DetailPage { ctl: win; app: win.currentApp } }

    // ---------------------------------------------------------------- avisos e confirmação
    KDialog {
        id: confirm
        property var app: null
        property bool removing: false
        cancelText: i18n.tr("Cancel")
        onConfirmed: removing ? store.remove(app.id) : store.install(app.id)
    }
    KDialog {
        id: errorDialog
        iconName: "dialog-warning"
        confirmText: i18n.tr("Close")
    }
    KToast {
        id: toast
        anchors { horizontalCenter: parent.horizontalCenter; bottom: parent.bottom; bottomMargin: Theme.s5 }
        property string details: ""
        onAction: {
            errorDialog.title = i18n.tr("Something went wrong")
            errorDialog.message = toast.text
            errorDialog.details = toast.details
            errorDialog.open()
        }
    }
    Connections {
        target: store
        function onToast(message, isError, details) {
            toast.details = details
            toast.show(message, isError, isError && details !== "" ? i18n.tr("Details") : "")
        }
    }
}
