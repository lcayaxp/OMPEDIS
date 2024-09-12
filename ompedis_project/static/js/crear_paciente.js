$(document).ready(function() {
    // Inicialización de Select2 para los campos de departamento y municipio
    $('#id_departamento').select2({
        placeholder: 'Seleccione un Departamento',
        width: '100%'
    }).on('change', function () {
        var departamentoId = $(this).val(); // Obtén el ID del departamento seleccionado
        var url = $(this).data('url');      // URL para cargar municipios (establecida en el template)

        if (departamentoId) {
            $.ajax({
                url: url,
                data: {
                    'departamento_id': departamentoId
                },
                success: function(data) {
                    var municipios = $("#id_municipio");
                    municipios.empty(); // Limpia el campo de municipios
                    municipios.append('<option value="">Seleccione un Municipio</option>'); // Añade la opción por defecto
                    $.each(data, function(index, value) {
                        municipios.append('<option value="' + value.id + '">' + value.nombre + '</option>');
                    });
                    municipios.prop('disabled', false); // Habilita el campo de municipios
                    municipios.select2({
                        placeholder: 'Seleccione un Municipio',
                        width: '100%'
                    });
                },
                error: function() {
                    alert('Error al cargar los municipios.'); // Mensaje de error en caso de fallo
                }
            });
        } else {
            $("#id_municipio").empty().append('<option value="">Seleccione un Departamento primero</option>');
            $("#id_municipio").prop('disabled', true); // Deshabilita el campo de municipios si no se selecciona un departamento
        }
    });

    // Inicializa Select2 para el campo de municipios
    $('#id_municipio').select2({
        placeholder: 'Seleccione un Municipio',
        width: '100%'
    });
});
