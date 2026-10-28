const CART_STORAGE_KEY = "loveJunckCart";
const ADDRESS_STORAGE_KEY = "loveJunckAddress";
const OBSERVATION_KEY = "loveJunckObservation";
// Nenhum número foi encontrado no projeto original. Configure abaixo com DDI + DDD + número, somente dígitos.
const WHATSAPP_NUMBER = "";

const PRECO_ADICIONAIS = { "Queijo extra": 300, "Bacon extra": 400, "Molho extra": 100 };

function formatarMoeda(valorCentavos) {
    return (valorCentavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function carregarJSON(chave, padrao) {
    try { return JSON.parse(localStorage.getItem(chave) || JSON.stringify(padrao)); }
    catch (_) { return padrao; }
}

function totalItem(item) {
    return item.precoCentavos + (Array.isArray(item.adicionais) ?
        item.adicionais.reduce((soma, adicional) => soma + (PRECO_ADICIONAIS[adicional] || 0), 0) : 0);
}

function exibirResumoPedido() {
    const listaItens = document.querySelector(".cart-items");
    const totalPedido = document.querySelector(".order-total");
    if (!listaItens || !totalPedido) return;

    const itens = carregarJSON(CART_STORAGE_KEY, []);
    const validos = Array.isArray(itens) ? itens.filter(item =>
        item && typeof item.nome === "string" && Number.isInteger(item.precoCentavos) &&
        Number.isInteger(item.quantidade) && item.precoCentavos >= 0 && item.quantidade > 0) : [];

    listaItens.replaceChildren();
    let total = 0;
    validos.forEach(item => {
        const subtotal = totalItem(item) * item.quantidade;
        total += subtotal;
        const linha = document.createElement("div");
        linha.className = "cart-item";
        const nome = document.createElement("span");
        nome.textContent = `${item.quantidade}x ${item.nome}${item.adicionais && item.adicionais.length ? " (" + item.adicionais.join(", ") + ")" : ""}`;
        const preco = document.createElement("span");
        preco.textContent = formatarMoeda(subtotal);
        linha.append(nome, preco);
        listaItens.append(linha);
    });
    if (!validos.length) {
        const vazio = document.createElement("p");
        vazio.className = "cart-item";
        vazio.textContent = "Seu carrinho está vazio.";
        listaItens.append(vazio);
    }
    totalPedido.textContent = formatarMoeda(total);
}

function enviarPedidoWhatsApp(formaPagamento) {
    // Se ainda não foi configurado um número real, não inventa destinatário nem afirma que enviou.
    if (!/^\d{10,15}$/.test(WHATSAPP_NUMBER)) {
        alert("O número do WhatsApp da lanchonete ainda não está configurado. No arquivo scripts/pagamento.js, preencha WHATSAPP_NUMBER com DDI + DDD + número (somente dígitos) e tente novamente.");
        return false;
    }

    const itens = carregarJSON(CART_STORAGE_KEY, []);
    if (!Array.isArray(itens) || !itens.length) {
        alert("Seu carrinho está vazio.");
        return false;
    }
    const endereco = carregarJSON(ADDRESS_STORAGE_KEY, {});
    const observacoes = localStorage.getItem(OBSERVATION_KEY) || "";
    const nomesPagamento = { pix: "PIX", card: "Cartão", cash: "Dinheiro na entrega" };
    let total = 0;
    const linhas = itens.map(item => {
        const adicionais = Array.isArray(item.adicionais) ? item.adicionais : [];
        const unitario = item.precoCentavos + adicionais.reduce((soma, nome) => soma + (PRECO_ADICIONAIS[nome] || 0), 0);
        const subtotal = unitario * item.quantidade;
        total += subtotal;
        return `• ${item.quantidade}x ${item.nome} — ${formatarMoeda(subtotal)}${adicionais.length ? "\n  Adicionais: " + adicionais.join(", ") : ""}`;
    });
    const enderecoTexto = [endereco.rua, endereco.numero, endereco.complemento, endereco.bairro, endereco.cep].filter(Boolean).join(", ");
    const mensagem = [
        "*Novo pedido — Love Junck Lanchonete*",
        "",
        ...linhas,
        "",
        `*Total: ${formatarMoeda(total)}*`,
        `Pagamento: ${nomesPagamento[formaPagamento] || formaPagamento}`,
        `Cliente: ${endereco.telefone || "Não informado"}`,
        `Endereço: ${enderecoTexto || "Não informado"}`,
        `Observações: ${observacoes.trim() || "Nenhuma"}`
    ].join("\n");
    const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(mensagem)}`;
    const janela = window.open(url, "_blank");
    if (!janela) {
        alert("O navegador bloqueou a abertura do WhatsApp. Permita pop-ups para este site e tente novamente.");
        return false;
    }
    return true;
}

exibirResumoPedido();

function newOrder() {
    localStorage.removeItem(CART_STORAGE_KEY);
    localStorage.removeItem(OBSERVATION_KEY);
    window.location.href = "../index.html";
}
