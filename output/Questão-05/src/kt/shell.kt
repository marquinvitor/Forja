const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Livro(private val titulo: String) {
    private var emprestado: Boolean = false

    fun getTitulo(): String {
        TODO("retorne o titulo do livro")
    }

    fun isEmprestado(): Boolean {
        TODO("retorne true se o livro estiver emprestado ou false caso contrario")
    }

    fun emprestar(): Boolean {
        TODO("marque o livro como emprestado se estiver disponivel e retorne true; caso contrario retorne false")
    }

    fun devolver(): Boolean {
        TODO("marque o livro como disponivel se estiver emprestado e retorne true; caso contrario retorne false")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do livro no formato 'titulo [status]'")
    }
}

class Socio(private val cpf: String, private val limite: Int) {
    private val livros: MutableList<Livro> = mutableListOf()

    fun getCpf(): String {
        TODO("retorne o cpf do socio")
    }

    fun getLimite(): Int {
        TODO("retorne o limite de emprestimos do socio")
    }

    fun getLivros(): List<Livro> {
        TODO("retorne a lista de livros atualmente emprestados ao socio")
    }

    fun podeEmprestar(): Boolean {
        TODO("retorne true se a quantidade de livros emprestados for menor que o limite")
    }

    fun adicionarLivro(livro: Livro): Boolean {
        TODO("adicione o livro a lista do socio se ele puder emprestar e retorne true; caso contrario retorne false")
    }

    fun removerLivro(titulo: String): Livro? {
        TODO("remova e retorne o livro com o titulo informado da lista do socio, ou null se nao encontrar")
    }

    fun temLivro(titulo: String): Boolean {
        TODO("retorne true se o socio possuir um livro com o titulo informado")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do socio no formato 'socio: cpf [limite: limite, emprestados: [titulos]]'")
    }
}

class Biblioteca {
    private val socios: MutableMap<String, Socio> = linkedMapOf()
    private val livros: MutableMap<String, Livro> = linkedMapOf()

    fun cadastrarSocio(cpf: String, limite: Int): Unit {
        TODO("cadastre um novo socio ou lance IllegalArgumentException('socio already exists') se o cpf ja existir")
    }

    fun cadastrarLivro(titulo: String): Unit {
        TODO("cadastre um novo livro ou lance IllegalArgumentException('livro already exists') se o titulo ja existir")
    }

    fun emprestar(cpf: String, titulo: String): Unit {
        TODO("valide socio, livro, disponibilidade e limite lancando as excecoes adequadas, e realize o emprestimo")
    }

    fun devolver(cpf: String, titulo: String): Unit {
        TODO("valide socio, livro e posse do livro lancando as excecoes adequadas, e realize a devolucao")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual de todos os socios seguidos de todos os livros cadastrados")
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
            "init" -> biblioteca = Biblioteca()
            "show" -> {
                val output: String = biblioteca.toString()
                if (output.isNotEmpty()) {
                    println(output)
                }
            }
            "add_socio" -> {
                try {
                    biblioteca.cadastrarSocio(parts[1], parts[2].toInt())
                } catch (e: Exception) {
                    println("fail: " + e.message)
                }
            }
            "add_livro" -> {
                try {
                    biblioteca.cadastrarLivro(parts[1])
                } catch (e: Exception) {
                    println("fail: " + e.message)
                }
            }
            "emprestar" -> {
                try {
                    biblioteca.emprestar(parts[1], parts[2])
                } catch (e: Exception) {
                    println("fail: " + e.message)
                }
            }
            "devolver" -> {
                try {
                    biblioteca.devolver(parts[1], parts[2])
                } catch (e: Exception) {
                    println("fail: " + e.message)
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}