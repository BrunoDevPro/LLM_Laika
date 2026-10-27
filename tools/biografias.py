"""Biografias inventadas para ensinar a Laika a achar, num Contexto, a informação certa sobre uma pessoa.

"Quantos idiomas Fernando Pessoa falava?" com o artigo como Contexto: o modelo respondia "falava quatro idiomas" sem
dizer quais, ou pegava outra frase do trecho. Aqui cada biografia junta vários fatos (onde nasceu, o que estudou,
idiomas, casamento, filhos, prêmios, obras, times, instrumentos) em ordem sorteada, e as perguntas pedem um deles, com
a resposta completa ("X falava quatro idiomas: português, inglês, francês e alemão."). Pessoas vivas ficam no presente
("fala", "mora"), as que já morreram, no passado. Uma parte pergunta algo que o texto não diz (resposta "não sei") e
outra junta duas perguntas em uma.

As pessoas são inventadas de propósito: sem o Contexto, nada disto pode virar "conhecimento" (só ensina a ler).
gerar_pergeresp.py grava data/qa/biografias.txt.
"""

import random

NOMES_M = """João Pedro Lucas Mateus Gabriel Rafael Daniel Bruno Thiago Felipe Gustavo André Ricardo Eduardo Marcelo
Rodrigo Leonardo Vítor Henrique Caio Otávio Antônio Francisco Joaquim Manuel Raul Sérgio Paulo Renato Fábio Hugo
Emanuel Samuel Benedito Augusto Teodoro Álvaro Inácio Mauro Davi Ivo Jorge Luís Nuno Rui Tomás Vicente Heitor Ícaro
Lorenzo Pietro Hans Pierre Kenji Omar Diego Andrés Malik Yuri Sven Arjun""".split()
NOMES_F = """Maria Ana Beatriz Júlia Mariana Larissa Camila Fernanda Letícia Gabriela Helena Alice Laura Sofia Isabela
Clara Luíza Cecília Rosa Teresa Lúcia Joana Marta Vera Sílvia Raquel Débora Patrícia Renata Bianca Carolina Tânia
Olga Irene Glória Aurora Celeste Iracema Jandira Dora Elisa Inês Leonor Matilde Rita Simone Yara Lívia Nina Hanna
Amélie Yuki Fátima Lucía Amara Ingrid Priya Natasha""".split()
SOBRENOMES = """Silva Santos Oliveira Souza Lima Pereira Costa Rodrigues Almeida Nascimento Carvalho Araújo Ribeiro Gomes
Martins Barbosa Rocha Dias Teixeira Moreira Cardoso Correia Mendes Freitas Pinto Campos Vieira Monteiro Moura Nunes
Andrade Batista Cavalcanti Duarte Fonseca Guimarães Lacerda Macedo Queiroz Sampaio Tavares Valente Brandão Coutinho
Esteves Falcão Leme Magalhães Pacheco Siqueira Toledo Vasconcelos Bittencourt Castelo Prado Quintana Sarmento
Ferraz Lobato Peixoto Rezende Viana""".split()
CIDADES = ["Recife", "Salvador", "Fortaleza", "Belém", "Manaus", "Curitiba", "Porto Alegre", "Florianópolis", "Goiânia",
           "Campinas", "Santos", "Niterói", "Ouro Preto", "Juiz de Fora", "Pelotas", "Londrina", "Natal", "Maceió",
           "Aracaju", "Teresina", "São Luís", "Cuiabá", "Campo Grande", "Vitória", "Lisboa", "Porto", "Coimbra", "Braga",
           "Luanda", "Maputo", "Praia", "Buenos Aires", "Montevidéu", "Santiago", "Lima", "Bogotá", "Madri", "Barcelona",
           "Paris", "Lyon", "Roma", "Milão", "Berlim", "Munique", "Viena", "Londres", "Dublin", "Tóquio", "Osaka",
           "Toronto", "Chicago", "Boston"]
IDIOMAS = ["português", "inglês", "francês", "espanhol", "alemão", "italiano", "russo", "japonês", "árabe", "latim",
           "grego", "mandarim", "holandês", "sueco", "polonês", "hebraico", "guarani", "tupi", "catalão", "turco"]
