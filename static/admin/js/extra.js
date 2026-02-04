document.addEventListener("DOMContentLoaded", function () {
    const campeonato = document.getElementById("id_campeonato");
    const equipe = document.getElementById("id_equipe");
    if (!campeonato) return;

    const endpoint = "/admin/placar/extra/equipes-por-campeonato/";

    function limparSelect(select) {
        select.innerHTML = '<option value="">---------</option>';
    }

    function carregarEquipes(campeonatoId) {
        // ✅ guarda seleção atual (edição)
        const selecionada = equipe.value;

        limparSelect(equipe);


        if (!campeonatoId) return;

        fetch(`${endpoint}?campeonato_id=${campeonatoId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    equipe.add(new Option(item.text, item.id));
                });

                // ✅ restaura seleção se existir
                if (selecionada) equipe.value = selecionada;
            });
    }

    // mudança de campeonato
    campeonato.addEventListener("change", function () {
        carregarEquipes(this.value);
    });

    // edição: carrega automaticamente
    if (campeonato.value) {
        carregarEquipes(campeonato.value);
    }
});

