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
            } else {
                showRow(vencedoraRow, vencedora, true);
                showRow(encerradaRow, encerrada);
            }
            return;
        }

        // =========================
        // 🟦 MODALIDADE COM PLACAR
        // =========================
        if (houveWoEhSim) {
            showRow(equipeWoRow, equipeWo, true);
            showRow(encerradaRow, encerrada);
        }

        if (houveWoEhNao) {
            showRow(placarARow, placarA, true);
            showRow(placarBRow, placarB, true);
            showRow(encerradaRow, encerrada);
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

document.addEventListener('DOMContentLoaded', function() {
    const faseField = document.getElementById('id_fase');
    const numeroField = document.getElementById('id_numero');

    // Mapear números válidos por fase
    const numerosPorFase = {
        'OIT': ['PRI', 'SEG', 'TER', 'QUA'],
        'QUA': ['QUI', 'SEX', 'SET', 'OIT'],
        'SEM': ['NON', 'DEC'],
        'TER': ['DECPRI'],
        'FIN': ['DECSEG']
    };

    function updateNumeroOptions() {
        const fase = faseField.value;
        const validNumbers = numerosPorFase[fase] || [];

        // Habilitar/desabilitar opções existentes
        for (let i = 0; i < numeroField.options.length; i++) {
            const option = numeroField.options[i];

            // Sempre permite a opção vazia
            if (option.value === "") {
                option.disabled = false;
                continue;
            }

            option.disabled = !validNumbers.includes(option.value);
        }

        // Se o valor atual não for válido, seleciona o primeiro válido
        if (!validNumbers.includes(numeroField.value) && validNumbers.length > 0) {
            numeroField.value = validNumbers[0];
        }
    }

    // Atualiza ao mudar a fase
    faseField.addEventListener('change', updateNumeroOptions);

    // Inicializa ao carregar a página
    updateNumeroOptions();
});

document.addEventListener('DOMContentLoaded', function () {
    const iniciadaCheckbox = document.getElementById('id_iniciada');

    if (!iniciadaCheckbox) return;

    // guarda o valor original (importante ao editar)
    let valorAnterior = iniciadaCheckbox.checked;

    iniciadaCheckbox.addEventListener('change', function () {

        // TRUE → FALSE
        if (!this.checked && valorAnterior) {
            const confirmado = confirm(
                "⚠️ Atenção!\n\n" +
                "Ao desmarcar a partida como iniciada, o resultado será apagado e os dados que eventualmente tenham sido gravados na próxima fase também.\n\n" +
                "Deseja continuar?"
            );

            if (!confirmado) {
                this.checked = true; // volta para true
            }
        }

        valorAnterior = this.checked;
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const encerradaCheckbox = document.getElementById('id_encerrada');

    if (!encerradaCheckbox) return;

    // valor original ao carregar o form (edição)
    let valorAnterior = encerradaCheckbox.checked;

    encerradaCheckbox.addEventListener('change', function () {

        // só entra se houve mudança real
        if (this.checked !== valorAnterior) {

            const mensagem = this.checked
                ? "⚠️ Atenção!\n\nAo ENCERRAR a partida, o resultado será enviado para a próxima fase.\n\nVerifique se está tudo correto!"
                : "⚠️ Atenção!\n\nAo REABRIR a partida, o resultado será removido da próxima fase.\n\nVerifique se é isso que deseja e que está tudo correto antes de salvar!";

            const confirmado = confirm(mensagem);

            if (!confirmado) {
                // volta ao estado anterior
                this.checked = valorAnterior;
                return;
            }

            valorAnterior = this.checked;
        }
    });
});