CURSOS = ["medicina", "direito", "engenharia civil", "arquitetura", "música", "física", "química", "biologia",
          "filosofia", "história", "letras", "matemática", "economia", "jornalismo", "artes plásticas", "astronomia",
          "agronomia", "educação física", "psicologia", "geografia", "cinema", "teatro", "computação", "farmácia"]
UNIVERSIDADES = ["na Universidade de São Paulo", "na Universidade Federal do Rio de Janeiro", "na Universidade de Coimbra",
                 "na Universidade de Lisboa", "na Universidade Federal de Minas Gerais", "na Sorbonne, em Paris",
                 "na Universidade de Bolonha", "na Universidade de Buenos Aires", "na Universidade Federal da Bahia",
                 "na Universidade de Brasília", "na Universidade Federal de Pernambuco", "em Oxford, na Inglaterra",
                 "na Universidade Estadual de Campinas", "numa escola técnica de Berlim",
                 "na Universidade Federal do Rio Grande do Sul", "no conservatório de Viena"]
INSTRUMENTOS = ["violão", "piano", "violino", "flauta", "saxofone", "bateria", "acordeão", "cavaquinho", "violoncelo",
                "trompete", "guitarra", "harpa", "clarinete", "pandeiro", "contrabaixo", "órgão"]
CLUBES = ["Atlético Serrano", "Esporte Clube Ribeira", "União Paulistana", "Clube Náutico do Vale", "Real Planalto",
          "Sporting da Lagoa", "Juventus do Norte", "Grêmio Litorâneo", "Estrela do Sul", "Ferroviário Central",
          "América do Cerrado", "Olímpico da Serra", "Bandeirantes FC", "Cruzeiro do Mar", "Vitória das Águas"]
PREMIOS = ["o Prêmio Camões", "o Prêmio Jabuti", "uma medalha de ouro nos Jogos Pan-Americanos", "o Prêmio Nacional de Ciência",
           "dois troféus de melhor atriz", "o Grammy Latino", "a Ordem do Mérito Cultural", "o prêmio de melhor arquiteto do ano",
           "a medalha de ouro na olimpíada de matemática", "o título de cidadão honorário de Lisboa", "o Prêmio Machado de Assis",
           "um troféu de melhor jogador do campeonato", "o prêmio de melhor documentário", "a Medalha Oswaldo Cruz"]
PALAVRAS = ["Mar", "Sertão", "Noite", "Cidade", "Silêncio", "Vento", "Rio", "Pedra", "Jardim", "Viagem", "Memória", "Ponte",
            "Estrela", "Areia", "Chuva", "Montanha", "Janela", "Sombra", "Luz", "Caminho", "Ilha", "Fogo", "Tempo", "Lua"]
ADJETIVOS = ["Azul", "Distante", "Escondido", "Antigo", "Perdido", "Branco", "Eterno", "Calado", "Dourado", "Inquieto"]
NUMEROS = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
NUMEROS_F = ["", "uma", "duas", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]

# (profissão masculina, feminina, área) e o que a pessoa faz de característico.
PROFISSOES = [
    ("escritor", "escritora", "obras"), ("poeta", "poeta", "obras"), ("pintor", "pintora", "quadros"),
    ("músico", "musicista", "musica"), ("cantor", "cantora", "musica"), ("jogador de futebol", "jogadora de futebol", "clubes"),
    ("médico", "médica", "ciencia"), ("engenheiro", "engenheira", "ciencia"), ("físico", "física", "ciencia"),
    ("arquiteto", "arquiteta", "projetos"), ("professor", "professora", "ciencia"), ("diplomata", "diplomata", "idiomas"),
    ("tradutor", "tradutora", "idiomas"), ("jornalista", "jornalista", "obras"), ("cineasta", "cineasta", "filmes"),
    ("ator", "atriz", "filmes"), ("bióloga", "bióloga", "ciencia"), ("compositor", "compositora", "musica"),
    ("nadador", "nadadora", "esporte"), ("astrônomo", "astrônoma", "ciencia"),
]


