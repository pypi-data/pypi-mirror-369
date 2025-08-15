from tkinter import *
from transformers import *

# --------------------------------------------------- #
#                     Pitonio                         #
#             BIBLIOTECA DE FUNÇÕES ÚTEIS             #
# --------------------------------------------------- #

## --- Funções de Entrada e Saída (I/O) ---
def mostra(txt, acao=None):
    """Exibe uma mensagem ou texto na tela."""
    if acao:
        mostra(f"{txt} - {acao}")
    else:
        print(txt)
def pegar_texto(txt):
    """Exibe uma mensagem para o usuário e retorna o texto (string) que ele digitar."""
    return input(txt)
def pegar_numero(num):
    """Exibe uma mensagem e retorna um número inteiro digitado pelo usuário."""
    return int(input(num))
## --- Funções de Manipulação de Dados ---
def tamanho(n):
    """Retorna o número de itens de um objeto (tamanho de uma lista, caracteres de um texto, etc.)."""
    return len(n)
def alcance(n1, n2):
    """Cria uma sequência de números que vai de 'n1' até 'n2' (incluindo o 'n2')."""
    return range(n1, n2 + 1)
def tem(l, i):
    """Verifica se um item 'i' está contido dentro de uma lista ou texto 'l'. Retorna True ou False."""
    if i in l:
        mostra(f"{i} esta em {l}")
    else:
        mostra(f"{i} não esta em {l}")
## --- Funções de Controle de Fluxo ---
def se(c, msg_verdade, msg_falso=None):
    """Simula uma estrutura 'se/senão'. Se a condição 'c' for verdadeira, mostra a 'msg_verdade', senão, mostra a 'msg_falso'."""
    if c:
        mostra(msg_verdade)
    elif msg_falso:
        mostra(msg_falso)
def caso(v, c, cp=None):
    """Simula uma estrutura 'switch/case' usando um dicionário.
    Procura o valor 'v' como chave no dicionário 'c' e executa a função associada.
    Se não encontrar, executa o caso padrão 'cp', se ele for fornecido.
    """
    func = c.get(v, cp)
    if func:
        func()
    else:
        mostra("Nenhum caso correspondeu.")
def pra(iteravel, acao=None, formato=None):
    """Funciona como um laço 'for' genérico e flexível.
    1. Se 'acao' (uma função) é passada, executa acao(item).
    2. Senão, se 'formato' (um texto) é passado, mostra o texto formatado com o item.
    3. Senão, apenas mostra o item.
    """
    for item in iteravel:
        if acao:
            acao(item)
        elif formato:
            mostra(formato.format(item))
        else:
            mostra(item)
## --- Funções de Lista ---
def mostrar_lista(l):
    """Percorre todos os itens de uma lista 'l' e mostra cada um deles na tela."""
    for i in l:
        mostra(i)
def remover_a_lista(l, i):
    """Remove a primeira ocorrência do item 'i' da lista 'l', somente se ele existir."""
    if i in l:
        l.remove(i)
def adicionar_a_lista(l, i):
    """Adiciona um item 'i' ao final da lista 'l'."""
    l.append(i)
## --- Funções de Comparação ---
def e_igual(a, b):
    """Verifica se 'a' é igual a 'b'."""
    return a == b
def e_diferente(a, b):
    """Verifica se 'a' é diferente de 'b'."""
    return a != b
def e_maior(a, b):
    """Verifica se 'a' é maior que 'b'."""
    return a > b
def e_menor(a, b):
    """Verifica se 'a' é menor que 'b'."""
    return a < b
def e_maior_igual(a, b):
    """Verifica se 'a' é maior ou igual a 'b'."""
    return a >= b
def e_menor_igual(a, b):
    """Verifica se 'a' é menor ou igual a 'b'."""
    return a <= b
## --- Funções Matemáticas ---
def soma(a, b):
    """Retorna a soma de 'a' e 'b'."""
    return a + b
def subtrair(a, b):
    """Retorna a subtração de 'b' de 'a' (a - b)."""
    return a - b
