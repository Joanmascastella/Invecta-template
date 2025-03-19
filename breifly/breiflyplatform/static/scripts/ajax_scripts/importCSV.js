document.getElementById('csvFileInput').addEventListener('change', handleFileUpload);

function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('csv_file', file);

  fetch('/upload/csv/', { 
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error('Upload failed.');
    }
  })
  .then(data => {
    Swal.fire(
      '¡Importado!',
      data.message || 'CSV importado correctamente.',
      'success'
    ).then(() => {
      location.reload(); 
    });
  })
  .catch(error => {
    Swal.fire(
      'Error!',
      error.message || 'Se produjo un error al importar el CSV.',
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