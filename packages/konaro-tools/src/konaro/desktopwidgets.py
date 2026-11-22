"""Widgets da área de trabalho nos cantos da tela (relógio, calendário, monitor, notas…).

O usuário escolhe quais quer nas Boas-vindas; também pode removê-los ou adicionar
outros pelo próprio Plasma (botão direito na área de trabalho > Adicionar widgets).
As mudanças são aplicadas ao vivo pelo motor de scripts do plasmashell.
"""

import json
import subprocess

# id, plugin do Plasma, canto, largura, altura, ligado por padrão
WIDGETS = [
    {"id": "clock", "plugin": "org.konaro.widget.clock", "corner": "top-left",
     "width": 180, "height": 180, "default": True,
     "name": "Clock", "description": "An analog clock in the top left corner.", "icon": "preferences-system-time"},
    {"id": "calendar", "plugin": "org.konaro.widget.calendar", "corner": "top-right",
     "width": 370, "height": 180, "default": True,
     "name": "Calendar", "description": "This month at a glance, in the top right corner.", "icon": "view-calendar"},
    {"id": "monitor", "plugin": "org.konaro.widget.system", "corner": "bottom-left",
     "width": 180, "height": 180, "default": False,
     "name": "System", "description": "CPU, memory and disk usage at a glance.", "icon": "utilities-system-monitor"},
    {"id": "notes", "plugin": "org.konaro.widget.notes", "corner": "bottom-right",
     "width": 180, "height": 180, "default": True,
     "name": "Notes", "description": "A sticky note for quick reminders.", "icon": "knotes"},
    {"id": "media", "plugin": "org.kde.plasma.mediacontroller", "corner": "bottom-left-high",
     "width": 300, "height": 140, "default": False,
     "name": "Now playing", "description": "Controls for the music or video that is playing.", "icon": "media-playback-start"},
]

_PLACE_JS = """
function konaroPlace(d, plugin, corner, w, h) {
    var g = screenGeometry(d.screen);
    var top = 56, side = 32, bottom = 120;
    var x = side, y = top;
    if (corner.indexOf("right") !== -1) x = g.width - side - w;
    if (corner.indexOf("bottom") !== -1) y = g.height - bottom - h;
    if (corner === "bottom-left-high") y = g.height - bottom - h - 200;
    return d.addWidget(plugin, x, y, w, h);
}
"""


def _evaluate(script):
    try:
        result = subprocess.run(
            ["qdbus6", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script],
            capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def current():
    """{id: ligado?} conforme o que está na área de trabalho agora (None se indisponível)."""
    plugins = json.dumps([w["plugin"] for w in WIDGETS])
    out = _evaluate("""
var plugins = %s; var found = {};
var ds = desktops();
for (var i = 0; i < ds.length; i++)
    for (var p = 0; p < plugins.length; p++)
        if (ds[i].widgets(plugins[p]).length > 0) found[plugins[p]] = true;
print(JSON.stringify(found));
""" % plugins)
    if out is None:
        return None
    try:
        found = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None
    return {w["id"]: bool(found.get(w["plugin"])) for w in WIDGETS}


def set_enabled(widget_id, enabled):
    widget = next((w for w in WIDGETS if w["id"] == widget_id), None)
    if widget is None:
        return False
    script = _PLACE_JS + """
var ds = desktops();
for (var i = 0; i < ds.length; i++) {
    var d = ds[i];
    var existing = d.widgets(%s);
    if (%s && existing.length === 0) konaroPlace(d, %s, %s, %d, %d);
    if (!%s) for (var j = 0; j < existing.length; j++) existing[j].remove();
}
""" % (json.dumps(widget["plugin"]), "true" if enabled else "false", json.dumps(widget["plugin"]),
       json.dumps(widget["corner"]), widget["width"], widget["height"], "true" if enabled else "false")
    return _evaluate(script) is not None
