function toggleEstadoPaciente(checkbox) {
    const pacienteId = checkbox.getAttribute('data-id');
    const estado = checkbox.checked ? 'activo' : 'inactivo';

    fetch('/pacientes/cambiar-estado/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            id: pacienteId,
            estado: estado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            alert('No se pudo actualizar el estado del paciente.');
            checkbox.checked = !checkbox.checked; // Revertir el estado del toggle
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al intentar cambiar el estado.');
        checkbox.checked = !checkbox.checked;
    });
}

// Obtener el token CSRF (si es necesario)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
