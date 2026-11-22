import QtQuick
import org.kde.kirigami as Kirigami

// Ícone do tema do sistema (cores originais para ícones de apps;
// `tinted` recolore ícones simbólicos com a cor do texto).
Kirigami.Icon {
    property string name: ""
    property bool tinted: false
    source: name
    fallback: "application-x-executable"
    isMask: tinted
    color: tinted ? Theme.ink : "transparent"
    smooth: true
}
