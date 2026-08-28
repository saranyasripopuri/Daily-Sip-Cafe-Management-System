// ==============================
// DAILY SIP - ORDER MODULE
// ==============================

let cart = [];

const menuButtons = document.querySelectorAll(".food-btn");
const cartItems = document.getElementById("cartItems");
const subtotal = document.getElementById("subtotal");
const gst = document.getElementById("gst");
const grandTotal = document.getElementById("grandTotal");

const clearOrderBtn = document.querySelector(".clear-order");
const placeOrderBtn = document.querySelector(".place-order");

const orderTypeRadios = document.querySelectorAll("input[name='orderType']");
const tableSection = document.getElementById("tableSection");
const tokenSection = document.getElementById("tokenSection");
const tableNumber = document.getElementById("tableNumber");
const tokenNumber = document.getElementById("tokenNumber");

// ------------------------------
// Order Type Toggle
// ------------------------------

orderTypeRadios.forEach(radio => {

    radio.addEventListener("change", () => {

        if (radio.value === "Dine In" && radio.checked) {

            tableSection.style.display = "block";
            tokenSection.style.display = "none";

        }

        if (radio.value === "Take Away" && radio.checked) {

            tableSection.style.display = "none";
            tokenSection.style.display = "block";

            tokenNumber.textContent =
                "#" + Math.floor(Math.random() * 900 + 100);

        }

    });

});

// ------------------------------
// Add Menu Item
// ------------------------------

menuButtons.forEach(button => {

    button.addEventListener("click", () => {

        const name = button.dataset.name;
        const price = Number(button.dataset.price);

        const existing = cart.find(item => item.name === name);

        if (existing) {

            existing.quantity++;

        } else {

            cart.push({
                name,
                price,
                quantity: 1
            });

        }

        updateCart();

    });

});

// ------------------------------
// Update Cart
// ------------------------------

function updateCart() {

    cartItems.innerHTML = "";

    if (cart.length === 0) {

        cartItems.innerHTML = "<p>No items added yet.</p>";

        subtotal.textContent = "₹0.00";
        gst.textContent = "₹0.00";
        grandTotal.textContent = "₹0.00";

        return;

    }

    let sub = 0;

    cart.forEach(item => {

        sub += item.price * item.quantity;

        cartItems.innerHTML += `

        <div class="cart-item">

            <div>

                <strong>${item.name}</strong><br>

                ₹${item.price}

            </div>

            <div>

                <button onclick="decreaseQuantity('${item.name}')">−</button>

                <span>${item.quantity}</span>

                <button onclick="increaseQuantity('${item.name}')">+</button>

                <button onclick="removeItem('${item.name}')">🗑</button>

            </div>

        </div>

        `;

    });

    const gstAmount = sub * 0.05;
    const total = sub + gstAmount;

    subtotal.textContent = "₹" + sub.toFixed(2);
    gst.textContent = "₹" + gstAmount.toFixed(2);
    grandTotal.textContent = "₹" + total.toFixed(2);

}

// ------------------------------
// Increase Quantity
// ------------------------------

function increaseQuantity(name) {

    const item = cart.find(i => i.name === name);

    if (item) {

        item.quantity++;

        updateCart();

    }

}

// ------------------------------
// Decrease Quantity
// ------------------------------

function decreaseQuantity(name) {

    const item = cart.find(i => i.name === name);

    if (!item) return;

    item.quantity--;

    if (item.quantity <= 0) {

        removeItem(name);

    } else {

        updateCart();

    }

}

// ------------------------------
// Remove Item
// ------------------------------

function removeItem(name) {

    cart = cart.filter(item => item.name !== name);

    updateCart();

}

// ------------------------------
// Clear Order
// ------------------------------

clearOrderBtn.addEventListener("click", () => {

    if (cart.length === 0) return;

    if (confirm("Clear current order?")) {

        cart = [];

        updateCart();

    }

});

// ------------------------------
// Place Order
// ------------------------------

placeOrderBtn.addEventListener("click", async () => {

    if (cart.length === 0) {

        alert("Please add items first.");
        return;

    }

    const orderType =
        document.querySelector("input[name='orderType']:checked").value;

    // Calculate totals
    let sub = 0;

    cart.forEach(item => {

        sub += item.price * item.quantity;

    });

    const gstAmount = sub * 0.05;
    const total = sub + gstAmount;

    const orderData = {

        order_type: orderType,

        table_number:
            orderType === "Dine In"
                ? tableNumber.value
                : null,

        token_number:
            orderType === "Take Away"
                ? parseInt(tokenNumber.textContent.replace("#", ""))
                : null,

        subtotal: sub,

        gst: gstAmount,

        grand_total: total,

        items: cart

    };

    try {

        const response = await fetch("/api/orders", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(orderData)

        });

        const result = await response.json();

        if (!response.ok) {

            throw new Error(result.message);

        }

        alert("Order placed successfully!");

        cart = [];

        updateCart();

    }

    catch (error) {

        alert(error.message);

    }

});