def lista(itens):
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


MASCULINAS = {"Mar", "Sertão", "Rio", "Jardim", "Silêncio", "Vento", "Caminho", "Fogo", "Tempo"}


def titulo_obra(rng):
    p, a = rng.choice(PALAVRAS), rng.choice(ADJETIVOS)
    m = p in MASCULINAS
    art, de = ("O", "do") if m else ("A", "da")
    adj = a if m or not a.endswith("o") else a[:-1] + "a"
    return rng.choice([f"{art} {p} {adj}", f"Canção {de} {p}", f"{p} de Outono", f"Os Dias {de} {p}",
                       f"Cartas {de} {p}", f"{art} {p} e o Vento"])


def pessoa(rng):
    f = rng.random() < 0.5
    nome = f"{rng.choice(NOMES_F if f else NOMES_M)} {rng.choice(SOBRENOMES)}"
    if rng.random() < 0.4:
        nome += f" {rng.choice(SOBRENOMES)}"
    prof_m, prof_f, area = rng.choice(PROFISSOES)
    viva = rng.random() < 0.45
    nasc = rng.randint(1950, 1998) if viva else rng.randint(1820, 1945)
    morte = None if viva else min(2023, nasc + rng.randint(35, 95))
    p = {"nome": nome, "f": f, "prof": prof_f if f else prof_m, "area": area, "viva": viva, "nasc": nasc,
         "morte": morte, "cidade": rng.choice(CIDADES)}
    p["idiomas"] = ["português"] + rng.sample(IDIOMAS[1:], rng.randint(1, 5 if area == "idiomas" else 3))
    if rng.random() < 0.7:
        p["curso"], p["uni"] = rng.choice(CURSOS), rng.choice(UNIVERSIDADES)
    if rng.random() < 0.6:
        p["conjuge"] = f"{rng.choice(NOMES_M if f else NOMES_F)} {rng.choice(SOBRENOMES)}"
    if rng.random() < 0.6:
        p["filhos"] = rng.randint(1, 6)
    if rng.random() < 0.5:
        p["premios"] = rng.sample(PREMIOS, rng.randint(1, 2))
    if area in ("obras", "filmes", "projetos") or rng.random() < 0.2:
        p["obras"] = list(dict.fromkeys(titulo_obra(rng) for _ in range(rng.randint(2, 4))))
    if area == "musica" or rng.random() < 0.15:
        p["instrumentos"] = rng.sample(INSTRUMENTOS, rng.randint(1, 3))
    if area == "clubes":
        p["clubes"] = rng.sample(CLUBES, rng.randint(2, 4))
    if rng.random() < 0.5:
        p["mora"] = rng.choice([c for c in CIDADES if c != p["cidade"]])
    return p


