function loadConfigs() {
    fetch('/api/configs', {
        method: 'GET'
    }).then(res => res.json()).then(data => {
        window.appConfigs = data;
        console.log(document.getElementsByClassName('ser-fee-rate'));
        document.addEventListener('DOMContentLoaded', () => {
            let el = document.getElementsByClassName('ser-fee-rate')[0];
            if (el) {
                el.innerText = (parseFloat(window.appConfigs['SERVICE_FEE']['value']) * 100) + '%';
            }
        });
        orderStats['service_fee_rate'] = window.appConfigs['SERVICE_FEE']['value']
    })
}

loadConfigs()

function toggleAddItemToCart(data, max_of_items = window.appConfigs['MAX_NUM_OF_ORDERS_ITEMS']['value']) {
    let incBtn = document.getElementsByClassName("inc-item")
    if (data.total_quantity >= parseInt(max_of_items)) {
        for (let btn of incBtn)
            btn.classList.add("disabled")
    } else {
        for (let btn of incBtn)
            btn.classList.remove("disabled")
    }
}

function updateCartCounter(data) {
    let counters = document.getElementsByClassName("cart-counter")
    for (let element of counters)
        element.innerText = data.total_quantity;
}

function updateCartInfo(data) {
    let subs = document.getElementsByClassName("cart-sub")
    for (let element of subs) {
        element.innerText = data.subtotal.toLocaleString('en-US') + ' VNĐ'
    }

    let ser_fee = document.getElementsByClassName("cart-ser-fee")
    for (let element of ser_fee) {
        element.innerText = data.service_fee.toLocaleString('en-US') + ' VNĐ'
    }

    let totals = document.getElementsByClassName("cart-total")
    for (let element of totals) {
        element.innerText = data.total_price.toLocaleString('en-US') + ' VNĐ'
    }

    updateCartCounter(data)
}

function updateOrderStats(price = 0.0, change = 0) {
    orderStats['total_quantity'] += change
    orderStats['subtotal'] += price * change

    orderStats['service_fee'] = orderStats['service_fee_rate'] * orderStats['subtotal']
    orderStats['total_price'] = orderStats['subtotal'] + orderStats['service_fee']
}

function myCustomAlert(message) {
    let alert = document.getElementById('custom-alert')
    alert.classList.remove('d-none')
    let alert_body = document.getElementById('alert-body')
    alert_body.innerText = message
}

function addToCart(id, name, image, price) {
    fetch('/api/carts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "id": id,
            "name": name,
            "image": image,
            "price": price
        })
    }).then(res => res.json()).then(data => {
        if (data.message) {
            myCustomAlert(data.message)
        } else {
            updateCartCounter(data)
        }
    })
}

function updateCart(id, change) {
    let qtyElement = document.getElementById(`qty-${id}`)
    let qty = parseInt(qtyElement.innerText)
    let newQty = qty + change

    fetch(`/api/carts/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "quantity": newQty,
        })
    }).then(res => res.json()).then(data => {
        qtyElement.innerText = newQty;

        if (parseInt(qtyElement.innerText) <= 1) {
            document.getElementById(`reduce-qty-${id}`).classList.add("disabled")
        } else {
            document.getElementById(`reduce-qty-${id}`).classList.remove("disabled")
        }

        let price = document.getElementById(`prod-${id}-price`).innerText
        document.getElementById(`price-${id}`).innerText = (parseFloat(newQty) * parseFloat(price) * 1000)
            .toLocaleString('en-US') + ' VNĐ'

        toggleAddItemToCart(data = data)
        updateCartInfo(data)
    })
}


function deleteCart(id) {
    const modalElement = document.getElementById(`removeItem-${id}`);

    // Lấy instance (đối tượng điều khiển) của Modal từ Bootstrap
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide();
    }
    fetch(`/api/carts/${id}`, {
        method: 'DELETE',
    }).then(res => res.json()).then(data => {
        if (data.flag) {
            location.reload()
        }

        document.getElementById(`prod-${id}`).remove()

        toggleAddItemToCart(data = data)
        updateCartInfo(data)
    })
}

function addNote(id, obj) {
    let note = obj.value
    fetch(`/api/carts/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'note': note,
        })
    }).then(res => res.json()).then(data => {})
}

