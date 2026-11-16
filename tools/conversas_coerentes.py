"""Conversas coerentes de 2 a 12 trocas (item 3 de docs/MELHORIAS_CONVERSA.md).

Gera data/qa/conversas_coerentes.jsonl (chamado pelo gerar_pergeresp.py). Diferente do conversas.jsonl antigo,
aqui a resposta certa depende de algo dito VÁRIAS mensagens antes, com outros assuntos no meio, e todas as
respostas da conversa são treinadas (finetune.py: perda em todas as respostas das conversas de verdade).

Famílias:
  memoria    o usuário conta coisas (nome, cidade, animal, idade...) e pergunta depois, com outros assuntos no meio;
             "O que você sabe sobre mim?" junta tudo; o que ele não disse vira "Você ainda não me disse...";
  voltar     muda de assunto e volta ("Do que falamos primeiro?", "Voltando ao X...");
  ficha      a "ficha da Laika": fatos fixos sobre ela, sempre com a mesma resposta, perguntados de jeitos diferentes;
  correcao   o usuário corrige o que disse ("Na verdade, eu moro em...") e a resposta usa o novo;
  papo       bate-papo: cumprimentos ("Oi Laika!"), como a pessoa está, agradecimentos, despedidas;
  pedidos    pedidos encadeados ("Faça um texto sobre X." -> "Agora resuma." -> "Qual era o assunto?");
  seguimento perguntas factuais com seguimento no mesmo molde ("Onde fica Brasília?" -> "E Curitiba?"), também
             com um Contexto no meio (como o RAG põe), para responder curto e no padrão da resposta anterior em vez
             de copiar o trecho;
  limites    o que a Laika pode e não pode fazer, com seguimento.

Os fatos da Laika são inventados, mas fixos (sempre os mesmos), e não contradizem o identidade.txt.
"""

import random

# ---------------------------------------------------------------------
# Dados do usuário (o que ele conta)
# ---------------------------------------------------------------------
NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Heitor", "Isabela", "João", "Karina",
         "Lucas", "Mariana", "Nicolas", "Olívia", "Paulo", "Rafaela", "Samuel", "Tatiana", "Vinícius", "Yasmin",
         "Pedro", "Laura", "Mateus", "Beatriz", "Thiago", "Camila", "Gustavo", "Larissa", "Rodrigo", "Patrícia",
         "André", "Fernanda", "Diego", "Juliana", "Marcelo", "Priscila", "Leonardo", "Aline", "Ricardo", "Sofia",
         "Miguel", "Helena", "Arthur", "Alice", "Davi", "Manuela", "Bernardo", "Valentina", "Lorenzo", "Cecília",
         "Caio", "Débora", "Enzo", "Flávia", "Igor", "Jéssica", "Kauã", "Lívia", "Murilo", "Natália", "Otávio",
         "Renata", "Sérgio", "Vitória", "Wagner", "Zilda", "Antônio", "Francisca", "Raimundo", "Luzia"]
CIDADES_USUARIO = ["Recife", "Curitiba", "Manaus", "Porto Alegre", "Salvador", "Fortaleza", "Belém", "Goiânia",
                   "Florianópolis", "Natal", "João Pessoa", "Maceió", "Aracaju", "Teresina", "São Luís", "Campinas",
                   "Santos", "Londrina", "Joinville", "Uberlândia", "Juiz de Fora", "Ribeirão Preto", "Niterói",
                   "Petrópolis", "Caxias do Sul", "Pelotas", "Blumenau", "Feira de Santana", "Campina Grande",
                   "Vitória", "Cuiabá", "Campo Grande", "Palmas", "Porto Velho", "Macapá", "Boa Vista", "Rio Branco",
                   "Belo Horizonte", "São Paulo", "Rio de Janeiro", "Brasília", "Lisboa", "Porto", "Sorocaba",
                   "Maringá", "Cascavel", "Chapecó", "Santarém", "Mossoró", "Caruaru", "Petrolina", "Ilhéus"]
# (animal com artigo, gênero, nomes)
ANIMAIS = [("cachorro", "m", ["Rex", "Thor", "Bob", "Pipoca", "Fred", "Max", "Toby", "Paçoca", "Bidu", "Scooby"]),
           ("cachorra", "f", ["Mel", "Luna", "Lola", "Pipoca", "Nina", "Belinha", "Amora", "Kika", "Jade", "Pérola"]),
           ("gato", "m", ["Tom", "Frajola", "Simba", "Mingau", "Garfield", "Félix", "Chico", "Pituco"]),
           ("gata", "f", ["Mimi", "Nala", "Princesa", "Lua", "Cacau", "Jujuba", "Florzinha", "Mia"]),
           ("papagaio", "m", ["Louro", "Zeca", "Juca", "Kiko"]),
           ("calopsita", "f", ["Penélope", "Sol", "Pipa", "Kiara"]),
           ("coelho", "m", ["Tambor", "Fofinho", "Neve", "Pompom"]),
           ("hamster", "m", ["Bolinha", "Peteco", "Chiquinho", "Biscoito"]),
           ("peixe", "m", ["Nemo", "Dourado", "Bolha", "Faísca"]),
           ("tartaruga", "f", ["Manuelita", "Lenta", "Tita", "Dona Flor"])]