def frases(p, rng):
    """As frases da biografia, cada uma com a chave do fato que ela traz."""
    n, ela = p["nome"], p["f"]
    pron, art = ("Ela", "a") if ela else ("Ele", "o")
    pres = p["viva"]
    v = (lambda presente, passado: presente if pres else passado)
    datas = f"{p['nasc']}" if pres else f"{p['nasc']} – {p['morte']}"
    s = []
    s.append(("def", f"{n} ({p['cidade']}, {datas}) {v('é', 'foi')} um{'a' if ela else ''} {p['prof']} "
                     f"{rng.choice(['brasileir', 'conhecid', 'premiad', 'respeitad'])}{'a' if ela else 'o'}."))
    s.append(("nasc", f"{pron} nasceu em {p['cidade']}, em {p['nasc']}" + ("." if pres else f", e morreu em {p['morte']}.")))
    k = len(p["idiomas"])
    s.append(("idiomas", rng.choice([
        f"{pron} {v('fala', 'falava')} {NUMEROS[k]} idiomas: {lista(p['idiomas'])}.",
        f"Além do português, {pron.lower()} {v('fala', 'falava')} {lista(p['idiomas'][1:])}.",
        f"{pron} {v('domina', 'dominava')} {NUMEROS_F[k]} línguas: {lista(p['idiomas'])}."])))
    if "curso" in p:
        s.append(("curso", f"{pron} estudou {p['curso']} {p['uni']}."))
    if "conjuge" in p:
        s.append(("conjuge", f"{pron} se casou com {p['conjuge']}" + (
            f", com quem {v('tem', 'teve')} {NUMEROS[p['filhos']]} filho{'s' if p['filhos'] > 1 else ''}."
            if "filhos" in p else ".")))
    elif "filhos" in p:
        s.append(("filhos", f"{pron} {v('tem', 'teve')} {NUMEROS[p['filhos']]} filho{'s' if p['filhos'] > 1 else ''}."))
    if "premios" in p:
        s.append(("premios", f"Ao longo da carreira, {pron.lower()} recebeu {lista(p['premios'])}."))
    if "obras" in p:
        verbo = {"obras": "escreveu", "filmes": "fez os filmes", "projetos": "projetou"}.get(p["area"], "criou")
        s.append(("obras", f"Entre as suas obras, {pron.lower()} {verbo} " + lista([f"\"{o}\"" for o in p["obras"]]) + "."))
    if "instrumentos" in p:
        s.append(("instrumentos", f"{pron} {v('toca', 'tocava')} {lista(p['instrumentos'])}."))
    if "clubes" in p:
        s.append(("clubes", f"{pron} jogou pelo {lista(p['clubes'])}."))
    if "mora" in p:
        s.append(("mora", f"{pron} {v('mora há', 'morou')} muitos anos em {p['mora']}."))
    rng.shuffle(s)
    s.sort(key=lambda x: x[0] != "def")  # a definição sempre primeiro, como na Wikipédia
    return s


def perguntas(p, rng):
    """(chave do fato, pergunta, resposta)."""
    n, ela, pres = p["nome"], p["f"], p["viva"]
    v = (lambda presente, passado: presente if pres else passado)
    k = len(p["idiomas"])
    r = []
    q = rng.choice([f"Quantos idiomas {n} {v('fala', 'falava')}?", f"Quantas línguas {n} {v('fala', 'falava')}?"])
    r.append(("idiomas", q, f"{n} {v('fala', 'falava')} {NUMEROS[k]} idiomas: {lista(p['idiomas'])}." if "idiomas" in q
              else f"{n} {v('fala', 'falava')} {NUMEROS_F[k]} línguas: {lista(p['idiomas'])}."))
    r.append(("idiomas", rng.choice([f"Que idiomas {n} {v('fala', 'falava')}?", f"Quais línguas {n} {v('fala', 'falava')}?",
                                     f"{n} {v('fala', 'falava')} quais idiomas?"]),
              f"{n} {v('fala', 'falava')} {lista(p['idiomas'])}."))
    r.append(("nasc", rng.choice([f"Onde {n} nasceu?", f"Onde nasceu {n}?"]), f"{n} nasceu em {p['cidade']}."))
    r.append(("nasc", rng.choice([f"Quando {n} nasceu?", f"Em que ano {n} nasceu?"]), f"{n} nasceu em {p['nasc']}."))
    if not pres:
        r.append(("nasc", f"Quando {n} morreu?", f"{n} morreu em {p['morte']}."))
    r.append(("def", rng.choice([f"Qual {v('é', 'era')} a profissão de {n}?", f"O que {n} {v('faz', 'fazia')}?",
                                 f"Quem {v('é', 'foi')} {n}?"]),
              f"{n} {v('é', 'foi')} um{'a' if ela else ''} {p['prof']}."))
    if "curso" in p:
        r.append(("curso", rng.choice([f"O que {n} estudou?", f"Onde {n} estudou?", f"{n} fez faculdade de quê?"]),
                  f"{n} estudou {p['curso']} {p['uni']}."))
    if "conjuge" in p:
        r.append(("conjuge", rng.choice([f"Com quem {n} se casou?", f"Quem {v('é', 'foi')} o marido de {n}?" if ela
                                         else f"Quem {v('é', 'foi')} a esposa de {n}?"]),
                  f"{n} se casou com {p['conjuge']}."))
    if "filhos" in p:
        f = p["filhos"]
        r.append(("conjuge" if "conjuge" in p else "filhos", f"Quantos filhos {n} {v('tem', 'teve')}?",
                  f"{n} {v('tem', 'teve')} {NUMEROS[f]} filho{'s' if f > 1 else ''}."))
    if "premios" in p:
        q = rng.choice([f"Que prêmios {n} ganhou?", f"{n} ganhou algum prêmio?", f"Quais prêmios {n} recebeu?"])
        r.append(("premios", q, f"{'Sim. ' if 'algum' in q else ''}{n} recebeu {lista(p['premios'])}."))
    if "obras" in p:
        r.append(("obras", rng.choice([f"Quais são as obras de {n}?", f"O que {n} {'escreveu' if p['area'] == 'obras' else 'fez'}?",
                                       f"Cite obras de {n}."]),
                  f"Entre as obras de {n} estão " + lista([f"\"{o}\"" for o in p["obras"]]) + "."))
    if "instrumentos" in p:
        q = len(p["instrumentos"])
        r.append(("instrumentos", rng.choice([f"Que instrumentos {n} {v('toca', 'tocava')}?",
                                              f"Quantos instrumentos {n} {v('toca', 'tocava')}?"]),
                  f"{n} {v('toca', 'tocava')} {lista(p['instrumentos'])}." if q == 1 else
                  f"{n} {v('toca', 'tocava')} {NUMEROS[q]} instrumentos: {lista(p['instrumentos'])}."))
    if "clubes" in p:
        r.append(("clubes", rng.choice([f"Em que times {n} jogou?", f"Por quais clubes {n} jogou?"]),
                  f"{n} jogou pelo {lista(p['clubes'])}."))
    if "mora" in p:
        r.append(("mora", f"Onde {n} {v('mora', 'morou')}?", f"{n} {v('mora há', 'morou')} muitos anos em {p['mora']}."))
    return r


