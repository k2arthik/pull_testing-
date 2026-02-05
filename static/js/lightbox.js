/**
 * Temple Gallery Lightbox Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    const templeCards = document.querySelectorAll('.temple-card');
    const modal = document.getElementById('templeLightbox');
    const closeBtn = document.querySelector('.modal-close');
    const modalName = document.getElementById('modalTempleName');
    const modalLocation = document.getElementById('modalTempleLocation');
    const galleryContainer = document.getElementById('galleryContainer');

    const templeData = {
        'kashi': {
            name: 'Kashi Vishwanath',
            location: 'Varanasi, UP',
            images: [
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Kashi_Vishwanath_Temple_Main_Area-3.jpg', title: 'Golden Temple Spire' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Dashashwamedh_Ghat, Benares.jpg', title: 'Dashashwamedh Ghat' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Shri Kashi Vishwanath Temple.jpg', title: 'Sacred Sanctum' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/View of Kashi Vishwanath Temple from a boat at night.jpg', title: 'Ganga Aarti View' }
            ]
        },
        'tirupati': {
            name: 'Tirupati Balaji',
            location: 'Tirumala, AP',
            images: [
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Tirumala_Tirupati.jpg', title: 'Ananda Nilayam Golden Vimanam' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Silathoranam_Tirupati.jpg', title: 'Sila Thoranam (Natural Arch)' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Swami_Pushkarini.jpg', title: 'Swami Pushkarini Holy Tank' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Silathoranam%2C_Tirumala_hills.jpg', title: 'Tirumala Seshachalam Hills' }
            ]
        },
        'meenakshi': {
            name: 'Meenakshi Temple',
            location: 'Madurai, TN',
            images: [
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Madurai_Meenakshi_Amman_Temple_Gopuram_view.jpg', title: 'Southern Gopuram (Gateway)' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Inside_the_Thousand_Pillar_Hall_Meenakshi_Amman_Temple%2C_Madurai.jpg', title: 'Hall of Thousand Pillars' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Madurai_Meenakshi_temple_tank.jpg', title: 'Golden Lotus Pond' },
                { url: 'https://commons.wikimedia.org/wiki/Special:FilePath/Tank_of_the_Golden_Lotus%2C_Meenakshi_Temple%2C_Madurai_%284%29_%2823675258818%29.jpg', title: 'Detailed Stucco Sculptures' }
            ]
        }
    };

    templeCards.forEach(card => {
        card.addEventListener('click', () => {
            const galleryId = card.getAttribute('data-gallery');
            const data = templeData[galleryId];

            if (data) {
                modalName.textContent = data.name;
                modalLocation.textContent = data.location;

                // Clear and fill gallery
                galleryContainer.innerHTML = '';
                data.images.forEach(img => {
                    const div = document.createElement('div');
                    div.className = 'gallery-item';
                    div.innerHTML = `
                        <img src="${img.url}" alt="${img.title}">
                        <div class="gallery-caption">${img.title}</div>
                    `;
                    galleryContainer.appendChild(div);
                });

                // Show modal
                modal.classList.add('active');
                document.body.style.overflow = 'hidden'; // Prevent scroll
            }
        });
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto'; // Restore scroll
    });

    // Close on click outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    });

    // Close on Escape key
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    });
});
