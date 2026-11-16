const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Livro(private val titulo: String) {
    private var emprestado: Boolean = false

    fun getTitulo(): String {
        return this.titulo
    }

    fun isEmprestado(): Boolean {
        return this.emprestado
    }

    fun emprestar(): Boolean {
        if (this.emprestado) {
            return false
        }
        this.emprestado = true
        return true
    }

    fun devolver(): Boolean {
        if (!this.emprestado) {
            return false
        }
        this.emprestado = false
        return true
    }

    override fun toString(): String {
        val status: String = if (this.emprestado) "emprestado" else "disponivel"
        return "${this.titulo} [$status]"
    }
}

class Socio(private val cpf: String, private val limite: Int) {
    private val livros: MutableList<Livro> = mutableListOf()

    fun getCpf(): String {
        return this.cpf
    }

    fun getLimite(): Int {
        return this.limite
    }

    fun getLivros(): List<Livro> {
        return this.livros.toList()
    }

    fun podeEmprestar(): Boolean {
        return this.livros.size < this.limite
    }

    fun adicionarLivro(livro: Livro): Boolean {
        if (!this.podeEmprestar()) {
            return false
        }
        this.livros.add(livro)
        return true
    }

    fun removerLivro(titulo: String): Livro? {
        val iterator: MutableIterator<Livro> = this.livros.iterator()
        while (iterator.hasNext()) {
            val livro: Livro = iterator.next()
            if (livro.getTitulo() == titulo) {
                iterator.remove()
                return livro
            }
        }
        return null
    }

    fun temLivro(titulo: String): Boolean {
        for (livro: Livro in this.livros) {
            if (livro.getTitulo() == titulo) {
                return true
            }
        }
        return false
    }

    override fun toString(): String {
        val titulos: String = this.livros.joinToString(separator = ", ") { it.getTitulo() }
        return "socio: ${this.cpf} [limite: ${this.limite}, emprestados: [$titulos]]"
    }
}

class Biblioteca {
    private val socios: MutableMap<String, Socio> = linkedMapOf()
    private val livros: MutableMap<String, Livro> = linkedMapOf()

    fun cadastrarSocio(cpf: String, limite: Int): Unit {
        if (this.socios.containsKey(cpf)) {
            throw IllegalArgumentException("socio already exists")
        }
        this.socios[cpf] = Socio(cpf, limite)
    }

    fun cadastrarLivro(titulo: String): Unit {
        if (this.livros.containsKey(titulo)) {
            throw IllegalArgumentException("livro already exists")
        }
        this.livros[titulo] = Livro(titulo)
    }

    fun emprestar(cpf: String, titulo: String): Unit {
        val socio: Socio = this.socios[cpf] ?: throw IllegalArgumentException("socio nao encontrado")
        val livro: Livro = this.livros[titulo] ?: throw IllegalArgumentException("livro nao encontrado")

        if (livro.isEmprestado()) {
            throw IllegalStateException("livro indisponivel")
        }
        if (!socio.podeEmprestar()) {
            throw IllegalStateException("limite de emprestimos excedido")
        }

        livro.emprestar()
        socio.adicionarLivro(livro)
    }

    fun devolver(cpf: String, titulo: String): Unit {
        val socio: Socio = this.socios[cpf] ?: throw IllegalArgumentException("socio nao encontrado")
        val livro: Livro = this.livros[titulo] ?: throw IllegalArgumentException("livro nao encontrado")

        if (!socio.temLivro(titulo)) {
            throw IllegalStateException("socio nao possui este livro")
        }

        socio.removerLivro(titulo)
        livro.devolver()
    }

    override fun toString(): String {
        val linhas: MutableList<String> = mutableListOf()
        for (socio: Socio in this.socios.values) {
            linhas.add(socio.toString())
        }
        for (livro: Livro in this.livros.values) {
            linhas.add("livro: " + livro.toString())
        }
        return linhas.joinToString(separator = "\n")
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