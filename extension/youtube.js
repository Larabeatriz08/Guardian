// Roda dentro do YouTube. Percebe a troca de video e envia titulo, canal e descricao.
console.log("Guardian: youtube.js carregado em", location.href);
let ultimo = "";

function texto(seletor) {
  const el = document.querySelector(seletor);
  return el ? el.textContent.replace(/\s+/g, " ").trim() : "";
}

function coletar() {
      console.log("Guardian: coletar()", location.pathname, "ultimo =", ultimo);
  const ehVideo =
    location.pathname === "/watch" || location.pathname.startsWith("/shorts/");
  if (!ehVideo || location.href === ultimo) return;

  const titulo =
    texto("h1.ytd-watch-metadata yt-formatted-string") ||
    document.title.replace(/ - YouTube$/, "").trim();
  if (!titulo || titulo === "YouTube") return;

  const canal =
    texto("ytd-video-owner-renderer ytd-channel-name a") ||
    texto("#owner #channel-name a");
  const descricao =
    texto("#description-inline-expander") ||
    texto("ytd-text-inline-expander");

  ultimo = location.href;
  try {
    chrome.runtime.sendMessage({
      type: "youtube",
      url: location.href,
      title: titulo,
      channel: canal,
      description: descricao.slice(0, 1000),
    });
  } catch (err) {
    // extensao recarregada: este script ficou orfao, nao ha o que fazer
  }
}

// o YouTube dispara este evento quando troca de video sem recarregar
document.addEventListener("yt-navigate-finish", () => setTimeout(coletar, 2000));
// primeira carga da pagina
setTimeout(coletar, 2500);