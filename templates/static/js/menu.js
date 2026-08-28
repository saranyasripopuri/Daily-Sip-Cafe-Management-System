// ==========================================
// DAILY SIP - MENU MANAGEMENT
// ==========================================

const menuList = document.getElementById("menuList");
const menuName = document.getElementById("menuName");
const menuPrice = document.getElementById("menuPrice");
const addMenuItemBtn = document.getElementById("addMenuItemBtn");


// ==========================================
// LOAD MENU ITEMS
// ==========================================

async function loadMenu() {

    try {

        const response = await fetch("/api/menu");

        const items = await response.json();

        menuList.innerHTML = "";


        if (items.length === 0) {

            menuList.innerHTML =
                "<p>No menu items added yet.</p>";

            return;

        }


        items.forEach(item => {

            menuList.innerHTML += `

                <div class="menu-item">

                    <span>
                        ${item.name}
                    </span>

                    <strong>
                        ₹${Number(item.price).toFixed(2)}
                    </strong>

                    <button
                        class="delete-menu-btn"
                        onclick="deleteMenuItem(${item.id})"
                    >
                        🗑 Delete
                    </button>

                </div>

            `;

        });

    }

    catch (error) {

        console.error(error);

        menuList.innerHTML =
            "<p>Error loading menu.</p>";

    }

}


// ==========================================
// DELETE MENU ITEM
// ==========================================

async function deleteMenuItem(itemId) {

    const confirmDelete = confirm(
        "Are you sure you want to delete this item?"
    );

    if (!confirmDelete) {

        return;

    }

    try {

        const response = await fetch(
            `/api/menu/${itemId}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(
                "Could not delete menu item. " + errorText
            );

        }

        alert("Menu item deleted successfully!");

        loadMenu();

    }

    catch (error) {

        console.error(error);

        alert(error.message);

    }

}

// ==========================================
// ADD MENU ITEM
// ==========================================

addMenuItemBtn.addEventListener("click", async () => {

    const name = menuName.value.trim();

    const price = menuPrice.value;


    if (!name || !price) {

        alert("Please enter item name and price.");

        return;

    }


    try {

        const response = await fetch("/api/menu", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                name: name,

                price: Number(price)

            })

        });


        const result = await response.json();


        if (!response.ok) {

            throw new Error(

                result.message ||
                "Could not add menu item."

            );

        }


        alert("Menu item added successfully!");


        menuName.value = "";

        menuPrice.value = "";


        loadMenu();

    }

    catch (error) {

        console.error(error);

        alert(error.message);

    }

});


// ==========================================
// INITIAL LOAD
// ==========================================

loadMenu();