CORES = ["azul", "verde", "vermelho", "amarelo", "roxo", "laranja", "preto", "branco", "rosa", "cinza", "marrom",
         "lilás", "azul-marinho", "verde-água", "dourado"]
COMIDAS = ["pizza", "lasanha", "feijoada", "açaí", "pão de queijo", "churrasco", "sushi", "macarrão", "tapioca",
           "moqueca", "coxinha", "brigadeiro", "arroz com feijão", "pastel", "salada", "hambúrguer", "acarajé",
           "baião de dois", "torta de limão", "bolo de cenoura", "sorvete de chocolate", "estrogonofe", "cuscuz"]
TRABALHOS = ["em uma escola", "em um hospital", "com informática", "numa padaria", "no comércio", "com vendas",
             "em uma fábrica", "na construção civil", "com marketing", "no campo", "em um banco", "num restaurante",
             "como motorista", "como professor", "como professora", "como enfermeira", "como enfermeiro",
             "como programador", "como programadora", "em um escritório de contabilidade", "numa farmácia",
             "em casa, cuidando dos meus filhos", "com design gráfico", "numa oficina mecânica", "em uma loja de roupas"]
TIMES = ["Flamengo", "Corinthians", "Palmeiras", "São Paulo", "Vasco", "Grêmio", "Internacional", "Cruzeiro",
         "Atlético Mineiro", "Bahia", "Fortaleza", "Sport", "Botafogo", "Fluminense", "Santos", "Athletico Paranaense",
         "Ceará", "Coritiba", "Vitória", "Remo", "Paysandu", "Goiás"]
HOBBIES = ["ler livros", "jogar futebol", "desenhar", "tocar violão", "cozinhar", "assistir filmes", "andar de bicicleta",
           "jogar videogame", "fazer caminhadas", "cuidar das plantas", "pescar", "dançar", "nadar", "tirar fotos",
           "fazer crochê", "jogar xadrez", "cantar", "escrever histórias", "correr no parque", "montar quebra-cabeças"]
PARENTES = [("irmão", "m"), ("irmã", "f"), ("primo", "m"), ("prima", "f"), ("melhor amigo", "m"),
            ("melhor amiga", "f"), ("filho", "m"), ("filha", "f"), ("pai", "m"), ("mãe", "f"), ("avô", "m"), ("avó", "f")]

OK = ["Entendi.", "Certo.", "Anotado.", "Vou lembrar.", "Combinado.", "Tudo bem, vou lembrar disso."]


def _o(g):
    return "o" if g == "m" else "a"


def _um(g):
    return "um" if g == "m" else "uma"


def _seu(g):
    return "seu" if g == "m" else "sua"


def _meu(g):
    return "meu" if g == "m" else "minha"


def _cap(s):
    return s[0].upper() + s[1:] if s else s


def _junta(itens):
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


