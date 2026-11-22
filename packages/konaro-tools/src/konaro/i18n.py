"""Traduções das ferramentas Konaro (inglês -> português do Brasil).

Os textos no código-fonte estão em inglês; se o idioma da sessão for
português, `_()` devolve a tradução. Idiomas da 1ª versão: en e pt_BR.
"""

import os


def _detect_language():
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if value:
            return "pt" if value.lower().startswith("pt") else "en"
    return "en"


LANG = _detect_language()


def set_language(lang):
    global LANG
    LANG = "pt" if str(lang).lower().startswith("pt") else "en"


def _(text):
    if LANG == "pt":
        return PT.get(text, text)
    return text


def pick(value):
    """Escolhe o idioma de um dict {"en": ..., "pt": ...} do catálogo."""
    if isinstance(value, dict):
        return value.get(LANG) or value.get("en") or next(iter(value.values()), "")
    return value or ""


PT = {
    # comuns
    "Cancel": "Cancelar",
    "Close": "Fechar",
    "Back": "Voltar",
    "Next": "Avançar",
    "Done": "Concluído",
    "Install": "Instalar",
    "Remove": "Remover",
    "Open": "Abrir",
    "Retry": "Tentar novamente",
    "Details": "Detalhes",
    "Working…": "Trabalhando…",
    "Please wait…": "Aguarde…",
    "Something went wrong": "Algo deu errado",
    "Restart now": "Reiniciar agora",
    "Later": "Depois",
    "Restart required": "Reinicialização necessária",
    "Restart the computer to finish.": "Reinicie o computador para concluir.",
    # erros
    "The operation was cancelled or the password was not confirmed.":
        "A operação foi cancelada ou a senha não foi confirmada.",
    "No internet connection. Connect to a network and try again.":
        "Sem conexão com a internet. Conecte-se a uma rede e tente novamente.",
    "Another installation or update is already running. Wait for it to finish and try again.":
        "Outra instalação ou atualização já está em andamento. Aguarde terminar e tente novamente.",
    "The package was not found in the configured sources.":
        "O pacote não foi encontrado nas fontes de software configuradas.",
    "There is not enough free disk space.":
        "Não há espaço livre suficiente no disco.",
    "The package system service is not available.":
        "O serviço de gerenciamento de pacotes não está disponível.",
    "Technical details": "Detalhes técnicos",
    # loja
    "Konaro Store": "Loja Konaro",
    "Search apps": "Buscar aplicativos",
    "Featured": "Destaques",
    "Games": "Jogos",
    "Windows apps": "Apps do Windows",
    "Internet": "Internet",
    "Productivity": "Produtividade",
    "Multimedia": "Multimídia",
    "Graphics": "Gráficos",
    "Development": "Desenvolvimento",
    "Utilities": "Utilitários",
    "Installed": "Instalados",
    "Installed ✓": "Instalado ✓",
    "No apps found.": "Nenhum aplicativo encontrado.",
    "Source": "Origem",
    "Format": "Formato",
    "Permissions": "Permissões",
    "Debian (official)": "Debian (oficial)",
    "Brave (official repository)": "Brave (repositório oficial)",
    "Flathub (community)": "Flathub (comunidade)",
    "Debian package (.deb)": "Pacote Debian (.deb)",
    "Flatpak (isolated)": "Flatpak (isolado)",
    "Install {name}?": "Instalar {name}?",
    "Remove {name}?": "Remover {name}?",
    "Your password may be requested.": "Sua senha pode ser solicitada.",
    "Installing {name}…": "Instalando {name}…",
    "Removing {name}…": "Removendo {name}…",
    "{name} was installed.": "{name} foi instalado.",
    "{name} was removed.": "{name} foi removido.",
    "Checking installed apps…": "Verificando aplicativos instalados…",
    "Loading permissions…": "Carregando permissões…",
    "Permissions are only shown for Flatpak apps. Debian packages run with your user's normal permissions.":
        "Permissões são exibidas apenas para apps Flatpak. Pacotes Debian rodam com as permissões normais do seu usuário.",
    "Could not read the permissions (are you online?).":
        "Não foi possível ler as permissões (você está conectado?).",
    "Requires internet": "Requer internet",
    "Wait for the current operation to finish.": "Aguarde a operação atual terminar.",
    # permissões flatpak
    "Network access": "Acesso à rede",
    "Full access to your home folder": "Acesso total à sua pasta pessoal",
    "Full access to the whole system's files": "Acesso a todos os arquivos do sistema",
    "Access to your Downloads folder": "Acesso à pasta Downloads",
    "Access to some of your folders": "Acesso a algumas das suas pastas",
    "Access to devices (cameras, controllers…)": "Acesso a dispositivos (câmeras, controles…)",
    "Hardware graphics acceleration": "Aceleração gráfica do hardware",
    "Sound": "Som",
    "Display (window)": "Tela (janela)",
    "Bluetooth": "Bluetooth",
    "No special permissions": "Nenhuma permissão especial",
    # atualizador
    "Konaro Updates": "Atualizações do Konaro",
    "Check for updates": "Verificar atualizações",
    "Checking for updates…": "Procurando atualizações…",
    "Your system is up to date.": "Seu sistema está atualizado.",
    "Security updates": "Atualizações de segurança",
    "Fix vulnerabilities. Recommended to install as soon as possible.":
        "Corrigem falhas de segurança. Recomendado instalar o quanto antes.",
    "System updates": "Atualizações do sistema",
    "Bug fixes and improvements for the system and its programs.":
        "Correções e melhorias para o sistema e seus programas.",
    "Konaro components": "Componentes do Konaro",
    "Konaro OS's own tools and appearance.": "Ferramentas e aparência próprias do Konaro OS.",
    "Apps (Flatpak)": "Aplicativos (Flatpak)",
    "Apps installed from Flathub.": "Aplicativos instalados pelo Flathub.",
    "{n} update(s)": "{n} atualização(ões)",
    "Install updates": "Instalar atualizações",
    "Installing updates…": "Instalando atualizações…",
    "Updates installed.": "Atualizações instaladas.",
    "May require a restart": "Pode exigir reinicialização",
    "Updates are never installed without your permission.":
        "Atualizações nunca são instaladas sem a sua permissão.",
    "Last check: {when}": "Última verificação: {when}",
    "Updates available": "Atualizações disponíveis",
    "{n} update(s) available, {s} of them for security.":
        "{n} atualização(ões) disponível(is), {s} de segurança.",
    "{n} update(s) available.": "{n} atualização(ões) disponível(is).",
    "Show": "Ver",
    # drivers
    "Konaro Drivers": "Drivers do Konaro",
    "Scanning your hardware…": "Analisando seu hardware…",
    "Scan again": "Analisar novamente",
    "Drivers are only installed with your permission.": "Drivers só são instalados com a sua permissão.",
    "Recommended drivers": "Drivers recomendados",
    "Your devices": "Seus dispositivos",
    "No additional drivers are needed. Everything is working with the drivers included in the system.":
        "Nenhum driver adicional é necessário. Tudo está funcionando com os drivers incluídos no sistema.",
    "Working (driver: {driver})": "Funcionando (driver: {driver})",
    "No driver in use": "Nenhum driver em uso",
    "Install recommended": "Instalar recomendado",
    "Why: {reason}": "Motivo: {reason}",
    "Packages: {pkgs}": "Pacotes: {pkgs}",
    "Origin: {origin}": "Origem: {origin}",
    "Proprietary NVIDIA driver": "Driver proprietário da NVIDIA",
    "Your NVIDIA graphics card ({device}) works better and faster in games with the official NVIDIA driver.":
        "Sua placa de vídeo NVIDIA ({device}) funciona melhor e mais rápido em jogos com o driver oficial da NVIDIA.",
    "Debian non-free (proprietary, redistributable)": "Debian non-free (proprietário, redistribuível)",
    "Additional component for your hardware": "Componente adicional para o seu hardware",
    "Debian suggests this package for a device found in this computer.":
        "O Debian indica este pacote para um dispositivo encontrado neste computador.",
    "Debian": "Debian",
    "The driver was installed. Restart the computer to start using it.":
        "O driver foi instalado. Reinicie o computador para começar a usá-lo.",
    "Video": "Vídeo",
    "Network": "Rede",
    "Wi-Fi": "Wi-Fi",
    "Audio": "Áudio",
    "Other": "Outro",
    "Install {name}? This changes the system and requires a restart.":
        "Instalar {name}? Isso altera o sistema e exige reinicialização.",
    # boas-vindas
    "Welcome to Konaro": "Bem-vindo ao Konaro",
    "Welcome to Konaro OS": "Bem-vindo ao Konaro OS",
    "Let's get your computer ready in a few steps. You can change everything later in Settings.":
        "Vamos deixar seu computador pronto em poucos passos. Você pode mudar tudo depois nas Configurações.",
    "Language": "Idioma",
    "The system language is applied the next time you log in.":
        "O idioma do sistema é aplicado no próximo login.",
    "You are trying Konaro OS without installing it. Nothing is changed on your computer until you install.":
        "Você está experimentando o Konaro OS sem instalar. Nada é alterado no seu computador até você instalar.",
    "Install Konaro OS": "Instalar o Konaro OS",
    "Appearance": "Aparência",
    "Choose how Konaro looks. You can switch at any time.":
        "Escolha a aparência do Konaro. Você pode trocar quando quiser.",
    "Light": "Claro",
    "Dark": "Escuro",
    "Reduce animations": "Reduzir animações",
    "Makes the interface faster on modest computers and more comfortable if motion bothers you.":
        "Deixa a interface mais rápida em computadores modestos e mais confortável se movimento incomoda você.",
    "Internet": "Internet",
    "You are connected to the internet.": "Você está conectado à internet.",
    "You are not connected to the internet yet. Connect to install apps and receive updates.":
        "Você ainda não está conectado à internet. Conecte-se para instalar apps e receber atualizações.",
    "Network settings": "Configurações de rede",
    "Privacy": "Privacidade",
    "Konaro OS does not collect any data about you or your computer. There is no account to create.":
        "O Konaro OS não coleta nenhum dado sobre você ou seu computador. Não é preciso criar conta.",
    "Share anonymous usage statistics with KDE (optional)":
        "Compartilhar estatísticas anônimas de uso com o KDE (opcional)",
    "Updates and drivers": "Atualizações e drivers",
    "Konaro tells you when updates are available — you choose when to install them.":
        "O Konaro avisa quando há atualizações — você escolhe quando instalar.",
    "Check drivers": "Verificar drivers",
    "Games and Windows apps": "Jogos e apps do Windows",
    "Steam with Proton runs thousands of Windows games. Lutris and Bottles help with other launchers and Windows programs. Wine is already installed: double-click a .exe file to run it.":
        "O Steam com Proton roda milhares de jogos do Windows. O Lutris e o Bottles ajudam com outros launchers e programas do Windows. O Wine já vem instalado: dê dois cliques em um arquivo .exe para executá-lo.",
    "Not every game or program works: anti-cheat systems and some DRM can block them.":
        "Nem todo jogo ou programa funciona: sistemas anti-cheat e alguns DRMs podem impedir.",
    "Open the Games section of the Store": "Abrir a seção Jogos da Loja",
    "Getting around": "Como usar",
    "The dock at the bottom opens your apps. Running apps show a dot.":
        "O dock na parte de baixo abre seus aplicativos. Apps abertos mostram um ponto.",
    "The Konaro logo at the top left opens all apps and search. You can also press the Meta (Windows) key.":
        "O logo Konaro no canto superior esquerdo abre todos os apps e a busca. Você também pode apertar a tecla Meta (Windows).",
    "The top right shows network, sound, battery, notifications and the clock.":
        "O canto superior direito mostra rede, som, bateria, notificações e o relógio.",
    "Meta + W shows all open windows.": "Meta + W mostra todas as janelas abertas.",
    "All set!": "Tudo pronto!",
    "Enjoy Konaro OS. You can open this welcome again from the app menu.":
        "Aproveite o Konaro OS. Você pode abrir estas boas-vindas de novo pelo menu de aplicativos.",
    "Show this welcome at every login": "Mostrar estas boas-vindas a cada login",
    "Start using Konaro": "Começar a usar o Konaro",
    "Open the Store": "Abrir a Loja",
    # ---- Loja (interface nova)
    "Store": "Loja",
    "Home": "Início",
    "Library": "Biblioteca",
    "Updates": "Atualizações",
    "Search apps and games": "Buscar apps e jogos",
    "Get started": "Para começar",
    "Play": "Para jogar",
    "Create and edit": "Criar e editar",
    "Talk with friends": "Conversar com amigos",
    "See all": "Ver tudo",
    "Installing…": "Instalando…",
    "Removing…": "Removendo…",
    "Install Bottles": "Instalar o Bottles",
    "Open Bottles": "Abrir o Bottles",
    "See Windows apps": "Ver apps do Windows",
    "Windows programs on Konaro": "Programas do Windows no Konaro",
    "Double-click a .exe file to open it with Wine. For more demanding programs, Bottles creates a separate, tidy environment for each one.":
        "Dê dois cliques em um arquivo .exe para abri-lo com o Wine. Para programas mais exigentes, o Bottles cria um ambiente separado e organizado para cada um.",
    "About this app": "Sobre este app",
    "Category": "Categoria",
    "Same as your user account": "As mesmas da sua conta de usuário",
    "This app is a Debian package, installed and updated together with the system.":
        "Este app é um pacote Debian, instalado e atualizado junto com o sistema.",
    "This app runs isolated from the rest of the system (Flatpak) and only reaches what its permissions allow.":
        "Este app roda isolado do resto do sistema (Flatpak) e só acessa o que as permissões dele permitem.",
    "Apps from the Store that are on this computer.": "Apps da Loja que estão neste computador.",
    "No apps installed from the Store yet.": "Nenhum app da Loja instalado ainda.",
    "Start on the Home page — popular apps are a click away.": "Comece pela página Início — os apps mais usados estão a um clique.",
    "Nothing found for “{q}”.": "Nada encontrado para “{q}”.",
    "Try another name, or browse a category on the left.": "Tente outro nome ou navegue por uma categoria à esquerda.",
    "Results for “{q}”": "Resultados para “{q}”",
    "{n} apps": "{n} apps",
    "Hide details": "Ocultar detalhes",
    # ---- Boas-vindas, Atualizações e Drivers (interfaces novas)
    "Check again": "Verificar novamente",
    "Hide": "Ocultar",
    "Last check: {when}.": "Última verificação: {when}.",
    "{n} update": "{n} atualização",
    "{n} updates": "{n} atualizações",
    "{n} update available": "{n} atualização disponível",
    "{n} updates available": "{n} atualizações disponíveis",
    "Everything is working.": "Tudo está funcionando.",
    "{n} recommended driver": "{n} driver recomendado",
    "{n} recommended drivers": "{n} drivers recomendados",
    "Packages": "Pacotes",
    "Step {n} of {total}": "Passo {n} de {total}",
    "Widgets": "Widgets",
    "Glance at the time, your calendar and notes right on the desktop. Turn on the ones you want — you can move or remove them later.":
        "Veja a hora, seu calendário e suas notas direto na área de trabalho. Ligue os que quiser — dá para mover ou remover depois.",
    "Wi-Fi, cable and mobile connections.": "Conexões Wi-Fi, cabo e celular.",
    "Security fixes and improvements for the system and your apps.": "Correções de segurança e melhorias para o sistema e seus apps.",
    "Extra drivers for graphics cards, Wi-Fi and other devices.": "Drivers extras para placas de vídeo, Wi-Fi e outros dispositivos.",
    "Clock": "Relógio",
    "An analog clock in the top left corner.": "Um relógio analógico no canto superior esquerdo.",
    "Calendar": "Calendário",
    "This month at a glance, in the top right corner.": "O mês inteiro num relance, no canto superior direito.",
    "Memory usage": "Uso de memória",
    "How much memory your apps are using.": "Quanta memória seus apps estão usando.",
    "Notes": "Notas",
    "A sticky note for quick reminders.": "Um bloco de notas para lembretes rápidos.",
    "Now playing": "Tocando agora",
    "Controls for the music or video that is playing.": "Controles da música ou do vídeo que está tocando.",
}
