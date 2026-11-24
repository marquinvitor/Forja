const val INVALID_QUANTITY_MSG: String = "fail: invalid quantity"
const val ITEM_ALREADY_EXISTS_MSG: String = "fail: item already exists"
const val ITEM_NOT_FOUND_MSG: String = "fail: item not found"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Item(
    private val name: String = "",
    private val price: Double = 0.0,
    private var quantity: Int = 0
) {
    companion object {
        const val MIN_QUANTITY: Int = 1
        const val MAX_QUANTITY: Int = 10
    }

    fun getName(): String {
        return this.name
    }

    fun getPrice(): Double {
        return this.price
    }

    fun getQuantity(): Int {
        return this.quantity
    }

    fun setQuantity(quantity: Int): Boolean {
        if (quantity < MIN_QUANTITY || quantity > MAX_QUANTITY) {
            return false
        }
        this.quantity = quantity
        return true
    }

    fun getTotal(): Double {
        return this.price * this.quantity
    }

    override fun toString(): String {
        return "${this.name}: ${this.quantity}: ${this.price}"
    }
}

class Cart {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        val existingItem: Item? = this.getItem(item.getName())
        if (existingItem != null) {
            return false
        }
        this.items.add(item)
        return true
    }

    fun getItem(name: String): Item? {
        for (item: Item in this.items) {
            if (item.getName().equals(name, ignoreCase = true)) {
                return item
            }
        }
        return null
    }

    fun removeItem(name: String): Boolean {
        val item: Item? = this.getItem(name)
        if (item != null) {
            return this.items.remove(item)
        }
        return false
    }

    fun getItems(): List<Item> {
        return this.items
    }

    fun getTotal(): Double {
        var total: Double = 0.0
        for (item: Item in this.items) {
            total += item.getTotal()
        }
        return total
    }

    override fun toString(): String {
        val sb: StringBuilder = StringBuilder()
        for (item: Item in this.items) {
            sb.append(item.toString()).append("\n")
        }
        sb.append("total: ").append(this.getTotal())
        return sb.toString()
    }
}

fun main(): Unit {
    val cart: Cart = Cart()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "add" -> {
                val item: Item = Item(parts[1], parts[2].toDouble())
                if (!item.setQuantity(parts[3].toInt())) {
                    println(INVALID_QUANTITY_MSG)
                } else if (!cart.addItem(item)) {
                    println(ITEM_ALREADY_EXISTS_MSG)
                }
            }
            "qty" -> {
                val item: Item? = cart.getItem(parts[1])
                if (item == null) {
                    println(ITEM_NOT_FOUND_MSG)
                } else if (!item.setQuantity(parts[2].toInt())) {
                    println(INVALID_QUANTITY_MSG)
                }
            }
            "remove" -> if (!cart.removeItem(parts[1])) {
                println(ITEM_NOT_FOUND_MSG)
            }
            "show" -> println(cart)
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}