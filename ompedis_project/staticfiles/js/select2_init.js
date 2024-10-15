// select2_init.js

$(document).ready(function() {
    // Inicialización de Select2 para el campo 'paciente'
    $('#id_paciente').select2({
        placeholder: 'Busca un paciente...',  // Texto de marcador de posición para el campo
        allowClear: true,                    // Permite limpiar la selección
        width: '100%',                       // Ajusta el ancho del Select2 al 100% del contenedor
        language: {
            noResults: function() {          // Mensaje personalizado para cuando no se encuentran resultados
                return "No se encontraron pacientes";
            }
        }
    });
});

