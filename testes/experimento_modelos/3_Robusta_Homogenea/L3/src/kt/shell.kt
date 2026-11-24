const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Book(id: String, title: String) {
    private var id: String = ""
    private var title: String = ""
    private var available: Boolean = true

    init {
        // TODO: inicialize os atributos
    }

    fun getId(): String {
        TODO("retorne o id do livro")
    }

    fun getTitle(): String {
        TODO("retorne o titulo do livro")
    }

    fun isAvailable(): Boolean {
        TODO("retorne se o livro esta disponivel")
    }

    fun borrow(): Unit {
        TODO("valide a disponibilidade e marque o livro como emprestado")
    }

    fun returnBook(): Unit {
        TODO("valide se o livro esta emprestado e marque como disponivel")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do livro")
    }
}

class Member(id: String, name: String, limit: Int) {
    private var id: String = ""
    private var name: String = ""
    private var limit: Int = 0
    private val borrowedBooks: MutableMap<String, Book> = mutableMapOf()

    init {
        // TODO: inicialize os atributos
    }

    fun getId(): String {
        TODO("retorne o id do socio")
    }

    fun getName(): String {
        TODO("retorne o nome do socio")
    }

    fun getLimit(): Int {
        TODO("retorne o limite maximo de emprestimos do socio")
    }

    fun getBorrowedBooks(): List<Book> {
        TODO("retorne a lista de livros emprestados")
    }

    fun canBorrow(): Boolean {
        TODO("verifique se o socio ainda pode pegar livros emprestados")
    }

    fun hasBook(bookId: String): Boolean {
        TODO("verifique se o socio possui o livro indicado pelo id")
    }

    fun addBook(book: Book): Unit {
        TODO("valide o limite e adicione o livro aos emprestimos do socio")
    }

    fun removeBook(bookId: String): Book {
        TODO("valide a posse do livro, remova dos emprestimos e o retorne")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do socio")
    }
}

class Library {
    private val books: MutableMap<String, Book> = mutableMapOf()
    private val members: MutableMap<String, Member> = mutableMapOf()

    fun addBook(book: Book): Unit {
        TODO("cadastre um livro no acervo validando duplicidade")
    }

    fun addMember(member: Member): Unit {
        TODO("cadastre um socio validando duplicidade")
    }

    fun getBook(id: String): Book {
        TODO("busque um livro pelo id ou lance excecao")
    }

    fun getMember(id: String): Member {
        TODO("busque um socio pelo id ou lance excecao")
    }

    fun borrowBook(memberId: String, bookId: String): Unit {
        TODO("realize o emprestimo de um livro para um socio")
    }

    fun returnBook(memberId: String, bookId: String): Unit {
        TODO("realize a devolucao de um livro por um socio")
    }

    fun getBooks(): List<Book> {
        TODO("retorne a lista de livros cadastrados")
    }

    fun getMembers(): List<Member> {
        TODO("retorne a lista de socios cadastrados")
    }
}

fun main(): Unit {
    val library: Library = Library()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "addBook" -> try {
                library.addBook(Book(parts[1], parts[2]))
            } catch (e: Exception) {
                println(e.message)
            }
            "addMember" -> try {
                library.addMember(Member(parts[1], parts[2], parts[3].toInt()))
            } catch (e: Exception) {
                println(e.message)
            }
            "books" -> for (book: Book in library.getBooks()) {
                println(book)
            }
            "members" -> for (member: Member in library.getMembers()) {
                println(member)
            }
            "borrow" -> try {
                library.borrowBook(parts[1], parts[2])
            } catch (e: Exception) {
                println(e.message)
            }
            "return" -> try {
                library.returnBook(parts[1], parts[2])
            } catch (e: Exception) {
                println(e.message)
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}