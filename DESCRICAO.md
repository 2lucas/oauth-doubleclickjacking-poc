## Descrição

A nível de código, o fluxo de device authorization da Vercel permite que um atacante construa um ataque de **pop-up forgery** — uma falsificação de janela popup que induz utilizadores legítimos a pressionarem o botão de <mark style="background: #FF5582A6;">{nome_da_empresa}</mark> sem se aperceberem.

O ataque não usa iframes (bloqueados por `X-Frame-Options` e `CSP frame-ancestors`) nem tenta roubar tokens diretamente. Em vez disso, coloca a página real de autorização — com todos os cookies de sessão intactos — dentro de uma janela popup legítima que persegue o cursor do rato durante um jogo. O clique que a vítima pensa ser no jogo acerta em cheio no botão de autorização.

---

### Como funciona

#### 1. Abertura do popup fantasma

O utilizador acede a uma página que imita um CAPTCHA do Cloudflare Turnstile. Ao clicar na checkbox, o evento de clique — que constitui **ativação do utilizador** — invoca `window.open()` para criar uma janela popup nomeada (`"popup"`), de seguida reduzida a 1×1 pixel e enviada para fora do ecrã (`left=9999, top=9999`).

```javascript
const blob = new Blob([`<body bgcolor=222222>`], { type: "text/html" });
w = window.open(URL.createObjectURL(blob), "popup", "width=1,height=1,left=9999,top=9999");
w.resizeTo(1, 1);
w.moveTo(9999, 9999);
```

Esta janela minúscula herda a mesma origem da página que a abriu, o que permite referenciá-la e manipulá-la a partir de qualquer página do mesmo domínio. Após 500 ms a página navega silenciosamente para o jogo.

#### 2. Reconexão no jogo

A página do jogo (Flappy Bird) recupera a referência ao popup fantasma chamando `window.open("", "popup")` — com URL vazia e o nome da janela existente, o navegador devolve o objeto `window` daquele popup sem abrir nada novo.

```javascript
w = window.open("", "popup");
```

#### 3. Rastreio do cursor

Um listener `mousemove` no canvas do jogo captura `e.screenX` e `e.screenY` — coordenadas absolutas de ecrã que funcionam mesmo com múltiplos monitores.

```javascript
canvas.contentWindow.addEventListener("mousemove", function (e) {
    mouse = [e.screenX, e.screenY];
});
```

Um loop (`while true`, 500 ms) compara a posição atual com a anterior. Se o rato se moveu para fora da área do botão alvo, o popup é reposicionado.

#### 4. Alinhamento milimétrico

O popup é redimensionado para o tamanho exato medido previamente (`POPUP_SIZE`) e carregado com o URL de autorização da Vercel. As coordenadas são calculadas subtraindo o deslocamento do botão (`BUTTON_OFFSET`) à posição do cursor — o centro do botão de autorização fica precisamente sob a ponta do rato.

```javascript
const x = mouse[0] - button.pos[0] - button.size[0] / 2;
const y = mouse[1] - button.pos[1] - button.size[1] / 2 - navbarHeight;

w.location = "about:blank";          // torna same-origin (permite moveTo/resizeTo)
w.moveTo(x, y);                       // posiciona o popup
w.resizeTo(POPUP_SIZE[0], POPUP_SIZE[1]); // redimensiona
w.location = TARGET_URL;              // carrega a página de autorização
```

A cada reposicionamento o popup é brevemente navegado para `about:blank` (same-origin) para que `moveTo()` e `resizeTo()` funcionem, e depois recarregado com o URL alvo.

#### 5. Captura do clique

Quando o jogador passa o terceiro obstáculo — momento de clique rápido e previsível — o jogo dispara um sinal `"trigger"`. O handler invoca `window.open("", "popup")` uma última vez, que **foca** o popup e o traz visualmente para a frente.

```javascript
// Trigger handler (game.html)
w = window.open("", "popup");  // foca o popup — trá-lo para a frente do jogo
done = true;
await sleep(4000);              // aguarda o clique acidental no botão
w.close();                      // fecha o popup e reinicia o ciclo
```

O utilizador, com a atenção no jogo, não percebe que a janela sob o cursor já não é o canvas. O clique seguinte — destinado a fazer o pássaro saltar — acerta no botão <mark style="background: #FF5582A6;">{nome_da_empresa}</mark>. A autorização é concedida instantaneamente porque a vítima já tem sessão ativa. Quatro segundos depois o popup fecha-se e o ciclo reinicia.

---

### Porque escapa às defesas tradicionais

| Defesa | Porque não bloqueia |
|---|---|
| `X-Frame-Options: DENY` | O ataque **não usa iframes** — a página corre como janela de nível superior |
| `Content-Security-Policy: frame-ancestors` | Idem — `frame-ancestors` só rege iframes, não popups |
| Popup blockers | O `window.open()` é invocado dentro de um evento de clique — tem ativação do utilizador |
| Same-origin policy | O popup é aberto com blob URL da mesma origem; a página alvo (Vercel) corre no seu próprio domínio |
| Deteção de janela invisível | O popup tem dimensões reais (497×714) — apenas o botão é visível, não é 1×1 |

---

### O que dificilmente se mitiga

- **A página alvo é servida no seu domínio legítimo**, com HTTPS e cookies first-party — impossível distinguir de uma abertura genuína por `window.open()`
- **O popup é aberto com ativação real do utilizador** (clique no CAPTCHA) — não é bloqueado por popup blockers
- **As dimensões do popup são as mínimas que mostram o botão**, não 1×1 — contorna deteções de janela invisível
- **`window.opener` existe legitimamente** — difícil bloquear sem quebrar fluxos OAuth legítimos que também usam popups
- **A página alvo nunca sabe que está posicionada sob o cursor** — o navegador não expõe a posição absoluta da janela ao JavaScript da própria página
- **Os cookies de sessão são enviados normalmente** — a página alvo corre no seu próprio domínio, como qualquer janela popup legítima
