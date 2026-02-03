document.addEventListener("DOMContentLoaded", function () {
    const modalidade = document.getElementById("id_modalidade");
    const houveWo = document.getElementById("id_houve_wo");

    const placarA = document.getElementById("id_placar_a");
    const placarB = document.getElementById("id_placar_b");
    const vencedora = document.getElementById("id_vencedora");
    const equipeWo = document.getElementById("id_equipe_wo");

    const placarARow = placarA?.closest(".form-row");
    const placarBRow = placarB?.closest(".form-row");
    const vencedoraRow = vencedora?.closest(".form-row");
    const equipeWoRow = equipeWo?.closest(".form-row");
    const houveWoRow = houveWo?.closest(".form-row");

    // Mapa vindo do Django (modalidade -> possui placar)
    const mapa = JSON.parse(
        modalidade?.getAttribute("data-possui-placar-map") || "{}"
    );

    // 🔧 Helpers seguros
    function hideRow(row, field) {
        if (row) row.style.display = "none";
        if (field) {
            field.disabled = true;
            field.required = false;
        }
    }

    function showRow(row, field, required = false) {
        if (row) row.style.display = "";
        if (field) {
            field.disabled = false;
            field.required = required;
        }
    }

    function atualizarCampos() {
        if (!modalidade) return;

        const possuiPlacar = Boolean(mapa[String(modalidade.value)]);
        const wo =
            houveWo &&
            ["sim", "true", "1"].includes(houveWo.value?.toLowerCase());

        // 🔒 Esconde tudo primeiro
        hideRow(placarARow, placarA);
        hideRow(placarBRow, placarB);
        hideRow(vencedoraRow, vencedora);
        hideRow(equipeWoRow, equipeWo);

        // Campo "houve WO" sempre visível
        if (houveWoRow) houveWoRow.style.display = "";

        // 🟨 Modalidade SEM placar
        if (!possuiPlacar) {
            if (wo) {
                // WO → escolher equipe WO
                showRow(equipeWoRow, equipeWo, true);
            } else {
                // Sem WO → escolher vencedora
                showRow(vencedoraRow, vencedora, true);
            }
            return;
        }

        // 🟦 Modalidade COM placar
        if (wo) {
            // WO → escolher equipe WO
            showRow(equipeWoRow, equipeWo, true);
        } else {
            // Sem WO → informar placar
            showRow(placarARow, placarA, true);
            showRow(placarBRow, placarB, true);
        }
    }

    // Inicializa
    atualizarCampos();

    // Eventos
    modalidade?.addEventListener("change", atualizarCampos);
    houveWo?.addEventListener("change", atualizarCampos);
});


document.addEventListener("DOMContentLoaded", function () {
    const campeonato = document.getElementById("id_campeonato");
    const equipeA = document.getElementById("id_equipe_a");
    const equipeB = document.getElementById("id_equipe_b");
    const equipeWo = document.getElementById("id_equipe_wo");
    const equipeVenc = document.getElementById("id_vencedora");

    if (!campeonato) return;

    const endpoint = "/admin/placar/partida/equipes-por-campeonato/";

    function limparSelect(select) {
        select.innerHTML = '<option value="">---------</option>';
    }

    function carregarEquipes(campeonatoId) {
        // ✅ guarda seleção atual (edição)
        const selecionadaA = equipeA.value;
        const selecionadaB = equipeB.value;
        const selecionadaWo = equipeWo.value;
        const selecionadaVenc = equipeVenc.value;

        limparSelect(equipeA);
        limparSelect(equipeB);
        limparSelect(equipeWo);
        limparSelect(equipeVenc);


        if (!campeonatoId) return;

        fetch(`${endpoint}?campeonato_id=${campeonatoId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    equipeA.add(new Option(item.text, item.id));
                    equipeB.add(new Option(item.text, item.id));
                    equipeWo.add(new Option(item.text, item.id));
                    equipeVenc.add(new Option(item.text, item.id));
                });

                // ✅ restaura seleção se existir
                if (selecionadaA) equipeA.value = selecionadaA;
                if (selecionadaB) equipeB.value = selecionadaB;
                if (selecionadaWo) equipeWo.value = selecionadaWo;
                if (selecionadaVenc) equipeVenc.value = selecionadaVenc;
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

