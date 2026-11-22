/*
 * Konaro OS — apresentação exibida enquanto o sistema é copiado para o disco.
 * Ocupa a espera com o que a pessoa vai encontrar ao terminar.
 * Licença: pendente (ver docs/LICENSES.md).
 */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation
    readonly property bool pt: Qt.locale().name.indexOf("pt") === 0
    readonly property string icons: "file:///usr/share/konaro/store/icons/"

    Timer {
        interval: 12000
        repeat: true
        running: presentation.activatedInCalamares
        onTriggered: presentation.goToNextSlide()
    }

    component Slide2: Slide {
        id: s
        property string heading
        property string body
        property var images: []
        Rectangle { anchors.fill: parent; color: "#F5F5F7" }
        Column {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 64
            width: parent.width - 128
            spacing: 18
            Row {
                spacing: 14
                visible: s.images.length > 0
                Repeater {
                    model: s.images
                    Image { source: modelData; width: 64; height: 64; sourceSize.width: 128; sourceSize.height: 128; smooth: true }
                }
            }
            Text {
                text: s.heading
                width: parent.width
                wrapMode: Text.WordWrap
                color: "#1D1D1F"
                font.family: "Inter Display"
                font.pixelSize: 34
                font.weight: Font.Bold
                font.letterSpacing: -0.6
            }
            Text {
                text: s.body
                width: Math.min(parent.width, 560)
                wrapMode: Text.WordWrap
                color: "#6E6E73"
                font.family: "Inter"
                font.pixelSize: 16
                lineHeight: 1.25
            }
        }
    }

    Slide2 {
        images: ["file:///usr/share/icons/hicolor/scalable/apps/konaro.svg"]
        heading: presentation.pt ? "Instalando o Konaro OS" : "Installing Konaro OS"
        body: presentation.pt ? "Isso leva alguns minutos e acontece sozinho. Enquanto isso, conheça o que vem por aí."
                              : "This takes a few minutes and happens on its own. Meanwhile, here is what is waiting for you."
    }
    Slide2 {
        images: [presentation.icons + "firefox-esr.png", presentation.icons + "libreoffice.png",
                 presentation.icons + "com.spotify.Client.png", presentation.icons + "vlc.png"]
        heading: presentation.pt ? "A Loja tem o que você precisa" : "The Store has what you need"
        body: presentation.pt ? "Navegadores, escritório, música, vídeo e muito mais. Um clique para instalar, outro para abrir."
                              : "Browsers, office, music, video and much more. One click to install, another to open."
    }
    Slide2 {
        images: [presentation.icons + "com.valvesoftware.Steam.png", presentation.icons + "lutris.png",
                 presentation.icons + "com.usebottles.bottles.png", presentation.icons + "wine.png"]
        heading: presentation.pt ? "Jogos e programas do Windows" : "Games and Windows programs"
        body: presentation.pt ? "O Steam com Proton roda milhares de jogos do Windows. Para outros programas, dois cliques no .exe abrem com o Wine."
                              : "Steam with Proton runs thousands of Windows games. For other programs, double-click the .exe to open it with Wine."
    }
    Slide2 {
        images: ["file:///usr/share/icons/hicolor/scalable/apps/konaro-updater.svg"]
        heading: presentation.pt ? "Sempre atualizado, do seu jeito" : "Up to date, on your terms"
        body: presentation.pt ? "O Konaro avisa quando há atualizações e você escolhe quando instalar. Nada muda sem a sua permissão."
                              : "Konaro tells you when updates are available and you choose when to install. Nothing changes without your permission."
    }

    function onActivate() { }
    function onLeave() { }
}
