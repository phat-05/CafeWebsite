let orders = {}

let orderStats = {
    total_quantity: 0,
    subtotal: 0,
    service_fee_rate: 0,
    service_fee: 0,
    total_price: 0,
}

window.addEventListener('DOMContentLoaded', async () => {
    await loadConfigs()
    orderStats.service_fee_rate = getConfig('SERVICE_FEE')

    document.querySelectorAll('.ser-fee-rate')
        .forEach(el => el.innerText = orderStats.service_fee_rate * 100 + '%')
})

function recalcOrderStats() {
    let qty = 0
    let sub = 0

    for (let id in orders) {
        qty += orders[id].quantity
        sub += orders[id].price * orders[id].quantity
    }

    orderStats.total_quantity = qty
    orderStats.subtotal = sub
    orderStats.service_fee = sub * orderStats.service_fee_rate
    orderStats.total_price = sub + orderStats.service_fee

    updateCartInfo(orderStats)
    toggleAddItemToCart(orderStats)
}

function filterProductByCategory(id, obj) {
    document.querySelectorAll('.product-item').forEach(el => {
        el.classList.toggle('d-none', el.dataset.cateId != id)
    })

    document.querySelectorAll('.btn-filter')
        .forEach(b => b.classList.remove('active'))
    obj.classList.add('active')
}

function getAllProducts(obj) {
    document.querySelectorAll('.product-item')
        .forEach(el => el.classList.remove('d-none'))

    document.querySelectorAll('.btn-filter')
        .forEach(b => b.classList.remove('active'))
    obj.classList.add('active')
}

function filterProductByKeyword(obj) {
    let key = obj.value.toLowerCase().trim()
    document.querySelectorAll('.product-item').forEach(el => {
        el.classList.toggle(
            'd-none',
            !el.dataset.name.toLowerCase().includes(key)
        )
    })
}

function addToOrder(id, name, price, unit) {
    let max = getConfig('MAX_NUM_OF_ORDERS_ITEMS')
    if (orderStats.total_quantity >= max) {
        myCustomAlert(`Không vượt quá ${max} sản phẩm`)
        return
    }

    if (!orders[id]) {
        orders[id] = {id, name, price, unit, quantity: 1}
    } else {
        orders[id].quantity++
    }

    recalcOrderStats()
    renderOrders()
}

async function changeQty(id, delta) {
    if (!orders[id]) return

    let max = getConfig('MAX_NUM_OF_ORDERS_ITEMS')
    if (delta > 0 && orderStats.total_quantity >= max) {
        myCustomAlert(`Không vượt quá ${max} sản phẩm`)
        return
    }

    let next = orders[id].quantity + delta
    if (next <= 0) {
        if (!(await myCustomAlert("Xoá sản phẩm?", true))) return
        delete orders[id]
    } else {
        orders[id].quantity = next
    }

    recalcOrderStats()
    renderOrders()
}

function renderOrders() {
    let tbody = document.getElementById('bill-body')
    let empty = document.getElementById('empty-cart-msg')

    tbody.innerHTML = ''
    empty.classList.toggle('d-none', orderStats.total_quantity > 0)

    for (let id in orders) {
        let i = orders[id]
        tbody.innerHTML += `
        <tr>
            <td>${i.name}</td>
            <td class="text-center">${formatCurrency(i.price)}</td>
            <td class="text-center">
                <button onclick="changeQty(${id},-1)">−</button>
                ${i.quantity}
                <button class="inc-item" onclick="changeQty(${id},1)">+</button>
            </td>
            <td class="text-center">${i.unit}</td>
            <td class="text-end">${formatCurrency(i.price * i.quantity)}</td>
        </tr>`
    }
}

async function clearOrder() {
    if (!orderStats.total_quantity) {
        myCustomAlert("Hoá đơn trống!")
        return
    }

    if (!(await myCustomAlert("Huỷ hoá đơn?", true))) return
    orders = {}
    recalcOrderStats()
    renderOrders()
}

async function order() {
    if (!orderStats.total_quantity) {
        myCustomAlert("Chưa có sản phẩm!")
        return
    }

    if (!(await myCustomAlert("Xác nhận đặt hàng?", true))) return

    fetch('/api/staff/order', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(orders)
    })
        .then(res => res.json())
        .then(data => {
            myCustomAlert(data.message || "Thành công")
            setTimeout(() => location.reload(), 1000)
        })
}

function getUncompOrderById(obj) {
    let id = obj.value.trim()

    document.querySelectorAll('.uncomp-order').forEach(el => {
        el.classList.toggle(
            'd-none',
            !el.dataset.id.includes(id)
        )
    })
}


async function payConfirm(id) {
    if (!(await myCustomAlert("Bạn có chắc muốn thanh toán đơn này?", true))) return

    fetch(`/api/staff/pay/${id}`, {
        method: 'POST'
    }).then(res => res.json()).then(data => {

        myCustomAlert(data.message);

        if (data.code === 200) {
            console.log(id)
            document.getElementById(`uncomp-${id}`).remove()
        }
    })
}