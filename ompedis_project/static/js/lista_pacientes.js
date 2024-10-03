document.addEventListener('htmx:afterRequest', function (event) {
    if (event.detail.target.id === 'confirm-modal .modal-content') {
        var modal = new bootstrap.Modal(document.getElementById('confirm-modal'));
        modal.show();
    }
});

document.addEventListener('htmx:afterOnLoad', function (event) {
    if (event.detail.target.id === 'confirm-modal .modal-content') {
        var modal = bootstrap.Modal.getInstance(document.getElementById('confirm-modal'));
        modal.hide();
        location.reload();  // Recarga la página para actualizar la lista de pacientes
    }
});