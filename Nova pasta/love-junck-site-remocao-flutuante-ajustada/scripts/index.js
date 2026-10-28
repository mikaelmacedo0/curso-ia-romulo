const CART_STORAGE_KEY = "loveJunckCart";
const OBSERVATION_KEY = "loveJunckObservation";
const ADDRESS_KEY = "loveJunckAddress";
const ADDITIONAL_PRICES = { "Queijo extra": 300, "Bacon extra": 400, "Molho extra": 100 };
// Nenhum número de WhatsApp foi encontrado no código original.
// Preencha com DDI + DDD + número, somente dígitos (ex.: 5585999999999).
const WHATSAPP_NUMBER = "";

let itensCarrinho = carregarCarrinho();
let selecionados = new Set();

function carregarCarrinho() {
    try {
        const itens = JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "[]");
        if (!Array.isArray(itens)) return [];
        return itens.filter(item => item && typeof item.nome === "string" &&
            Number.isInteger(item.precoCentavos) && Number.isInteger(item.quantidade) &&
            item.precoCentavos >= 0 && item.quantidade > 0)
            .map(item => ({ ...item, adicionais: Array.isArray(item.adicionais) ? item.adicionais : [] }));
    } catch (erro) {
        console.error("Não foi possível carregar o carrinho salvo.", erro);
        return [];
    }
}

function formatarMoeda(centavos) {
    return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function salvarCarrinho() {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(itensCarrinho));
        return true;
    } catch (erro) {
        console.error("Não foi possível salvar o carrinho.", erro);
        alert("Não foi possível salvar o carrinho neste navegador.");
        return false;
    }
}

function precoUnitario(item) {
    return item.precoCentavos + (item.adicionais || []).reduce((soma, nome) => soma + (ADDITIONAL_PRICES[nome] || 0), 0);
}

function chaveItem(item) {
    return item.nome + "|" + [...(item.adicionais || [])].sort().join(",");
}

function atualizarCarrinho() {
    const lista = document.querySelector(".lista-carrinho");
    const totalEl = document.querySelector(".valor-total");
    const contador = document.querySelector(".contador");
    if (!lista || !totalEl || !contador) return;

    lista.replaceChildren();
    let total = 0;
    let quantidadeTotal = 0;

    itensCarrinho.forEach((item, indice) => {
        const subtotal = precoUnitario(item) * item.quantidade;
        total += subtotal;
        quantidadeTotal += item.quantidade;

        const linha = document.createElement("div");
        linha.className = "item-carrinho";
        const marcar = document.createElement("input");
        marcar.type = "checkbox";
        marcar.className = "marcar-item";
        marcar.setAttribute("aria-label", "Selecionar " + item.nome);
        marcar.checked = selecionados.has(indice);
        marcar.addEventListener("change", () => {
            marcar.checked ? selecionados.add(indice) : selecionados.delete(indice);
            atualizarControlesSelecao();
        });

        const detalhes = document.createElement("div");
        detalhes.className = "detalhes-item";
        const nome = document.createElement("span");
        nome.textContent = item.nome;
        const adicionais = document.createElement("small");
        adicionais.textContent = item.adicionais.length ? "Adicionais: " + item.adicionais.join(", ") : "";
        detalhes.append(nome);
        if (adicionais.textContent) detalhes.append(adicionais);

        const controles = document.createElement("div");
        controles.className = "controles-quantidade";
        const menos = document.createElement("button");
        menos.type = "button"; menos.textContent = "−"; menos.setAttribute("aria-label", "Diminuir quantidade");
        menos.disabled = item.quantidade <= 1;
        menos.addEventListener("click", () => alterarQuantidade(indice, -1));
        const qtd = document.createElement("span");
        qtd.textContent = item.quantidade;
        const mais = document.createElement("button");
        mais.type = "button"; mais.textContent = "+"; mais.setAttribute("aria-label", "Aumentar quantidade");
        mais.addEventListener("click", () => alterarQuantidade(indice, 1));
        controles.append(menos, qtd, mais);

        const preco = document.createElement("strong");
        preco.textContent = formatarMoeda(subtotal);
        linha.append(marcar, detalhes, controles, preco);
        lista.append(linha);
    });

    if (!itensCarrinho.length) {
        const vazio = document.createElement("p");
        vazio.textContent = "Seu carrinho está vazio. Adicione produtos do cardápio.";
        lista.append(vazio);
    }

    totalEl.textContent = formatarMoeda(total);
    const totalRodape = document.getElementById("total-rodape");
    if (totalRodape) totalRodape.textContent = formatarMoeda(total);
    contador.textContent = quantidadeTotal;
    atualizarControlesSelecao();
}

