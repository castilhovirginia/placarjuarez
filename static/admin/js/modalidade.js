// admin/js/modalidade.js
document.addEventListener("DOMContentLoaded", function () {
    if (typeof django === "undefined" || !django.jQuery) {
        console.error("django.jQuery não está disponível!");
        return;
    }

    var $ = django.jQuery;

    function atualizarPossuiSets($row) {
        var $possuiPlacar = $row.find('[id$="possui_placar"]');
        var $possuiSetsInput = $row.find('[id$="possui_sets"]');
        var $possuiSetsRow = $possuiSetsInput.closest('.form-row');

        if (!$possuiSetsInput.length) {
            return;
        }

        if ($possuiPlacar.is(':checked')) {
            $possuiSetsRow.show();
            $possuiSetsInput.prop('required', true);
        } else {
            $possuiSetsRow.hide();
            $possuiSetsInput.prop('required', false);

            // limpa o valor (checkbox ou select)
            if ($possuiSetsInput.is(':checkbox')) {
                $possuiSetsInput.prop('checked', false);
            } else {
                $possuiSetsInput.val('');
            }
        }
    }

    function initRow($row) {
        atualizarPossuiSets($row);

        $row.find('[id$="possui_placar"]').on('change', function () {
            atualizarPossuiSets($row);
        });
    }

    // Formulário principal
    initRow($(document));

    // Inlines existentes
    $('.inline-related').each(function () {
        initRow($(this));
    });

    // Novos inlines adicionados dinamicamente
    $(document).on('formset:added', function (event, $row) {
        initRow($row);
    });
});
