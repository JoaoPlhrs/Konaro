// Konaro — tokens do sistema de design (ver docs/design/DESIGN.md).
// Segue o esquema de cores do sistema: Konaro Claro ou Konaro Escuro.
pragma Singleton
import QtQuick

QtObject {
    id: theme

    property SystemPalette palette: SystemPalette { colorGroup: SystemPalette.Active }
    readonly property bool dark: {
        const c = palette.window
        return (0.299 * c.r + 0.587 * c.g + 0.114 * c.b) < 0.5
    }

    // ---- cores
    readonly property color paper:    dark ? "#161618" : "#F5F5F7"
    readonly property color surface:  dark ? "#1F1F22" : "#FFFFFF"
    readonly property color raised:   dark ? "#2A2A2E" : "#FFFFFF"
    readonly property color rail:     dark ? "#1B1B1E" : "#ECECEF"
    readonly property color ink:      dark ? "#F5F5F7" : "#1D1D1F"
    readonly property color stone:    dark ? "#A1A1A6" : "#6E6E73"
    readonly property color hairline: dark ? "#38383C" : "#D2D2D7"
    readonly property color fill:     dark ? "#2C2C30" : "#E8E8ED"
    readonly property color inverse:    dark ? "#161618" : "#FFFFFF"
    readonly property color success:  dark ? "#32D74B" : "#1F8A4C"
    readonly property color danger:   dark ? "#FF6961" : "#C42B1C"
    readonly property color scrim:    dark ? Qt.rgba(0, 0, 0, 0.55) : Qt.rgba(0.11, 0.11, 0.12, 0.28)

    // ---- tipografia
    readonly property string display: "Inter Display"
    readonly property string body: "Inter"
    readonly property int sizeHero: 34
    readonly property int sizeTitle: 24
    readonly property int sizeHeading: 18
    readonly property int sizeBody: 14
    readonly property int sizeSmall: 12
    readonly property int sizeTiny: 11

    // ---- forma e espaço
    readonly property int radiusHero: 20
    readonly property int radiusBlock: 16
    readonly property int radiusCard: 14
    readonly property int radiusControl: 10
    readonly property int s1: 4
    readonly property int s2: 8
    readonly property int s3: 12
    readonly property int s4: 16
    readonly property int s5: 24
    readonly property int s6: 32
    readonly property int s7: 48

    // ---- movimento (zero quando o sistema pede animações reduzidas)
    property bool reducedMotion: false
    readonly property int quick: reducedMotion ? 0 : 140
    readonly property int smooth: reducedMotion ? 0 : 240
}