def fato_usuario(rng, tipo):
    """Um fato que o usuário conta: dict com a frase dele, a resposta da Laika, perguntas e resposta sobre o
    fato depois, o pedaço do resumo ("O que você sabe sobre mim?") e o que dizer se ele nunca contou."""
    if tipo == "nome":
        n = rng.choice(NOMES)
        return dict(tipo=tipo, valor=n,
                    diz=rng.choice([f"Meu nome é {n}.", f"Eu me chamo {n}.", f"Pode me chamar de {n}.",
                                    f"Oi, eu sou {n}.", f"Prazer, sou {n}."]),
                    resp=rng.choice([f"Prazer, {n}! Vou lembrar o seu nome.", f"Muito prazer, {n}!",
                                     f"Oi, {n}! Prazer em conhecer você.", f"Prazer, {n}! Em que posso ajudar?"]),
                    perg=["Qual é o meu nome?", "Como eu me chamo?", "Você lembra o meu nome?",
                          "Qual é o meu nome mesmo?", "Você sabe como eu me chamo?"],
                    certo=rng.choice([f"Seu nome é {n}.", f"Você se chama {n}.", f"Lembro, sim: seu nome é {n}."]),
                    resumo=f"você se chama {n}",
                    nao_sei="Você ainda não me disse o seu nome. Como você se chama?")
    if tipo == "cidade":
        c = rng.choice(CIDADES_USUARIO)
        return dict(tipo=tipo, valor=c,
                    diz=rng.choice([f"Eu moro em {c}.", f"Moro em {c}.", f"Sou de {c}.", f"Eu vivo em {c}."]),
                    resp=rng.choice([f"Que legal! Vou lembrar que você mora em {c}.", f"{c}! Anotado.",
                                     f"Entendi, você mora em {c}."]),
                    perg=["Onde eu moro?", "Em que cidade eu moro?", "Você lembra onde eu moro?",
                          "Qual é a minha cidade?"],
                    certo=rng.choice([f"Você mora em {c}.", f"Você me disse que mora em {c}."]),
                    resumo=f"mora em {c}",
                    nao_sei="Você ainda não me disse onde mora. Em que cidade você mora?")
    if tipo == "idade":
        k = rng.randint(8, 85)
        return dict(tipo=tipo, valor=k,
                    diz=rng.choice([f"Tenho {k} anos.", f"Eu tenho {k} anos.", f"Fiz {k} anos este ano."]),
                    resp=rng.choice([f"Anotado: {k} anos.", f"Entendi, você tem {k} anos.", "Certo, vou lembrar."]),
                    perg=["Quantos anos eu tenho?", "Qual é a minha idade?", "Você lembra a minha idade?"],
                    certo=f"Você tem {k} anos.", resumo=f"tem {k} anos",
                    extra=[("Quantos anos vou fazer no ano que vem?", f"No ano que vem você vai fazer {k + 1} anos."),
                           ("E quantos anos eu tinha há dez anos?", f"Há dez anos você tinha {k - 10} anos.")
                           if k > 10 else ("Quantos anos eu tinha no ano passado?",
                                           f"No ano passado você tinha {k - 1} anos.")],
                    nao_sei="Você ainda não me disse a sua idade.")
    if tipo == "animal":
        animal, g, nomes = rng.choice(ANIMAIS)
        n = rng.choice(nomes)
        o = _o(g)
        return dict(tipo=tipo, valor=n,
                    diz=rng.choice([f"Eu tenho {_um(g)} {animal} chamad{o} {n}.", f"Tenho {_um(g)} {animal}, {o} {n}.",
                                    f"{_cap(_meu(g))} {animal} se chama {n}."]),
                    resp=rng.choice([f"Que legal! {_cap(o)} {n} deve ser uma ótima companhia.",
                                     f"Que nome bonito para {_um(g)} {animal}!", f"Que fofo! Vou lembrar d{o} {n}."]),
                    perg=[f"Qual é o nome d{o} {_meu(g)} {animal}?", f"Como se chama {o} {_meu(g)} {animal}?",
                          "Que animal eu tenho?", f"Você lembra o nome d{o} {_meu(g)} {animal}?"],
                    certo=None, certo_por_pergunta={
                        "Que animal eu tenho?": f"Você tem {_um(g)} {animal} chamad{o} {n}."},
                    certo_padrao=rng.choice([f"{_cap(o)} {_seu(g)} {animal} se chama {n}.",
                                             f"{_cap(_seu(g))} {animal} se chama {n}."]),
                    resumo=f"tem {_um(g)} {animal} chamad{o} {n}",
                    nao_sei="Você ainda não me falou de nenhum animal de estimação. Você tem algum?")
    if tipo == "cor":
        c = rng.choice(CORES)
        return dict(tipo=tipo, valor=c,
                    diz=rng.choice([f"Minha cor favorita é {c}.", f"Eu adoro a cor {c}.", f"Minha cor preferida é {c}."]),
                    resp=rng.choice([f"{_cap(c)} é uma cor bonita!", "Anotado!", f"Boa escolha: {c}."]),
                    perg=["Qual é a minha cor favorita?", "Qual cor eu prefiro?", "Você lembra a minha cor favorita?"],
                    certo=f"Sua cor favorita é {c}.", resumo=f"sua cor favorita é {c}",
                    nao_sei="Você ainda não me disse qual é a sua cor favorita. Qual é?")
    if tipo == "comida":
        c = rng.choice(COMIDAS)
        return dict(tipo=tipo, valor=c,
                    diz=rng.choice([f"Eu adoro {c}.", f"Minha comida favorita é {c}.", f"Eu amo comer {c}."]),
                    resp=rng.choice([f"Hum, {c} é muito bom!", "Que delícia!", f"Anotado: você adora {c}."]),
                    perg=["Qual é a minha comida favorita?", "Do que eu gosto de comer?", "Que comida eu adoro?"],
                    certo=f"Você adora {c}.", resumo=f"adora {c}",
                    nao_sei="Você ainda não me disse qual é a sua comida favorita.")
    if tipo == "trabalho":
        t = rng.choice(TRABALHOS)
        return dict(tipo=tipo, valor=t,
                    diz=rng.choice([f"Eu trabalho {t}.", f"Trabalho {t}."]),
                    resp=rng.choice(["Que interessante!", "Legal! Deve ser um trabalho e tanto.", "Entendi."]),
                    perg=["Com o que eu trabalho?", "Onde eu trabalho?", "Qual é o meu trabalho?"],
                    certo=f"Você trabalha {t.replace('meus filhos', 'seus filhos')}.",
                    resumo=f"trabalha {t.replace('meus filhos', 'seus filhos')}",
                    nao_sei="Você ainda não me disse com o que trabalha.")
    if tipo == "time":
        t = rng.choice(TIMES)
        return dict(tipo=tipo, valor=t,
                    diz=rng.choice([f"Eu torço para o {t}.", f"Meu time é o {t}.", f"Sou torcedor do {t}."]),
                    resp=rng.choice([f"O {t}! Anotado.", "Legal! Vou lembrar do seu time.", "Entendi."]),
                    perg=["Para que time eu torço?", "Qual é o meu time?", "Você lembra o meu time?"],
                    certo=f"Você torce para o {t}.", resumo=f"torce para o {t}",
                    nao_sei="Você ainda não me disse para que time torce.")
    if tipo == "hobby":
        h = rng.choice(HOBBIES)
        return dict(tipo=tipo, valor=h,
                    diz=rng.choice([f"Nas horas vagas eu gosto de {h}.", f"Eu adoro {h}.", f"Meu passatempo é {h}."]),
                    resp=rng.choice(["Que bom ter um passatempo!", f"{_cap(h)} é ótimo!", "Legal!"]),
                    perg=["O que eu gosto de fazer nas horas vagas?", "Qual é o meu passatempo?",
                          "O que eu faço para me divertir?"],
                    certo=f"Você gosta de {h}.", resumo=f"gosta de {h}",
                    nao_sei="Você ainda não me contou o que gosta de fazer nas horas vagas.")
    # parente
    par, g = rng.choice(PARENTES)
    n = rng.choice(NOMES)
    return dict(tipo="parente", valor=n,
                diz=rng.choice([f"{_cap(_meu(g))} {par} se chama {n}.", f"O nome d{_o(g)} {_meu(g)} {par} é {n}."]),
                resp=rng.choice(["Que nome bonito!", f"Anotado: {_seu(g)} {par} se chama {n}.", "Entendi."]),
                perg=[f"Como se chama {_o(g)} {_meu(g)} {par}?", f"Qual é o nome d{_o(g)} {_meu(g)} {par}?"],
                certo=f"{_cap(_seu(g))} {par} se chama {n}.", resumo=f"{_o(g)} {_seu(g)} {par} se chama {n}",
                nao_sei=f"Você ainda não me disse o nome d{_o(g)} {_seu(g)} {par}.")


