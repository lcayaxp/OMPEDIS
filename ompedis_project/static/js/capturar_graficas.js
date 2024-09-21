document.addEventListener("DOMContentLoaded", function () {
    // Seleccionar los gráficos
    const genderChart = document.getElementById('genderChart');
    const ageRangeChart = document.getElementById('ageRangeChart');
    const weeklyTherapiesChart = document.getElementById('weeklyTherapiesChart');

    // Función para capturar la imagen de un gráfico en base64
    function getChartImage(chartElement) {
        return chartElement.toDataURL("image/png");
    }

    // Al hacer clic en el botón de exportar PDF
    document.getElementById('exportarPdfBtn').addEventListener('click', function () {
        // Capturar las imágenes base64 de los gráficos
        const genderChartImage = getChartImage(genderChart);
        const ageRangeChartImage = getChartImage(ageRangeChart);
        const weeklyTherapiesChartImage = getChartImage(weeklyTherapiesChart);

        // Enviar las imágenes al backend usando fetch con POST
        fetch('/reportes/exportar-pdf/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Obtener el token CSRF para proteger la solicitud
            },
            body: JSON.stringify({
                gender_chart: genderChartImage,
                age_range_chart: ageRangeChartImage,
                weekly_therapies_chart: weeklyTherapiesChartImage,
            })
        })
        .then(response => response.blob())  // Recibir el PDF como blob
        .then(blob => {
            // Crear un enlace de descarga para el PDF
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'reportes_con_graficas.pdf';
            link.click();
        })
        .catch(error => {
            console.error('Error al exportar el PDF:', error);
        });
    });

    // Función para obtener el token CSRF (si usas protección CSRF)
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
