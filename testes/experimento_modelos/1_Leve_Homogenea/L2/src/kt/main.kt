const val EXISTING_ITEM_MSG: String = "fail: existing item"
const val INVALID_QUANTITY_MSG: String = "fail: invalid quantity"
const val ITEM_NOT_FOUND_MSG: String = "fail: item not found"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Item(private val name: String, private val price: Double, private var quantity: Int) {
    companion object {
        const val MIN_QUANTITY: Int = 1
        const val MAX_QUANTITY: Int = 10
    }

    init {
        if (quantity < MIN_QUANTITY || quantity > MAX_QUANTITY) {
            // Caso seja instanciado com valor inválido diretamente, garantimos a restrição
            // Mas a validação de criação é tratada no fluxo principal ou construtor.
        }
    }

    fun getName(): String {
        return name
    }

    fun getPrice(): Double {
        return price
    }

    fun getQuantity(): Int {
        return quantity
    }

    fun setQuantity(qty: Int): Boolean {
        if (qty < MIN_QUANTITY || qty > MAX_QUANTITY) {
            return false
        }
        quantity = qty
        return true
    }

    override fun toString(): String {
        return "$name: $quantity x ${"%.2f".format(price)}"
    }
}

class Cart {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        for (existing: Item in items) {
            if (existing.getName() == item.getName()) {
                return false
            }
        }
        items.add(item)
        return true
    }

    fun removeItem(name: String): Boolean {
        var found: Item? = null
        for (item: Item in items) {
            if (item.getName() == name) {
                found = item
                break
            }
        }
        if (found != null) {
            items.remove(found)
            return true
        }
        return false
    }

    fun getItems(): List<Item> {
        return items
    }

    fun getTotal(): Double {
        var total: Double = 0.0
        for (item: Item in items) {
            total += item.getPrice() * item.getQuantity()
        }
        return total
    }
}

fun main(): Unit {
    var currentCart: Cart = Cart()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        if (parts.isEmpty() || parts[0].isEmpty()) {
            continue
        }

        when (parts[0]) {
            "end" -> break
            "init" -> currentCart = Cart()
            "add" -> {
                val name: String = parts[1]
                val price: Double = parts[2].toDouble()
                val quantity: Int = parts[3].toInt()
                
                if (quantity < Item.MIN_QUANTITY || quantity > Item.MAX_QUANTITY) {
                    println(INVALID_QUANTITY_MSG)
                } else {
                    val newItem: Item = Item(name, price, quantity)
                    if (!currentCart.addItem(newItem)) {
                        println(EXISTING_ITEM_MSG)
                    }
                }
            }
            "remove" -> {
                val name: String = parts[1]
                if (!currentCart.removeItem(name)) {
                    println(ITEM_NOT_FOUND_MSG)
                }
            }
            "show" -> {
                for (item: Item in currentCart.getItems()) {
                    println(item)
                }
                println("total: " + "%.2f".format(currentCart.getTotal()))
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}