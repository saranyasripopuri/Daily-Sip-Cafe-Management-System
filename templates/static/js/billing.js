// =====================================
// DAILY SIP - BILLING MODULE
// =====================================

const billingContainer =
    document.getElementById("billingOrders");

// -----------------------------
// Load Ready Orders
// -----------------------------

async function loadBillingOrders() {

    try {

        const response =
            await fetch("/api/billing/orders");

        const orders =
            await response.json();

        displayBillingOrders(orders);

    }

    catch (error) {

        billingContainer.innerHTML =
            "<h3>Error loading billing orders.</h3>";

    }

}

// -----------------------------
// Display Orders
// -----------------------------

function displayBillingOrders(orders) {

    if (orders.length === 0) {

        billingContainer.innerHTML =
            "<h2>No Ready Orders</h2>";

        return;

    }

    billingContainer.innerHTML = "";

    orders.forEach(order => {

        let itemsHTML = "";

        order.items.forEach(item => {

            itemsHTML += `
                <li>
                    ${item.name}
                    (${item.quantity})
                    - ₹${item.subtotal}
                </li>
            `;

        });

        billingContainer.innerHTML += `

        <div class="billing-card">

            <h2>Order #${order.id}</h2>

            <p>
                <strong>Order Type:</strong>
                ${order.order_type}
            </p>

            <p>
                <strong>Table:</strong>
                ${order.table_number || "-"}
            </p>

            <p>
                <strong>Token:</strong>
                ${order.token_number || "-"}
            </p>

            <ul>

                ${itemsHTML}

            </ul>

            <hr>

            <p>
                <strong>Subtotal:</strong>
                ₹${order.subtotal}
            </p>

            <p>
                <strong>GST:</strong>
                ₹${order.gst}
            </p>

            <p>
                <strong>Grand Total:</strong>
                ₹${order.grand_total}
            </p>

            <br>

            <select id="payment${order.id}">

                <option value="Cash">
                    Cash
                </option>

                <option value="UPI">
                    UPI
                </option>

                <option value="Card">
                    Card
                </option>

            </select>

            <button
                onclick="completePayment(${order.id})">

                Complete Payment

            </button>

        </div>

        <br>

        `;

    });

}

// -----------------------------
// Complete Payment
// -----------------------------

async function completePayment(orderId) {

    const paymentMethod =
        document.getElementById(
            `payment${orderId}`
        ).value;

    try {

        const response =
            await fetch(
                `/api/orders/${orderId}/payment`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        payment_method:
                            paymentMethod

                    })

                }
            );

        const result =
            await response.json();

        alert(result.message);

        loadBillingOrders();

    }

    catch (error) {

        alert(error);

    }

}

// -----------------------------
// Initial Load
// -----------------------------

loadBillingOrders();