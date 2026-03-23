// Cart Management Logic
document.addEventListener('DOMContentLoaded', function () {
    updateCartCount();

    // If we are on the cart page, render the items
    if (document.getElementById('cart-items')) {
        renderCartItems();
    }
});

function getCart() {
    const cart = localStorage.getItem('poojaCart');
    return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
    localStorage.setItem('poojaCart', JSON.stringify(cart));
    updateCartCount();
}

/**
 * Add a pooja to the cart
 * @param {string} id - Unique slug/id of the pooja
 * @param {string} title - Display title
 * @param {string} price - Price string (e.g., "₹3,000")
 * @param {string} image - Image URL
 */
function addToCart(id, title, price, image) {
    let cart = getCart();

    // Collect extra details if we are on a detail page
    const dateInput = document.getElementById('pooja_date');
    const nameInput = document.getElementById('devotee_name');
    const gothramInput = document.getElementById('devotee_gothram');
    const nakshatramInput = document.getElementById('devotee_nakshatram');

    const details = {
        date: dateInput ? dateInput.value : '',
        devoteeName: nameInput ? nameInput.value : '',
        gothram: gothramInput ? gothramInput.value : '',
        nakshatram: nakshatramInput ? nakshatramInput.value : ''
    };

    // Check if already in cart (with same details for simplicity, or just same ID?)
    // User might want to book the same pooja twice with different dates/people.
    // For now, let's allow multiple entries if details vary, or just update.
    // Let's stick to unique ID for now to keep it simple as per initial request.
    const exists = cart.find(item => item.id === id);
    if (!exists) {
        cart.push({ id, title, price, image, details });
        saveCart(cart);
        alert(`${title} added to your cart!`);
    } else {
        // Update details if already exists
        exists.details = details;
        saveCart(cart);
        alert(`${title} updated with your details.`);
    }
}

function removeFromCart(id) {
    let cart = getCart();
    cart = cart.filter(item => item.id !== id);
    saveCart(cart);
    renderCartItems();
}

function updateCartCount() {
    const cart = getCart();
    const countElements = document.querySelectorAll('.cart-count');
    countElements.forEach(el => {
        el.textContent = cart.length;
        el.style.display = cart.length > 0 ? 'flex' : 'none';
    });
}

function renderCartItems() {
    const cartContainer = document.getElementById('cart-items');
    const subtotalEl = document.getElementById('subtotal');
    const totalEl = document.getElementById('total-amount');

    if (!cartContainer) return;

    const cart = getCart();

    if (cart.length === 0) {
        cartContainer.innerHTML = '<p style="text-align: center; color: #888; padding: 20px 0;">Your cart is empty.</p>';
        subtotalEl.textContent = '₹0.00';
        totalEl.textContent = '₹0.00';
        return;
    }

    let html = '';
    let total = 0;

    cart.forEach(item => {
        // Extract numeric price for calculation (assuming format "₹3,000" or range "₹3,000 - ₹10,000")
        // We'll take the base price for the summary
        const basePriceStr = item.price.split('-')[0].replace(/[^\d]/g, '');
        const price = parseInt(basePriceStr) || 0;
        total += price;

        html += `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.title}" class="cart-item-img">
                <div class="cart-item-details">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin: 0; font-weight: 600;">${item.title}</h4>
                        <button type="button" onclick="removeFromCart('${item.id}')" style="background: none; border: none; color: #ff3333; cursor: pointer; font-size: 14px;"><i class="fas fa-trash"></i></button>
                    </div>
                    <p style="color: #E24028; font-weight: 700; margin: 4px 0;">${item.price}</p>
                    ${item.details ? `
                        <div class="item-devotee-info" style="font-size: 12px; color: #666; background: #f9f9f9; padding: 6px; border-radius: 4px; margin-top: 5px;">
                            ${item.details.date ? `<div><strong>Date:</strong> ${item.details.date}</div>` : ''}
                            ${item.details.devoteeName ? `<div><strong>Name:</strong> ${item.details.devoteeName}</div>` : ''}
                            ${item.details.gothram ? `<div><strong>Gothram:</strong> ${item.details.gothram}</div>` : ''}
                            ${item.details.nakshatram ? `<div><strong>Star:</strong> ${item.details.nakshatram}</div>` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });

    cartContainer.innerHTML = html;
    const formattedTotal = '₹' + total.toLocaleString('en-IN');
    if (subtotalEl) subtotalEl.textContent = formattedTotal;
    if (totalEl) totalEl.textContent = formattedTotal;

    // Handle checkout form submission
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function (e) {
            e.preventDefault();
            alert('Payment initiated. This would redirect to Razorpay in a live environment.');
            // Clear cart after successful checkout (simulated)
            localStorage.removeItem('poojaCart');
            updateCartCount();
            window.location.href = '/'; // Redirect to home
        });
    }
}