# Perguntas sobre fatos que o texto pode não trazer (resposta "não sei" quando faltam).
FALTANDO = {
    "curso": "O que {n} estudou?", "conjuge": "Com quem {n} se casou?", "premios": "Que prêmios {n} ganhou?",
    "instrumentos": "Que instrumentos {n} {toca}?", "clubes": "Em que times {n} jogou?", "obras": "Quais são as obras de {n}?",
}
NAO_DIZ = "O trecho que encontrei não fala sobre isso, então não sei responder com certeza."


def exemplos(n_pessoas=1200, seed=7):
    """[(Contexto, pergunta, resposta)]: ~5 perguntas por biografia, 1 com duas perguntas em uma, 1 "não sei" a cada 8."""
    rng = random.Random(seed)
    out = []
    for i in range(n_pessoas):
        p = pessoa(rng)
        contexto = " ".join(f for _, f in frases(p, rng))
        qs = perguntas(p, rng)
        rng.shuffle(qs)
        for _, q, a in qs[:5]:
            out.append((contexto, q, a))
        # Duas perguntas em uma: "Onde X nasceu e quantos idiomas ele falava?" (a 2ª sem o nome no fim: "onde nasceu ele").
        segundas = [x for x in qs[1:] if not x[1].endswith(p["nome"] + "?") and x[0] != qs[0][0]]
        if segundas:
            (_, q1, a1), (_, q2, a2) = qs[0], segundas[0]
            pron = "ela" if p["f"] else "ele"
            q2b = q2.replace(p["nome"], pron)
            q2b = q2b[0].lower() + q2b[1:]
            a2b = (("Ela" if p["f"] else "Ele") + a2[len(p["nome"]):]) if a2.startswith(p["nome"]) else a2
            out.append((contexto, f"{q1[:-1]} e {q2b}", f"{a1} {a2b}"))
        faltam = [c for c in FALTANDO if c not in p]
        if faltam and i % 8 == 0:
            out.append((contexto, FALTANDO[rng.choice(faltam)].format(n=p["nome"], toca="toca" if p["viva"] else "tocava"), NAO_DIZ))
    return out