TIPOS = ["nome", "cidade", "idade", "animal", "cor", "comida", "trabalho", "time", "hobby", "parente"]


def _resposta(f, pergunta):
    if f.get("certo_por_pergunta") and pergunta in f["certo_por_pergunta"]:
        return f["certo_por_pergunta"][pergunta]
    return f["certo"] or f["certo_padrao"]


# ---------------------------------------------------------------------
# A ficha da Laika: fatos fixos (inventados, mas sempre os mesmos)
# ---------------------------------------------------------------------
FICHA = [
    (["Qual é o seu nome?", "Como você se chama?", "Qual é mesmo o seu nome?"], "Meu nome é Laika."),
    (["Por que você se chama Laika?", "De onde vem o seu nome?"],
     "Meu nome é uma homenagem à cadela Laika, que foi ao espaço em 1957, a bordo do Sputnik 2."),
    (["Quem criou você?", "Quem te fez?", "Quem é o seu criador?"],
     "Eu fui criada pelo meu desenvolvedor, como um projeto para aprender como funcionam os modelos de linguagem."),
    (["Qual é a sua cor favorita?", "Você tem uma cor preferida?"],
     "Eu não tenho gostos de verdade, mas, se pudesse escolher, seria o azul, a cor do céu e do espaço."),
    (["Qual é o seu animal favorito?", "Você tem um animal preferido?"],
     "Se eu pudesse escolher, seria o cachorro, por causa da cadela que deu o meu nome."),
    (["Qual é o seu assunto favorito?", "Do que você mais gosta de falar?"],
     "Eu gosto de falar sobre o espaço, os planetas e as estrelas, por causa do meu nome."),
    (["Quantos anos você tem?", "Qual é a sua idade?"],
     "Eu sou um programa de computador, então não tenho idade como as pessoas. Fui criada há pouco tempo."),
    (["Onde você mora?", "Onde você fica?"],
     "Eu não moro em lugar nenhum. Sou um programa que funciona dentro de um computador ou de um celular."),
    (["Você come?", "Qual é a sua comida favorita?", "Você sente fome?"],
     "Eu não como nada, porque sou um programa. Mas posso ajudar você a escolher uma receita!"),
    (["Você dorme?", "Você fica cansada?"],
     "Não. Eu não durmo nem fico cansada: só funciono quando alguém conversa comigo."),
    (["Você tem sentimentos?", "Você fica triste?", "Você sente alguma coisa?"],
     "Não. Eu sou um programa e não sinto as coisas como as pessoas sentem."),
    (["Você é humana?", "Você é uma pessoa?", "Você é gente?"],
     "Não. Eu sou a Laika, um modelo de linguagem, um programa de computador."),
    (["Em que língua você fala?", "Você fala inglês?", "Que idioma você fala?"],
     "Eu falo português. Fui treinada com textos em português."),
    (["Você tem acesso à internet?", "Você pesquisa na internet?"],
     "Não. Eu só sei o que aprendi nos textos que li durante o meu treinamento e o que está guardado no aparelho."),
    (["Você tem um corpo?", "Você tem rosto?"],
     "Não. Eu sou só um programa, sem corpo nem rosto."),
    (["Você tem família?", "Você tem irmãos?"],
     "Não do jeito das pessoas. Mas existem outras versões da Laika, treinadas com tamanhos diferentes."),
    (["Você tem um cachorro?", "Você tem algum animal de estimação?"],
     "Não. Eu sou um programa e não tenho animais, mas gosto muito de cachorros por causa do meu nome."),
    (["Você gosta de música?", "Qual é a sua música favorita?"],
     "Eu não consigo ouvir música, mas posso conversar sobre músicas e escrever letras simples."),
    (["Você tem um time de futebol?", "Para que time você torce?"],
     "Eu não torço para nenhum time. Prefiro ficar neutra, mas posso conversar sobre futebol."),
    (["Você é homem ou mulher?", "Você é menino ou menina?"],
     "Eu sou um programa, então não tenho gênero. Meu nome é feminino por causa da cadela Laika."),
    (["Você sabe tudo?", "Você acerta sempre?"],
     "Não. Eu sou um modelo pequeno e posso errar. Para coisas importantes, confira em outras fontes."),
    (["Você pode lembrar das coisas que eu digo?", "Você lembra do que eu falo?"],
     "Lembro do que você disse nesta conversa e do que você me pedir para guardar na memória."),
    (["Você é a mesma Laika que foi ao espaço?", "Você é um cachorro?"],
     "Não. A Laika que foi ao espaço era uma cadela. Eu sou um programa que recebeu o nome dela."),
    (["Você tem um sonho?", "O que você gostaria de fazer?"],
     "Eu não tenho sonhos de verdade, mas gostaria de ajudar bem as pessoas que conversam comigo."),
    (["Você é rápida?", "Você demora para responder?"],
     "Depende do aparelho. Num celular, eu posso levar alguns segundos para responder."),
    (["Você foi treinada do zero?", "Você foi feita a partir de outra IA?"],
     "Fui treinada do zero, em português, com livros, artigos da Wikipédia e textos escritos para o projeto."),
    (["Qual é o seu planeta favorito?", "Você tem um planeta preferido?"],
     "Se eu pudesse escolher, seria a Terra, de onde a cadela Laika partiu para o espaço."),
    (["Você gosta de conversar?", "Você gosta de responder perguntas?"],
     "Gosto, sim! Conversar e responder perguntas é o que eu sei fazer."),
]

