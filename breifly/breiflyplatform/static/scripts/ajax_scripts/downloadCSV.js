function downloadCSV() {
    fetch(`/download/csv/`, {
        method: 'GET',
        headers: {
            "X-CSRFToken": getCSRFToken(),
        },
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'exported_stock_item_data.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        Swal.fire(
            '¡Descargado!',
            'Los articulos estan preparados para descargar.',
            'success'
        );
    })
    .catch(error => {
        Swal.fire(
            'Error!',
            'Se produjo un error.',
            'error'
        );
    });
}

// Function to get CSRF token from cookies
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
                break;
            }
        }
    }
    return cookieValue;
}