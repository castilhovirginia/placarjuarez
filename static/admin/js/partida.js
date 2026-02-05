document.addEventListener("DOMContentLoaded", function () {
    const modalidade = document.getElementById("id_modalidade");
    const iniciada = document.getElementById("id_iniciada");
    const houveWo = document.getElementById("id_houve_wo");
    const equipeA = document.getElementById("id_equipe_a");
    const equipeB = document.getElementById("id_equipe_b");

    const placarA = document.getElementById("id_placar_a");
    const placarB = document.getElementById("id_placar_b");
    const vencedora = document.getElementById("id_vencedora");
    const equipeWo = document.getElementById("id_equipe_wo");
    const encerrada = document.getElementById("id_encerrada");

    function validarEquipesAntesDeIniciar() {
        if (!equipeA?.value || !equipeB?.value) {
            alert("Selecione a Equipe A e a Equipe B antes de iniciar a partida.");
            return false;
        }

        if (equipeA.value === equipeB.value) {
            alert("Equipe A e Equipe B não podem ser a mesma.");
            return false;
        }

        return true;
    }

    function limparCamposDependentes() {
        if (houveWo) houveWo.value = "";
        if (equipeWo) equipeWo.value = "";
        if (placarA) placarA.value = "";
        if (placarB) placarB.value = "";
        if (vencedora) vencedora.value = "";
        if (encerrada) encerrada.checked = false;
    }

    function limparEquipeWo() {
        if (equipeWo) {
            equipeWo.value = "";
            placarA.value = "";
            placarB.value = "";
            vencedora.value= "";
            encerrada.checked = false;
        }
    }

    function getRow(field) {
        return field?.closest(".form-row, .fieldBox, .form-group");
    }

    const placarARow = getRow(placarA);
    const placarBRow = getRow(placarB);
    const vencedoraRow = getRow(vencedora);
    const equipeWoRow = getRow(equipeWo);
    const houveWoRow = getRow(houveWo);
    const encerradaRow = getRow(encerrada);

    const mapa = JSON.parse(
        modalidade?.getAttribute("data-possui-placar-map") || "{}"
    );

    function hideRow(row, field) {
        if (row) row.style.display = "none";
        if (field) {
            field.required = false;
            field.disabled = true;
        }
    }

    function showRow(row, field, required = false, disabled = false) {
        if (row) row.style.display = "";
        if (field) {
            field.required = required;
            field.disabled = disabled;
        }
        }

    function atualizarCampos() {
        if (!modalidade || !iniciada) return;

        const possuiPlacar = Boolean(mapa[String(modalidade.value)]);
        const partidaIniciada = iniciada.checked;

        const houveWoValor = houveWo?.value; // "", "sim", "nao"
        const houveWoEhNao = houveWoValor === "nao";
        const houveWoEhSim = houveWoValor === "sim";

        // 🔒 Esconde tudo sempre
        hideRow(houveWoRow, houveWo);
        hideRow(equipeWoRow, equipeWo);
        hideRow(placarARow, placarA);
        hideRow(placarBRow, placarB);
        hideRow(vencedoraRow, vencedora);
        hideRow(encerradaRow, encerrada);

        // ⛔ Partida não iniciada
        if (!partidaIniciada) return;

        // ▶ Partida iniciada → só mostra Houve WO
        showRow(houveWoRow, houveWo, true);

        // ⛔ Ainda não escolheu WO
        if (!houveWoValor) return;

        // =========================
        // 🟨 MODALIDADE SEM PLACAR
        // =========================
        if (!possuiPlacar) {
            if (houveWoEhSim) {
                showRow(equipeWoRow, equipeWo, true);
                showRow(encerradaRow, encerrada);
                encerrada.checked = true;
                encerrada.disabled = true;
            } else {
                showRow(vencedoraRow, vencedora, true);
                showRow(encerradaRow, encerrada);
                encerrada.disabled = false;
            }
            return;
        }

        // =========================
        // 🟦 MODALIDADE COM PLACAR
        // =========================
        if (houveWoEhSim) {
            showRow(equipeWoRow, equipeWo, true);
            showRow(encerradaRow, encerrada);
            encerrada.checked = true;
            encerrada.disabled = false;
        }

        if (houveWoEhNao) {
            showRow(placarARow, placarA, true);
            showRow(placarBRow, placarB, true);
            showRow(encerradaRow, encerrada);
            encerrada.disabled = false;
            encerrada.checked = false;
        }
    }

    atualizarCampos();

    modalidade?.addEventListener("change", atualizarCampos);
    iniciada?.addEventListener("change", function () {
        if (iniciada.checked) {
            const valido = validarEquipesAntesDeIniciar();

            if (!valido) {
                iniciada.checked = false;
                return;
            }
        } else {
            // 🔄 voltou para false → limpa tudo
            limparCamposDependentes();
        }

        atualizarCampos();
    });
    houveWo?.addEventListener("change", function () {
        // limpa equipe WO sempre que Houve WO mudar
        limparEquipeWo();
        atualizarCampos();
    });
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

