document.addEventListener('DOMContentLoaded', function () {
    const requestTypeField = document.getElementById('id_request_type');
    const statusField = document.getElementById('id_status');

    function toggleStatusOptions() {
        const selectedType = requestTypeField.value;

        Array.from(statusField.options).forEach(option => {
            if (selectedType === 'other' && (option.value === 'accepted' || option.value === 'rejected')) {
                option.style.display = 'none';
                if (option.selected) {
                    statusField.value = 'pending';
                }
            } else {
                option.style.display = '';
            }
        });
    }

    toggleStatusOptions();
    requestTypeField.addEventListener('change', toggleStatusOptions);
});
