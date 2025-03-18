document.addEventListener('DOMContentLoaded', function() {
    // Attach click event to all edit buttons
    const editButtons = document.querySelectorAll('.edit-item-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName;
            const itemSerial = this.dataset.itemSerial;
            const itemProvider = this.dataset.itemProvider;
            const itemCategory = this.dataset.itemCategory;
            const itemPrice = this.dataset.itemPrice;

            document.getElementById('editItemId').value = itemId;
            document.getElementById('editItemName').value = itemName;
            document.getElementById('editItemSerial').value = itemSerial;
            document.getElementById('editItemProvider').value = itemProvider;
            document.getElementById('editItemCategory').value = itemCategory;
            // Convert price to a float (if possible) before setting the input value
            document.getElementById('editItemPrice').value = itemPrice ? parseFloat(itemPrice) : '';

            const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
            editModal.show();
        });
    });

    // Save edited item via PUT request
    document.getElementById('saveEditItem').addEventListener('click', function() {
        const itemId = document.getElementById('editItemId').value;
        const itemName = document.getElementById('editItemName').value;
        const itemSerial = document.getElementById('editItemSerial').value;
        const itemProvider = document.getElementById('editItemProvider').value;
        const itemCategory = document.getElementById('editItemCategory').value;
        const itemPrice = document.getElementById('editItemPrice').value;

        fetch(`/update-item/${itemId}/`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                name: itemName,
                serial_number: itemSerial,
                provider: itemProvider,
                category: itemCategory,
                price: itemPrice
            })
        })
        .then(response => {
            if (response.ok) {
                Swal.fire(
                    '¡Actualizado!',
                    'El producto ha sido actualizado.',
                    'success'
                );
                // Update the list item in the DOM
                const listItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('li');
                listItem.innerHTML = `
                    <div>
                        <strong>${itemName}</strong><br>
                        Número de Serie: ${itemSerial}<br>
                        Proveedor: ${itemProvider}<br>
                        Categoría: ${itemCategory}<br>
                        Precio: ${itemPrice}
                    </div>
                    <div>
                        <a href="#" class="btn btn-sm btn-primary mx-1 edit-item-btn"
                           data-item-id="${itemId}"
                           data-item-name="${itemName}"
                           data-item-serial="${itemSerial}"
                           data-item-provider="${itemProvider}"
                           data-item-category="${itemCategory}"
                           data-item-price="${itemPrice}"
                           style="width: 80px; display: inline-block;">Editar</a>
                        <a href="#" class="btn btn-sm btn-danger mx-1 delete-user-btn"
                           onclick="deleteItem('${itemId}')"
                           data-user-id="${itemId}"
                           style="width: 80px; display: inline-block;">Eliminar</a>
                    </div>
                `;
                // Re-bind the edit event for the updated edit button
                listItem.querySelector('.edit-item-btn').addEventListener('click', function() {
                    const itemId = this.dataset.itemId;
                    const itemName = this.dataset.itemName;
                    const itemSerial = this.dataset.itemSerial;
                    const itemProvider = this.dataset.itemProvider;
                    const itemCategory = this.dataset.itemCategory;
                    const itemPrice = this.dataset.itemPrice;
                    
                    document.getElementById('editItemId').value = itemId;
                    document.getElementById('editItemName').value = itemName;
                    document.getElementById('editItemSerial').value = itemSerial;
                    document.getElementById('editItemProvider').value = itemProvider;
                    document.getElementById('editItemCategory').value = itemCategory;
                    document.getElementById('editItemPrice').value = itemPrice ? parseFloat(itemPrice) : '';

                    const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
                    editModal.show();
                });
                // Close the modal
                const editModalElement = document.getElementById('editItemModal');
                const modalInstance = bootstrap.Modal.getInstance(editModalElement);
                modalInstance.hide();
            } else {
                Swal.fire(
                    'Error',
                    'No se pudo actualizar el producto.',
                    'error'
                );
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire(
                'Error',
                'Ocurrió un error al actualizar el producto.',
                'error'
            );
        });
    });
});

// CSRF token retrieval function (provided)
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