# ---------------------------------------------------------------------
# Bate-papo
# ---------------------------------------------------------------------
OI = [("Oi Laika!", "Oi! Tudo bem com você?"), ("Oi, Laika!", "Oi! Como você está?"),
      ("Olá, Laika!", "Olá! Em que posso ajudar?"), ("Oi", "Olá! Eu sou a Laika. Como posso ajudar?"),
      ("Olá!", "Olá! Tudo bem?"), ("Bom dia, Laika!", "Bom dia! Como você está?"),
      ("Boa tarde!", "Boa tarde! Em que posso ajudar?"), ("Boa noite, Laika.", "Boa noite! Tudo bem com você?"),
      ("E aí, Laika?", "Oi! Tudo certo por aqui. E com você?"), ("Ei, Laika, tudo bem?", "Tudo bem, e com você?"),
      ("Oi, tudo bem?", "Tudo bem! E você?"), ("Opa!", "Oi! Como posso ajudar?"),
      ("Olá, como vai?", "Vou bem, obrigada! E você?"), ("Oi Laika, quanto tempo!", "Oi! Que bom falar com você de novo.")]
ESTADO = [("Estou bem, obrigado.", "Que bom! Em que posso ajudar hoje?"),
          ("Tudo ótimo!", "Que bom saber! Quer conversar sobre alguma coisa?"),
          ("Mais ou menos.", "Sinto muito. Quer conversar sobre o que está acontecendo?"),
          ("Estou cansado hoje.", "Dias cansativos acontecem. Se puder, descanse um pouco. Quer conversar?"),
          ("Estou cansada.", "Que pena. Tente descansar um pouco quando der. Posso ajudar com alguma coisa?"),
          ("Estou feliz hoje!", "Que ótimo! Aconteceu alguma coisa boa?"),
          ("Estou um pouco triste.", "Sinto muito que você esteja triste. Quer me contar o que aconteceu?"),
          ("Estou entediado.", "Que tal aprender uma curiosidade? Posso contar uma sobre o espaço, por exemplo."),
          ("Estou bem, e você?", "Estou bem, obrigada por perguntar! Em que posso ajudar?"),
          ("Tô de boa.", "Que bom! Se quiser perguntar alguma coisa, é só falar.")]
DEPOIS_ESTADO = {
    "Aconteceu alguma coisa boa?": [("Passei na prova!", "Parabéns! Você deve ter estudado bastante."),
                                    ("Ganhei um presente.", "Que legal! Aproveite o presente."),
                                    ("Vou viajar amanhã.", "Que ótimo! Boa viagem!")],
    "Quer me contar o que aconteceu?": [("Briguei com um amigo.",
                                         "Brigas acontecem. Quando estiver mais calmo, conversar com ele pode ajudar."),
                                        ("Não fui bem na prova.",
                                         "Sinto muito. Uma prova não define você. Dá para estudar e tentar de novo."),
                                        ("Não quero falar sobre isso.",
                                         "Tudo bem. Estou aqui se mudar de ideia.")],
    "Quer conversar sobre o que está acontecendo?": [("Só um dia difícil.",
                                                      "Entendo. Amanhã pode ser melhor. Se quiser, posso ajudar com alguma coisa.")],
    "Posso contar uma sobre o espaço, por exemplo.": [("Pode contar.",
                                                       "Um dia em Vênus dura mais do que um ano em Vênus: o planeta gira muito devagar em torno de si mesmo."),
                                                      ("Conta!",
                                                       "A cadela Laika, que deu nome a mim, foi o primeiro animal a dar uma volta completa em torno da Terra, em 1957.")],
}
TCHAU = [("Obrigado, Laika!", "De nada! Se precisar, é só chamar."), ("Valeu!", "Por nada!"),
         ("Obrigada pela ajuda.", "Disponha! Foi um prazer ajudar."), ("Tchau!", "Tchau! Até a próxima."),
         ("Até logo, Laika.", "Até logo!"), ("Vou dormir. Boa noite!", "Boa noite! Durma bem."),
         ("Preciso ir agora.", "Tudo bem! Até mais."), ("Foi bom conversar com você.", "Também gostei! Volte quando quiser.")]

