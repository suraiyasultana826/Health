function showModal(message, type) {
    const modal = document.getElementById('feedback-modal');
    const modalMessage = document.getElementById('modal-message');
    modalMessage.innerText = message;
    modal.className = `fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50`;
    modalMessage.className = `p-4 rounded-lg ${type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`;
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('feedback-modal').style.display = 'none';
}

function openAddDoctorModal() {
    document.getElementById('add-doctor-modal').style.display = 'block';
}

function closeAddDoctorModal() {
    document.getElementById('add-doctor-modal').style.display = 'none';
    document.getElementById('add-doctor-form').reset();
}

function openEditDoctorModal(id, name, specialty) {
    document.getElementById('edit-doctor-id').value = id;
    document.getElementById('edit-doctor-name').value = name;
    document.getElementById('edit-doctor-specialty').value = specialty;
    document.getElementById('edit-doctor-modal').style.display = 'block';
}

function closeEditDoctorModal() {
    document.getElementById('edit-doctor-modal').style.display = 'none';
    document.getElementById('edit-doctor-form').reset();
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input, select');
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

async function submitForm(event, endpoint, formId, entity) {
    event.preventDefault();
    if (!validateForm(formId)) {
        showModal('Please fill all required fields', 'error');
        return;
    }
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.status === 'success') {
            const idKey = entity.toLowerCase() + '_id';
            showModal(`Success: ${entity} ${formId.includes('add') ? 'created with ID ' + result[idKey] : 'updated'}`, 'success');
            form.reset();
            if (formId.includes('add')) closeAddDoctorModal();
            if (formId.includes('edit')) closeEditDoctorModal();
            setTimeout(() => window.location.reload(), 2000);
        } else {
            showModal(result.message || `Error processing ${entity.toLowerCase()} request`, 'error');
        }
    } catch (error) {
        showModal(`Error submitting ${entity.toLowerCase()} form`, 'error');
    }
}

async function deleteEntity(id, entity, endpoint) {
    if (!confirm(`Are you sure you want to delete ${entity} ID ${id}?`)) return;
    const formData = new FormData();
    formData.append(`${entity.toLowerCase()}_id`, id);
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.status === 'success') {
            showModal(`Success: ${entity} deleted`, 'success');
            setTimeout(() => window.location.reload(), 2000);
        } else {
            showModal(result.message || `Error deleting ${entity.toLowerCase()}`, 'error');
        }
    } catch (error) {
        showModal(`Error deleting ${entity.toLowerCase()}`, 'error');
    }
}

function filterDoctors() {
    const searchName = document.getElementById('search-name').value.toLowerCase();
    const filterSpecialty = document.getElementById('filter-specialty').value;
    const rows = document.querySelectorAll('#doctors-table tbody tr');

    rows.forEach(row => {
        const name = row.dataset.name.toLowerCase();
        const specialty = row.dataset.specialty;
        const matchesName = name.includes(searchName);
        const matchesSpecialty = filterSpecialty === '' || specialty === filterSpecialty;
        row.style.display = matchesName && matchesSpecialty ? '' : 'none';
    });
}