def multiplicar(a, b):
    """Retorna a multiplicação de 'a' por 'b'."""
    return a * b
def dividir(a, b):
    """Retorna a divisão de 'a' por 'b'. Impede a divisão por zero."""
    if b == 0:
        mostra("Não é possível dividir por zero.")
        return None
    return a / b
def potencia(a, b):
    """Retorna 'a' elevado à potência de 'b'."""
    return a ** b
def raiz_quadrada(a):
    """Retorna a raiz quadrada de 'a'. Impede a raiz quadrada de números negativos."""
    if a < 0:
        mostra("Não é possível calcular a raiz quadrada de um número negativo.")
        return None
    return a ** 0.5
def fatorial(n):
    """Calcula o fatorial de 'n' (n!). Retorna 1 para n = 0 ou n = 1."""
    if n < 0:
        mostra("Não é possível calcular o fatorial de um número negativo.")
        return None
    if n == 0 or n == 1:
        return 1
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado
## --- Funções de Manipulação de Texto ---
def maiusculas(t):
    """Converte todo o texto 't' para letras maiúsculas."""
    return t.upper()
def minusculas(t):
    """Converte todo o texto 't' para letras minúsculas."""
    return t.lower()
def capitalizar(t):
    """Converte a primeira letra de cada palavra do texto 't' para maiúscula."""
    return t.title()
def inverter(t):
    """Inverte a ordem dos caracteres no texto 't'."""
    return t[::-1]
def titulo(t):
    """Converte a primeira letra de cada palavra do texto 't' para maiúscula e o restante para minúscula."""
    return t.capitalize()
## --- Funções de Interface Gráfica (Tkinter) ---
def criar_janela(titulo="Minha Janela", largura=300, altura=200):
    """Cria uma janela Tkinter com o título, largura e altura especificados."""
    janela = Tk()
    janela.title(titulo)
    janela.geometry(f"{largura}x{altura}")
    return janela
def mostrar_janela(janela):
    """Exibe a janela Tkinter."""
    janela.mainloop()
def adicionar_botao(janela, texto, comando):
    """Adiciona um botão à janela Tkinter com o texto e comando especificados."""
    botao = Button(janela, text=texto, command=comando)
    botao.pack()
    return botao
def adicionar_label(janela, texto):
    """Adiciona um rótulo (label) à janela Tkinter com o texto especificado."""
    label = Label(janela, text=texto)
    label.pack()
    return label
def adicionar_entrada(janela, texto):
    """Adiciona um campo de entrada (entry) à janela Tkinter com o texto especificado."""
    entrada = Entry(janela)
    entrada.insert(0, texto)
    entrada.pack()
    return entrada
def adicionar_caixa_de_selecao(janela, texto, variavel):
    """Adiciona uma caixa de seleção (checkbutton) à janela Tkinter com o texto e variável especificados."""
    checkbutton = Checkbutton(janela, text=texto, variable=variavel)
    checkbutton.pack()
    return checkbutton
## --- Funções de IAs ---
def gerar_texto(prompt, max_len=50, caminho_modelo=None):
    """Gera texto usando um modelo padrão ou um modelo fornecido pelo usuário."""
    modelo = caminho_modelo if caminho_modelo else "distilgpt2"
    pipe = pipeline("text-generation", model=modelo)
    resultado = pipe(prompt, max_length=max_len)
    return resultado[0]["generated_text"]
def sentimento(texto, caminho_modelo=None):
    modelo = caminho_modelo if caminho_modelo else "distilbert-base-uncased-finetuned-sst-2-english"
    pipe_ = pipeline("sentiment-analysis", model=modelo)
    return pipe_(texto)[0]['label']
def traduzir_para_pt(texto, caminho_modelo=None):
    modelo = caminho_modelo if caminho_modelo else "Helsinki-NLP/opus-mt-en-pt"
    pipe_ = pipeline("translation_en_to_pt", model=modelo)
    return pipe_(texto)[0]['translation_text']
