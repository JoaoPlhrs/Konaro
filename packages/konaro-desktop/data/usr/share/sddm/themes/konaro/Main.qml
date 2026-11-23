/*
 * Konaro OS — tela de login (tema do SDDM).
 *
 * Layout inspirado na tela de login do macOS: papel de parede inteiro, data e hora
 * grandes no alto, e embaixo a foto, o nome e o campo de senha em pílula de vidro.
 * No canto superior direito: layout do teclado e o menu de energia.
 * Usa só QtQuick (sem Plasma) para abrir rápido e não depender da sessão.
 * Arte e código originais do projeto. Licença: pendente (ver docs/LICENSES.md).
 */
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Effects

Rectangle {
    id: root
    width: 1600
    height: 900
    color: "#1c1c1e"

    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0
    function t(ptText, enText) { return pt ? ptText : enText }
    readonly property real unit: Math.max(1, Math.min(width / 1600, height / 900))
    property int userIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property bool busy: false

    // ------------------------------------------------------------------ fundo
    Image {
        id: wallpaper
        anchors.fill: parent
        source: config.background || "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
        smooth: true
    }
    // leve escurecimento no topo e na base para o texto branco ler bem
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.22) }
            GradientStop { position: 0.35; color: Qt.rgba(0, 0, 0, 0.0) }
            GradientStop { position: 0.7; color: Qt.rgba(0, 0, 0, 0.0) }
            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.30) }
        }
    }

    // ------------------------------------------------------------- data e hora
    property date now: new Date()
    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.height * 0.085
        spacing: 2 * root.unit
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: {
                var s = Qt.locale().toString(root.now, root.pt ? "dddd, d 'de' MMMM" : "dddd, MMMM d")
                return s.charAt(0).toUpperCase() + s.slice(1)
            }
            color: Qt.rgba(1, 1, 1, 0.92)
            font.family: "Inter Display"
            font.pixelSize: 26 * root.unit
            font.weight: Font.DemiBold
        }
        Text {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(root.now, "hh:mm")
            color: Qt.rgba(1, 1, 1, 0.86)
            font.family: "Inter Display"
            font.pixelSize: 150 * root.unit
            font.weight: Font.Bold
            font.letterSpacing: -2 * root.unit
        }
    }

    // ------------------------------------------------- canto superior direito
    Row {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 14 * root.unit
        spacing: 18 * root.unit

        Text {
            anchors.verticalCenter: parent.verticalCenter
            visible: keyboard.layouts.length > 0
            text: {
                var l = keyboard.layouts[keyboard.currentLayout]
                if (!l) return ""
                var n = l.shortName === "br" ? "Brasileiro" : (l.shortName === "us" ? (root.pt ? "Inglês (EUA)" : "U.S.") : l.longName)
                return n + "  ⌨"
            }
            color: "white"
            font.family: "Inter"
            font.pixelSize: 13 * root.unit
            font.weight: Font.Medium
            MouseArea {
                anchors.fill: parent
                enabled: keyboard.layouts.length > 1
                cursorShape: Qt.PointingHandCursor
                onClicked: keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length
            }
        }
        Text {
            id: powerButton
            anchors.verticalCenter: parent.verticalCenter
            text: "⏻"
            color: "white"
            font.pixelSize: 16 * root.unit
            MouseArea {
                anchors.fill: parent
                anchors.margins: -8
                cursorShape: Qt.PointingHandCursor
                onClicked: powerMenu.visible = !powerMenu.visible
            }
        }
    }

    Rectangle {
        id: powerMenu
        visible: false
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 44 * root.unit
        anchors.rightMargin: 12 * root.unit
        width: 210 * root.unit
        height: menuColumn.implicitHeight + 12 * root.unit
        radius: 12 * root.unit
        color: Qt.rgba(0.96, 0.96, 0.97, 0.86)
        border.color: Qt.rgba(1, 1, 1, 0.5)
        z: 10
        Column {
            id: menuColumn
            anchors.fill: parent
            anchors.margins: 6 * root.unit
            Repeater {
                model: [
                    { label: root.t("Repousar", "Sleep"), ok: sddm.canSuspend, act: function() { sddm.suspend() } },
                    { label: root.t("Reiniciar", "Restart"), ok: sddm.canReboot, act: function() { sddm.reboot() } },
                    { label: root.t("Desligar", "Shut Down"), ok: sddm.canPowerOff, act: function() { sddm.powerOff() } }
                ]
                delegate: Rectangle {
                    width: menuColumn.width
                    height: 34 * root.unit
                    radius: 7 * root.unit
                    color: hov.hovered ? "#0A84FF" : "transparent"
                    opacity: modelData.ok ? 1 : 0.4
                    HoverHandler { id: hov }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        x: 12 * root.unit
                        text: modelData.label
                        color: hov.hovered ? "white" : "#1d1d1f"
                        font.family: "Inter"
                        font.pixelSize: 14 * root.unit
                    }
                    MouseArea {
                        anchors.fill: parent
                        enabled: modelData.ok
                        onClicked: modelData.act()
                    }
                }
            }
        }
    }

    // ------------------------------------------------------ usuário e senha
    ListView {
        id: users
        model: userModel
        currentIndex: root.userIndex
        orientation: ListView.Horizontal
        interactive: false
        spacing: 34 * root.unit
        width: Math.min(contentWidth, root.width * 0.8)
        height: 150 * root.unit
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: passwordBox.top
        anchors.bottomMargin: 12 * root.unit
        highlightFollowsCurrentItem: false

        delegate: Item {
            id: userDelegate
            readonly property bool current: index === root.userIndex
            readonly property string userName: model.name
            readonly property string displayName: model.realName && model.realName.length ? model.realName : model.name
            // a foto genérica do SDDM não conta: mostramos a inicial do nome, como no macOS
            readonly property string photo: model.icon && String(model.icon).indexOf("/usr/share/sddm/faces/") === -1 ? String(model.icon) : ""
            width: 120 * root.unit
            height: users.height
            opacity: current ? 1 : 0.7

            Item {
                id: avatar
                width: (current ? 64 : 52) * root.unit
                height: width
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: nameLabel.top
                anchors.bottomMargin: 10 * root.unit
                Behavior on width { NumberAnimation { duration: 160 } }

                Rectangle {
                    id: avatarBg
                    anchors.fill: parent
                    radius: width / 2
                    gradient: Gradient {
                        GradientStop { position: 0; color: "#A1A1A6" }
                        GradientStop { position: 1; color: "#6E6E73" }
                    }
                    border.color: Qt.rgba(1, 1, 1, 0.85)
                    border.width: 2
                    Text {
                        anchors.centerIn: parent
                        visible: face.status !== Image.Ready
                        text: userDelegate.displayName.charAt(0).toUpperCase()
                        color: "white"
                        font.family: "Inter Display"
                        font.weight: Font.DemiBold
                        font.pixelSize: parent.width * 0.44
                    }
                }
                Image {
                    id: face
                    anchors.fill: parent
                    anchors.margins: 2
                    source: userDelegate.photo ? (userDelegate.photo.indexOf("file:") === 0 ? userDelegate.photo : "file://" + userDelegate.photo) : ""
                    fillMode: Image.PreserveAspectCrop
                    visible: false
                }
                Rectangle {
                    id: faceMask
                    anchors.fill: face
                    radius: width / 2
                    visible: false
                    layer.enabled: true
                }
                MultiEffect {
                    anchors.fill: face
                    source: face
                    maskEnabled: true
                    maskSource: faceMask
                    visible: face.status === Image.Ready
                }
            }
            Text {
                id: nameLabel
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                text: userDelegate.displayName
                color: "white"
                font.family: "Inter"
                font.weight: Font.DemiBold
                font.pixelSize: 15 * root.unit
                style: Text.Raised
                styleColor: Qt.rgba(0, 0, 0, 0.25)
            }
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: { root.userIndex = index; password.text = ""; password.forceActiveFocus() }
            }
        }
    }

    // pílula de vidro com o campo de senha
    Item {
        id: passwordBox
        width: 200 * root.unit
        height: 30 * root.unit
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: hint.top
        anchors.bottomMargin: 14 * root.unit

        // vidro: recorte desfocado do papel de parede atrás da pílula
        ShaderEffectSource {
            id: behind
            sourceItem: wallpaper
            sourceRect: Qt.rect(passwordBox.x, passwordBox.y, passwordBox.width, passwordBox.height)
            anchors.fill: parent
            visible: false
        }
        Rectangle {
            id: pillMask
            anchors.fill: parent
            radius: height / 2
            visible: false
            layer.enabled: true
        }
        MultiEffect {
            anchors.fill: parent
            source: behind
            blurEnabled: true
            blur: 1.0
            blurMax: 32
            maskEnabled: true
            maskSource: pillMask
        }
        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: Qt.rgba(1, 1, 1, password.activeFocus ? 0.30 : 0.24)
            border.color: Qt.rgba(1, 1, 1, 0.35)
            border.width: 1
        }

        TextField {
            id: password
            anchors.fill: parent
            leftPadding: 14 * root.unit
            rightPadding: 34 * root.unit
            verticalAlignment: TextInput.AlignVCenter
            echoMode: TextInput.Password
            passwordCharacter: "●"
            placeholderText: root.t("Digite a Senha", "Enter Password")
            placeholderTextColor: Qt.rgba(1, 1, 1, 0.75)
            color: "white"
            selectionColor: Qt.rgba(1, 1, 1, 0.4)
            font.family: "Inter"
            font.pixelSize: 13 * root.unit
            background: Item {}
            focus: true
            enabled: !root.busy
            Keys.onEscapePressed: { text = ""; powerMenu.visible = false }
            onAccepted: root.login()
        }
        // seta "entrar", aparece quando há texto
        Rectangle {
            anchors.right: parent.right
            anchors.rightMargin: 4 * root.unit
            anchors.verticalCenter: parent.verticalCenter
            width: 22 * root.unit
            height: width
            radius: width / 2
            color: Qt.rgba(1, 1, 1, 0.35)
            visible: password.text.length > 0
            Text {
                anchors.centerIn: parent
                text: "→"
                color: "white"
                font.pixelSize: 13 * root.unit
                font.weight: Font.Bold
            }
            MouseArea { anchors.fill: parent; onClicked: root.login() }
        }

        SequentialAnimation {
            id: shake
            loops: 1
            NumberAnimation { target: passwordBox; property: "anchors.horizontalCenterOffset"; to: -14; duration: 60 }
            NumberAnimation { target: passwordBox; property: "anchors.horizontalCenterOffset"; to: 12; duration: 70 }
            NumberAnimation { target: passwordBox; property: "anchors.horizontalCenterOffset"; to: -8; duration: 70 }
            NumberAnimation { target: passwordBox; property: "anchors.horizontalCenterOffset"; to: 5; duration: 60 }
            NumberAnimation { target: passwordBox; property: "anchors.horizontalCenterOffset"; to: 0; duration: 50 }
        }
    }

    // ------------------------------------------------ sessão (ambiente gráfico)
    // Canto inferior esquerdo: escolher Wayland, X11 ou outro ambiente instalado
    // (ex.: GNOME, Xfce). Só aparece quando há mais de uma opção.
    function sessionLabel(name) {
        return (name || "").replace("Plasma", "Konaro")
    }
    Text {
        id: sessionButton
        visible: sessionRepeater.count > 1
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 18 * root.unit
        property string current: ""
        text: "▴  " + (current || root.t("Sessão", "Session"))
        color: Qt.rgba(1, 1, 1, 0.85)
        font.family: "Inter"
        font.pixelSize: 12 * root.unit
        MouseArea {
            anchors.fill: parent; anchors.margins: -8
            cursorShape: Qt.PointingHandCursor
            onClicked: sessionMenu.visible = !sessionMenu.visible
        }
    }
    Rectangle {
        id: sessionMenu
        visible: false
        anchors.left: parent.left
        anchors.bottom: sessionButton.top
        anchors.leftMargin: 12 * root.unit
        anchors.bottomMargin: 8 * root.unit
        width: 240 * root.unit
        height: sessionColumn.implicitHeight + 12 * root.unit
        radius: 12 * root.unit
        color: Qt.rgba(0.96, 0.96, 0.97, 0.86)
        border.color: Qt.rgba(1, 1, 1, 0.5)
        z: 10
        Column {
            id: sessionColumn
            anchors.fill: parent
            anchors.margins: 6 * root.unit
            Repeater {
                id: sessionRepeater
                model: sessionModel
                delegate: Rectangle {
                    width: sessionColumn.width
                    height: 34 * root.unit
                    radius: 7 * root.unit
                    readonly property bool sel: index === root.sessionIndex
                    color: hovS.hovered ? "#0A84FF" : "transparent"
                    HoverHandler { id: hovS }
                    Component.onCompleted: if (sel) sessionButton.current = root.sessionLabel(model.name)
                    onSelChanged: if (sel) sessionButton.current = root.sessionLabel(model.name)
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        x: 12 * root.unit
                        text: (parent.sel ? "✓  " : "    ") + root.sessionLabel(model.name)
                        color: hovS.hovered ? "white" : "#1d1d1f"
                        font.family: "Inter"
                        font.pixelSize: 14 * root.unit
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: { root.sessionIndex = index; sessionMenu.visible = false; password.forceActiveFocus() }
                    }
                }
            }
        }
    }

    Text {
        id: hint
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: root.height * 0.07
        text: root.busy ? root.t("Entrando…", "Logging in…") : (failed ? root.t("Senha incorreta. Tente de novo.", "Incorrect password. Try again.") : " ")
        property bool failed: false
        color: Qt.rgba(1, 1, 1, 0.85)
        font.family: "Inter"
        font.pixelSize: 12 * root.unit
    }

    function login() {
        var item = users.itemAtIndex(root.userIndex)
        if (!item || root.busy) return
        root.busy = true
        hint.failed = false
        sddm.login(item.userName, password.text, root.sessionIndex)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.busy = false
            hint.failed = true
            password.text = ""
            password.forceActiveFocus()
            shake.start()
        }
        function onLoginSucceeded() { root.busy = false }
    }

    MouseArea {
        anchors.fill: parent
        z: -1
        onClicked: { powerMenu.visible = false; sessionMenu.visible = false; password.forceActiveFocus() }
    }

    Component.onCompleted: password.forceActiveFocus()
}
