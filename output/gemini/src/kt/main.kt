const val INVALID_COMMAND_MSG: String = "fail: invalid command"
const val BOOK_ALREADY_EXISTS_MSG: String = "fail: book already exists"
const val BOOK_NOT_FOUND_MSG: String = "fail: book not found"
const val BOOK_ALREADY_LENT_MSG: String = "fail: book already lent"

class Livro(private val codigo: String, private val titulo: String) {
    private var emprestado: Boolean = false

    fun getCodigo(): String {
        return codigo
    }

    fun getTitulo(): String {
        return titulo
    }

    fun isEmprestado(): Boolean {
        return emprestado
    }

    fun setEmprestado(emprestado: Boolean): Unit {
        this.emprestado = emprestado
    }

    override fun toString(): String {
        return "$codigo:$titulo:$emprestado"
    }
}

class Membro(private val id: String, private val nome: String) {
    fun getId(): String {
        return id
    }

    fun getNome(): String {
        return nome
    }
}

class Biblioteca {
    private val livros: MutableMap<String, Livro> = mutableMapOf()
    private val membros: MutableMap<String, Membro> = mutableMapOf()

    fun adicionarLivro(livro: Livro): Unit {
        if (livros.containsKey(livro.getCodigo())) {
            throw IllegalArgumentException("Book already exists")
        }
        livros[livro.getCodigo()] = livro
    }

    fun adicionarMembro(membro: Membro): Unit {
        membros[membro.getId()] = membro
    }

    fun emprestarLivro(codigo: String): Unit {
        val livro: Livro = livros[codigo] ?: throw NoSuchElementException("Book not found")
        if (livro.isEmprestado()) {
            throw IllegalStateException("Book already lent")
        }
        livro.setEmprestado(true)
    }

    fun devolverLivro(codigo: String): Unit {
        val livro: Livro = livros[codigo] ?: throw NoSuchElementException("Book not found")
        livro.setEmprestado(false)
    }

    fun getLivros(): List<Livro> {
        return livros.values.toList()
    }
}

fun main(): Unit {
    var biblioteca: Biblioteca = Biblioteca()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "show" -> {
                for (livro: Livro in biblioteca.getLivros()) { println(livro) }
            }
            "add_book" -> {
                val codigo: String = parts[1]
                val titulo: String = parts[2]
                try { biblioteca.adicionarLivro(Livro(codigo, titulo)) } catch (e: IllegalArgumentException) { println(BOOK_ALREADY_EXISTS_MSG) }
            }
            "add_member" -> {
                val id: String = parts[1]
                val nome: String = parts[2]
                biblioteca.adicionarMembro(Membro(id, nome))
            }
            "lend" -> {
                val codigo: String = parts[1]
                try { biblioteca.emprestarLivro(codigo) } catch (e: NoSuchElementException) { println(BOOK_NOT_FOUND_MSG) } catch (e: IllegalStateException) { println(BOOK_ALREADY_LENT_MSG) }
            }
            "return" -> {
                val codigo: String = parts[1]
                try { biblioteca.devolverLivro(codigo) } catch (e: NoSuchElementException) { println(BOOK_NOT_FOUND_MSG) }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}
