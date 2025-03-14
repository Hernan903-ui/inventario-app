document.addEventListener('DOMContentLoaded', () => {
    // Validación de formularios en tiempo real
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            let valid = true;
            form.querySelectorAll('input[required]').forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('invalid');
                    valid = false;
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Por favor complete todos los campos requeridos');
            }
        });
    });

    // Resaltar campos inválidos
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', () => {
            if (input.checkValidity()) {
                input.classList.remove('invalid');
            }
        });
    });

    // Agregar ícono de alerta a productos con stock bajo
    document.querySelectorAll('.stock-bajo').forEach(row => {
        const alertIcon = document.createElement('span');
        alertIcon.className = 'alert-icon';
        alertIcon.textContent = '⚠️';
        row.querySelector('td:first-child').appendChild(alertIcon);
    });
});