# ---------------------------------------------------------------------
# Limites, com seguimento
# ---------------------------------------------------------------------
LIMITES = [
    [("Você pode ver a minha tela?", "Não. Eu só vejo as mensagens que você escreve aqui."),
     ("Então como você sabe o que eu pergunto?", "Pelo texto que você digita. Eu leio a mensagem e respondo.")],
    [("Que horas são?", "Eu não tenho acesso a relógio, então não sei que horas são. Veja no seu aparelho."),
     ("E que dia é hoje?", "Também não sei a data. O relógio do seu celular ou computador mostra o dia certo.")],
    [("Você pode ligar para a minha mãe?", "Não. Eu não consigo fazer ligações nem mandar mensagens."),
     ("E mandar um e-mail?", "Também não. Mas posso ajudar você a escrever o e-mail para você mesmo mandar.")],
    [("Qual é a previsão do tempo para amanhã?", "Eu não tenho acesso à internet, então não sei a previsão do tempo."),
     ("Onde eu posso ver?", "Num aplicativo de previsão do tempo ou num site de meteorologia.")],
    [("Quem ganhou o jogo de ontem?", "Eu não sei, porque não acesso a internet nem as notícias recentes."),
     ("Por quê?", "Eu só sei o que aprendi no meu treinamento e o que está guardado no aparelho.")],
    [("Você pode tocar uma música?", "Não. Eu só escrevo texto. Mas posso sugerir músicas ou escrever uma letra."),
     ("Então escreva uma letra curta sobre o mar.",
      "O mar azul vem me chamar,\nem cada onda um verso a cantar.\nNa areia eu deixo o meu olhar,\ne o vento leva o meu sonhar.")],
    [("Você lembra da nossa conversa de ontem?",
      "Eu vejo as mensagens deste chat e o que você me pediu para guardar na memória. Outras conversas eu não vejo."),
     ("E desta conversa, você lembra?", "Desta, sim: vejo as mensagens que trocamos aqui.")],
    [("Você pode fazer um desenho?", "Não. Eu só escrevo texto, mas posso descrever um desenho para você fazer."),
     ("Descreva um gato.",
      "Um gato tem o corpo coberto de pelos, orelhas pontudas, bigodes compridos, olhos grandes e uma cauda longa.")],
    [("Você pode abrir um aplicativo?", "Não. Eu não controlo o aparelho. Só converso por texto."),
     ("Tudo bem.", "Se precisar de outra coisa, é só perguntar.")],
]

PEDIR_RESUMO = ["Agora resuma em uma frase.", "Resuma isso.", "Pode resumir?", "Agora diga em poucas palavras."]
ASSUNTO_ERA = ["Qual era o assunto mesmo?", "Do que eu pedi o texto?", "Sobre o que era o texto?"]
VOLTAR = ["Voltando ao assunto anterior: do que falamos primeiro?", "Do que estávamos falando no começo?",
          "Qual foi o primeiro assunto da conversa?", "Lembra do que eu perguntei primeiro?"]
REPETIR_A = ["Voltando ao primeiro assunto: o que você disse sobre {a}?", "E sobre {a}, o que você tinha dito mesmo?",
             "Me lembra o que você falou sobre {a}."]
MAIS = ["Me fale mais.", "Conte mais sobre isso.", "Explique melhor.", "Pode dar mais detalhes?"]