function atualizarControlesSelecao() {
    const totalMarcados = selecionados.size;
    const botoesRemocao = document.querySelectorAll(".remover-selecionados, .remover-flutuante");
    const contadorRemocao = document.querySelector(".contador-remocao");
    const todos = document.getElementById("selecionar-todos");
    botoesRemocao.forEach(botao => {
        botao.disabled = totalMarcados === 0;
        if (botao.classList.contains("remover-flutuante")) {
            // Exibe o botão flutuante somente enquanto houver itens selecionados.
            botao.classList.toggle("is-visible", totalMarcados > 0);
            botao.setAttribute("aria-hidden", totalMarcados > 0 ? "false" : "true");
            botao.setAttribute("aria-label", totalMarcados ? `Remover ${totalMarcados} item(ns) selecionado(s)` : "Remover pedidos selecionados");
            botao.title = totalMarcados ? `Remover ${totalMarcados} item(ns) selecionado(s)` : "Selecione itens no carrinho para removê-los";
            botao.tabIndex = totalMarcados > 0 ? 0 : -1;
        }
    });
    if (contadorRemocao) contadorRemocao.textContent = totalMarcados;
    if (todos) {
        todos.checked = itensCarrinho.length > 0 && totalMarcados === itensCarrinho.length;
        todos.indeterminate = totalMarcados > 0 && totalMarcados < itensCarrinho.length;
    }
}

function alterarQuantidade(indice, delta) {
    if (!itensCarrinho[indice]) return;
    itensCarrinho[indice].quantidade = Math.max(1, itensCarrinho[indice].quantidade + delta);
    salvarCarrinho();
    atualizarCarrinho();
}

function adicionarProduto(botao) {
    const produto = botao.closest(".produto");
    const nome = produto.querySelector("h3").textContent.trim();
    const textoPreco = produto.querySelector("strong").textContent;
    const encontrado = textoPreco.match(/R\$\s*([\d.]+,\d{2})/);
    if (!encontrado) {
        alert("Não foi possível identificar o preço deste produto.");
        return;
    }
    const precoCentavos = Math.round(Number(encontrado[1].replace(/\./g, "").replace(",", ".")) * 100);
    const elegivelAdicionais = /burguer|hambúrguer|cheeseburguer|x-|pastel/i.test(nome);
    let adicionais = [];
    if (elegivelAdicionais) {
        const resposta = prompt("Adicionais opcionais (digite os números separados por vírgula):\n1 - Queijo extra (+ R$ 3,00)\n2 - Bacon extra (+ R$ 4,00)\n3 - Molho extra (+ R$ 1,00)\nDeixe em branco para não adicionar.");
        if (resposta === null) return;
        const mapa = { "1": "Queijo extra", "2": "Bacon extra", "3": "Molho extra" };
        adicionais = [...new Set(resposta.split(",").map(x => mapa[x.trim()]).filter(Boolean))];
    }
    const item = { nome, precoCentavos, quantidade: 1, adicionais };
    const existente = itensCarrinho.find(i => chaveItem(i) === chaveItem(item));
    if (existente) existente.quantidade += 1;
    else itensCarrinho.push(item);
    salvarCarrinho();
    atualizarCarrinho();
}

document.querySelectorAll(".produto .adicionar").forEach(botao => {
    botao.addEventListener("click", () => adicionarProduto(botao));
});

const busca = document.getElementById("busca-produtos");
if (busca) {
    busca.addEventListener("input", () => {
        const termo = busca.value.trim().toLocaleLowerCase("pt-BR");
        document.querySelectorAll(".categoria").forEach(categoria => {
            let visiveis = 0;
            categoria.querySelectorAll(".produto").forEach(produto => {
                const corresponde = produto.textContent.toLocaleLowerCase("pt-BR").includes(termo);
                produto.hidden = !corresponde;
                if (corresponde) visiveis++;
            });
            categoria.hidden = visiveis === 0;
        });
    });
}

const observacao = document.getElementById("observacao");
if (observacao) {
    observacao.value = localStorage.getItem(OBSERVATION_KEY) || "";
    observacao.addEventListener("input", () => localStorage.setItem(OBSERVATION_KEY, observacao.value));
}

const todos = document.getElementById("selecionar-todos");
if (todos) {
    todos.addEventListener("change", () => {
        selecionados = todos.checked ? new Set(itensCarrinho.map((_, i) => i)) : new Set();
        atualizarCarrinho();
    });
}
function removerItensSelecionados() {
    if (!selecionados.size) {
        document.getElementById("carrinho")?.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
    }
    if (!confirm(`Remover ${selecionados.size} item(ns) selecionado(s) do carrinho?`)) return;
    itensCarrinho = itensCarrinho.filter((_, indice) => !selecionados.has(indice));
    selecionados.clear();
    salvarCarrinho();
    atualizarCarrinho();
}

document.querySelectorAll(".remover-selecionados, .remover-flutuante").forEach(botao => {
    botao.addEventListener("click", removerItensSelecionados);
});

const removerFlutuante = document.getElementById("remover-flutuante");
if (removerFlutuante) {
    removerFlutuante.addEventListener("keydown", evento => {
        if (evento.key === "Escape") removerFlutuante.blur();
    });
}

const finalizar = document.querySelector(".finalizar");
if (finalizar) {
    finalizar.addEventListener("click", () => {
        if (!itensCarrinho.length) {
            alert("Adicione pelo menos um produto antes de continuar para o pagamento.");
            return;
        }
        window.location.href = "./html/endereco.html";
    });
}

atualizarCarrinho();
