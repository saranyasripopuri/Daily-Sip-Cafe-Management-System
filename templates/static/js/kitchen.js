// ==========================================
// KITCHEN DISPLAY SYSTEM
// ==========================================


const kitchenOrdersContainer =
    document.getElementById("kitchenOrders");


// Only run kitchen code when kitchen page exists

if (kitchenOrdersContainer) {

    loadKitchenOrders();

}


// ==========================================
// LOAD ORDERS FROM DATABASE
// ==========================================

async function loadKitchenOrders() {

    if (!kitchenOrdersContainer) {

        return;

    }


    kitchenOrdersContainer.innerHTML =

        "<p>Loading orders...</p>";


    try {


        const response = await fetch(

            "/api/kitchen/orders"

        );


        if (!response.ok) {

            throw new Error(

                "Could not load kitchen orders."

            );

        }


        const orders = await response.json();


        displayKitchenOrders(orders);


    }

    catch (error) {


        console.error(error);


        kitchenOrdersContainer.innerHTML = `

            <p>

                Error loading orders.

            </p>

        `;

    }

}


// ==========================================
// DISPLAY KITCHEN ORDERS
// ==========================================

function displayKitchenOrders(orders) {


    kitchenOrdersContainer.innerHTML = "";


    if (orders.length === 0) {


        kitchenOrdersContainer.innerHTML = `

            <div class="no-orders">

                <h2>☕ No Active Orders</h2>

                <p>

                    New orders will appear here.

                </p>

            </div>

        `;


        return;

    }


    orders.forEach(order => {


        let locationText;


        if (order.order_type === "Dine In") {

            locationText =
                order.table_number;

        }

        else {

            locationText =

                "Take Away - Token #" +

                order.token_number;

        }


        let itemsHTML = "";


        order.items.forEach(item => {


            itemsHTML += `

                <div class="kitchen-item">

                    <span>

                        ${item.name}

                    </span>


                    <strong>

                        × ${item.quantity}

                    </strong>

                </div>

            `;


        });


        let actionButton = "";


        if (order.status === "Pending") {


            actionButton = `

                <button

                    class="start-preparing-btn"

                    onclick="changeOrderStatus(

                        ${order.id},

                        'Preparing'

                    )"

                >

                    👨‍🍳 Start Preparing

                </button>

            `;


        }


        if (order.status === "Preparing") {


            actionButton = `

                <button

                    class="mark-ready-btn"

                    onclick="changeOrderStatus(

                        ${order.id},

                        'Ready'

                    )"

                >

                    ✅ Mark Ready

                </button>

            `;


        }


        kitchenOrdersContainer.innerHTML += `


            <div class="kitchen-order-card">


                <div class="kitchen-order-top">


                    <h2>

                        Order #${order.id}

                    </h2>


                    <span

                        class="status-badge

                        ${order.status.toLowerCase()}"

                    >

                        ${order.status}

                    </span>


                </div>


                <p class="order-location">

                    ${locationText}

                </p>


                <div class="kitchen-items">

                    ${itemsHTML}

                </div>


                <div class="kitchen-order-footer">


                    <strong>

                        Total ₹${

                            Number(

                                order.grand_total

                            ).toFixed(2)

                        }

                    </strong>


                </div>


                ${actionButton}


            </div>


        `;


    });


}


// ==========================================
// CHANGE ORDER STATUS
// ==========================================

async function changeOrderStatus(

    orderId,

    newStatus

) {


    try {


        const response = await fetch(

            `/api/orders/${orderId}/status`,

            {

                method: "PUT",

                headers: {

                    "Content-Type":

                        "application/json"

                },

                body: JSON.stringify({

                    status: newStatus

                })

            }

        );


        const result =

            await response.json();


        if (!response.ok) {


            throw new Error(

                result.message ||

                "Could not update order."

            );


        }


        // Reload kitchen orders

        loadKitchenOrders();


    }

    catch (error) {


        console.error(error);


        alert(

            "Error: " +

            error.message

        );


    }

}