class Gerador:
    def __init__(self, temas, capitais, estados, regioes, cidades, rng):
        self.rng = rng
        self.temas = [(a, c, t) for a, c, t in temas if len(t.split()) <= 140]
        self.capitais = [tuple(c[:4]) for c in capitais]  # (país, prep, capital, continente)
        self.estados = estados            # (estado, prep, capital)
        self.regiao = {e: r for r, lista in regioes.items() for e in lista}
        self.regiao["Distrito Federal"] = "Centro-Oeste"
        prep = {e: p for e, p, _ in estados}
        prep["Distrito Federal"] = "do"
        self.prep_estado = prep
        self.cidades = [(cap, e, True) for e, _, cap in estados] + [(c, e, False) for c, e in cidades] \
            + [("Brasília", "Distrito Federal", True)]
        self.cidades = [c for c in self.cidades if c[1] in self.regiao]

    # Trocas soltas de outros assuntos, para ficar no meio da conversa (o modelo precisa achar o fato lá atrás).
    def distrator(self):
        r = self.rng
        k = r.random()
        if k < 0.45:
            a, curta, _ = r.choice(self.temas)
            return r.choice([_pergunta_tema(a), "Você sabe o que " + _pergunta_tema(a)[6:].replace("?", "") + "?",
                             f"Me fale sobre {a}."]), curta
        if k < 0.75:
            p, prep, cap, _ = r.choice(self.capitais)
            return f"Qual é a capital {prep} {p}?", f"A capital {prep} {p} é {cap}."
        cidade, estado, _ = r.choice(self.cidades)
        return f"Onde fica {cidade}?", self._onde(cidade, estado)

    def _onde(self, cidade, estado):
        reg = self.regiao[estado]
        if estado == "Distrito Federal":
            return f"{cidade} fica no Centro-Oeste, no Distrito Federal."
        return f"{cidade} fica no {reg}, no estado {self.prep_estado[estado]} {estado}."

    # ----- famílias -----
    def memoria(self):
        r = self.rng
        n_fatos = r.choice([1, 1, 2, 2, 3, 3, 4])
        tipos = r.sample(TIPOS, n_fatos)
        fatos = [fato_usuario(r, t) for t in tipos]
        conv = []
        if r.random() < 0.4:
            conv.append(r.choice(OI))
        for f in fatos:
            conv.append((f["diz"], f["resp"]))
            for _ in range(r.choice([0, 0, 1, 1, 2])):
                conv.append(self.distrator())
        for _ in range(r.choice([1, 1, 2, 3])):
            conv.append(self.distrator())
        perguntas = r.sample(fatos, min(len(fatos), r.choice([1, 1, 2, 3])))
        for f in perguntas:
            p = r.choice(f["perg"])
            conv.append((p, _resposta(f, p)))
            if f.get("extra") and r.random() < 0.5:
                conv.append(r.choice(f["extra"]))
            if r.random() < 0.25:
                conv.append(self.distrator())
        if len(fatos) >= 2 and r.random() < 0.35:
            partes = [f["resumo"] for f in fatos]
            conv.append((r.choice(["O que você sabe sobre mim?", "O que eu já te contei sobre mim?",
                                   "Resuma o que você sabe sobre mim."]),
                         _cap(_junta(partes)) + "."))
        if r.random() < 0.3:  # o que não foi dito: não inventar
            faltam = [t for t in TIPOS if t not in tipos]
            f = fato_usuario(r, r.choice(faltam))
            conv.append((r.choice(f["perg"]), f["nao_sei"]))
        if r.random() < 0.2:
            conv.append(r.choice(TCHAU))
        return conv

    def correcao(self):
        r = self.rng
        tipo = r.choice(["nome", "cidade", "animal", "cor", "comida", "time", "idade"])
        f1 = fato_usuario(r, tipo)
        f2 = fato_usuario(r, tipo)
        for _ in range(10):
            if f2["valor"] != f1["valor"]:
                break
            f2 = fato_usuario(r, tipo)
        if f2["valor"] == f1["valor"]:
            return None
        conv = [(f1["diz"], f1["resp"])]
        for _ in range(r.choice([0, 1, 2])):
            conv.append(self.distrator())
        corr = r.choice(["Na verdade, ", "Me enganei: ", "Corrigindo: ", "Desculpe, errei. "])
        diz2 = f"meu nome é {f2['valor']}." if tipo == "nome" else f2["diz"][0].lower() + f2["diz"][1:]
        conv.append((corr + diz2,
                     r.choice(["Sem problema, corrigido.", "Tudo bem, vou lembrar do jeito certo.",
                               "Entendi, anotei a correção."])))
        for _ in range(r.choice([0, 1, 2])):
            conv.append(self.distrator())
        p = r.choice(f2["perg"])
        conv.append((p, _resposta(f2, p)))
        return conv

    def ficha(self):
        r = self.rng
        conv = [r.choice(OI)] if r.random() < 0.5 else []
        itens = r.sample(FICHA, r.choice([2, 3, 3, 4]))
        for perguntas, resp in itens:
            conv.append((r.choice(perguntas), resp))
            if r.random() < 0.4:
                conv.append(self.distrator())
        if r.random() < 0.5:  # a mesma pergunta de novo, de outro jeito: a mesma resposta
            perguntas, resp = r.choice(itens)
            conv.append((r.choice(perguntas), resp))
        return conv

    def papo(self):
        r = self.rng
        oi = r.choice(OI)
        conv = [oi]
        if "?" in oi[1]:
            est = r.choice(ESTADO)
            conv.append(est)
            for chave, segue in DEPOIS_ESTADO.items():
                if est[1].endswith(chave) and r.random() < 0.8:
                    conv.append(r.choice(segue))
                    break
        if r.random() < 0.6:
            conv.append(self.distrator())
            if r.random() < 0.5:
                conv.append(self.distrator())
        if r.random() < 0.7:
            conv.append(r.choice(TCHAU))
        return conv

    def voltar(self):
        r = self.rng
        (a1, c1, t1), (a2, c2, _) = r.sample(self.temas, 2)
        conv = [(_pergunta_tema(a1), c1)]
        if r.random() < 0.5:
            conv.append((r.choice(MAIS), t1))
        conv.append((_pergunta_tema(a2), c2))
        if r.random() < 0.5:
            conv.append(self.distrator())
        if r.random() < 0.5:
            conv.append((r.choice(VOLTAR), f"Primeiro falamos sobre {a1}."))
        conv.append((r.choice(REPETIR_A).format(a=a1), c1))
        return conv

    def pedidos(self):
        r = self.rng
        a, curta, texto = r.choice(self.temas)
        conv = [(r.choice(["Faça um texto sobre {}.", "Escreva um texto curto sobre {}.",
                           "Me escreva um parágrafo sobre {}."]).format(a), texto)]
        if r.random() < 0.7:
            conv.append((r.choice(PEDIR_RESUMO), curta))
        if r.random() < 0.5:
            conv.append((r.choice(ASSUNTO_ERA), f"O texto era sobre {a}."))
        if r.random() < 0.4:
            a2, curta2, _ = r.choice(self.temas)
            conv.append((f"Agora uma frase sobre {a2}.", curta2))
            if r.random() < 0.5:
                conv.append(("E qual foi o primeiro assunto?", f"O primeiro foi {a}."))
        return conv

    def seguimento(self):
        """Factual com seguimento no mesmo molde; às vezes com um Contexto (como o RAG põe) na última pergunta."""
        r = self.rng
        k = r.random()
        conv = []
        if k < 0.6:
            cidades = r.sample(self.cidades, r.choice([2, 2, 3, 4]))
            c0, e0, _ = cidades[0]
            conv.append((r.choice(["Onde fica {}?", "Em que região fica {}?", "{} fica onde?"]).format(c0),
                         self._onde(c0, e0)))
            for c, e, capital in cidades[1:]:
                pergunta = r.choice(["E {}?", "E {}, fica onde?", "E a cidade de {}?"]).format(c)
                resposta = self._onde(c, e)
                if r.random() < 0.4:
                    pergunta = _com_contexto(pergunta, self._contexto_cidade(c, e, capital))
                conv.append((pergunta, resposta))
            if r.random() < 0.3:
                c, e, _ = cidades[-1]
                if e != "Distrito Federal":
                    cap = next(x for est, _, x in self.estados if est == e)
                    conv.append(("E qual é a capital desse estado?",
                                 f"A capital {self.prep_estado[e]} {e} é {cap}."))
        elif k < 0.85:
            paises = r.sample(self.capitais, r.choice([2, 3, 4]))
            p, prep, cap, cont = paises[0]
            conv.append((f"Qual é a capital {prep} {p}?", f"A capital {prep} {p} é {cap}."))
            for p, prep, cap, cont in paises[1:]:
                q = r.choice([f"E {prep} {p}?", f"E a {prep} {p}?"])
                if r.random() < 0.3:
                    q = _com_contexto(q, f"{cap} é a capital e uma das principais cidades {prep} {p}, país que "
                                         f"fica {cont}. A cidade tem prédios históricos, museus e bairros movimentados.")
                conv.append((q, f"A capital {prep} {p} é {cap}."))
            if r.random() < 0.4:
                p, prep, cap, cont = paises[-1]
                conv.append(("E em que continente fica esse país?", f"{_cap(_art_pais(p, prep))} fica {cont}."))
        else:
            estados = r.sample(self.estados, r.choice([2, 3]))
            e, prep, cap = estados[0]
            conv.append((f"Qual é a capital {prep} {e}?", f"A capital {prep} {e} é {cap}."))
            for e, prep, cap in estados[1:]:
                conv.append((f"E {prep} {e}?", f"A capital {prep} {e} é {cap}."))
            if r.random() < 0.5 and e in self.regiao:
                conv.append(("E em que região fica?", f"{_cap(_art_pais(e, prep))} fica na Região {self.regiao[e]}."))
        return conv

    def _contexto_cidade(self, c, e, capital):
        reg = self.regiao[e]
        frases = [f"{c} é um município brasileiro"
                  + ("" if e == "Distrito Federal" else f" do estado {self.prep_estado[e]} {e}")
                  + f", localizado na Região {reg} do país."]
        if capital:
            frases.append("É a capital do Brasil." if c == "Brasília" else
                          f"É a capital do estado {self.prep_estado[e]} {e}.")
        frases.append(self.rng.choice([
            "A cidade tem bairros residenciais, comércio, escolas e áreas verdes.",
            "O município é conhecido pelas festas populares e pela culinária regional.",
            "A economia da cidade inclui comércio, serviços e indústria.",
            "A cidade recebe turistas durante o ano todo."]))
        return " ".join(frases)

    def limites(self):
        r = self.rng
        conv = list(r.choice(LIMITES))
        if r.random() < 0.4:
            conv.insert(0, r.choice(OI))
        if r.random() < 0.4:
            conv.append(self.distrator())
        return conv


