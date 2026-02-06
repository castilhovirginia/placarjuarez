document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // 🎯 CAMPOS
    // =========================
    const fields = {
        modalidade: document.getElementById("id_modalidade"),
        iniciada: document.getElementById("id_iniciada"),

        equipeA: document.getElementById("id_equipe_a"),
        equipeB: document.getElementById("id_equipe_b"),

        houveWo: document.getElementById("id_houve_wo"),
        equipeWo: document.getElementById("id_equipe_wo"),

        placarA: document.getElementById("id_placar_a"),
        placarB: document.getElementById("id_placar_b"),

        houveEmpate: document.getElementById("id_houve_empate"),
        desempateA: document.getElementById("id_desempate_a"),
        desempateB: document.getElementById("id_desempate_b"),

        vencedora: document.getElementById("id_vencedora"),
        encerrada: document.getElementById("id_encerrada"),

        // Campos de sets
        primeiroSetA: document.getElementById("id_primeiroset_a"),
        primeiroSetB: document.getElementById("id_primeiroset_b"),
        segundoSetA: document.getElementById("id_segundoset_a"),
        segundoSetB: document.getElementById("id_segundoset_b"),
        terceiroSetA: document.getElementById("id_terceiroset_a"),
        terceiroSetB: document.getElementById("id_terceiroset_b"),
    };

    const setFields = [
        "primeiroSetA", "primeiroSetB",
        "segundoSetA", "segundoSetB",
        "terceiroSetA", "terceiroSetB"
    ];

    const dependentes = [
        "houveWo", "equipeWo",
        "placarA", "placarB",
        "houveEmpate", "desempateA", "desempateB",
        ...setFields,
        "vencedora",
        "encerrada"
    ];

    // =========================
    // 🧱 HELPERS VISUAIS
    // =========================
    const getRow = (field) => field?.closest(".form-row, .fieldBox, .form-group");
    const rows = {};
    Object.keys(fields).forEach(k => rows[k] = getRow(fields[k]));

    function hide(field) {
        if (rows[field]) rows[field].style.display = "none";
        if (fields[field]) {
            fields[field].required = false;
            fields[field].readOnly = false;
        }
    }

    function show(field, { required = false, readOnly = false } = {}) {
        if (rows[field]) rows[field].style.display = "";
        if (fields[field]) {
            fields[field].required = required;
            fields[field].readOnly = readOnly;
        }
    }

    function hideDependentes() {
        dependentes.forEach(f => hide(f));
    }

    // =========================
    // 📦 MAPAS DO TEMPLATE
    // =========================
    const possuiPlacarMap = JSON.parse(fields.modalidade?.dataset.possuiPlacarMap || "{}");
    const possuiSetMap = JSON.parse(fields.modalidade?.dataset.possuiSet || "{}");

    // =========================
    // 🧠 ESTADO
    // =========================
    function isTrue(value) {
        return ["true", "True", "sim", "1"].includes(String(value));
    }

    function getState() {
        const modalidadeVal = fields.modalidade?.value;
        return {
            iniciada: fields.iniciada?.checked,
            possuiPlacar: Boolean(possuiPlacarMap[modalidadeVal]),
            possuiSet: Boolean(possuiSetMap[modalidadeVal]),

            houveWoValor: fields.houveWo?.value,
            houveWoSim: fields.houveWo?.value === "sim",

            houveEmpateSim: isTrue(fields.houveEmpate?.value),
        };
    }

    // =========================
    // 🎨 RENDER
    // =========================
    function render() {
        // Oculta todos os campos dependentes
        hideDependentes();

        // Campos sempre visíveis
        show("modalidade");
        show("iniciada");
        show("equipeA");
        show("equipeB");

        const s = getState();

        // ⛔ Partida não iniciada → só mostra os campos base
        if (!s.iniciada) return;

        // ▶ Iniciada → mostrar Houve WO
        show("houveWo", { required: true });

        if (!s.houveWoValor) return;

        // =========================
        // 🟨 Sem placar
        // =========================
        if (!s.possuiPlacar) {
            if (s.houveWoSim) {
                show("equipeWo", { required: true });
            } else {
                show("vencedora", { required: true });
            }
            show("encerrada");
            return;
        }

        // =========================
        // 🟦 Com placar
        // =========================
        if (s.houveWoSim) {
            show("equipeWo", { required: true });
            show("encerrada");
            return;
        }

        // 🟦 Com placar, sem WO
        show("placarA", { required: true });
        show("placarB", { required: true });
        show("houveEmpate");
        show("encerrada");

        // ⚖️ Empate
        if (s.houveEmpateSim) {
            show("desempateA", { required: true });
            show("desempateB", { required: true });

            // Torna placares somente leitura
            show("placarA", { readOnly: true });
            show("placarB", { readOnly: true });
        }

        // 🆕 Campos de sets
        if (s.possuiPlacar && !s.houveWoSim && s.possuiSet) {
            setFields.forEach(f => show(f));
        }
    }

    // =========================
    // ✅ VALIDAÇÕES
    // =========================
    function validarEquipesAntesDeIniciar() {
        if (!fields.equipeA?.value || !fields.equipeB?.value) {
            alert("Selecione a Equipe A e a Equipe B antes de iniciar a partida.");
            return false;
        }

        if (fields.equipeA.value === fields.equipeB.value) {
            alert("Equipe A e Equipe B não podem ser a mesma.");
            return false;
        }

        return true;
    }

    function podeMarcarEmpate() {
        const a = fields.placarA?.value;
        const b = fields.placarB?.value;

        if (a === "" || b === "") return false;
        return Number(a) === Number(b);
    }

    function limparDependentes() {
        dependentes.forEach(f => {
            if (fields[f]) fields[f].value = "";
        });

        if (fields.encerrada) fields.encerrada.checked = false;
    }

    // =========================
    // 🔔 LISTENERS
    // =========================
    fields.modalidade?.addEventListener("change", render);

    fields.iniciada?.addEventListener("change", () => {
        if (fields.iniciada.checked && !validarEquipesAntesDeIniciar()) {
            fields.iniciada.checked = false;
            return;
        }

        if (!fields.iniciada.checked) limparDependentes();

        render();
    });

    fields.houveWo?.addEventListener("change", render);

    fields.houveEmpate?.addEventListener("change", function () {
        if (isTrue(fields.houveEmpate.value) && !podeMarcarEmpate()) {
            alert("Só é possível marcar empate quando o Placar A e o Placar B forem iguais.");
            fields.houveEmpate.value = "";
        }
        render();
    });

    // =========================
    // 🚀 INIT
    // =========================
    render();
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
