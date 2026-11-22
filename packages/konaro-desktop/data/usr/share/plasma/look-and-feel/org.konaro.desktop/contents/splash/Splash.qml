/*
 * Konaro OS — tela de boas-vindas exibida enquanto a sessão Plasma carrega.
 *
 * Mostra rapidamente "olá" em vários idiomas e termina em "Welcome to Konaro".
 * Por ser o splash do Plasma (ksplashqml), ela:
 *   - NÃO faz parte do boot nem da tela de login (não pode travar a inicialização);
 *   - fecha sozinha quando o Plasma termina de carregar, mesmo no meio da sequência;
 *   - pode ser desativada em Configurações > Aparência > Tela de abertura.
 * Se as animações estiverem desativadas no sistema, mostra apenas a mensagem final.
 *
 * A LISTA DE IDIOMAS É PROVISÓRIA (docs/PENDING.md). Ela usa apenas escritas
 * cobertas pelas fontes da imagem (latina, grega, cirílica).
 *
 * Licença: pendente (ver docs/LICENSES.md).
 */

import QtQuick
import org.kde.kirigami 2 as Kirigami

Rectangle {
    id: root
    color: "#0b0b0c"

    // Definido pelo ksplashqml conforme a sessão avança (1..6).
    property int stage

    readonly property var greetings: [
        "Olá", "Hello", "Hola", "Bonjour", "Ciao", "Hallo",
        "Привет", "Γεια σου", "Merhaba", "Hej", "Cześć"
    ]
    readonly property string finalMessage: "Welcome to Konaro"
    readonly property bool animationsEnabled: Kirigami.Units.longDuration > 1

    property int index: -1

    function advance() {
        if (index < greetings.length) {
            index += 1;
        } else {
            ticker.stop();
        }
    }

    Component.onCompleted: {
        if (animationsEnabled) {
            ticker.start();
        } else {
            index = greetings.length;
        }
    }

    Timer {
        id: ticker
        interval: 420
        repeat: true
        triggeredOnStart: true
        onTriggered: root.advance()
    }

    Text {
        id: word
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -Kirigami.Units.gridUnit
        text: root.index < 0 ? ""
            : (root.index < root.greetings.length ? root.greetings[root.index] : root.finalMessage)
        color: "#f5f5f7"
        font.family: "Inter"
        font.pixelSize: Math.round(Math.min(root.width, root.height) / 11)
        font.weight: root.index >= root.greetings.length ? Font.DemiBold : Font.Light
        Accessible.role: Accessible.StaticText
        Accessible.name: root.finalMessage

        onTextChanged: if (root.animationsEnabled) fadeIn.restart()
        NumberAnimation on opacity {
            id: fadeIn
            from: 0; to: 1
            duration: 260
            easing.type: Easing.OutCubic
        }
    }

    // Indicador discreto de progresso, alimentado pelos estágios reais do Plasma.
    Rectangle {
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: word.bottom
        anchors.topMargin: Kirigami.Units.gridUnit * 3
        width: Kirigami.Units.gridUnit * 10
        height: 3
        radius: 1.5
        color: "#2c2c2e"

        Rectangle {
            height: parent.height
            radius: parent.radius
            color: "#8e8e93"
            width: parent.width * Math.min(root.stage, 6) / 6
            Behavior on width {
                enabled: root.animationsEnabled
                NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
            }
        }
    }
}
