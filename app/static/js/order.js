let configs = {}

async function loadConfigs() {
    const res = await fetch('/api/configs')
    configs = await res.json()
}

function getConfig(key) {
    return configs[key] ? Number(configs[key].value) : 0
}

window.addEventListener('DOMContentLoaded', async () => {
    await loadConfigs()
})


function myCustomAlert(message, confirm = false) {
    return new Promise(resolve => {
        const box = document.getElementById('custom-alert')
        const body = document.getElementById('alert-body')
        const ok = document.getElementById('my-confirm')
        const closeBtns = document.getElementsByClassName('btn-close')

        body.innerText = message
        box.classList.remove('d-none')

        ok.classList.toggle('d-none', !confirm)

        ok.onclick = () => {
            box.classList.add('d-none')
            resolve(true)
        }

        for (let b of closeBtns) {
            b.onclick = () => {
                box.classList.add('d-none')
                resolve(false)
            }
        }
    })
}

function formatCurrency(v) {
    return v.toLocaleString('en-US') + ' VNĐ'
}


function toggleAddItemToCart(data, max_of_items = getConfig('MAX_NUM_OF_ORDERS_ITEMS')) {
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
    document.querySelectorAll('.cart-counter')
        .forEach(el => el.innerText = data.total_quantity)
}

function updateCartInfo(data) {
    document.querySelectorAll('.cart-sub')
        .forEach(el => el.innerText = formatCurrency(data.subtotal))
    document.querySelectorAll('.cart-ser-fee')
        .forEach(el => el.innerText = formatCurrency(data.service_fee))
    document.querySelectorAll('.cart-total')
        .forEach(el => el.innerText = formatCurrency(data.total_price))
    updateCartCounter(data)
}

function addToCart(id, name, image, price) {
    fetch('/api/carts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id, name, image, price})
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) myCustomAlert(data.message)
        else updateCartCounter(data)
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

        toggleAddItemToCart(data)
        updateCartInfo(data)
    })
}

function deleteCart(id) {
    fetch(`/api/carts/${id}`, {
        method: 'DELETE',
    }).then(res => res.json()).then(data => {
        location.reload()
        document.getElementById(`prod-${id}`).remove()

        toggleAddItemToCart(data)
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

async function customerOrder() {
    if (!(await myCustomAlert("Xác nhận đặt hàng?", true))) return

    fetch('/api/order', {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            myCustomAlert(data.message)
            setTimeout(() => location.reload(), 1000)
        })
}