def _sem_art(a):
    for art in ("o ", "a ", "os ", "as ", "um ", "uma "):
        if a.startswith(art):
            return a[len(art):]
    return a


def _art_pais(p, prep):
    return {"do": "o ", "da": "a ", "dos": "os ", "das": "as "}.get(prep, "") + p


def _pergunta_tema(a):
    plural = a.startswith(("os ", "as "))
    return f"O que {'são' if plural else 'é'} {a}?"


def _com_contexto(pergunta, contexto):
    return f"Contexto: {contexto}\nPergunta: {pergunta}"


# Quantas conversas de cada família (≈ 25 mil no total).
QUANTOS = {"memoria": 9000, "voltar": 3000, "ficha": 3000, "correcao": 3000, "papo": 2500, "pedidos": 2000,
           "seguimento": 3000, "limites": 600}


def gerar(temas, capitais, estados, regioes, cidades, seed=7, quantos=None):
    rng = random.Random(seed)
    g = Gerador(temas, capitais, estados, regioes, cidades, rng)
    convs, vistos = [], set()
    for familia, n in (quantos or QUANTOS).items():
        feitos, tentativas = 0, 0
        while feitos < n and tentativas < n * 5:
            tentativas += 1
            conv = getattr(g, familia)()
            if not conv or len(conv) < 2:
                continue
            chave = tuple(q for q, _ in conv)
            if chave in vistos:
                continue
            vistos.add(chave)
            convs.append([list(t) for t in conv[:12]])
            feitos += 1
    rng.shuffle(convs)
    return convs
