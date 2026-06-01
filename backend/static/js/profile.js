document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const data = {
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                email: document.getElementById('email').value,
            };
            try {
                const resp = await apiRequest('/auth/profile/', {
                    method: 'PATCH',
                    body: data,
                });
                if (resp && resp.ok) {
                    showToast('Perfil actualizado correctamente', 'success');
                } else if (resp) {
                    const err = await resp.json();
                    showToast(Object.values(err).flat().join(', '), 'danger');
                }
            } catch (e) {
                handleApiError(e);
            }
        });
    }

    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const current = document.getElementById('currentPassword').value;
            const newPass = document.getElementById('newPassword').value;
            const confirm = document.getElementById('confirmPassword').value;
            if (newPass !== confirm) {
                showToast('Las contraseñas no coinciden', 'danger');
                return;
            }
            try {
                const resp = await apiRequest('/auth/profile/', {
                    method: 'PATCH',
                    body: { current_password: current, password: newPass },
                });
                if (resp && resp.ok) {
                    showToast('Contraseña cambiada correctamente', 'success');
                    passwordForm.reset();
                } else if (resp) {
                    const err = await resp.json();
                    showToast(Object.values(err).flat().join(', '), 'danger');
                }
            } catch (e) {
                handleApiError(e);
            }
        });
    }
});