function filterProductByCategory(id, obj) {
    let p = document.getElementsByClassName('product-item')
    console.log(p)
    for (let element of p) {
        element.classList.remove('d-none')
        if (element.dataset.cateId != id) {
            element.classList.add("d-none")
        }
    }
    let cates = document.getElementsByClassName('btn-filter')
    for (let element of cates) {
        element.classList.remove('active')
    }
    obj.classList.add("active")
}

function getAllProducts(obj) {
    let p = document.getElementsByClassName('product-item')
    for (let element of p) {
        element.classList.remove('d-none')
    }
    let cates = document.getElementsByClassName('btn-filter')
    for (let element of cates) {
        element.classList.remove('active')
    }
    obj.classList.add("active")
}

function filterProductByKeyword(obj) {
    let p = document.getElementsByClassName('product-item')
    for (let element of p) {
        let name = element.dataset.name.toLowerCase()
        if (name.includes(obj.value.toLowerCase().trim())) {
            element.classList.remove('d-none')
        } else {
            element.classList.add('d-none')
        }
    }
}

let orderStats = {
    "total_quantity": 0,
    "subtotal": 0,
    "service_fee_rate": 0,
    "service_fee": 0,
    "total_price": 0,
}

let orders = {}

function addToOrder(id, name, price) {
    if (orderStats['total_quantity'] >= window.appConfigs['MAX_NUM_OF_ORDERS_ITEMS']['value']) {
        myCustomAlert(`Không thể thêm sản phẩm! Không được vượt quá ` +
            `${window.appConfigs['MAX_NUM_OF_ORDERS_ITEMS']['value']} sản phẩm trên 1 hoá đơn.`)
        toggleAddItemToCart(orderStats)
        return
    }

    if (id in orders) {
        orders[id]['quantity'] += 1
    } else {
        orders[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }
    }

    updateOrderStats(price, 1)
    updateCartInfo(orderStats)
    renderOrders()
}

function renderOrders() {
    let tbody = document.getElementById("bill-body");

    console.log(orderStats.total_quantity)

    if (orderStats.total_quantity > 0) {
        document.getElementById("empty-cart-msg").classList.add("d-none")
    } else {
        document.getElementById("empty-cart-msg").classList.remove("d-none")
    }

    tbody.innerHTML = ''

    for (let id in orders) {
        let item = orders[id];
        let lineTotal = item.price * item.quantity;

        let row = `
            <tr>
                <td class="text-start">
                    <div class="fw-semibold">${item.name}</div>
                </td>
                <td class="text-center">
                    ${item.price.toLocaleString('en-US')} VNĐ
                </td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm">
                        <button id="reduce-qty-${id}"
                                class="btn btn-outline-primary"
                                onclick="changeQty(${id}, -1)">−</button>

                        <span class="px-2 border d-inline-flex align-items-center">
                            ${item.quantity}
                        </span>

                        <button class="btn btn-outline-primary inc-item"
                                onclick="changeQty(${id}, 1)">+</button>
                    </div>
                </td>
                <td class="text-end pe-3 fw-semibold">
                    ${lineTotal.toLocaleString('en-US')} VNĐ
                </td>
            </tr>
        `
        tbody.innerHTML += row
    }
}

function changeQty(id, change) {
    if (!(id in orders)) {
        return;
    }

    orders[id].quantity += change;

    if (orders[id].quantity <= 0) {
        if (confirm("Bạn có chắc muốn xoá sản phẩm này không?") == true) {
            updateOrderStats(orders[id].price, -1);
            delete orders[id];
            renderOrders()
        } else {
            return;
        }
    } else {
        updateOrderStats(orders[id].price, change);
    }

    toggleAddItemToCart(orderStats)
    updateCartInfo(orderStats)
    renderOrders();
}

function clearOrder() {
    if (orderStats.total_quantity <= 0) {
        myCustomAlert('Giỏ hàng trống!')
        return
    }
    if (confirm("Bạn có muốn huỷ hoá đơn không? Huỷ hoá đơn sẽ quay lại giao diện tạo hoá đơn khác.") == true) {
        location.reload()
    }
}

function order() {
    fetch("/api/order", {
        method: 'POST'
    }).then(res => res.json()).then(data => {
        MyCustomAlert(data.message)
        location.reload()
    })
}