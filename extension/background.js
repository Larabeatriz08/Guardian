const API = "http://127.0.0.1:8765/event";
const lastSent = new Map(); // tabId -> ultima URL enviada (evita eventos repetidos)

function ignoravel(url) {
  // so interessam paginas web; ignora chrome://, edge://, about:blank etc.
  return !url || !/^https?:/i.test(url);
}

async function reportar(tab) {
  if (ignoravel(tab.url)) return;
  if (lastSent.get(tab.id) === tab.url) return;
  lastSent.set(tab.id, tab.url);

  try {
    const resp = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: tab.url,
        title: tab.title || "",
        active: !!tab.active,
      }),
    });
    const data = await resp.json();
    if (data.action === "block") {
      chrome.tabs.update(tab.id, { url: chrome.runtime.getURL("blocked.html") });
    }
  } catch (err) {
    // backend desligado: por enquanto deixa passar (veremos como reforcar no Passo 8)
    console.warn("Guardian: backend indisponivel", err);
  }
}

// 1) Navegacao: URL mudou ou pagina terminou de carregar
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url || changeInfo.status === "complete") {
    reportar(tab);
  }
});

// 2) Troca de aba ativa
chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  reportar(tab);
});

// 3) Limpeza
chrome.tabs.onRemoved.addListener((tabId) => lastSent.delete(tabId));

// 4) Varredura de TODAS as abas (pega abas em segundo plano)
async function varrer() {
  const abas = await chrome.tabs.query({});
  abas.forEach(reportar);
}

chrome.alarms.create("varredura", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name === "varredura") varrer();
});

chrome.runtime.onStartup.addListener(varrer);
chrome.runtime.onInstalled.addListener(varrer);