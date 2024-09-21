// static/js/signup.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(form);

        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show SweetAlert success message
                Swal.fire({
                    title: '¡Registro exitoso!',
                    text: 'Usuario registrado con éxito.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = data.redirect_url; // Redirect to the specified URL
                    }
                });
            } else {
                // Show SweetAlert error message
                Swal.fire({
                    title: 'Error',
                    text: data.error || 'No se pudo registrar el usuario.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        })
        .catch(error => {
            // Show SweetAlert error message for network errors
            Swal.fire({
                title: 'Error',
                text: 'Ocurrió un error al intentar registrar el usuario.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    });
});