const ADDRESS_STORAGE_KEY = "loveJunckAddress";

function goToPayment() {
    const dados = {
        cep: document.getElementById("cep").value.trim(),
        rua: document.getElementById("rua").value.trim(),
        numero: document.getElementById("numero").value.trim(),
        bairro: document.getElementById("bairro").value.trim(),
        complemento: document.getElementById("complemento").value.trim(),
        telefone: document.getElementById("telefone").value.trim()
    };
    if (!dados.cep || !dados.rua || !dados.numero || !dados.bairro || !dados.telefone) {
        alert("Por favor, preencha todos os campos obrigatórios.");
        return;
    }
    localStorage.setItem(ADDRESS_STORAGE_KEY, JSON.stringify(dados));
    window.location.href = "../html/pagamento.html";
}

document.addEventListener("DOMContentLoaded", () => {
    try {
        const dados = JSON.parse(localStorage.getItem(ADDRESS_STORAGE_KEY) || "{}");
        Object.entries(dados).forEach(([id, valor]) => {
            const campo = document.getElementById(id);
            if (campo && typeof valor === "string") campo.value = valor;
        });
    } catch (erro) {
        console.warn("Não foi possível recuperar o endereço salvo.", erro);
    }
});
