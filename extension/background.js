const API = "http://127.0.0.1:8765/event";
const enviados = new Set(); // "idDaAba|url|fase" (evita eventos repetidos)

function ignoravel(url) {
  // so interessam paginas web; ignora chrome://, edge://, about:blank etc.
  return !url || !/^https?:/i.test(url);
}

async function lerTexto(tabId) {
  try {
    const r = await chrome.scripting.executeScript({
      target: { tabId },
      func: () =>
        (document.body ? document.body.innerText : "")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 1500),
    });
    return (r && r[0] && r[0].result) || "";
  } catch (err) {
    return ""; // aba descartada, pagina protegida etc.
  }
}

async function reportar(tab, comTexto) {
  if (ignoravel(tab.url)) return;
  if (comTexto && tab.status !== "complete") return; // espera carregar

  const chave = `${tab.id}|${tab.url}|${comTexto ? "texto" : "url"}`;
  if (enviados.has(chave)) return;
  enviados.add(chave);

  const texto = comTexto ? await lerTexto(tab.id) : "";

  try {
    const resp = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: tab.url,
        title: tab.title || "",
        text: texto,
        active: !!tab.active,
      }),
    });
    const data = await resp.json();
    if (data.action === "block") {
      chrome.tabs.update(tab.id, { url: chrome.runtime.getURL("blocked.html") });
    }
  } catch (err) {
    enviados.delete(chave); // tenta de novo na proxima varredura
    console.warn("Guardian: backend indisponivel", err);
  }
}

function reportarTudo(tab) {
  reportar(tab, false);
  reportar(tab, true);
}

// 1) Navegacao: URL mudou (fase rapida) ou pagina terminou de carregar (com texto)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) reportar(tab, false);
  if (changeInfo.status === "complete") reportarTudo(tab);
});

// 2) Troca de aba ativa
chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  reportarTudo(tab);
});

// 3) Limpeza
chrome.tabs.onRemoved.addListener((tabId) => {
  for (const k of [...enviados]) {
    if (k.startsWith(tabId + "|")) enviados.delete(k);
  }
});

// 4) Varredura de TODAS as abas (pega abas em segundo plano)
async function varrer() {
  const abas = await chrome.tabs.query({});
  abas.forEach(reportarTudo);
}

chrome.alarms.create("varredura", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name === "varredura") varrer();
});

chrome.runtime.onStartup.addListener(varrer);
chrome.runtime.onInstalled.addListener(varrer);