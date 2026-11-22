"""Infraestrutura comum das apps Konaro em QML.

- carrega o módulo de componentes `Konaro` (qml/Konaro) e a tela da app;
- expõe `i18n.tr()` para o QML (inglês -> português do Brasil);
- fornece `image://glow/<ícone>`: o ícone do app ampliado e desfocado, usado como
  "luz" atrás dos destaques (a única cor da interface vem dos apps);
- `--screenshot ARQUIVO` salva uma captura da janela (testes automatizados).
"""

import os
import sys

from PyQt6.QtCore import QObject, QSize, Qt, QTimer, QUrl, pyqtSlot
from PyQt6.QtGui import QColor, QGuiApplication, QIcon, QImage, QPainter, QRadialGradient
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuick import QQuickImageProvider, QQuickWindow, QSGRendererInterface

from . import i18n

QML_DIR = os.path.join(os.path.dirname(__file__), "qml")


class Translator(QObject):
    @pyqtSlot(str, result=str)
    def tr(self, text):
        return i18n._(text)

    @pyqtSlot(int, str, str, result=str)
    def plural(self, n, singular, plural):
        """Plural simples (pt e en): 1 → singular; demais → plural. Use {n} no texto."""
        return i18n._(singular if n == 1 else plural).replace("{n}", str(n))

    @pyqtSlot(result=str)
    def language(self):
        return i18n.LANG


def _theme_icon(name, size):
    if name.startswith("/") and os.path.exists(name):
        icon = QIcon(name)
    else:
        icon = QIcon.fromTheme(name)
    if icon.isNull():
        icon = QIcon.fromTheme("application-x-executable")
    return icon.pixmap(QSize(size, size)).toImage()


def _box_blur(buf, w, h, radius, passes=3):
    """Desfoque de caixa separável em ARGB premultiplicado (imagem pequena, Python puro)."""
    for _ in range(passes):
        for horizontal in (True, False):
            out = bytearray(len(buf))
            span = 2 * radius + 1
            outer, inner = (h, w) if horizontal else (w, h)
            for o in range(outer):
                for c in range(4):
                    acc = 0
                    idx = (lambda i: (o * w + i) * 4 + c) if horizontal else (lambda i: (i * w + o) * 4 + c)
                    for i in range(-radius, radius + 1):
                        acc += buf[idx(min(max(i, 0), inner - 1))]
                    for i in range(inner):
                        out[idx(i)] = acc // span
                        acc += buf[idx(min(i + radius + 1, inner - 1))] - buf[idx(max(i - radius, 0))]
            buf = out
    return buf


def make_glow(icon_image):
    """Gera a "luz" de um ícone: desfoque real + ampliação + esmaecimento radial."""
    small = QImage(72, 72, QImage.Format.Format_ARGB32_Premultiplied)
    small.fill(QColor(0, 0, 0, 0))
    painter = QPainter(small)
    painter.drawImage(16, 16, icon_image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied))
    painter.end()
    w, h = small.width(), small.height()
    raw = bytearray(small.constBits().asstring(small.sizeInBytes()))
    blurred = _box_blur(raw, w, h, radius=6)
    soft = QImage(bytes(blurred), w, h, w * 4, QImage.Format.Format_ARGB32_Premultiplied).copy()
    big = soft.scaled(512, 512, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    painter = QPainter(big)
    fade = QRadialGradient(256, 256, 256)
    fade.setColorAt(0.0, QColor(0, 0, 0, 255))
    fade.setColorAt(0.55, QColor(0, 0, 0, 190))
    fade.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.fillRect(big.rect(), fade)
    painter.end()
    return big


class GlowProvider(QQuickImageProvider):
    """Ícone ampliado com desfoque barato (reduz e amplia com suavização)."""

    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)
        self._cache = {}

    def requestImage(self, image_id, requested_size):
        name = image_id.split("?")[0]
        if name not in self._cache:
            self._cache[name] = make_glow(_theme_icon(name, 40))
        image = self._cache[name]
        return image, image.size()


def run(app_id, title, qml_file, context=None, screenshot=None, size=None):
    """Cria a aplicação, publica os objetos de `context` no QML e executa."""
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Software)
    # Os componentes Konaro desenham o próprio visual; o estilo "Basic" evita que o
    # estilo de controles do Plasma (org.kde.desktop) se misture a eles.
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    app.setApplicationName(app_id)
    app.setApplicationDisplayName(title)
    app.setDesktopFileName(app_id)
    app.setWindowIcon(QIcon.fromTheme(app_id, QIcon.fromTheme("konaro")))

    engine = QQmlApplicationEngine()
    engine.addImportPath(QML_DIR)
    engine.addImageProvider("glow", GlowProvider())
    translator = Translator()
    engine.rootContext().setContextProperty("i18n", translator)
    for name, obj in (context or {}).items():
        engine.rootContext().setContextProperty(name, obj)
    engine.load(QUrl.fromLocalFile(os.path.join(QML_DIR, qml_file)))
    if not engine.rootObjects():
        return 1
    window = engine.rootObjects()[0]
    if size:
        window.setWidth(size[0])
        window.setHeight(size[1])
    if screenshot:
        def grab():
            window.grabWindow().save(screenshot)
            app.quit()
        QTimer.singleShot(int(os.environ.get("KONARO_SHOT_DELAY", "3500")), grab)
    code = app.exec()
    # Destrói a interface antes dos objetos Python publicados no contexto,
    # para que as ligações QML não sejam reavaliadas com objetos já apagados.
    del window
    del engine          # o motor (e a janela) é destruído aqui, com o contexto ainda vivo
    del translator
    return code
