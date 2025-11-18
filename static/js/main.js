// JavaScript pour l'application ALUBILLES

document.addEventListener('DOMContentLoaded', function() {
    // Prévisualisation de la photo
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photo-preview');
    const photoUpload = document.querySelector('.photo-upload');

    if (photoInput) {
        photoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (photoPreview) {
                        photoPreview.src = e.target.result;
                        photoPreview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });

        // Clic sur la zone de téléchargement
        if (photoUpload) {
            photoUpload.addEventListener('click', function() {
                photoInput.click();
            });
        }
    }

    // Validation du formulaire
    const form = document.getElementById('inscription-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const nom = document.getElementById('nom').value.trim();
            const prenom = document.getElementById('prenom').value.trim();

            if (!nom || !prenom) {
                e.preventDefault();
                alert('Le nom et le prénom sont obligatoires!');
                return false;
            }

            // Afficher un message de chargement
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Inscription en cours...';
            }
        });
    }

    // Confirmation de suppression
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Etes-vous sur de vouloir supprimer ce membre?')) {
                e.preventDefault();
            }
        });
    });

    // Charger les statistiques
    loadStats();
});

// Fonction pour charger les statistiques
function loadStats() {
    const statsContainer = document.getElementById('stats-container');
    if (statsContainer) {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-membres').textContent = data.total_membres;
            })
            .catch(error => console.error('Erreur:', error));
    }
}

// Fonction pour formater la date
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}
