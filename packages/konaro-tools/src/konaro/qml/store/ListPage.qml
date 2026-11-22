// Loja Konaro — lista de apps: categoria, biblioteca (instalados) ou resultado de busca.
import QtQuick
import QtQuick.Layouts
import Konaro

KScrollPage {
    id: root
    property var ctl
    property string category: ""
    property string query: ""

    readonly property var items: {
        const all = ctl.apps
        const curated = all.filter(a => !a.full)
        if (category === "search") {
            const q = query.trim().toLowerCase()
            const key = "search:" + q
            const mine = curated.filter(a => a.name.toLowerCase().includes(q) || a.summaryText.toLowerCase().includes(q)
                                   || a.categoryText.toLowerCase().includes(q) || a.id.toLowerCase().includes(q))
            // resultados do catálogo completo para esta mesma busca
            return mine.concat(all.filter(a => a.full && a.source === key))
        }
        if (category === "installed") return all.filter(a => a.state === "installed")
        return curated.filter(a => a.category === category)
                      .concat(all.filter(a => a.full && a.source === "browse:" + category))
    }
    readonly property string heading: {
        if (category === "search") return i18n.tr("Results for “{q}”").replace("{q}", query.trim())
        if (category === "installed") return i18n.tr("Library")
        const c = ctl.categories.find(c => c.id === category)
        return c ? c.label : ""
    }

    ColumnLayout {
        width: parent.width
        spacing: Theme.s1
        KText { text: root.heading; heading: true; font.pixelSize: 30; font.letterSpacing: -0.6; Layout.fillWidth: true }
        KText {
            text: root.category === "installed"
                  ? i18n.tr("Apps from the Store that are on this computer.")
                  : i18n.tr("{n} apps").replace("{n}", root.items.length) + (store.loadingMore ? " · " + i18n.tr("searching the full catalog…") : "")
            secondary: true
            Layout.fillWidth: true
        }
    }

    GridLayout {
        width: parent.width
        columns: width > 1060 ? 3 : 2
        columnSpacing: Theme.s3
        rowSpacing: Theme.s1
        Repeater {
            model: root.items
            KAppRow {
                Layout.fillWidth: true
                app: modelData
                note: root.category === "search" ? modelData.categoryText : modelData.originText
                actionText: root.ctl.actionLabel(modelData)
                actionEnabled: root.ctl.actionEnabled(modelData)
                progress: root.ctl.progressFor(modelData)
                onOpened: root.ctl.showApp(modelData)
                onAction: root.ctl.primaryAction(modelData)
            }
        }
    }

    // estados vazios: dizem o que fazer, sem pedir desculpas
    ColumnLayout {
        visible: root.items.length === 0
        width: parent.width
        spacing: Theme.s2
        KIcon { name: root.category === "installed" ? "folder-download-symbolic" : "search"; tinted: true; color: Theme.stone; Layout.preferredWidth: 40; Layout.preferredHeight: 40; Layout.topMargin: Theme.s6 }
        KText {
            text: root.category === "installed" ? i18n.tr("No apps installed from the Store yet.")
                                                : i18n.tr("Nothing found for “{q}”.").replace("{q}", root.query.trim())
            font.pixelSize: 16; font.weight: Font.DemiBold; Layout.fillWidth: true
        }
        KText {
            text: root.category === "installed" ? i18n.tr("Start on the Home page — popular apps are a click away.")
                                                : i18n.tr("Try another name, or browse a category on the left.")
            secondary: true; Layout.fillWidth: true
        }
    }
}
