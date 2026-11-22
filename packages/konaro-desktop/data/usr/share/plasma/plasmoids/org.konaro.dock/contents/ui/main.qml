/*
 * Konaro OS — Dock.
 *
 * Gerenciador de tarefas em forma de dock: atalhos fixados e apps abertos no mesmo
 * lugar. Sob o ponteiro, cada ícone sobe e cresce; os vizinhos acompanham numa
 * curva suave (como no macOS). Tudo acontece dentro da altura do painel.
 *
 * Usa o mesmo modelo de tarefas do Plasma (org.kde.taskmanager), então funciona com
 * os atalhos de teclado, a busca e a lista de janelas do sistema.
 * Licença: pendente (ver docs/LICENSES.md).
 */
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.extras as PlasmaExtras
import org.kde.kirigami as Kirigami
import org.kde.taskmanager as TaskManager

PlasmoidItem {
    id: dock

    readonly property bool vertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical
    readonly property real thickness: vertical ? width : height
    readonly property real iconBase: Math.round(thickness * 0.62)
    readonly property real gap: Math.round(iconBase * 0.24)
    readonly property real zoom: Plasmoid.configuration.magnification / 100
    readonly property bool animate: Kirigami.Units.longDuration > 1

    preferredRepresentation: fullRepresentation

    // Atalhos salvos. Aceita também uma entrada única "a,b,c" (gravada como texto por
    // scripts antigos), que de outro modo viraria um atalho inválido com ícone em branco.
    function launchersFromConfig() {
        const out = []
        const saved = Plasmoid.configuration.launchers || []
        for (let i = 0; i < saved.length; ++i) {
            const parts = String(saved[i]).split(",")
            for (let j = 0; j < parts.length; ++j) {
                const url = parts[j].trim()
                if (url.length > 0 && out.indexOf(url) === -1) out.push(url)
            }
        }
        return out
    }

    TaskManager.VirtualDesktopInfo { id: desktopInfo }
    TaskManager.ActivityInfo { id: activityInfo }

    TaskManager.TasksModel {
        id: tasksModel
        virtualDesktop: desktopInfo.currentDesktop
        screenGeometry: Plasmoid.containment.screenGeometry
        activity: activityInfo.currentActivity
        filterByVirtualDesktop: false
        filterByScreen: false
        filterByActivity: true
        sortMode: TaskManager.TasksModel.SortManual
        groupMode: TaskManager.TasksModel.GroupApplications
        groupInline: false
        separateLaunchers: false
        launchInPlace: true
        hideActivatedLaunchers: true
        onLauncherListChanged: Plasmoid.configuration.launchers = launcherList
        Component.onCompleted: launcherList = dock.launchersFromConfig()
    }

    // A configuração pode mudar depois que o dock já existe (ex.: o layout padrão grava
    // os atalhos logo após criar o applet, ou o usuário fixa um app).
    Connections {
        target: Plasmoid.configuration
        function onLaunchersChanged() {
            const wanted = dock.launchersFromConfig()
            if (JSON.stringify(tasksModel.launcherList) !== JSON.stringify(wanted)) {
                tasksModel.launcherList = wanted
            }
        }
    }

    fullRepresentation: Item {
        id: rep
        // posição do ponteiro ao longo do dock (-1 = fora)
        readonly property real pointer: hover.hovered ? (dock.vertical ? hover.point.position.y : hover.point.position.x) : -1
        Layout.preferredWidth: dock.vertical ? -1 : row.implicitWidth + dock.gap * 2
        Layout.minimumWidth: dock.vertical ? -1 : row.implicitWidth + dock.gap * 2
        Layout.preferredHeight: dock.vertical ? row.implicitHeight + dock.gap * 2 : -1
        Layout.minimumHeight: dock.vertical ? row.implicitHeight + dock.gap * 2 : -1
        Layout.fillHeight: !dock.vertical
        Layout.fillWidth: dock.vertical

        HoverHandler { id: hover }

        Grid {
            id: row
            anchors.centerIn: parent
            rows: dock.vertical ? -1 : 1
            columns: dock.vertical ? 1 : -1
            spacing: dock.gap

            Repeater {
                id: tasks
                model: tasksModel

                delegate: Item {
                    id: task
                    required property var model
                    required property int index

                    width: dock.vertical ? dock.thickness : dock.iconBase
                    height: dock.vertical ? dock.iconBase : dock.thickness

                    readonly property real center: dock.vertical ? row.y + y + height / 2 : row.x + x + width / 2
                    readonly property real reach: dock.iconBase * 2.4
                    readonly property real distance: rep.pointer < 0 ? 1e9 : Math.abs(rep.pointer - center)
                    // 1 sob o ponteiro, caindo suavemente até 0 a ~2,4 ícones de distância
                    readonly property real influence: distance >= reach ? 0 : (Math.cos(Math.PI * distance / reach) + 1) / 2
                    readonly property real grow: 1 + dock.zoom * influence
                    readonly property real rise: dock.iconBase * 0.16 * influence

                    Accessible.role: Accessible.Button
                    Accessible.name: model.display || ""

                    Kirigami.Icon {
                        id: icon
                        source: model.decoration
                        width: dock.iconBase
                        height: dock.iconBase
                        active: mouse.containsMouse
                        scale: task.grow
                        transformOrigin: dock.vertical ? Item.Left : Item.Bottom
                        x: dock.vertical ? Math.round(dock.thickness * 0.14) + task.rise : 0
                        y: dock.vertical ? 0 : task.height - height - Math.round(dock.thickness * 0.14) - task.rise
                        Behavior on scale { enabled: dock.animate; NumberAnimation { duration: 110; easing.type: Easing.OutCubic } }
                        Behavior on y { enabled: dock.animate && !dock.vertical; NumberAnimation { duration: 110; easing.type: Easing.OutCubic } }
                        Behavior on x { enabled: dock.animate && dock.vertical; NumberAnimation { duration: 110; easing.type: Easing.OutCubic } }
                    }

                    // abrindo: o ícone pulsa de leve
                    SequentialAnimation {
                        running: dock.animate && task.model.IsStartup === true
                        loops: Animation.Infinite
                        NumberAnimation { target: icon; property: "opacity"; to: 0.55; duration: 380 }
                        NumberAnimation { target: icon; property: "opacity"; to: 1; duration: 380 }
                        onStopped: icon.opacity = 1
                    }

                    // ponto de app aberto (mais forte quando é a janela ativa)
                    Rectangle {
                        visible: !task.model.IsLauncher && !task.model.IsStartup
                        width: 5; height: 5; radius: 2.5
                        color: Kirigami.Theme.textColor
                        opacity: task.model.IsActive ? 0.95 : 0.5
                        x: dock.vertical ? 2 : (parent.width - width) / 2
                        y: dock.vertical ? (parent.height - height) / 2 : parent.height - height - 2
                    }

                    PlasmaCore.ToolTipArea {
                        anchors.fill: parent
                        mainText: task.model.display || ""
                        location: Plasmoid.location
                        interactive: false

                        MouseArea {
                            id: mouse
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
                            onClicked: (event) => {
                                const idx = tasksModel.makeModelIndex(task.index)
                                if (event.button === Qt.RightButton) {
                                    menu.openFor(task)
                                } else if (event.button === Qt.MiddleButton) {
                                    tasksModel.requestNewInstance(idx)
                                } else if (task.model.IsLauncher) {
                                    tasksModel.requestActivate(idx)
                                } else if (task.model.IsActive && (task.model.ChildCount || 0) <= 1) {
                                    tasksModel.requestToggleMinimized(idx)
                                } else {
                                    tasksModel.requestActivate(idx)
                                }
                            }
                        }
                    }
                }
            }
        }

        // ------------------------------------------------ menu de contexto
        PlasmaExtras.Menu {
            id: menu
            property var target: null
            readonly property string launcher: target ? (target.model.LauncherUrlWithoutIcon || "").toString() : ""
            readonly property bool pinned: launcher !== "" && tasksModel.launcherPosition(launcher) !== -1

            function openFor(item) {
                target = item
                visualParent = item
                openRelative()
            }

            PlasmaExtras.MenuItem {
                text: Qt.locale().name.startsWith("pt") ? "Abrir nova janela" : "Open new window"
                icon: "window-new"
                onClicked: tasksModel.requestNewInstance(tasksModel.makeModelIndex(menu.target.index))
            }
            PlasmaExtras.MenuItem {
                visible: menu.launcher !== ""
                text: menu.pinned ? (Qt.locale().name.startsWith("pt") ? "Remover do dock" : "Unpin from dock")
                                  : (Qt.locale().name.startsWith("pt") ? "Manter no dock" : "Keep in dock")
                icon: menu.pinned ? "window-unpin" : "window-pin"
                onClicked: menu.pinned ? tasksModel.requestRemoveLauncher(menu.launcher)
                                       : tasksModel.requestAddLauncher(menu.launcher)
            }
            PlasmaExtras.MenuItem {
                visible: menu.target !== null && menu.target.model.IsWindow === true
                text: Qt.locale().name.startsWith("pt") ? "Fechar" : "Close"
                icon: "window-close"
                onClicked: tasksModel.requestClose(tasksModel.makeModelIndex(menu.target.index))
            }
        }
    }
}
