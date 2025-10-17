let sockets = {};

// WebSocket initialization
function initWebSocket(table) {
    sockets[table] = new WebSocket(`ws://localhost:8080/ws/${table}`);
    sockets[table].onmessage = function(event) {
        if (event.data === `update_${table}`) {
            console.log(`Received WebSocket update for ${table}`);
            refreshList(table);
        }
    };
    sockets[table].onclose = function() {
        console.log(`WebSocket closed for ${table}, reconnecting...`);
        setTimeout(() => initWebSocket(table), 5000);
    };
    sockets[table].onerror = function(error) {
        console.error(`WebSocket error for ${table}:`, error);
    };
}

// Refresh list via WebSocket updates
async function refreshList(table) {
    try {
        console.log(`Refreshing list for ${table}`);
        const response = await fetch(`/${table}/list`);
        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
        const data = await response.json();
        console.log(`Fetched data for ${table}:`, data);
        const tableBody = document.querySelector(`#${table}-table tbody`);
        const noDataMessage = document.querySelector(`#${table}-list p`);
        if (data.length > 0) {
            tableBody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'border-t';
                row.dataset.name = item.name || item.date || item.id;
                row.dataset.filter = item.specialty || item.email || item.is_available || item.appointment_id || item.reason || '';
                if (table === 'doctors') {
                    row.innerHTML = `
                        <td class="p-3">${item.id}</td>
                        <td class="p-3">${item.name}</td>
                        <td class="p-3">${item.specialty}</td>
                        <td class="p-3 flex space-x-2">
                            <button onclick="openEditModal('${table}', ${item.id}, '${item.name.replace(/'/g, "\\'")}', '${item.specialty.replace(/'/g, "\\'")}')" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteEntity(${item.id}, 'Doctor', '/${table}/delete')" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                } else if (table === 'patients') {
                    row.innerHTML = `
                        <td class="p-3">${item.id}</td>
                        <td class="p-3">${item.name}</td>
                        <td class="p-3">${item.email}</td>
                        <td class="p-3 flex space-x-2">
                            <button onclick="openEditModal('${table}', ${item.id}, '${item.name.replace(/'/g, "\\'")}', '${item.email.replace(/'/g, "\\'")}')" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteEntity(${item.id}, 'Patient', '/${table}/delete')" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                } else if (table === 'appointment_slots') {
                    row.innerHTML = `
                        <td class="p-3">${item.id}</td>
                        <td class="p-3">${item.doctor_id}</td>
                        <td class="p-3">${item.date}</td>
                        <td class="p-3">${item.start_time}</td>
                        <td class="p-3">${item.end_time}</td>
                        <td class="p-3">${item.is_available}</td>
                        <td class="p-3 flex space-x-2">
                            <button onclick="openEditModal('${table}', ${item.id}, ${item.doctor_id}, '${item.date}', '${item.start_time}', '${item.end_time}', ${item.is_available})" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteEntity(${item.id}, 'Slot', '/${table}/delete')" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                } else if (table === 'appointments') {
                    row.innerHTML = `
                        <td class="p-3">${item.id}</td>
                        <td class="p-3">${item.patient_id}</td>
                        <td class="p-3">${item.slot_id}</td>
                        <td class="p-3">${item.booked_at}</td>
                        <td class="p-3 flex space-x-2">
                            <button onclick="openEditModal('${table}', ${item.id}, ${item.patient_id}, ${item.slot_id})" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteEntity(${item.id}, 'Appointment', '/${table}/delete')" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                } else if (table === 'cancellations') {
                    row.innerHTML = `
                        <td class="p-3">${item.id}</td>
                        <td class="p-3">${item.appointment_id}</td>
                        <td class="p-3">${item.reason || ''}</td>
                        <td class="p-3">${item.cancelled_at}</td>
                        <td class="p-3 flex space-x-2">
                            <button onclick="openEditModal('${table}', ${item.id}, ${item.appointment_id}, '${item.reason ? item.reason.replace(/'/g, "\\'") : ''}')" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteEntity(${item.id}, 'Cancellation', '/${table}/delete')" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                }
                tableBody.appendChild(row);
            });
            if (noDataMessage) noDataMessage.remove();
        } else {
            tableBody.innerHTML = '';
            if (!noDataMessage) {
                const p = document.createElement('p');
                p.className = 'text-gray-600';
                p.textContent = `No ${table} found.`;
                document.getElementById(`${table}-list`).appendChild(p);
            }
        }
        filterList(table);
    } catch (error) {
        console.error(`Error refreshing ${table} list:`, error);
        showModal(`Error refreshing ${table} list: ${error.message}`, 'error');
    }
}

// Modal feedback
function showModal(message, type) {
    const modal = document.getElementById('feedback-modal');
    const modalMessage = document.getElementById('modal-message');
    
    modalMessage.className = `p-6 rounded-lg shadow-lg max-w-md w-full ${
        type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    }`;
    modalMessage.innerHTML = `
        <p class="text-lg font-semibold mb-4">${message}</p>
        <button onclick="closeModal()" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 w-full">Close</button>
    `;
    
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('feedback-modal').classList.add('hidden');
}

// Add modal functions
function openAddModal(entity) {
    console.log(`Opening add modal for ${entity}`);
    document.getElementById(`add-${entity}-modal`).classList.remove('hidden');
}

function closeAddModal(entity) {
    document.getElementById(`add-${entity}-modal`).classList.add('hidden');
    document.getElementById(`add-${entity}-form`).reset();
}

// Edit modal functions
function openEditModal(entity, id, ...fields) {
    console.log(`Opening edit modal for ${entity} ID ${id}`, fields);
    const modal = document.getElementById(`edit-${entity}-modal`);
    document.getElementById(`edit-${entity}-id`).value = id;
    
    if (entity === 'doctors') {
        document.getElementById(`edit-${entity}-name`).value = fields[0];
        document.getElementById(`edit-${entity}-specialty`).value = fields[1];
    } else if (entity === 'patients') {
        document.getElementById(`edit-${entity}-name`).value = fields[0];
        document.getElementById(`edit-${entity}-email`).value = fields[1];
    } else if (entity === 'appointment_slots') {
        document.getElementById(`edit-${entity}-doctor-id`).value = fields[0];
        document.getElementById(`edit-${entity}-date`).value = fields[1];
        document.getElementById(`edit-${entity}-start-time`).value = fields[2];
        document.getElementById(`edit-${entity}-end-time`).value = fields[3];
        document.getElementById(`edit-${entity}-is-available`).value = fields[4] ? 'true' : 'false';
    } else if (entity === 'appointments') {
        document.getElementById(`edit-${entity}-patient-id`).value = fields[0];
        document.getElementById(`edit-${entity}-slot-id`).value = fields[1];
    } else if (entity === 'cancellations') {
        document.getElementById(`edit-${entity}-appointment-id`).value = fields[0];
        document.getElementById(`edit-${entity}-reason`).value = fields[1];
    }
    
    modal.classList.remove('hidden');
}

function closeEditModal(entity) {
    document.getElementById(`edit-${entity}-modal`).classList.add('hidden');
    document.getElementById(`edit-${entity}-form`).reset();
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input:not([type="hidden"]), select');
    let valid = true;
    inputs.forEach(input => {
        if (!input.value && input.hasAttribute('required')) {
            input.classList.add('border-red-500');
            valid = false;
        } else {
            input.classList.remove('border-red-500');
        }
    });
    return valid;
}

// Submit form
async function submitForm(event, endpoint, formId, entityName) {
    event.preventDefault();
    console.log(`Submitting form ${formId} to ${endpoint}`);
    
    if (!validateForm(formId)) {
        showModal('Please fill all required fields', 'error');
        return;
    }
    
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    console.log('Form data:', Object.fromEntries(formData));
    
    // Determine entity type for modal closing
    const entityLower = entityName.toLowerCase();
    const isAddForm = formId.includes('add');
    const modalEntity = entityLower === 'slot' ? 'appointment_slots' : entityLower + 's';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error response: ${errorText}`);
            throw new Error(`HTTP error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`Form submission result:`, result);
        
        if (result.status === 'success') {
            // FIRST: Close the form modal
            if (isAddForm) {
                closeAddModal(modalEntity);
            } else {
                closeEditModal(modalEntity);
            }
            
            // Reset the form
            form.reset();
            
            // SECOND: Show success feedback modal (after a tiny delay to ensure form modal closes)
            setTimeout(() => {
                showModal(`${entityName} ${isAddForm ? 'added' : 'updated'} successfully!`, 'success');
            }, 100);
            
            // THIRD: Reload page after showing message
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            // On error, also close form modal first, then show error
            if (isAddForm) {
                closeAddModal(modalEntity);
            } else {
                closeEditModal(modalEntity);
            }
            
            setTimeout(() => {
                showModal(`Error: ${result.detail || 'Unknown error'}`, 'error');
            }, 100);
        }
    } catch (error) {
        console.error('Error:', error);
        
        // On exception, close form modal first
        if (isAddForm) {
            closeAddModal(modalEntity);
        } else {
            closeEditModal(modalEntity);
        }
        
        setTimeout(() => {
            showModal(`Error: ${error.message}`, 'error');
        }, 100);
    }
}

// Delete entity
async function deleteEntity(id, entityName, endpoint) {
    if (!confirm(`Are you sure you want to delete this ${entityName.toLowerCase()}?`)) {
        return;
    }
    
    const formData = new FormData();
    formData.append(`${entityName.toLowerCase()}_id`, id);
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showModal(`${entityName} deleted successfully!`, 'success');
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showModal(`Error: ${result.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showModal(`Error: ${error.message}`, 'error');
    }
}

// Filter list
function filterList(entity) {
    const searchInput = document.getElementById(`search-${entity}`);
    const filterSelect = document.getElementById(`filter-${entity}`);
    
    if (!searchInput) return;
    
    const searchValue = searchInput.value.toLowerCase();
    const filterValue = filterSelect ? filterSelect.value : '';
    const rows = document.querySelectorAll(`#${entity}-table tbody tr`);

    rows.forEach(row => {
        const name = row.dataset.name.toLowerCase();
        const filter = row.dataset.filter;
        const matchesSearch = name.includes(searchValue);
        const matchesFilter = filterValue === '' || filter === filterValue;
        row.style.display = matchesSearch && matchesFilter ? '' : 'none';
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    ['doctors', 'patients', 'appointment_slots', 'appointments', 'cancellations'].forEach(table => {
        if (document.getElementById(`${table}-table`)) {
            console.log(`Initializing WebSocket for ${table}`);
            initWebSocket(table);
            refreshList(table);
        }
    });
});