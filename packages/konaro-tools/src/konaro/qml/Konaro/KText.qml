import QtQuick

// Texto com as definições padrão do Konaro (Inter, cor de texto principal).
Text {
    property bool secondary: false
    property bool heading: false
    color: secondary ? Theme.stone : Theme.ink
    font.family: heading ? Theme.display : Theme.body
    font.pixelSize: Theme.sizeBody
    font.weight: heading ? Font.Bold : Font.Normal
    font.letterSpacing: heading ? -0.4 : 0
    wrapMode: Text.WordWrap
    textFormat: Text.PlainText
    linkColor: Theme.ink
    Accessible.role: Accessible.StaticText
    Accessible.name: text
}
