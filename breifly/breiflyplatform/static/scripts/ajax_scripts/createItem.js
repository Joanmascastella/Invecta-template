document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('saveCreateItem').addEventListener('click', function() {
        const formData = {
            name: document.getElementById('createItemName').value,
            serial_number: document.getElementById('createItemSerial').value,
            provider: document.getElementById('createItemProvider').value,
            category: document.getElementById('createItemCategory').value,
            price: parseFloat(document.getElementById('createItemPrice').value)
        };

        fetch('/create-item/', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Error creating item'); });
            }
            return response.json();
        })
        .then(newItem => {
            Swal.fire('¡Creado!', 'El artículo ha sido creado.', 'success');
            
            const itemsList = document.getElementById('items-list');
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.setAttribute('data-item-id', newItem.item_id);
            li.innerHTML = `
                <div>
                    <strong>${newItem.name}</strong><br>
                    Número de Serie: ${newItem.serial_number}<br>
                    Proveedor: ${newItem.provider}<br>
                    Categoría: ${newItem.category}<br>
                    Precio: ${newItem.price}
                </div>
                <div>
                    <a href="#" class="btn btn-sm btn-primary mx-1 edit-item-btn"
                       data-item-id="${newItem.item_id}"
                       data-item-name="${newItem.name}"
                       data-item-serial="${newItem.serial_number}"
                       data-item-provider="${newItem.provider}"
                       data-item-category="${newItem.category}"
                       data-item-price="${newItem.price}"
                       style="width: 80px; display: inline-block;">Editar</a> <br>
                    <a href="#" class="btn btn-sm btn-danger mx-1 delete-user-btn"
                       onclick="deleteItem('${newItem.item_id}')"
                       data-user-id="${newItem.item_id}"
                       style="width: 80px; display: inline-block;">Eliminar</a>
                </div>
            `;
            itemsList.prepend(li); // Add new item to the top of the list

            const createModal = bootstrap.Modal.getInstance(document.getElementById('createItemModal'));
            createModal.hide();
            document.getElementById('createItemForm').reset();
        })
        .catch(error => {
            Swal.fire('Error', error.message, 'error');
        });
    });
});