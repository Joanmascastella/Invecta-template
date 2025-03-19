function updateUserRole(userId) {
    const newRole = document.getElementById(`role-select-${userId}`).value;

    Swal.fire({
        title: '¿Estás seguro?',
        text: "¡Cambiar el rol del usuario!",
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, ¡actualizar!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/update-user/${userId}/`, {
                method: 'PUT',
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ new_role: newRole }),
            })
            .then(response => {
                if (response.ok) {
                    Swal.fire(
                        '¡Actualizado!',
                        'El rol del usuario ha sido actualizado.',
                        'success'
                    );
                    // Reload the page or update the role display
                    location.reload();
                } else {
                    Swal.fire(
                        'Error!',
                        'No se pudo actualizar el rol del usuario.',
                        'error'
                    );
                }
            })
            .catch(error => {
                Swal.fire(
                    'Error!',
                    'Se produjo un error.',
                    'error'
                );
            });
        }
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