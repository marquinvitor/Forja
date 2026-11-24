const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Book(private val id: String, private val title: String) {
    private var isAvailable: Boolean = true

    fun getId(): String {
        return this.id
    }

    fun getTitle(): String {
        return this.title
    }

    fun isAvailable(): Boolean {
        return this.isAvailable
    }

    fun setAvailable(status: Boolean): Unit {
        this.isAvailable = status
    }

    override fun toString(): String {
        val statusStr: String = if (this.isAvailable) "available" else "unavailable"
        return "book: ${this.id} : ${this.title} : $statusStr"
    }
}

class Member(private val id: String, private val maxLoans: Int) {
    private val borrowedBooks: MutableMap<String, Book> = mutableMapOf()

    fun getId(): String {
        return this.id
    }

    fun getMaxLoans(): Int {
        return this.maxLoans
    }

    fun getBorrowedCount(): Int {
        return this.borrowedBooks.size
    }

    fun borrowBook(book: Book): Unit {
        if (this.borrowedBooks.size >= this.maxLoans) {
            throw IllegalArgumentException("fail: member reached loan limit")
        }
        this.borrowedBooks[book.getId()] = book
    }

    fun returnBook(book: Book): Unit {
        if (!this.borrowedBooks.containsKey(book.getId())) {
            throw IllegalArgumentException("fail: member does not have this book")
        }
        this.borrowedBooks.remove(book.getId())
    }

    override fun toString(): String {
        return "member: ${this.id} : loans: ${this.borrowedBooks.size} / max: ${this.maxLoans}"
    }
}

class Library {
    private val books: MutableMap<String, Book> = mutableMapOf()
    private val members: MutableMap<String, Member> = mutableMapOf()

    fun addBook(book: Book): Unit {
        if (this.books.containsKey(book.getId())) {
            throw IllegalArgumentException("fail: book already exists")
        }
        this.books[book.getId()] = book
    }

    fun addMember(member: Member): Unit {
        if (this.members.containsKey(member.getId())) {
            throw IllegalArgumentException("fail: member already exists")
        }
        this.members[member.getId()] = member
    }

    fun borrowBook(memberId: String, bookId: String): Unit {
        val member: Member = this.members[memberId] ?: throw IllegalArgumentException("fail: member not found")
        val book: Book = this.books[bookId] ?: throw IllegalArgumentException("fail: book not found")

        if (!book.isAvailable()) {
            throw IllegalArgumentException("fail: book is not available")
        }

        member.borrowBook(book)
        book.setAvailable(false)
    }

    fun returnBook(memberId: String, bookId: String): Unit {
        val member: Member = this.members[memberId] ?: throw IllegalArgumentException("fail: member not found")
        val book: Book = this.books[bookId] ?: throw IllegalArgumentException("fail: book not found")

        member.returnBook(book)
        book.setAvailable(true)
    }

    fun show(): String {
        val sb: StringBuilder = StringBuilder()
        for (book: Book in this.books.values.sortedBy { it.getId() }) {
            sb.append(book.toString()).append("\n")
        }
        for (member: Member in this.members.values.sortedBy { it.getId() }) {
            sb.append(member.toString()).append("\n")
        }
        return sb.toString()
    }
}

fun main(): Unit {
    var library: Library = Library()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        if (parts.isEmpty() || parts[0].isEmpty()) continue

        try {
            when (parts[0]) {
                "end" -> break
                "init" -> library = Library()
                "addBook" -> library.addBook(Book(parts[1], parts[2]))
                "addMember" -> library.addMember(Member(parts[1], parts[2].toInt()))
                "show" -> print(library.show())
                "borrow" -> library.borrowBook(parts[1], parts[2])
                "return" -> library.returnBook(parts[1], parts[2])
                else -> println(INVALID_COMMAND_MSG)
            }
        } catch (e: Exception) {
            println(e.message)
        }
    }
}