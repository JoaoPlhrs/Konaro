// Konaro OS Fênix Lite — Firefox mais leve para computadores com pouca memória.
// Menos processos em paralelo, abas paradas liberadas quando a memória aperta e
// menos gravações no disco.
pref("dom.ipc.processCount", 2);
pref("browser.tabs.unloadOnLowMemory", true);
pref("browser.sessionstore.interval", 60000);
pref("browser.cache.disk.capacity", 262144);
