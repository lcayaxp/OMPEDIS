document.addEventListener("DOMContentLoaded", function () {
    const successMessage = document.getElementById("success-message");

    if (successMessage) {
        // Mostrar el mensaje de éxito durante 5 segundos
        successMessage.style.display = "block";
        setTimeout(() => {
            successMessage.style.display = "none";
        }, 5000);
    }
});
