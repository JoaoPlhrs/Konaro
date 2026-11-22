/*
 * Konaro OS — layout padrão da área de trabalho (Plasma 6).
 *
 * Executado pelo plasmashell no primeiro login de cada usuário (ou ao aplicar
 * o tema global com "usar layout da área de trabalho").
 *
 *   Barra superior: lançador (logo Konaro) · menu global · ... · bandeja · relógio
 *   Dock inferior : flutuante, centralizado, do tamanho do conteúdo, desvia de janelas
 *
 * Licença: pendente (ver docs/LICENSES.md).
 */

// ---------------------------------------------------------------- barra superior
var top = new Panel;
top.location = "top";
top.height = 2 * Math.round(gridUnit * 1.6 / 2);
top.floating = false;
top.hiding = "none";
top.opacity = "translucent";   // vidro: o que flutua fica translúcido com desfoque

// Iniciar do Konaro (tela cheia, abre com a tecla Super/Windows)
var launcher = top.addWidget("org.konaro.launcher");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "konaro-start");

top.addWidget("org.kde.plasma.appmenu");
top.addWidget("org.kde.plasma.panelspacer");

// Teclados de idiomas asiáticos/índicos precisam do painel de método de entrada
// (mesma lista usada pelo layout padrão do Plasma).
var imeLanguages = ["as", "bn", "bo", "brx", "doi", "gu", "hi", "ja", "kn", "ko",
                    "kok", "ks", "lep", "mai", "ml", "mni", "mr", "ne", "or", "pa",
                    "sa", "sat", "sd", "si", "ta", "te", "th", "ur", "vi", "zh_CN", "zh_TW"];
if (imeLanguages.indexOf(languageId) != -1) {
    top.addWidget("org.kde.plasma.kimpanel");
}

top.addWidget("org.kde.plasma.systemtray");
var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateDisplayFormat", "1"); // 1 = BesideTime

// ----------------------------------------------------------------- dock inferior
var dock = new Panel;
dock.location = "bottom";
dock.height = 2 * Math.round(gridUnit * 3.9 / 2);
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "dodgewindows";
dock.opacity = "translucent";

// Dock: arquivos, navegador padrão, Loja, Steam (se instalado) e Configurações.
var launchers = ["applications:org.kde.dolphin.desktop", "preferred://browser"];
var optional = ["konaro-store.desktop", "com.valvesoftware.Steam.desktop", "net.lutris.Lutris.desktop"];
for (var i = 0; i < optional.length; i++) {
    if (applicationExists(optional[i])) {
        launchers.push("applications:" + optional[i]);
    }
}
launchers.push("applications:systemsettings.desktop");
// Na sessão live, o instalador aparece no dock. Após a instalação o Calamares é
// removido, então usuários do sistema instalado não recebem esse atalho.
if (applicationExists("konaro-install.desktop")) {
    launchers.unshift("applications:konaro-install.desktop");
}

// Dock Konaro: os ícones sobem e crescem sob o ponteiro (org.konaro.dock)
var tasks = dock.addWidget("org.konaro.dock");
tasks.currentConfigGroup = ["General"];
// lista de verdade (StringList); um texto com vírgulas viraria um único atalho inválido
tasks.writeConfig("launchers", launchers);

dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");

// -------------------------------------------------------------- papel de parede
var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = "org.kde.image";
    desktopsArray[j].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktopsArray[j].writeConfig("Image", "file:///usr/share/wallpapers/Konaro/");
}

// ------------------------------------------------------- widgets nos cantos
// Relógio (sup. esq.), calendário (sup. dir.) e notas (inf. dir.). O usuário pode
// removê-los (botão direito) ou ligar/desligar cada um — e outros, como o uso de
// memória — nas Boas-vindas. Mesmas posições usadas por konaro/desktopwidgets.py.
var cornerWidgets = [
    // widgets do Konaro em cartões (estilo dos widgets do macOS): pequeno 180, médio 370x180
    ["org.konaro.widget.clock", "top-left", 180, 180],
    ["org.konaro.widget.calendar", "top-right", 370, 180],
    ["org.konaro.widget.notes", "bottom-right", 180, 180]
];
for (var k = 0; k < desktopsArray.length; k++) {
    var d = desktopsArray[k];
    var g = screenGeometry(d.screen);
    for (var w = 0; w < cornerWidgets.length; w++) {
        var spec = cornerWidgets[w];
        var x = 32, y = 56;
        if (spec[1].indexOf("right") !== -1) x = g.width - 32 - spec[2];
        if (spec[1].indexOf("bottom") !== -1) y = g.height - 120 - spec[3];
        if (d.widgets(spec[0]).length === 0) {
            d.addWidget(spec[0], x, y, spec[2], spec[3]);
        }
    }
}
