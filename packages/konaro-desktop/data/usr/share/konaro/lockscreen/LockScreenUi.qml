/*
 * Konaro OS — tela de bloqueio (aparece ao bloquear, ao suspender e ao voltar).
 *
 * Mesmo desenho da tela de login do Konaro: o papel de parede (desenhado pelo
 * próprio bloqueador, atrás desta interface), data e hora grandes no alto, a foto
 * e o nome do usuário e o campo de senha em pílula de vidro embaixo.
 *
 * Substitui SOMENTE a interface (LockScreenUi.qml) do bloqueador do Plasma, via
 * dpkg-divert; a autenticação continua sendo a do KDE (PAM), pelo objeto
 * "authenticator" do kscreenlocker. Código original do Konaro OS.
 */
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.private.sessions as Sessions

Item {
    id: ui

    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0
    function t(a, b) { return pt ? a : b }
    readonly property real unit: Math.max(1, Math.min(width / 1600, height / 900))
    property bool busy: false
    property bool failed: false

    // leve escurecimento para o texto branco ler bem sobre qualquer papel de parede
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.42) }
            GradientStop { position: 0.4; color: Qt.rgba(0, 0, 0, 0.12) }
            GradientStop { position: 0.7; color: Qt.rgba(0, 0, 0, 0.12) }
            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.5) }
        }
    }

    Sessions.SessionManagement { id: sessions }
    Connections {
        target: sessions
        function onAboutToSuspend() { password.text = "" }
    }
    Connections {
        target: root
        function onClearPassword() { password.text = ""; password.forceActiveFocus() }
    }

    Connections {
        target: authenticator
        function onFailed(kind) {
            if (kind !== 0) return            // autenticadores sem senha (ex.: digital) não contam
            ui.busy = false
            ui.failed = true
            password.text = ""
            shake.start()
            retry.restart()
        }
        function onSucceeded() { Qt.quit() }
        function onPromptForSecretChanged() { password.forceActiveFocus() }
    }
    Timer { id: retry; interval: 1500; onTriggered: authenticator.startAuthenticating() }

    // o teclado virtual do Qt abriria sozinho ao focar a senha; num computador com
    // teclado físico ele só atrapalha, então fica escondido
    Connections {
        target: Qt.inputMethod
        function onVisibleChanged() { if (Qt.inputMethod.visible) Qt.inputMethod.hide() }
    }

    // ---------------------------------------------------------- data e hora
    property date now: new Date()
    Timer { interval: 1000; running: true; repeat: true; onTriggered: ui.now = new Date() }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: ui.height * 0.085
        spacing: 2 * ui.unit
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: {
                const s = Qt.locale().toString(ui.now, ui.pt ? "dddd, d 'de' MMMM" : "dddd, MMMM d")
                return s.charAt(0).toUpperCase() + s.slice(1)
            }
            color: Qt.rgba(1, 1, 1, 0.92)
            font.family: "Inter Display"
            font.pixelSize: 26 * ui.unit
            font.weight: Font.DemiBold
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(ui.now, "hh:mm")
            color: Qt.rgba(1, 1, 1, 0.88)
            font.family: "Inter Display"
            font.pixelSize: 150 * ui.unit
            font.weight: Font.Bold
            font.letterSpacing: -2 * ui.unit
        }
    }

    // ------------------------------------------------------- canto direito
    Row {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 16 * ui.unit
        spacing: 18 * ui.unit
        Text {
            visible: root.suspendToRamSupported
            text: ui.t("Repousar", "Sleep")
            color: "white"
            font.pixelSize: 13 * ui.unit
            font.weight: Font.Medium
            MouseArea { anchors.fill: parent; anchors.margins: -6; cursorShape: Qt.PointingHandCursor; onClicked: root.suspendToRam() }
        }
    }

    // ------------------------------------------------- usuário e senha
    Column {
        id: who
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: pill.top
        anchors.bottomMargin: 14 * ui.unit
        spacing: 10 * ui.unit

        Item {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 68 * ui.unit; height: width
            Rectangle {
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
                    text: (kscreenlocker_userName || "?").charAt(0).toUpperCase()
                    color: "white"
                    font.pixelSize: parent.width * 0.44
                    font.weight: Font.DemiBold
                }
            }
            Kirigami.ShadowedImage {
                id: face
                anchors.fill: parent
                anchors.margins: 2
                radius: width / 2
                source: kscreenlocker_userImage !== ""
                        ? "file://" + kscreenlocker_userImage.split("/").map(encodeURIComponent).join("/") : ""
                fillMode: Image.PreserveAspectCrop
                visible: status === Image.Ready
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: kscreenlocker_userName
            color: "white"
            font.pixelSize: 15 * ui.unit
            font.weight: Font.DemiBold
            style: Text.Raised
            styleColor: Qt.rgba(0, 0, 0, 0.25)
        }
    }

    Rectangle {
        id: pill
        width: 210 * ui.unit
        height: 32 * ui.unit
        radius: height / 2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: hint.top
        anchors.bottomMargin: 14 * ui.unit
        color: Qt.rgba(1, 1, 1, password.activeFocus ? 0.30 : 0.24)
        border.color: Qt.rgba(1, 1, 1, 0.38)

        TextInput {
            id: password
            anchors.fill: parent
            anchors.leftMargin: 14 * ui.unit
            anchors.rightMargin: 34 * ui.unit
            verticalAlignment: TextInput.AlignVCenter
            echoMode: TextInput.Password
            passwordCharacter: "●"
            color: "white"
            selectionColor: Qt.rgba(1, 1, 1, 0.4)
            font.pixelSize: 13 * ui.unit
            focus: true
            enabled: !ui.busy
            onAccepted: ui.submit()
            Keys.onEscapePressed: text = ""
            Text {
                anchors.verticalCenter: parent.verticalCenter
                visible: password.text.length === 0
                text: ui.t("Digite a Senha", "Enter Password")
                color: Qt.rgba(1, 1, 1, 0.75)
                font.pixelSize: 13 * ui.unit
            }
        }
        Rectangle {
            anchors.right: parent.right
            anchors.rightMargin: 4 * ui.unit
            anchors.verticalCenter: parent.verticalCenter
            width: 24 * ui.unit; height: width; radius: width / 2
            color: Qt.rgba(1, 1, 1, 0.35)
            visible: password.text.length > 0
            Text { anchors.centerIn: parent; text: "→"; color: "white"; font.pixelSize: 13 * ui.unit; font.bold: true }
            MouseArea { anchors.fill: parent; onClicked: ui.submit() }
        }
        SequentialAnimation {
            id: shake
            NumberAnimation { target: pill; property: "anchors.horizontalCenterOffset"; to: -14; duration: 60 }
            NumberAnimation { target: pill; property: "anchors.horizontalCenterOffset"; to: 12; duration: 70 }
            NumberAnimation { target: pill; property: "anchors.horizontalCenterOffset"; to: -8; duration: 70 }
            NumberAnimation { target: pill; property: "anchors.horizontalCenterOffset"; to: 0; duration: 60 }
        }
    }

    Text {
        id: hint
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: ui.height * 0.07
        text: ui.busy ? ui.t("Desbloqueando…", "Unlocking…")
              : ui.failed ? ui.t("Senha incorreta. Tente de novo.", "Incorrect password. Try again.")
              : (root.notification || " ")
        color: Qt.rgba(1, 1, 1, 0.85)
        font.pixelSize: 12 * ui.unit
    }

    function submit() {
        if (ui.busy) return
        ui.busy = true
        ui.failed = false
        authenticator.respond(password.text)
    }

    Component.onCompleted: {
        authenticator.startAuthenticating()
        password.forceActiveFocus()
    }
}
