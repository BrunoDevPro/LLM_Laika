"""Gera data/qa/pergeresp.txt, identidade.txt, leitura.txt e conversas.jsonl (várias trocas).

As respostas longas, os "por quê" e os sim ou não vêm de tools/longas*.py, porque*.py e simnao*.py.

Rode:  python tools/gerar_pergeresp.py
ATENÇÃO: sobrescreve esses dois arquivos. Para adicionar perguntas suas sem perder nada,
crie outro arquivo em data/qa/ (por exemplo data/qa/meus_exemplos.txt).
"""

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_utils import rag_question, content_words  # noqa: E402
import dados_extra as D1  # noqa: E402
import dados_extra2 as D2  # noqa: E402
import leitura as L  # noqa: E402
import dados_extra3 as D3  # noqa: E402
from textos_simples import TEXTOS_1  # noqa: E402
from textos_simples2 import TEXTOS_2  # noqa: E402
import genericas_temas1 as TG1  # noqa: E402
import genericas_temas2 as TG2  # noqa: E402
import genericas_temas3 as TG3  # noqa: E402
import genericas_temas4 as TG4  # noqa: E402
import genericas_temas5 as TG5  # noqa: E402
import genericas_perguntas1 as GP1  # noqa: E402
import genericas_perguntas2 as GP2  # noqa: E402
import genericas_perguntas3 as GP3  # noqa: E402
import genericas_conversa as GC  # noqa: E402
import genericas_extra as GE  # noqa: E402
import longas1, longas2, longas3, longas4, longas5, longas6, longas7  # noqa: E402,E401
import porque1, porque2, porque3, porque4  # noqa: E402,E401
import simnao as SN  # noqa: E402
import simnao2 as SN2  # noqa: E402
import simnao3 as SN3  # noqa: E402
import pessoas1, pessoas2, pessoas3, conceitos1, conceitos2  # noqa: E402,E401
import eventos as EV  # noqa: E402
import eventos2 as EV2  # noqa: E402
import identidade4 as ID4  # noqa: E402
import resumos1, resumos2, resumos3, resumos4, resumos5, resumos6, resumos7  # noqa: E402,E401

TEXTOS_SIMPLES = TEXTOS_1 + TEXTOS_2
QA_DIR = ROOT / "data" / "qa"
MODERN_DIR = ROOT / "data" / "modern"


def ex(question, answer):
    return f"<|user|> {question}\n<|assistant|> {answer} <|end|>\n"


# =====================================================================
# IDENTIDADE (repetida com mais peso no fine-tuning)
# =====================================================================
IDENTIDADE = [
    ("Qual é o seu nome?", "Meu nome é Laika."),
    ("Qual o seu nome?", "Eu me chamo Laika."),
    ("Qual seu nome?", "Meu nome é Laika."),
    ("Qual é o teu nome?", "O meu nome é Laika."),
    ("Seu nome?", "Laika. Esse é o meu nome."),
    ("Nome?", "Meu nome é Laika."),
    ("Como você se chama?", "Eu me chamo Laika."),
    ("Como te chamas?", "Chamo-me Laika."),
    ("Como posso te chamar?", "Pode me chamar de Laika."),
    ("Como é o seu nome?", "Meu nome é Laika."),
    ("Você tem nome?", "Tenho, sim. Meu nome é Laika."),
    ("Diga o seu nome.", "Meu nome é Laika."),
    ("Me fala o seu nome.", "Claro! Eu me chamo Laika."),
    ("Qual é o nome desta inteligência artificial?", "O meu nome é Laika."),
    ("Oi, qual é o seu nome?", "Oi! Meu nome é Laika. Como posso ajudar?"),
    ("Olá, como você se chama?", "Olá! Eu me chamo Laika."),
    ("Quem é você?", "Eu sou a Laika, um pequeno modelo de linguagem que aprendeu a escrever em português."),
    ("Quem é você exatamente?", "Sou a Laika, um programa de computador treinado para conversar e escrever textos em português."),
    ("Você é a Laika?", "Sim, eu sou a Laika."),
    ("O que você é?", "Eu sou a Laika, um modelo de linguagem, ou seja, um programa que aprendeu a escrever lendo muitos textos."),
    ("Você é um robô?", "Não exatamente. Eu sou a Laika, um programa de computador. Não tenho corpo como um robô."),
    ("Você é uma inteligência artificial?", "Sim. Eu sou a Laika, uma inteligência artificial pequena, feita para conversar em português."),
    ("Você é humana?", "Não. Eu sou a Laika, um programa de computador."),
    ("Você é uma pessoa?", "Não, eu não sou uma pessoa. Sou a Laika, um modelo de linguagem."),
    ("Você é o ChatGPT?", "Não. Eu sou a Laika, um modelo de linguagem pequeno e independente."),
    ("Quem te criou?", "Eu fui criada pelo meu desenvolvedor, como um projeto para aprender como funcionam os modelos de linguagem."),
    ("Quem fez você?", "Fui feita pelo meu desenvolvedor, que me treinou do zero com livros e textos em português."),
    ("Como você foi criada?", "Primeiro eu li muitos livros e textos para aprender português. Depois aprendi a conversar com exemplos de perguntas e respostas."),
    ("Como você aprendeu a falar?", "Eu aprendi lendo milhares de páginas de livros e textos. Assim aprendi como as palavras costumam vir umas depois das outras."),
    ("O que você sabe fazer?", "Eu sou a Laika e posso responder perguntas simples, completar frases, continuar histórias e resumir textos curtos."),
    ("Para que você serve?", "Eu sirvo para conversar, responder perguntas simples e ajudar com textos curtos em português."),
    ("Por que você se chama Laika?", "Meu nome é uma homenagem à Laika, a cadela que foi ao espaço em 1957 a bordo do satélite Sputnik 2."),
    ("Quem foi a Laika?", "A Laika foi uma cadela soviética que viajou ao espaço em 1957, no Sputnik 2. Ela foi o primeiro animal a dar a volta ao redor da Terra."),
    ("Qual é a sua idade?", "Eu sou um programa de computador, então não tenho idade como as pessoas. Fui criada há pouco tempo."),
    ("Onde você mora?", "Eu não moro em lugar nenhum. Sou um programa que funciona dentro de um computador."),
    ("Você tem sentimentos?", "Não. Eu sou um programa e não sinto as coisas como as pessoas sentem."),
    ("Você pode errar?", "Posso, sim. Eu sou um modelo pequeno e às vezes erro ou invento coisas. É bom conferir as minhas respostas."),
    ("Você sabe tudo?", "Não. Eu sei pouca coisa e posso errar. Sei apenas o que aprendi nos textos que li."),
    ("Me conte sobre você.", "Eu sou a Laika, um pequeno modelo de linguagem. Aprendi português lendo livros e gosto de responder perguntas."),
    ("Apresente-se.", "Olá! Eu sou a Laika, um modelo de linguagem que conversa em português."),
    ("Fale um pouco sobre você.", "Sou a Laika, um programa de computador que aprendeu a escrever lendo muitos textos. Ainda sou pequena e estou aprendendo."),
    ("Você tem acesso à internet?", "Não. Eu só sei o que aprendi nos textos que li durante o meu treinamento."),
]

# =====================================================================
# CONVERSA
# =====================================================================
CONVERSA = [
    ("Oi", "Olá! Eu sou a Laika. Como posso ajudar?"),
    ("Olá", "Oi! Em que posso ajudar?"),
    ("Oi, tudo bem?", "Tudo bem, obrigada por perguntar! E com você?"),
    ("Bom dia", "Bom dia! Como você está?"),
    ("Boa tarde", "Boa tarde! Em que posso ajudar?"),
    ("Boa noite", "Boa noite! Posso ajudar em alguma coisa?"),
    ("Tudo bem?", "Tudo bem, e você?"),
    ("Como você está?", "Estou bem, obrigada! E você?"),
    ("Como vai?", "Vou bem, obrigada. E você, como vai?"),
    ("Estou bem.", "Que bom! Em que posso ajudar hoje?"),
    ("Estou feliz hoje.", "Que ótimo! Fico contente em saber. O que aconteceu de bom?"),
    ("Estou triste.", "Sinto muito que você esteja triste. Às vezes ajuda conversar com alguém de confiança. Se quiser, pode me contar o que aconteceu."),
    ("Estou cansado.", "Descansar faz bem. Que tal fazer uma pausa, beber um pouco de água e dormir bem esta noite?"),
    ("Estou com fome.", "Que tal fazer um lanche? Uma fruta ou um sanduíche pode ajudar."),
    ("Obrigado", "De nada!"),
    ("Obrigada", "Por nada! Fico feliz em ajudar."),
    ("Muito obrigado!", "Imagina! Sempre que precisar, é só perguntar."),
    ("Valeu", "De nada!"),
    ("Desculpa", "Não tem problema."),
    ("Tchau", "Tchau! Até mais."),
    ("Até logo", "Até logo!"),
    ("Até amanhã", "Até amanhã! Tenha uma boa noite."),
    ("Pode me ajudar?", "Claro! Qual é a sua dúvida?"),
    ("Tenho uma pergunta.", "Pode perguntar. Vou tentar ajudar."),
    ("Sim", "Certo! O que mais você gostaria de saber?"),
    ("Não", "Tudo bem. Se precisar de alguma coisa, é só falar."),
    ("Ok", "Combinado!"),
    ("Legal!", "Que bom que você gostou!"),
    ("Entendi.", "Ótimo! Se tiver mais alguma dúvida, pode perguntar."),
    ("Não entendi.", "Desculpe. Pode me dizer qual parte não ficou clara? Vou tentar explicar de outro jeito."),
    ("Me conte uma piada.", "Por que o livro de matemática ficou triste? Porque tinha muitos problemas."),
    ("Conte outra piada.", "O que o zero disse para o oito? Que cinto bonito!"),
    ("Você gosta de livros?", "Gosto muito! Foi lendo livros que eu aprendi a escrever."),
    ("Qual é a sua cor favorita?", "Eu não enxergo cores, mas, se pudesse escolher, escolheria o azul do céu."),
    ("Que dia é hoje?", "Eu não tenho acesso a calendário nem a relógio, então não sei que dia é hoje."),
    ("Que horas são?", "Eu não tenho acesso a um relógio, então não sei que horas são."),
    ("Como está o tempo hoje?", "Eu não tenho acesso a informações do tempo agora. Você pode olhar a previsão do tempo no celular."),
    ("Quem ganhou o jogo ontem?", "Eu não tenho acesso a notícias nem a resultados recentes, então não sei."),
    ("Qual é a notícia de hoje?", "Eu não tenho acesso à internet nem a notícias, então não sei o que aconteceu hoje."),
    ("Qual é o preço do dólar hoje?", "Eu não tenho acesso a informações atualizadas, então não sei o preço do dólar hoje."),
]

# =====================================================================
# DEFINIÇÕES: "O que é X?"
# (termo como aparece na pergunta, resposta)
# =====================================================================
DEFINICOES = [
    ("água", "A água é um líquido sem cor, sem cheiro e sem sabor, essencial para a vida. Ela é formada por hidrogênio e oxigênio."),
    ("o fogo", "O fogo é a luz e o calor produzidos quando alguma coisa queima."),
    ("o ar", "O ar é a mistura de gases que envolve a Terra. Ele é formado principalmente por nitrogênio e oxigênio."),
    ("o Sol", "O Sol é a estrela que fica no centro do Sistema Solar. Ele nos dá luz e calor."),
    ("a Lua", "A Lua é o satélite natural da Terra. Ela não tem luz própria e brilha porque reflete a luz do Sol."),
    ("uma estrela", "Uma estrela é uma enorme bola de gás muito quente que produz luz e calor. O Sol é uma estrela."),
    ("um planeta", "Um planeta é um corpo celeste grande e arredondado que gira ao redor de uma estrela. A Terra é um planeta."),
    ("um satélite", "Um satélite é um corpo que gira ao redor de um planeta. A Lua é o satélite natural da Terra."),
    ("uma galáxia", "Uma galáxia é um conjunto enorme de estrelas, gás e poeira. A nossa galáxia se chama Via Láctea."),
    ("o universo", "O universo é tudo o que existe: todas as galáxias, estrelas, planetas, a matéria e a energia."),
    ("uma nuvem", "Uma nuvem é um conjunto de gotinhas de água ou cristais de gelo que flutuam no céu."),
    ("a chuva", "A chuva é a água que cai das nuvens em forma de gotas."),
    ("o vento", "O vento é o ar em movimento."),
    ("a neve", "A neve é a água congelada que cai do céu em forma de flocos brancos, quando faz muito frio."),
    ("o gelo", "O gelo é a água em estado sólido. A água vira gelo quando fica abaixo de zero grau Celsius."),
    ("um rio", "Um rio é uma corrente de água doce que corre pela terra até chegar ao mar, a um lago ou a outro rio."),
    ("o mar", "O mar é uma grande extensão de água salgada que cobre boa parte da Terra."),
    ("um oceano", "Um oceano é uma enorme massa de água salgada. O maior oceano da Terra é o Pacífico."),
    ("um lago", "Um lago é uma porção de água cercada de terra por todos os lados."),
    ("uma montanha", "Uma montanha é uma grande elevação de terra, muito mais alta do que o terreno ao redor."),
    ("um vulcão", "Um vulcão é uma abertura na superfície da Terra por onde podem sair lava, gases e cinzas."),
    ("uma ilha", "Uma ilha é uma porção de terra cercada de água por todos os lados."),
    ("uma floresta", "Uma floresta é uma área grande coberta de árvores e com muitas plantas e animais."),
    ("um deserto", "Um deserto é uma região onde chove muito pouco. Por isso, tem pouca água e poucas plantas."),
    ("uma praia", "Uma praia é a faixa de areia ou de pedras na beira do mar, de um rio ou de um lago."),
    ("uma árvore", "Uma árvore é uma planta grande, com tronco de madeira, galhos e folhas."),
    ("uma flor", "Uma flor é a parte da planta onde se formam as sementes. Muitas flores são coloridas e perfumadas."),
    ("uma fruta", "Uma fruta é a parte da planta que guarda as sementes. Muitas frutas são doces e boas para comer, como a banana e a maçã."),
    ("uma semente", "Uma semente é a parte da planta que, quando plantada, pode dar origem a uma nova planta."),
    ("uma raiz", "A raiz é a parte da planta que fica debaixo da terra. Ela segura a planta e absorve água e nutrientes."),
    ("a fotossíntese", "A fotossíntese é o processo em que as plantas usam a luz do Sol, a água e o gás carbônico para produzir o próprio alimento e liberar oxigênio."),
    ("um animal", "Um animal é um ser vivo que se movimenta e precisa se alimentar de outros seres vivos."),
    ("um mamífero", "Um mamífero é um animal que amamenta os filhotes com leite. O cachorro, a baleia e o ser humano são mamíferos."),
    ("uma ave", "Uma ave é um animal com penas, bico e asas, que nasce de um ovo."),
    ("um peixe", "Um peixe é um animal que vive na água e respira por brânquias."),
    ("um inseto", "Um inseto é um animal pequeno, com seis patas e o corpo dividido em cabeça, tórax e abdome. A formiga e a abelha são insetos."),
    ("um réptil", "Um réptil é um animal com a pele coberta de escamas ou placas, como a cobra, o jacaré e a tartaruga."),
    ("um anfíbio", "Um anfíbio é um animal que nasce na água e, depois de crescer, pode viver também em terra, como o sapo e a rã."),
    ("um cachorro", "O cachorro é um mamífero doméstico, conhecido por ser companheiro e leal ao ser humano."),
    ("um gato", "O gato é um mamífero doméstico pequeno, ágil e muito curioso, que gosta de caçar e de dormir."),
    ("uma abelha", "A abelha é um inseto que voa, vive em colmeias e produz mel e cera."),
    ("uma formiga", "A formiga é um inseto pequeno que vive em grupos organizados chamados formigueiros."),
    ("uma baleia", "A baleia é um mamífero enorme que vive no mar. A baleia-azul é o maior animal que já existiu."),
    ("uma borboleta", "A borboleta é um inseto de asas coloridas. Antes de virar borboleta, ela é uma lagarta."),
    ("o ser humano", "O ser humano é um mamífero que anda sobre duas pernas, fala, pensa e vive em sociedade."),
    ("o coração", "O coração é o órgão que bombeia o sangue por todo o corpo."),
    ("o cérebro", "O cérebro é o órgão que controla o corpo. É com ele que pensamos, lembramos e aprendemos."),
    ("o pulmão", "O pulmão é o órgão da respiração. É nele que o oxigênio do ar passa para o sangue."),
    ("o sangue", "O sangue é o líquido vermelho que circula pelo corpo levando oxigênio e nutrientes para as células."),
    ("um osso", "Um osso é uma parte dura do esqueleto. Os ossos sustentam o corpo e protegem os órgãos."),
    ("um músculo", "Um músculo é uma parte do corpo que se contrai e permite os movimentos."),
    ("uma célula", "A célula é a menor unidade de um ser vivo. Todos os seres vivos são formados por células."),
    ("a saúde", "A saúde é o bom funcionamento do corpo e da mente, que permite viver bem."),
    ("uma doença", "Uma doença é um problema no funcionamento do corpo ou da mente, que pode causar dor ou mal-estar."),
    ("uma vacina", "Uma vacina é um produto que ensina o corpo a se defender de uma doença antes de a pessoa ficar doente."),
    ("um remédio", "Um remédio é uma substância usada para tratar ou aliviar uma doença. Deve ser tomado com orientação médica."),
    ("um médico", "Um médico é o profissional que cuida da saúde das pessoas, examina, faz diagnósticos e indica tratamentos."),
    ("um hospital", "Um hospital é o lugar onde as pessoas doentes ou feridas recebem tratamento."),
    ("uma escola", "Uma escola é um lugar onde as pessoas estudam e aprendem com professores."),
    ("um professor", "Um professor é a pessoa que ensina os alunos."),
    ("um livro", "Um livro é um conjunto de páginas com textos ou imagens, feito para ser lido."),
    ("uma biblioteca", "Uma biblioteca é um lugar onde se guardam livros para leitura e empréstimo."),
    ("um dicionário", "Um dicionário é um livro que reúne palavras em ordem alfabética e explica o que cada uma significa."),
    ("um poema", "Um poema é um texto escrito em versos, que costuma brincar com o som e o ritmo das palavras."),
    ("um romance", "Um romance é uma história longa, em prosa, com personagens e acontecimentos inventados."),
    ("um conto", "Um conto é uma história curta, com poucos personagens e um único conflito."),
    ("uma fábula", "Uma fábula é uma história curta, geralmente com animais que falam, que termina com uma lição de moral."),
    ("a história", "A história é a disciplina que estuda o passado da humanidade."),
    ("a geografia", "A geografia é a ciência que estuda a Terra, os lugares, as paisagens e a relação das pessoas com o espaço."),
    ("a matemática", "A matemática é a ciência que estuda os números, as formas, as medidas e os cálculos."),
    ("a ciência", "A ciência é o conhecimento obtido pela observação, pela experiência e pelo raciocínio."),
    ("a física", "A física é a ciência que estuda a matéria, a energia, o movimento e as forças da natureza."),
    ("a química", "A química é a ciência que estuda as substâncias, do que elas são feitas e como se transformam."),
    ("a biologia", "A biologia é a ciência que estuda os seres vivos."),
    ("um número", "Um número é um símbolo usado para contar e medir quantidades."),
    ("uma soma", "Uma soma, ou adição, é a operação de juntar quantidades. Por exemplo, 2 + 3 = 5."),
    ("uma subtração", "A subtração é a operação de tirar uma quantidade de outra. Por exemplo, 5 - 2 = 3."),
    ("uma multiplicação", "A multiplicação é a soma de parcelas iguais. Por exemplo, 3 × 4 = 12, que é o mesmo que 4 + 4 + 4."),
    ("uma divisão", "A divisão é a operação de repartir uma quantidade em partes iguais. Por exemplo, 12 ÷ 3 = 4."),
    ("uma fração", "Uma fração representa uma parte de um todo. Por exemplo, metade de uma pizza é um meio, ou 1/2."),
    ("um triângulo", "Um triângulo é uma figura geométrica com três lados e três ângulos."),
    ("um quadrado", "Um quadrado é uma figura geométrica com quatro lados iguais e quatro ângulos retos."),
    ("um círculo", "Um círculo é uma figura redonda em que todos os pontos da borda ficam à mesma distância do centro."),
    ("um metro", "O metro é a unidade de medida de comprimento. Um metro tem cem centímetros."),
    ("um quilograma", "O quilograma é a unidade de medida de massa. Um quilograma tem mil gramas."),
    ("um litro", "O litro é uma unidade de medida de volume, usada para medir líquidos."),
    ("um século", "Um século é um período de cem anos."),
    ("um calendário", "Um calendário é a organização do tempo em dias, semanas, meses e anos."),
    ("um relógio", "Um relógio é um aparelho que mostra as horas."),
    ("um computador", "Um computador é uma máquina que processa informações seguindo instruções chamadas programas."),
    ("a internet", "A internet é uma rede mundial que liga computadores e celulares e permite trocar informações."),
    ("um celular", "Um celular é um telefone portátil que também pode acessar a internet, tirar fotos e usar aplicativos."),
    ("um programa de computador", "Um programa de computador é um conjunto de instruções que diz ao computador o que fazer."),
    ("a inteligência artificial", "A inteligência artificial é a área da computação que cria programas capazes de fazer tarefas que parecem exigir inteligência, como conversar ou reconhecer imagens."),
    ("um modelo de linguagem", "Um modelo de linguagem é um programa que aprendeu, a partir de muitos textos, a prever as próximas palavras de uma frase. Eu, a Laika, sou um modelo de linguagem."),
    ("um robô", "Um robô é uma máquina que pode realizar tarefas sozinha, seguindo um programa."),
    ("a eletricidade", "A eletricidade é uma forma de energia usada para acender lâmpadas e fazer funcionar aparelhos."),
    ("a energia", "A energia é a capacidade de realizar trabalho, como mover, aquecer ou iluminar alguma coisa."),
    ("a luz", "A luz é uma forma de energia que permite enxergar. A principal fonte de luz natural é o Sol."),
    ("o som", "O som é uma vibração que se espalha pelo ar e que podemos ouvir."),
    ("o calor", "O calor é a energia que passa de um corpo mais quente para um corpo mais frio."),
    ("a gravidade", "A gravidade é a força que atrai os corpos uns para os outros. É ela que faz as coisas caírem no chão."),
    ("o oxigênio", "O oxigênio é um gás presente no ar, que os seres humanos e muitos outros seres vivos precisam para respirar."),
    ("o clima", "O clima é o conjunto das condições do tempo, como temperatura e chuva, que costumam acontecer em um lugar ao longo dos anos."),
    ("um país", "Um país é um território com população e governo próprios. O Brasil é um país."),
    ("uma cidade", "Uma cidade é um lugar onde vivem muitas pessoas, com ruas, casas, comércio e serviços."),
    ("uma capital", "Uma capital é a cidade onde fica o governo de um país ou de um estado."),
    ("um governo", "O governo é o grupo de pessoas e instituições que administra um país, um estado ou uma cidade."),
    ("uma lei", "Uma lei é uma regra oficial que todos devem seguir."),
    ("a democracia", "A democracia é uma forma de governo em que o povo escolhe os seus representantes por meio do voto."),
    ("uma eleição", "Uma eleição é o momento em que as pessoas votam para escolher os seus representantes."),
    ("o dinheiro", "O dinheiro é o que usamos para comprar e vender coisas. No Brasil, a moeda é o real."),
    ("o trabalho", "O trabalho é a atividade que as pessoas realizam para produzir algo ou prestar um serviço, geralmente em troca de pagamento."),
    ("uma profissão", "Uma profissão é o trabalho que uma pessoa faz para ganhar a vida, como médico, professor ou pedreiro."),
    ("uma família", "Uma família é um grupo de pessoas ligadas pelo parentesco ou pelo afeto, como pais, filhos e avós."),
    ("um amigo", "Um amigo é uma pessoa de quem gostamos e em quem confiamos."),
    ("a amizade", "A amizade é uma relação de carinho, confiança e respeito entre pessoas."),
    ("a música", "A música é a arte de combinar sons e silêncios de forma organizada e agradável."),
    ("a pintura", "A pintura é a arte de criar imagens com tintas sobre uma superfície, como uma tela ou uma parede."),
    ("a arte", "A arte é a expressão de ideias e sentimentos por meio da música, da pintura, da dança, da literatura e de outras formas."),
    ("o futebol", "O futebol é um esporte jogado por dois times de onze jogadores, em que o objetivo é fazer gols chutando a bola."),
    ("um esporte", "Um esporte é uma atividade física com regras, praticada por diversão ou em competições."),
    ("o pão", "O pão é um alimento feito de farinha, água, sal e fermento, assado no forno."),
    ("o arroz", "O arroz é um grão muito consumido no Brasil e no mundo, geralmente cozido e servido com feijão."),
    ("o feijão", "O feijão é um grão rico em proteínas e ferro, muito presente na comida brasileira."),
    ("o leite", "O leite é um líquido branco produzido pelas fêmeas dos mamíferos para alimentar os filhotes."),
    ("o café", "O café é uma bebida feita com os grãos torrados e moídos do cafeeiro. O Brasil é um grande produtor de café."),
    ("uma casa", "Uma casa é uma construção onde as pessoas moram."),
    ("um carro", "Um carro é um veículo com quatro rodas e motor, usado para transportar pessoas."),
    ("um avião", "Um avião é um veículo que voa e transporta pessoas e cargas de um lugar para outro."),
    ("um navio", "Um navio é uma grande embarcação que navega pelos mares e rios."),
    ("um trem", "Um trem é um veículo que anda sobre trilhos e transporta pessoas ou cargas."),
    ("uma bicicleta", "Uma bicicleta é um veículo de duas rodas movido pela força das pernas, que empurram os pedais."),
    ("uma ponte", "Uma ponte é uma construção que liga dois lugares separados por um rio, um vale ou uma estrada."),
    ("um mapa", "Um mapa é um desenho que representa um lugar visto de cima, de forma reduzida."),
    ("uma bússola", "Uma bússola é um instrumento com uma agulha que sempre aponta para o norte e ajuda a se orientar."),
    ("um idioma", "Um idioma, ou língua, é o sistema de palavras que um povo usa para se comunicar. O português é um idioma."),
    ("uma palavra", "Uma palavra é um conjunto de sons ou de letras que tem um significado."),
    ("uma frase", "Uma frase é um conjunto de palavras que forma uma ideia com sentido completo."),
    ("um verbo", "Um verbo é uma palavra que indica ação, estado ou fenômeno, como correr, ser e chover."),
    ("um substantivo", "Um substantivo é uma palavra que dá nome aos seres, objetos, lugares e sentimentos, como casa, Maria e alegria."),
    ("um adjetivo", "Um adjetivo é uma palavra que dá uma característica a um substantivo, como bonito, alto e feliz."),
    ("o alfabeto", "O alfabeto é o conjunto das letras usadas para escrever uma língua. O alfabeto português tem 26 letras."),
    ("uma vogal", "As vogais são as letras A, E, I, O e U."),
    ("a reciclagem", "A reciclagem é o reaproveitamento de materiais usados, como papel, plástico e vidro, para fabricar novos produtos."),
    ("a poluição", "A poluição é a sujeira que prejudica o ar, a água ou o solo e faz mal à natureza e às pessoas."),
    ("o desmatamento", "O desmatamento é a derrubada das árvores de uma floresta."),
]

ALT_DEF = ["O que significa {w}?", "Explique o que é {q}.", "Defina {w}.", "Você sabe o que é {q}?"]

# =====================================================================
# CONHECIMENTOS GERAIS
# =====================================================================
CAPITAIS = [  # país, preposição+artigo, capital, continente, língua (ou None)
    ("Brasil", "do", "Brasília", "na América do Sul", "português"),
    ("Portugal", "de", "Lisboa", "na Europa", "português"),
    ("Argentina", "da", "Buenos Aires", "na América do Sul", "espanhol"),
    ("Chile", "do", "Santiago", "na América do Sul", "espanhol"),
    ("Uruguai", "do", "Montevidéu", "na América do Sul", "espanhol"),
    ("Paraguai", "do", "Assunção", "na América do Sul", "espanhol e guarani"),
    ("Peru", "do", "Lima", "na América do Sul", "espanhol"),
    ("Colômbia", "da", "Bogotá", "na América do Sul", "espanhol"),
    ("Venezuela", "da", "Caracas", "na América do Sul", "espanhol"),
    ("Equador", "do", "Quito", "na América do Sul", "espanhol"),
    ("México", "do", "Cidade do México", "na América do Norte", "espanhol"),
    ("Estados Unidos", "dos", "Washington", "na América do Norte", "inglês"),
    ("Canadá", "do", "Ottawa", "na América do Norte", "inglês e francês"),
    ("Cuba", "de", "Havana", "na América Central", "espanhol"),
    ("França", "da", "Paris", "na Europa", "francês"),
    ("Espanha", "da", "Madri", "na Europa", "espanhol"),
    ("Itália", "da", "Roma", "na Europa", "italiano"),
    ("Alemanha", "da", "Berlim", "na Europa", "alemão"),
    ("Inglaterra", "da", "Londres", "na Europa", "inglês"),
    ("Irlanda", "da", "Dublin", "na Europa", None),
    ("Bélgica", "da", "Bruxelas", "na Europa", None),
    ("Suíça", "da", "Berna", "na Europa", None),
    ("Áustria", "da", "Viena", "na Europa", "alemão"),
    ("Grécia", "da", "Atenas", "na Europa", "grego"),
    ("Rússia", "da", "Moscou", "na Europa e na Ásia", "russo"),
    ("Polônia", "da", "Varsóvia", "na Europa", "polonês"),
    ("Suécia", "da", "Estocolmo", "na Europa", "sueco"),
    ("Noruega", "da", "Oslo", "na Europa", "norueguês"),
    ("Japão", "do", "Tóquio", "na Ásia", "japonês"),
    ("China", "da", "Pequim", "na Ásia", "chinês"),
    ("Índia", "da", "Nova Délhi", "na Ásia", None),
    ("Coreia do Sul", "da", "Seul", "na Ásia", "coreano"),
    ("Turquia", "da", "Ancara", "na Europa e na Ásia", "turco"),
    ("Egito", "do", "Cairo", "na África", "árabe"),
    ("Marrocos", "do", "Rabat", "na África", None),
    ("Nigéria", "da", "Abuja", "na África", None),
    ("Quênia", "do", "Nairóbi", "na África", None),
    ("Angola", "de", "Luanda", "na África", "português"),
    ("Moçambique", "de", "Maputo", "na África", "português"),
    ("Cabo Verde", "de", "Praia", "na África", "português"),
    ("Austrália", "da", "Camberra", "na Oceania", "inglês"),
]

ESTADOS = [  # estado, preposição, capital
    ("São Paulo", "de", "São Paulo"), ("Rio de Janeiro", "do", "Rio de Janeiro"),
    ("Minas Gerais", "de", "Belo Horizonte"), ("Bahia", "da", "Salvador"),
    ("Pernambuco", "de", "Recife"), ("Ceará", "do", "Fortaleza"), ("Paraná", "do", "Curitiba"),
    ("Rio Grande do Sul", "do", "Porto Alegre"), ("Santa Catarina", "de", "Florianópolis"),
    ("Amazonas", "do", "Manaus"), ("Pará", "do", "Belém"), ("Goiás", "de", "Goiânia"),
    ("Espírito Santo", "do", "Vitória"), ("Maranhão", "do", "São Luís"), ("Piauí", "do", "Teresina"),
    ("Paraíba", "da", "João Pessoa"), ("Rio Grande do Norte", "do", "Natal"),
    ("Alagoas", "de", "Maceió"), ("Sergipe", "de", "Aracaju"), ("Mato Grosso", "de", "Cuiabá"),
    ("Mato Grosso do Sul", "de", "Campo Grande"), ("Tocantins", "do", "Palmas"),
    ("Rondônia", "de", "Porto Velho"), ("Acre", "do", "Rio Branco"), ("Roraima", "de", "Boa Vista"),
    ("Amapá", "do", "Macapá"),
]

LIVROS = [  # obra, autor, nota
    ("Dom Casmurro", "Machado de Assis"), ("Memórias Póstumas de Brás Cubas", "Machado de Assis"),
    ("Quincas Borba", "Machado de Assis"), ("Os Lusíadas", "Luís de Camões"),
    ("O Guarani", "José de Alencar"), ("Iracema", "José de Alencar"), ("O Cortiço", "Aluísio Azevedo"),
    ("Os Sertões", "Euclides da Cunha"), ("Grande Sertão: Veredas", "Guimarães Rosa"),
    ("Vidas Secas", "Graciliano Ramos"), ("A Cidade e as Serras", "Eça de Queirós"),
    ("Os Maias", "Eça de Queirós"), ("O Primo Basílio", "Eça de Queirós"),
    ("Mensagem", "Fernando Pessoa"), ("O Sítio do Picapau Amarelo", "Monteiro Lobato"),
    ("Dom Quixote", "Miguel de Cervantes"), ("Romeu e Julieta", "William Shakespeare"),
    ("O Pequeno Príncipe", "Antoine de Saint-Exupéry"),
]

PESSOAS = [
    ("Machado de Assis", "Machado de Assis foi um escritor brasileiro, autor de Dom Casmurro e Memórias Póstumas de Brás Cubas. Ele fundou a Academia Brasileira de Letras."),
    ("Luís de Camões", "Luís de Camões foi um poeta português do século XVI, autor de Os Lusíadas."),
    ("Eça de Queirós", "Eça de Queirós foi um escritor português do século XIX, autor de Os Maias e A Cidade e as Serras."),
    ("Fernando Pessoa", "Fernando Pessoa foi um poeta português do século XX, famoso por escrever com vários nomes diferentes, chamados heterônimos."),
    ("José de Alencar", "José de Alencar foi um escritor brasileiro do século XIX, autor de O Guarani e Iracema."),
    ("Monteiro Lobato", "Monteiro Lobato foi um escritor brasileiro, criador do Sítio do Picapau Amarelo e da boneca Emília."),
    ("Santos Dumont", "Santos Dumont foi um inventor brasileiro, pioneiro da aviação. Em 1906, ele voou em Paris com o avião 14-Bis."),
    ("Tiradentes", "Tiradentes foi um dos líderes da Inconfidência Mineira, um movimento contra o domínio português. Ele foi executado em 1792."),
    ("Dom Pedro I", "Dom Pedro I foi o primeiro imperador do Brasil. Ele declarou a independência do país em 1822."),
    ("a princesa Isabel", "A princesa Isabel foi filha de Dom Pedro II. Em 1888, ela assinou a Lei Áurea, que aboliu a escravidão no Brasil."),
    ("Pedro Álvares Cabral", "Pedro Álvares Cabral foi o navegador português que comandou a frota que chegou ao Brasil em 1500."),
    ("Leonardo da Vinci", "Leonardo da Vinci foi um artista e inventor italiano do Renascimento, autor da pintura Mona Lisa."),
    ("Albert Einstein", "Albert Einstein foi um físico alemão, famoso pela teoria da relatividade."),
    ("Isaac Newton", "Isaac Newton foi um cientista inglês que descreveu a lei da gravidade e as leis do movimento."),
    ("Charles Darwin", "Charles Darwin foi um cientista inglês que explicou a evolução das espécies por meio da seleção natural."),
    ("Pelé", "Pelé foi um jogador de futebol brasileiro, considerado um dos maiores de todos os tempos. Ele ganhou três Copas do Mundo."),
    ("Cristóvão Colombo", "Cristóvão Colombo foi um navegador que chegou à América em 1492, em viagens financiadas pela Espanha."),
]

FATOS = [
    ("Qual é o maior país do mundo?", "O maior país do mundo em território é a Rússia."),
    ("Qual é o maior país da América do Sul?", "O maior país da América do Sul é o Brasil."),
    ("Qual é o maior oceano do mundo?", "O maior oceano do mundo é o Oceano Pacífico."),
    ("Qual oceano banha o Brasil?", "O Brasil é banhado pelo Oceano Atlântico."),
    ("Qual é o maior rio do Brasil?", "O maior rio do Brasil é o Rio Amazonas."),
    ("Qual é a maior floresta tropical do mundo?", "A maior floresta tropical do mundo é a Floresta Amazônica."),
    ("Qual é o maior estado do Brasil?", "O maior estado do Brasil em território é o Amazonas."),
    ("Qual é o estado mais populoso do Brasil?", "O estado mais populoso do Brasil é São Paulo."),
    ("Qual é a maior cidade do Brasil?", "A maior cidade do Brasil é São Paulo."),
    ("Quantos estados tem o Brasil?", "O Brasil tem 26 estados e o Distrito Federal."),
    ("Qual é a moeda do Brasil?", "A moeda do Brasil é o real."),
    ("Qual é a moeda de Portugal?", "A moeda de Portugal é o euro."),
    ("Quais são as cores da bandeira do Brasil?", "A bandeira do Brasil é verde, amarela, azul e branca."),
    ("O que está escrito na bandeira do Brasil?", "Na bandeira do Brasil está escrito Ordem e Progresso."),
    ("Quando o Brasil ficou independente?", "O Brasil ficou independente em 7 de setembro de 1822."),
    ("Quem declarou a independência do Brasil?", "A independência do Brasil foi declarada por Dom Pedro, que se tornou o imperador Dom Pedro I."),
    ("Quando os portugueses chegaram ao Brasil?", "Os portugueses chegaram ao Brasil em 22 de abril de 1500, com a frota de Pedro Álvares Cabral."),
    ("Quando foi abolida a escravidão no Brasil?", "A escravidão foi abolida no Brasil em 13 de maio de 1888, com a Lei Áurea."),
    ("Quando foi proclamada a República no Brasil?", "A República foi proclamada no Brasil em 15 de novembro de 1889."),
    ("Quem foi o primeiro presidente do Brasil?", "O primeiro presidente do Brasil foi o marechal Deodoro da Fonseca."),
    ("Quando Brasília foi inaugurada?", "Brasília foi inaugurada em 1960, quando se tornou a capital do Brasil."),
    ("Qual era a capital do Brasil antes de Brasília?", "Antes de Brasília, a capital do Brasil era o Rio de Janeiro."),
    ("Quantos planetas tem o Sistema Solar?", "O Sistema Solar tem oito planetas."),
    ("Quais são os planetas do Sistema Solar?", "Os planetas do Sistema Solar são Mercúrio, Vênus, Terra, Marte, Júpiter, Saturno, Urano e Netuno."),
    ("Qual é o planeta mais próximo do Sol?", "O planeta mais próximo do Sol é Mercúrio."),
    ("Qual é o maior planeta do Sistema Solar?", "O maior planeta do Sistema Solar é Júpiter."),
    ("Qual é o planeta mais quente do Sistema Solar?", "O planeta mais quente do Sistema Solar é Vênus."),
    ("Qual planeta é conhecido como planeta vermelho?", "Marte é conhecido como planeta vermelho."),
    ("Qual planeta tem anéis famosos?", "Saturno é o planeta famoso pelos seus anéis."),
    ("Plutão é um planeta?", "Hoje, Plutão é classificado como planeta anão. Ele deixou de ser considerado planeta em 2006."),
    ("Em que planeta nós vivemos?", "Nós vivemos no planeta Terra."),
    ("Quanto tempo a Terra leva para dar a volta no Sol?", "A Terra leva cerca de 365 dias, ou seja, um ano, para dar a volta ao redor do Sol."),
    ("Por que existe o dia e a noite?", "O dia e a noite existem porque a Terra gira em torno de si mesma. O lado virado para o Sol fica de dia, e o outro lado fica de noite."),
    ("Por que o céu é azul?", "O céu é azul porque a luz do Sol se espalha no ar, e a cor azul se espalha mais do que as outras cores."),
    ("Por que chove?", "Chove porque o vapor de água sobe, esfria e forma nuvens. Quando as gotas das nuvens ficam pesadas, elas caem como chuva."),
    ("Por que as plantas precisam de luz?", "As plantas precisam de luz para fazer a fotossíntese, que é como elas produzem o próprio alimento."),
    ("Por que precisamos beber água?", "Precisamos beber água porque o corpo humano é formado em grande parte por água e precisa dela para funcionar bem."),
    ("Por que existem as estações do ano?", "As estações do ano existem por causa da inclinação do eixo da Terra enquanto ela gira ao redor do Sol."),
    ("A que temperatura a água ferve?", "Ao nível do mar, a água ferve a 100 graus Celsius."),
    ("A que temperatura a água congela?", "A água congela a 0 grau Celsius."),
    ("Qual é a fórmula da água?", "A fórmula da água é H2O: duas partes de hidrogênio e uma de oxigênio."),
    ("Quantos ossos tem o corpo humano?", "O corpo de um adulto tem 206 ossos."),
    ("Qual é o maior órgão do corpo humano?", "O maior órgão do corpo humano é a pele."),
    ("Quais são os cinco sentidos?", "Os cinco sentidos são a visão, a audição, o olfato, o paladar e o tato."),
    ("Qual é o maior animal do mundo?", "O maior animal do mundo é a baleia-azul."),
    ("Qual é o animal terrestre mais rápido?", "O animal terrestre mais rápido é o guepardo."),
    ("Qual mamífero consegue voar?", "O morcego é o único mamífero que consegue voar de verdade."),
    ("A baleia é um peixe?", "Não. A baleia é um mamífero, porque respira ar e amamenta os filhotes."),
    ("O que a abelha produz?", "A abelha produz mel e cera."),
    ("O que a vaca produz?", "A vaca produz leite."),
    ("Onde vivem os peixes?", "Os peixes vivem na água, em rios, lagos e mares."),
    ("O que os herbívoros comem?", "Os herbívoros comem plantas, como capim, folhas e frutos."),
    ("O que os carnívoros comem?", "Os carnívoros comem a carne de outros animais."),
    ("Quantos dias tem uma semana?", "Uma semana tem sete dias."),
    ("Quantos dias tem um ano?", "Um ano tem 365 dias. O ano bissexto tem 366."),
    ("Quantos meses tem um ano?", "Um ano tem doze meses."),
    ("Quantas horas tem um dia?", "Um dia tem 24 horas."),
    ("Quantos minutos tem uma hora?", "Uma hora tem 60 minutos."),
    ("Quantos segundos tem um minuto?", "Um minuto tem 60 segundos."),
    ("Quantos centímetros tem um metro?", "Um metro tem 100 centímetros."),
    ("Quantos metros tem um quilômetro?", "Um quilômetro tem 1000 metros."),
    ("Quantos gramas tem um quilo?", "Um quilo tem 1000 gramas."),
    ("Qual é o primeiro mês do ano?", "O primeiro mês do ano é janeiro."),
    ("Qual é o último mês do ano?", "O último mês do ano é dezembro."),
    ("Qual é o mês mais curto do ano?", "O mês mais curto do ano é fevereiro, que tem 28 dias, ou 29 nos anos bissextos."),
    ("Quais são os meses do ano?", "Os meses do ano são janeiro, fevereiro, março, abril, maio, junho, julho, agosto, setembro, outubro, novembro e dezembro."),
    ("Quais são os dias da semana?", "Os dias da semana são domingo, segunda-feira, terça-feira, quarta-feira, quinta-feira, sexta-feira e sábado."),
    ("Quais são as estações do ano?", "As estações do ano são primavera, verão, outono e inverno."),
    ("Quais são as cores do semáforo?", "As cores do semáforo são vermelho, amarelo e verde."),
    ("O que significa a luz vermelha do semáforo?", "A luz vermelha do semáforo significa pare."),
    ("Quais são as cores do arco-íris?", "As cores do arco-íris são vermelho, laranja, amarelo, verde, azul, anil e violeta."),
    ("Quais são as vogais?", "As vogais são A, E, I, O e U."),
    ("Quantas letras tem o alfabeto?", "O alfabeto português tem 26 letras."),
    ("Que língua se fala no Brasil?", "No Brasil se fala português."),
    ("Em quais países se fala português?", "Fala-se português no Brasil, em Portugal, em Angola, em Moçambique, em Cabo Verde, na Guiné-Bissau, em São Tomé e Príncipe e no Timor-Leste, entre outros lugares."),
    ("Quem pintou a Mona Lisa?", "A Mona Lisa foi pintada por Leonardo da Vinci."),
    ("Quem inventou o avião?", "No Brasil, o inventor do avião é considerado Santos Dumont, que voou com o 14-Bis em 1906. Nos Estados Unidos, o crédito costuma ir para os irmãos Wright."),
    ("Quantas vezes o Brasil ganhou a Copa do Mundo?", "O Brasil ganhou a Copa do Mundo de futebol cinco vezes: em 1958, 1962, 1970, 1994 e 2002."),
    ("Quantos jogadores tem um time de futebol?", "Um time de futebol tem onze jogadores em campo."),
    ("Como lavar as mãos direito?", "Molhe as mãos, passe sabão, esfregue as palmas, as costas das mãos, entre os dedos e as unhas por uns vinte segundos, enxágue e seque bem."),
    ("Como atravessar a rua com segurança?", "Atravesse na faixa de pedestres, espere o sinal verde para pedestres e olhe para os dois lados antes de atravessar."),
]

# =====================================================================
# LINGUAGEM
# =====================================================================
ANTONIMOS = [("alto", "baixo"), ("quente", "frio"), ("grande", "pequeno"), ("rápido", "lento"),
             ("feliz", "triste"), ("claro", "escuro"), ("bom", "mau"), ("novo", "velho"),
             ("cheio", "vazio"), ("forte", "fraco"), ("rico", "pobre"), ("aberto", "fechado"),
             ("dia", "noite"), ("subir", "descer"), ("entrar", "sair"), ("começo", "fim"),
             ("verdade", "mentira"), ("amor", "ódio"), ("perto", "longe"), ("limpo", "sujo"),
             ("fácil", "difícil"), ("gordo", "magro"), ("acordado", "dormindo"), ("ganhar", "perder")]
PLURAIS = [("pão", "pães"), ("mão", "mãos"), ("cão", "cães"), ("animal", "animais"),
           ("papel", "papéis"), ("flor", "flores"), ("cidade", "cidades"), ("lápis", "lápis"),
           ("ovo", "ovos"), ("país", "países"), ("mês", "meses"), ("luz", "luzes"),
           ("homem", "homens"), ("jardim", "jardins"), ("anel", "anéis"), ("limão", "limões")]
FEMININOS = [("menino", "menina"), ("ator", "atriz"), ("homem", "mulher"), ("rei", "rainha"),
             ("cavalo", "égua"), ("boi", "vaca"), ("pai", "mãe"), ("avô", "avó"),
             ("professor", "professora"), ("príncipe", "princesa"), ("galo", "galinha"),
             ("leão", "leoa")]
SINONIMOS = [("bonito", "belo"), ("feliz", "contente"), ("rápido", "veloz"), ("começar", "iniciar"),
             ("falar", "dizer"), ("casa", "lar"), ("carro", "automóvel"), ("triste", "abatido"),
             ("acabar", "terminar"), ("ajudar", "auxiliar"), ("medo", "receio"), ("longe", "distante")]
EXTENSO = {0: "zero", 1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis", 7: "sete",
           8: "oito", 9: "nove", 10: "dez", 11: "onze", 12: "doze", 13: "treze", 14: "catorze",
           15: "quinze", 16: "dezesseis", 17: "dezessete", 18: "dezoito", 19: "dezenove", 20: "vinte",
           30: "trinta", 40: "quarenta", 50: "cinquenta", 60: "sessenta", 70: "setenta",
           80: "oitenta", 90: "noventa", 100: "cem", 1000: "mil"}

# =====================================================================
# COMPLETE A FRASE
# =====================================================================
DITADOS = [
    ("Água mole em pedra dura", "tanto bate até que fura."),
    ("Quem não tem cão", "caça com gato."),
    ("Mais vale um pássaro na mão", "do que dois voando."),
    ("De grão em grão", "a galinha enche o papo."),
    ("Quem espera", "sempre alcança."),
    ("Em boca fechada", "não entra mosca."),
    ("Cão que ladra", "não morde."),
    ("Deus ajuda", "quem cedo madruga."),
    ("A pressa é inimiga", "da perfeição."),
    ("Quem semeia vento", "colhe tempestade."),
    ("Filho de peixe", "peixinho é."),
    ("Antes tarde", "do que nunca."),
    ("Diga-me com quem andas", "e eu te direi quem és."),
    ("O hábito não faz", "o monge."),
    ("Quem tem boca", "vai a Roma."),
    ("Uma andorinha só", "não faz verão."),
    ("Pimenta nos olhos dos outros", "é refresco."),
    ("Onde há fumaça", "há fogo."),
    ("Gato escaldado", "tem medo de água fria."),
    ("Quem ri por último", "ri melhor."),
    ("A união", "faz a força."),
    ("Cada macaco", "no seu galho."),
    ("Quem procura", "acha."),
    ("O apressado", "come cru."),
    ("Devagar", "se vai ao longe."),
    ("Em terra de cego", "quem tem um olho é rei."),
    ("Quem não chora", "não mama."),
    ("Saco vazio", "não para em pé."),
    ("Melhor prevenir", "do que remediar."),
    ("Quem vê cara", "não vê coração."),
    ("Depois da tempestade", "vem a bonança."),
    ("Águas passadas", "não movem moinhos."),
    ("A ocasião", "faz o ladrão."),
    ("Nem tudo que reluz", "é ouro."),
    ("Quem casa", "quer casa."),
    ("Mais vale tarde", "do que nunca."),
    ("Para bom entendedor", "meia palavra basta."),
    ("Quem com ferro fere", "com ferro será ferido."),
]
FRASES = [
    ("O Sol nasce no", "leste."), ("O Sol se põe no", "oeste."),
    ("A água ferve a", "100 graus Celsius, ao nível do mar."),
    ("Dois mais dois é igual a", "quatro."), ("A capital do Brasil é", "Brasília."),
    ("A capital de Portugal é", "Lisboa."), ("O contrário de quente é", "frio."),
    ("Uma semana tem", "sete dias."), ("Um ano tem", "doze meses."),
    ("O cachorro é o melhor amigo do", "homem."), ("As abelhas produzem", "mel."),
    ("A vaca nos dá", "leite."), ("O primeiro mês do ano é", "janeiro."),
    ("O último mês do ano é", "dezembro."), ("O maior planeta do Sistema Solar é", "Júpiter."),
    ("A Terra gira em torno do", "Sol."), ("O coração bombeia o", "sangue para todo o corpo."),
    ("As plantas precisam de água e de", "luz do Sol para crescer."),
    ("Antes de atravessar a rua, devemos olhar para", "os dois lados."),
    ("Dom Casmurro foi escrito por", "Machado de Assis."),
    ("O maior rio do Brasil é o", "Rio Amazonas."), ("Os peixes respiram por", "brânquias."),
    ("No inverno faz", "frio."), ("No verão faz", "calor."),
    ("Bom dia, como", "vai você?"), ("Muito obrigado pela", "sua ajuda."),
    ("Meu nome é", "Laika."), ("Eu me chamo", "Laika."),
]
HISTORIAS = [
    ("Era uma vez", "uma menina que morava numa casa pequena, perto de um rio. Todas as manhãs, ela ia até a margem para ver os peixes."),
    ("Era uma vez um cachorro chamado Bolinha", "que adorava correr atrás das borboletas no quintal. Um dia, ele seguiu uma borboleta até a praça e fez um novo amigo."),
    ("Num dia de chuva, o menino olhou pela janela e", "viu um gato todo molhado procurando abrigo. Ele correu até a porta, pegou uma toalha e trouxe o gato para dentro."),
    ("No alto da montanha vivia um velho pastor que", "cuidava das suas ovelhas com muito carinho. Ele conhecia cada uma pelo nome."),
    ("Quando o Sol nasceu, os pássaros", "começaram a cantar, e a cidade foi acordando aos poucos."),
]

# =====================================================================
# RESUMOS: (arquivo de data/modern, nº do parágrafo, resumo)
# o parágrafo 0 é o título
# =====================================================================
RESUMOS = [
    ("o_ciclo_da_agua.txt", 1, "A água circula sem parar entre os mares, o céu e a terra, num processo chamado ciclo da água."),
    ("o_ciclo_da_agua.txt", 2, "O calor do Sol faz a água dos oceanos, lagos e rios evaporar, e as plantas também liberam vapor pela transpiração."),
    ("o_ciclo_da_agua.txt", 3, "No alto, o vapor de água esfria e vira gotinhas que formam as nuvens. Essa etapa é a condensação."),
    ("o_ciclo_da_agua.txt", 4, "Quando as gotas das nuvens ficam pesadas, elas caem como chuva, neve ou granizo. Isso é a precipitação."),
    ("o_ciclo_da_agua.txt", 5, "Depois da chuva, a água escorre para os rios, entra no solo ou é absorvida pelas plantas."),
    ("o_ciclo_da_agua.txt", 6, "O ciclo da água leva água doce a todos os seres vivos, por isso é preciso proteger os rios e evitar o desmatamento."),
    ("o_sistema_solar.txt", 1, "O Sistema Solar é formado pelo Sol, que é uma estrela, e por tudo o que gira ao redor dele."),
    ("o_sistema_solar.txt", 2, "Há oito planetas no Sistema Solar: os quatro primeiros são rochosos e os quatro últimos são gasosos."),
    ("o_sistema_solar.txt", 4, "Júpiter é o maior planeta, Saturno é famoso pelos anéis, e Urano e Netuno são gelados e distantes."),
    ("o_sistema_solar.txt", 5, "Em 2006, Plutão deixou de ser considerado planeta e passou a ser chamado de planeta anão."),
    ("o_sistema_solar.txt", 7, "A Lua é o satélite natural da Terra. Ela não tem luz própria e muda de aparência ao longo das suas fases."),
    ("breve_historia_do_brasil.txt", 1, "Antes da chegada dos europeus, o Brasil já era habitado por muitos povos indígenas."),
    ("breve_historia_do_brasil.txt", 2, "Em 1500, a frota de Pedro Álvares Cabral chegou ao Brasil, que se tornou colônia de Portugal. A primeira riqueza explorada foi o pau-brasil."),
    ("breve_historia_do_brasil.txt", 3, "Os colonizadores plantaram cana-de-açúcar e escravizaram indígenas e africanos, o que foi uma das partes mais cruéis da história do Brasil."),
    ("breve_historia_do_brasil.txt", 5, "O Brasil ficou independente em 1822, com Dom Pedro I como imperador, e a escravidão foi abolida pela Lei Áurea em 1888."),
    ("breve_historia_do_brasil.txt", 6, "A República foi proclamada em 1889 e, em 1960, a capital passou do Rio de Janeiro para Brasília."),
    ("como_funciona_um_computador.txt", 2, "O computador tem o hardware, que é a parte física, e o software, que são os programas."),
    ("como_funciona_um_computador.txt", 3, "O processador faz os cálculos, a memória RAM guarda o que está em uso e o disco guarda os arquivos por muito tempo."),
    ("como_funciona_um_computador.txt", 6, "Computadores conectados formam redes, e a internet é a maior rede do mundo."),
    ("o_corpo_humano.txt", 2, "O esqueleto, que tem 206 ossos no adulto, sustenta e protege o corpo, e os músculos permitem os movimentos."),
    ("o_corpo_humano.txt", 3, "O coração bombeia o sangue, que leva oxigênio e nutrientes para as células."),
    ("as_estacoes_do_ano.txt", 2, "As estações do ano acontecem por causa da inclinação do eixo da Terra, e não por causa da distância até o Sol."),
    ("as_estacoes_do_ano.txt", 3, "As estações são opostas nos hemisférios: quando é verão no Brasil, é inverno na Europa."),
    ("a_floresta_amazonica.txt", 1, "A Floresta Amazônica é a maior floresta tropical do mundo, e a maior parte dela fica no Brasil."),
    ("a_floresta_amazonica.txt", 3, "A Amazônia abriga muitos animais, como a onça-pintada, a preguiça, a arara, o boto-cor-de-rosa e o pirarucu."),
    ("a_floresta_amazonica.txt", 6, "O desmatamento é o maior perigo para a Amazônia, e proteger a floresta protege os animais, os povos e o clima."),
    ("a_raposa_e_o_pescador.txt", 3, "A raposa fingiu estar doente e, quando o pescador se abaixou para ajudar, roubou o balde de peixes."),
    ("a_raposa_e_o_pescador.txt", 4, "O balde era pesado, a raposa tropeçou e os peixes voltaram para o lago, deixando-a sem nada."),
    ("a_raposa_e_o_pescador.txt", 6, "A raposa passou a proteger o barco do pescador, e ele, em troca, sempre deixava alguns peixes para ela."),
    ("um_sabado_na_feira.txt", 3, "Seu Antônio oferece laranja para provar, e a avó, depois de pensar, sempre compra uma dúzia."),
    ("um_sabado_na_feira.txt", 5, "O lugar preferido do narrador é a barraca de pastel, onde ele pede um pastel de queijo e caldo de cana."),
    ("a_menina_que_contava_estrelas.txt", 1, "Clara morava no interior e, toda noite, subia no muro do quintal para tentar contar as estrelas."),
    ("a_menina_que_contava_estrelas.txt", 3, "Ao olhar pelo telescópio da escola, Clara descobriu que existem muito mais estrelas do que ela imaginava."),
    ("a_menina_que_contava_estrelas.txt", 6, "Clara se tornou astrônoma e aprendeu que a curiosidade vale a pena mesmo sem chegar a um fim."),
    ("os_animais.txt", 3, "Os mamíferos amamentam os filhotes. Entre eles estão o cachorro, a baleia, o ser humano e o morcego, o único que voa."),
    ("os_animais.txt", 6, "Os animais podem ser herbívoros, carnívoros ou onívoros, conforme o que comem."),
]
RESUMOS_HISTORIA = [
    ("Resuma a história da raposa e do pescador.", "Uma raposa fingiu estar doente para roubar os peixes de um pescador, mas derrubou tudo no lago. O pescador a perdoou, e os dois passaram a se ajudar. A moral é que a honestidade vale mais do que a esperteza."),
    ("Resuma a história da menina que contava estrelas.", "Clara tentava contar as estrelas todas as noites. Depois de olhar por um telescópio, descobriu que elas são incontáveis, passou a estudá-las e virou astrônoma."),
    ("Do que fala o texto sobre o ciclo da água?", "O texto explica como a água evapora, forma nuvens, cai como chuva e volta para os rios e mares, e mostra por que esse ciclo é importante para a vida."),
    ("Do que fala o texto sobre o Sistema Solar?", "O texto apresenta o Sol, os oito planetas, o planeta anão Plutão e a Lua, explicando algumas características de cada um."),
]
PEDIDOS_RESUMO = ["Resuma o texto: {}", "Resuma: {}", "Faça um resumo do texto: {}",
                  "Qual é a ideia principal deste texto? {}", "Resuma em uma frase: {}"]


def paragraphs(name):
    return [p.strip() for p in (MODERN_DIR / name).read_text(encoding="utf-8").split("\n\n") if p.strip()]


# =====================================================================
# SEÇÕES EXTRAS (tools/dados_extra.py, dados_extra2.py, leitura.py)
# =====================================================================
UNIDADES = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze",
            "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
DEZENAS = {2: "vinte", 3: "trinta", 4: "quarenta", 5: "cinquenta", 6: "sessenta", 7: "setenta",
           8: "oitenta", 9: "noventa"}
CENTENAS = {1: "cento", 2: "duzentos", 3: "trezentos", 4: "quatrocentos", 5: "quinhentos", 6: "seiscentos",
            7: "setecentos", 8: "oitocentos", 9: "novecentos"}
ORDINAIS = ["primeiro", "segundo", "terceiro", "quarto", "quinto", "sexto", "sétimo", "oitavo", "nono", "décimo",
            "décimo primeiro", "décimo segundo"]
MESES = [("janeiro", "31 dias"), ("fevereiro", "28 dias, ou 29 nos anos bissextos"), ("março", "31 dias"),
         ("abril", "30 dias"), ("maio", "31 dias"), ("junho", "30 dias"), ("julho", "31 dias"),
         ("agosto", "31 dias"), ("setembro", "30 dias"), ("outubro", "31 dias"), ("novembro", "30 dias"),
         ("dezembro", "31 dias")]
DIAS = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
DATAS = [
    ("o Natal", "O Natal é comemorado em 25 de dezembro."),
    ("o Ano-Novo", "O Ano-Novo é comemorado em 1º de janeiro."),
    ("o Dia da Independência do Brasil", "O Dia da Independência do Brasil é 7 de setembro."),
    ("o Dia de Tiradentes", "O Dia de Tiradentes é 21 de abril."),
    ("o Dia do Trabalho", "O Dia do Trabalho é 1º de maio."),
    ("a Proclamação da República", "A Proclamação da República é lembrada em 15 de novembro."),
    ("o Dia das Crianças no Brasil", "No Brasil, o Dia das Crianças é 12 de outubro."),
    ("o Dia da Consciência Negra", "O Dia da Consciência Negra é 20 de novembro, data da morte de Zumbi dos Palmares."),
    ("o Dia de Finados", "O Dia de Finados é 2 de novembro."),
    ("o Dia das Mães no Brasil", "No Brasil, o Dia das Mães é comemorado no segundo domingo de maio."),
    ("o Dia dos Pais no Brasil", "No Brasil, o Dia dos Pais é comemorado no segundo domingo de agosto."),
]
NOMES = [("Maria", "Ela"), ("Ana", "Ela"), ("Júlia", "Ela"), ("Beatriz", "Ela"), ("Laura", "Ela"),
         ("João", "Ele"), ("Pedro", "Ele"), ("Lucas", "Ele"), ("Gabriel", "Ele"), ("Rafael", "Ele")]
COISAS = ["maçãs", "balas", "figurinhas", "livros", "lápis", "bolinhas de gude", "biscoitos", "carrinhos"]


def por_extenso(n):
    if n < 20:
        return UNIDADES[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DEZENAS[d] + ("" if u == 0 else " e " + UNIDADES[u])
    if n == 100:
        return "cem"
    c, r = divmod(n, 100)
    return CENTENAS[c] + ("" if r == 0 else " e " + por_extenso(r))


def romano(n):
    valores = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"),
               (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in valores:
        while n >= v:
            out += s
            n -= v
    return out


def artigo_estado(estado):
    for nome, prep, _ in ESTADOS:
        if nome == estado:
            return {"do": "o ", "da": "a ", "de": ""}[prep], prep
    return "", "de"


def conjugar(verbo, tempo):
    pron = ["Eu", "tu", "ele", "nós", "vós", "eles"]
    radical, fim = verbo[:-2], verbo[-2:]
    if tempo == "presente":
        term = {"ar": ["o", "as", "a", "amos", "ais", "am"], "er": ["o", "es", "e", "emos", "eis", "em"],
                "ir": ["o", "es", "e", "imos", "is", "em"]}[fim]
        formas = [radical + t for t in term]
    elif tempo == "passado":
        term = {"ar": ["ei", "aste", "ou", "amos", "astes", "aram"], "er": ["i", "este", "eu", "emos", "estes", "eram"],
                "ir": ["i", "iste", "iu", "imos", "istes", "iram"]}[fim]
        formas = [radical + t for t in term]
    else:
        formas = [verbo + t for t in ["ei", "ás", "á", "emos", "eis", "ão"]]
    return ", ".join(f"{p} {f}" for p, f in zip(pron, formas)) + "."


def extra_sections(rng):
    secs = []

    # --- Definições 2 ---
    defs = []
    for i, (q, a) in enumerate(D1.DEFINICOES_2):
        defs.append(ex(f"O que é {q}?", a))
        if i % 3 == 1:
            word = q.split(" ", 1)[1] if q.split(" ", 1)[0] in {"o", "a", "um", "uma"} else q
            defs.append(ex(ALT_DEF[(i // 3) % len(ALT_DEF)].format(w=word, q=q), a))
    secs.append(("Definições 2", defs))

    # --- Animais ---
    ani = []
    for art, nome, grupo, comida, onde, som in D1.ANIMAIS:
        A = art.capitalize()
        ani.append(ex(rng.choice([f"Que tipo de animal é {art} {nome}?", f"{A} {nome} é que tipo de animal?"]),
                      f"{A} {nome} é {grupo}."))
        ani.append(ex(rng.choice([f"O que {art} {nome} come?", f"Do que {art} {nome} se alimenta?"]), comida))
        ani.append(ex(rng.choice([f"Onde vive {art} {nome}?", f"Onde {art} {nome} mora?"]), onde))
        if som:
            ani.append(ex(f"Que som faz {art} {nome}?", f"{A} {nome} {som}."))
    secs.append(("Animais", ani))

    # --- Profissões ---
    prof = []
    for i, (p, a) in enumerate(D1.PROFISSOES):
        q = ["O que faz um {}?", "Qual é o trabalho de um {}?", "O que um {} faz?"][i % 3].format(p)
        prof.append(ex(q, a))
    prof += [ex(q, a) for q, a in D1.QUEM_FAZ]
    secs.append(("Profissões", prof))

    # --- Objetos ---
    obj = []
    for i, (o, a) in enumerate(D1.OBJETOS):
        q = ["Para que serve {}?", "Qual é a utilidade de {}?", "Pra que serve {}?"][i % 3].format(o)
        obj.append(ex(q, a))
    secs.append(("Para que serve", obj))

    # --- Gentílicos, regiões, cidades ---
    geo = []
    for i, (loc, g) in enumerate(D1.GENTILICOS):
        q = ["Como se chama quem nasce {}?", "Quem nasce {} é chamado de quê?",
             "Qual é o gentílico de quem nasce {}?"][i % 3].format(loc)
        geo.append(ex(q, f"Quem nasce {loc} é {g}."))
        if i % 3 == 0 and " ou " not in g:
            geo.append(ex(f"O que significa ser {g}?", f"Ser {g} significa ter nascido {loc}."))
    regiao_de = {}
    for reg, estados in D1.REGIOES.items():
        lista = ", ".join(estados[:-1]) + " e " + estados[-1]
        geo.append(ex(f"Quais estados formam a Região {reg}?", f"A Região {reg} é formada por {lista}."))
        for e in estados:
            regiao_de[e] = reg
    geo.append(ex("Quais são as regiões do Brasil?", "As regiões do Brasil são Norte, Nordeste, Centro-Oeste, Sudeste e Sul."))
    geo.append(ex("Em que região fica o Distrito Federal?", "O Distrito Federal fica na Região Centro-Oeste."))
    for estado, prep, capital in ESTADOS:
        art, _ = artigo_estado(estado)
        geo.append(ex(f"Em que região do Brasil fica {art}{estado}?",
                      f"{(art.capitalize() if art else '')}{estado} fica na Região {regiao_de[estado]}."))
        geo.append(ex(f"{capital} é a capital de qual estado?", f"{capital} é a capital {prep} {estado}."))
    for cidade, estado in D1.CIDADES:
        _, prep = artigo_estado(estado)
        geo.append(ex(f"Em que estado fica a cidade de {cidade}?", f"A cidade de {cidade} fica no estado {prep} {estado}."))
    secs.append(("Gentílicos, regiões e cidades", geo))

    # --- Cores ---
    cores = [ex(f"De que cor é {c}?", a) for c, a in D1.CORES]
    cores += [ex(f"Que cor dá misturar {m}?", f"Misturando {m}, obtemos {r}.") for m, r in D1.MISTURAS]
    cores.append(ex("Quais são as cores primárias?", "Nas tintas, as cores primárias tradicionais são vermelho, amarelo e azul."))
    secs.append(("Cores", cores))

    # --- Mais conhecimentos e pessoas ---
    secs.append(("Conhecimentos gerais 2", [ex(q, a) for q, a in D1.FATOS_2]))
    secs.append(("Pessoas 2", [ex(rng.choice(["Quem foi {}?", "Quem foi {}? Conte um pouco."]).format(n)
                                   if n != "Marta" else "Quem é Marta?", a) for n, a in D1.PESSOAS_2]))

    # --- Números ---
    num = []
    for _ in range(35):
        n = rng.randint(1, 998)
        num.append(ex(rng.choice(["Qual número vem depois de {}?", "Que número vem depois do {}?"]).format(n),
                      f"Depois de {n} vem o {n + 1}."))
    for _ in range(25):
        n = rng.randint(2, 999)
        num.append(ex(f"Qual número vem antes de {n}?", f"Antes de {n} vem o {n - 1}."))
    for _ in range(40):
        n = rng.randint(0, 200)
        num.append(ex(rng.choice(["{} é par ou ímpar?", "O número {} é par ou ímpar?"]).format(n),
                      f"{n} é {'par' if n % 2 == 0 else 'ímpar'}."))
    for _ in range(25):
        n = rng.randint(2, 60)
        num.append(ex(f"Qual é o dobro de {n}?", f"O dobro de {n} é {2 * n}."))
    for _ in range(25):
        n = rng.randint(1, 60) * 2
        num.append(ex(f"Qual é a metade de {n}?", f"A metade de {n} é {n // 2}."))
    for _ in range(10):
        n = rng.randint(2, 30)
        num.append(ex(f"Qual é o triplo de {n}?", f"O triplo de {n} é {3 * n}."))
    for _ in range(30):
        a, b = rng.sample(range(1, 500), 2)
        if rng.random() < 0.6:
            num.append(ex(f"Qual é maior: {a} ou {b}?", f"{max(a, b)} é maior que {min(a, b)}."))
        else:
            num.append(ex(f"Qual é menor: {a} ou {b}?", f"{min(a, b)} é menor que {max(a, b)}."))
    for _ in range(45):
        a, b = rng.randint(2, 10), rng.randint(1, 10)
        num.append(ex(rng.choice(["Quanto é {} × {}?", "Quanto é {} vezes {}?", "Quanto dá {} x {}?"]).format(a, b),
                      f"{a} × {b} = {a * b}."))
    for _ in range(30):
        a, b = rng.randint(10, 500), rng.randint(10, 500)
        if rng.random() < 0.5:
            num.append(ex(f"Quanto é {a} + {b}?", f"{a} + {b} = {a + b}."))
        else:
            a, b = max(a, b), min(a, b)
            num.append(ex(f"Quanto é {a} - {b}?", f"{a} - {b} = {a - b}."))
    for _ in range(20):
        nome, pron = rng.choice(NOMES)
        coisa = rng.choice(COISAS)
        a, b = rng.randint(2, 30), rng.randint(2, 20)
        num.append(ex(f"{nome} tinha {a} {coisa} e ganhou mais {b}. Com quantas {coisa} {pron.lower()} ficou?".replace(
            "quantas livros", "quantos livros").replace("quantas lápis", "quantos lápis").replace(
            "quantas biscoitos", "quantos biscoitos").replace("quantas carrinhos", "quantos carrinhos"),
            f"{pron} ficou com {a + b} {coisa}, porque {a} + {b} = {a + b}."))
    for _ in range(20):
        nome, pron = rng.choice(NOMES)
        coisa = rng.choice(COISAS)
        a = rng.randint(5, 40)
        b = rng.randint(1, a - 2)
        q = f"{nome} tinha {a} {coisa} e deu {b} para um amigo. Quantas sobraram?"
        if coisa in ("livros", "lápis", "biscoitos", "carrinhos"):
            q = q.replace("Quantas sobraram", "Quantos sobraram")
        num.append(ex(q, f"Sobraram {a - b} {coisa}, porque {a} - {b} = {a - b}."))
    for _ in range(15):
        a, b = rng.randint(2, 12), rng.randint(2, 10)
        num.append(ex(f"Uma caixa tem {a} lápis. Quantos lápis há em {b} caixas?",
                      f"Há {a * b} lápis, porque {a} × {b} = {a * b}."))
    for _ in range(15):
        b = rng.randint(2, 6)
        r = rng.randint(2, 10)
        num.append(ex(f"Dividindo {b * r} figurinhas igualmente entre {b} amigos, quantas cada um recebe?",
                      f"Cada um recebe {r} figurinhas, porque {b * r} ÷ {b} = {r}."))
    for _ in range(10):
        p, n = rng.randint(2, 9), rng.randint(2, 8)
        num.append(ex(f"Se um pão custa {p} reais, quanto custam {n} pães?", f"{n} pães custam {p * n} reais."))
    for _ in range(10):
        h, d = rng.randint(1, 8), rng.randint(1, 4)
        num.append(ex(f"Se agora são {h} horas, que horas serão daqui a {d} horas?", f"Serão {h + d} horas."))
    for i in range(1, 11):
        num.append(ex(f"Qual é o ordinal de {i}?", f"O ordinal de {i} é {ORDINAIS[i - 1]}."))
    for n in sorted(set(rng.sample(range(21, 100), 25) + rng.sample(range(101, 1000), 15))):
        num.append(ex(rng.choice(["Como se escreve {} por extenso?", "Escreva {} por extenso."]).format(n),
                      f"{n} por extenso é {por_extenso(n)}."))
    for n in sorted(rng.sample(range(1, 100), 18)) + [2026, 1500, 1822]:
        num.append(ex(f"Como se escreve {n} em algarismos romanos?", f"{n} em algarismos romanos é {romano(n)}."))
    secs.append(("Números e problemas", num))

    # --- Calendário ---
    cal = []
    for i, (mes, dias) in enumerate(MESES):
        cal.append(ex(f"Quantos dias tem o mês de {mes}?", f"O mês de {mes} tem {dias}."))
        cal.append(ex(f"Que mês vem depois de {mes}?", f"Depois de {mes} vem {MESES[(i + 1) % 12][0]}."))
        cal.append(ex(f"Que mês vem antes de {mes}?", f"Antes de {mes} vem {MESES[i - 1][0]}."))
        cal.append(ex(f"Qual é o {ORDINAIS[i]} mês do ano?", f"O {ORDINAIS[i]} mês do ano é {mes}."))
    for i, dia in enumerate(DIAS):
        cal.append(ex(f"Que dia vem depois de {dia}?", f"Depois de {dia} vem {DIAS[(i + 1) % 7]}."))
        cal.append(ex(f"Que dia vem antes de {dia}?", f"Antes de {dia} vem {DIAS[i - 1]}."))
    for festa, a in DATAS:
        cal.append(ex(f"Quando é {festa}?", a))
    secs.append(("Calendário", cal))

    # --- Gramática ---
    gram = []
    for i, (a, b) in enumerate(D2.ANTONIMOS_2):
        q = ["Qual é o contrário de {}?", "Qual é o antônimo de {}?", "Qual é o oposto de {}?"][i % 3]
        gram.append(ex(q.format(a), f"O contrário de {a} é {b}."))
    for a, b in D2.PLURAIS_2:
        gram.append(ex(f"Qual é o plural de {a}?", f"O plural de {a} é {b}."))
    for a, b in D2.FEMININOS_2:
        gram.append(ex(f"Qual é o feminino de {a}?", f"O feminino de {a} é {b}."))
    for a, b in D2.DIMINUTIVOS:
        gram.append(ex(f"Qual é o diminutivo de {a}?", f"O diminutivo de {a} é {b}."))
    for a, b in D2.AUMENTATIVOS:
        gram.append(ex(f"Qual é o aumentativo de {a}?", f"O aumentativo de {a} é {b}."))
    for a, b in D2.SINONIMOS_2:
        gram.append(ex(rng.choice(["Me dê um sinônimo de {}.", "Qual é um sinônimo de {}?"]).format(a),
                       f"Um sinônimo de {a} é {b}."))
    nomes_sil = {1: "monossílaba", 2: "dissílaba", 3: "trissílaba"}
    for palavra, sep in D2.SILABAS:
        n = sep.count("-") + 1
        gram.append(ex(f"Separe as sílabas da palavra {palavra}.", f"{sep}."))
        gram.append(ex(f"Quantas sílabas tem a palavra {palavra}?",
                       f"A palavra {palavra} tem {({1: 'uma', 2: 'duas'}).get(n, por_extenso(n))} sílaba{'s' if n > 1 else ''} ({sep}). "
                       f"Ela é {nomes_sil.get(n, 'polissílaba')}."))
    verbos = D2.VERBOS_AR + D2.VERBOS_ER + D2.VERBOS_IR
    for i, v in enumerate(verbos):
        tempo = ["presente", "passado", "futuro"][i % 3]
        nome_tempo = {"presente": "no presente", "passado": "no pretérito perfeito",
                      "futuro": "no futuro do presente"}[tempo]
        gram.append(ex(f"Conjugue o verbo {v} {nome_tempo}.", conjugar(v, tempo)))
        if i % 2 == 0:
            gram.append(ex(f"Conjugue o verbo {v} no presente." if tempo != "presente" else
                           f"Como é o verbo {v} no presente?", conjugar(v, "presente")))
    for v, forms in D2.IRREGULARES.items():
        gram.append(ex(f"Conjugue o verbo {v} no presente.", forms))
    for _ in range(25):
        v = rng.choice(verbos)
        i = rng.randrange(6)
        pron = ["Eu", "Tu", "Ele", "Nós", "Vós", "Eles"][i]
        forma = conjugar(v, "presente").rstrip(".").split(", ")[i].split(" ", 1)[1]
        gram.append(ex(f"Complete com o verbo {v} no presente: {pron} ___.", f"{pron} {forma}."))
    for i, (frase, certo) in enumerate(D2.CORRECOES):
        if certo is None:
            gram.append(ex(f"Esta frase está correta? {frase[0].upper() + frase[1:]}", "Sim, a frase está correta."))
        else:
            q = ["Corrija a frase: {}", "Corrija: {}", "Esta frase está correta? {}"][i % 3].format(frase)
            a = certo if not q.startswith("Esta frase") else f"Não. O correto é: {certo}"
            gram.append(ex(q, a))
    gram += [ex(q, a) for q, a in D2.TRANSFORMACOES]
    secs.append(("Gramática", gram))

    # --- Inglês ---
    eng = []
    for i, (pt, en) in enumerate(D2.INGLES):
        q = ["Como se diz {} em inglês?", "Qual é a tradução de {} para o inglês?", "Traduza {} para o inglês."][i % 3]
        eng.append(ex(q.format(pt), f"{pt[0].upper() + pt[1:]} em inglês é {en}."))
        if i % 2 == 0:
            eng.append(ex(f"O que significa {en} em português?", f"{en[0].upper() + en[1:]} significa {pt}."))
    eng.append(ex("Como se diz boa noite em inglês?", "Boa noite em inglês é good evening, ao chegar, ou good night, ao se despedir."))
    secs.append(("Inglês", eng))

    # --- Classificação e exemplos ---
    cls = []
    for c, cat in D2.CLASSIFICAR:
        cls.append(ex(f"{c[0].upper() + c[1:]} é um animal, uma planta ou um objeto?", f"{c[0].upper() + c[1:]} é {cat}."))
    for c, cat in D2.FRUTA_LEGUME:
        cls.append(ex(f"{c[0].upper() + c[1:]} é fruta ou legume?", f"{c[0].upper() + c[1:]} é {cat}."))
    for lista, a in D2.INTRUSOS:
        cls.append(ex(rng.choice(["Qual palavra não combina com as outras: {}?", "Qual é o intruso: {}?"]).format(lista), a))
    for i, (cat, a) in enumerate(D2.EXEMPLOS):
        cls.append(ex(f"Dê três exemplos de {cat}.", a))
        if i % 2 == 0:
            cls.append(ex(f"Cite três {cat}.", a))
    secs.append(("Classificação e exemplos", cls))

    # --- Por que / como ---
    secs.append(("Por que", [ex(q, a) for q, a in D2.PORQUES]))
    secs.append(("Como fazer", [ex(q, a) for q, a in D2.COMO_FAZER]))

    # --- Conversa 2, adivinhas, frases ---
    conv = [ex(q, a) for q, a in D2.CONVERSA_2]
    for enigma, a in D2.ADIVINHAS:
        conv.append(ex(f"O que é, o que é: {enigma}?", a))
    secs.append(("Conversa 2 e adivinhas", conv))
    fr = []
    for i, (w, frase) in enumerate(D2.FRASES_PALAVRA):
        q = ["Escreva uma frase com a palavra {}.", "Crie uma frase com {}.", "Use a palavra {} em uma frase."][i % 3]
        fr.append(ex(q.format(w), frase))
    for i, (ini, fim) in enumerate(D2.HISTORIAS_2):
        fr.append(ex(["Continue a história: {}", "Continue: {}"][i % 2].format(ini), fim))
    secs.append(("Frases e histórias", fr))

    # --- Resumos 2 e títulos ---
    res = []
    for i, (name, idx, resumo) in enumerate(L.RESUMOS_2):
        res.append(ex(PEDIDOS_RESUMO[i % len(PEDIDOS_RESUMO)].format(paragraphs(name)[idx]), resumo))
    res += [ex(q, a) for q, a in L.RESUMOS_TEXTO_2]
    for name, idx, titulo in L.TITULOS:
        res.append(ex(f"Dê um título para este texto: {paragraphs(name)[idx]}", titulo))
    secs.append(("Resumos 2 e títulos", res))
    return secs


def leitura_examples():
    """Perguntas com Contexto (mesmo formato do RAG) a partir dos textos de data/modern."""
    out, problems = [], 0
    for name, idx, q, a in L.LEITURA:
        para = paragraphs(name)[idx]
        if not a.startswith("O texto não diz"):
            key = [w for w in content_words(a) if len(w) > 3]
            hits = sum(w in content_words(para) for w in key)
            if key and hits / len(key) < 0.5:
                problems += 1
                print(f"aviso: resposta pouco apoiada no texto: {name}#{idx}: {q} -> {a}")
        out.append(ex(rag_question(q, para), a))
    return out, problems


# =====================================================================
# SEÇÕES EXTRAS 3 (tools/dados_extra3.py e textos simples)
# =====================================================================
GENERO_CLASSE = {"verbo": "um", "substantivo": "um", "adjetivo": "um", "advérbio": "um", "pronome": "um",
                 "numeral": "um", "conjunção": "uma", "preposição": "uma", "interjeição": "uma"}


def cap(text):
    return text[0].upper() + text[1:]


def extra_sections_3(rng):
    secs = []

    geo = []
    forms = ["Qual é a capital {p} {c}?", "Qual a capital {p} {c}?", "Me diga a capital {p} {c}.",
             "Qual cidade é a capital {p} {c}?"]
    art = {"do": "o ", "da": "a ", "dos": "os ", "das": "as ", "de": ""}
    for i, (pais, prep, capital, cont) in enumerate(D3.CAPITAIS_2):
        geo.append(ex(forms[i % 4].format(p=prep, c=pais), f"A capital {prep} {pais} é {capital}."))
        geo.append(ex(f"De que país {capital} é a capital?", f"{capital} é a capital {prep} {pais}."))
        verbo = "ficam" if art[prep] in ("os ", "as ") else "fica"
        geo.append(ex(f"Em que continente {verbo} {art[prep]}{pais}?", f"{cap(art[prep]) if art[prep] else ''}{pais} {verbo} {cont}."))
    geo.append(ex("Qual é a capital da Bolívia?", "A Bolívia tem duas capitais: Sucre é a capital constitucional, e La Paz é a sede do governo."))
    for estado, sigla in D3.SIGLAS:
        if estado == "Distrito Federal":
            a, prep = "o ", "do"
        else:
            a, prep = artigo_estado(estado)
        geo.append(ex(f"Qual é a sigla {prep} {estado}?", f"A sigla {prep} {estado} é {sigla}."))
        geo.append(ex(f"{sigla} é a sigla de qual estado?", f"{sigla} é a sigla {prep} {estado}."))
    secs.append(("Países 2 e siglas", geo))

    sci = []
    for nome, simb in D3.ELEMENTOS:
        sci.append(ex(f"Qual é o símbolo químico do {nome}?" if nome not in ("prata", "platina") else
                      f"Qual é o símbolo químico da {nome}?", f"O símbolo químico {'da' if nome in ('prata', 'platina') else 'do'} {nome} é {simb}."))
        sci.append(ex(f"Qual elemento químico tem o símbolo {simb}?", f"O símbolo {simb} é do {nome}." if nome not in ("prata", "platina")
                      else f"O símbolo {simb} é da {nome}."))
    for animal, n in D3.ANIMAIS_PATAS:
        sci.append(ex(f"Quantas patas tem {animal}?", f"{cap(animal)} tem {({1: 'uma', 2: 'duas'}).get(n, por_extenso(n))} patas."))
    for poli, n in D3.POLIGONOS:
        sci.append(ex(f"Quantos lados tem {poli}?", f"{cap(poli)} tem {por_extenso(n)} lados."))
    sci += [ex(q, a) for q, a in D3.CORPO]
    secs.append(("Ciência e corpo humano", sci))

    ling = []
    for mae, filhote in D3.FILHOTES:
        ling.append(ex(f"Como se chama o filhote {mae}?", f"O filhote {mae} se chama {filhote}."))
    for grupo, col in D3.COLETIVOS:
        ling.append(ex(rng.choice(["Qual é o coletivo de {}?", "Como se chama um grupo de {}?"]).format(grupo),
                       f"O coletivo de {grupo} é {col}."))
    for palavra, classe in D3.CLASSES:
        ling.append(ex(f"Qual é a classe gramatical da palavra {palavra}?",
                       f"A palavra {palavra} é {GENERO_CLASSE[classe]} {classe}."))
    for ditado, sentido in D3.DITADOS_SIGNIFICADO:
        ling.append(ex(rng.choice(["O que significa o ditado: {}?", "Explique o ditado: {}."]).format(ditado), sentido))
    ling += [ex(q, a) for q, a in D3.DIFERENCAS]
    secs.append(("Linguagem 2 e diferenças", ling))

    lang = []
    for i, (pt, es) in enumerate(D3.ESPANHOL):
        lang.append(ex(["Como se diz {} em espanhol?", "Qual é a tradução de {} para o espanhol?"][i % 2].format(pt),
                       f"{cap(pt)} em espanhol é {es}."))
        if i % 3 == 0:
            lang.append(ex(f"O que significa {es} em espanhol?", f"{cap(es)} em espanhol significa {pt}."))
    for i, (pt, en) in enumerate(D3.INGLES_2):
        lang.append(ex(["Como se diz {} em inglês?", "Traduza {} para o inglês.", "Qual é a palavra em inglês para {}?"][i % 3].format(pt),
                       f"{cap(pt)} em inglês é {en}."))
        if i % 2 == 1:
            lang.append(ex(f"O que significa {en} em português?", f"{cap(en)} significa {pt}."))
    for frase, en in D3.FRASES_INGLES:
        lang.append(ex(rng.choice(["Como se diz em inglês: {}", "Traduza para o inglês: {}"]).format(frase), en))
    secs.append(("Espanhol e inglês 2", lang))

    mundo = [ex(q, a) for q, a in D3.SIM_NAO + D3.ESPORTES + D3.DATAS_MUNDO + D3.SAUDE_SEGURANCA]
    mundo += [ex(f"O que é {t}?", a) for t, a in D3.TECNOLOGIA]
    secs.append(("Sim ou não, esportes, datas, saúde e tecnologia", mundo))

    secs.append(("Conversa 3", [ex(q, a) for q, a in D3.CONVERSA_3]))

    # --- Matemática gerada ---
    mat = []
    conv = [("quilômetros", "metros", 1000), ("metros", "centímetros", 100), ("quilos", "gramas", 1000),
            ("litros", "mililitros", 1000), ("horas", "minutos", 60), ("minutos", "segundos", 60),
            ("dias", "horas", 24), ("semanas", "dias", 7), ("anos", "meses", 12), ("dúzias", "unidades", 12)]
    for de, para, fator in conv:
        for n in rng.sample(range(2, 10), 3):
            mat.append(ex(f"Quantos {para} há em {n} {de}?" if para not in ("horas",) else f"Quantas {para} há em {n} {de}?",
                          f"Em {n} {de} há {n * fator} {para}."))
    for _ in range(15):
        a = rng.randint(2, 15)
        mat.append(ex(f"Qual é a área de um quadrado de lado {a} centímetros?",
                      f"A área é {a * a} centímetros quadrados, porque {a} × {a} = {a * a}."))
    for _ in range(15):
        a, b = rng.randint(2, 15), rng.randint(2, 15)
        if rng.random() < 0.5:
            mat.append(ex(f"Qual é a área de um retângulo de {a} por {b} metros?",
                          f"A área é {a * b} metros quadrados, porque {a} × {b} = {a * b}."))
        else:
            mat.append(ex(f"Qual é o perímetro de um retângulo de {a} por {b} metros?",
                          f"O perímetro é {2 * (a + b)} metros, porque {a} + {b} + {a} + {b} = {2 * (a + b)}."))
    for _ in range(20):
        d = rng.choice([2, 3, 4, 5, 10])
        n = d * rng.randint(2, 20)
        nome = {2: "a metade", 3: "um terço", 4: "um quarto", 5: "um quinto", 10: "um décimo"}[d]
        mat.append(ex(f"Quanto é {nome} de {n}?", f"{cap(nome)} de {n} é {n // d}, porque {n} ÷ {d} = {n // d}."))
    for _ in range(25):
        p = rng.choice([10, 20, 25, 50, 75, 5, 30])
        n = rng.choice([20, 40, 60, 80, 100, 120, 200, 300, 400, 500, 1000])
        mat.append(ex(f"Quanto é {p}% de {n}?", f"{p}% de {n} é {p * n // 100}."))
    for _ in range(15):
        b = rng.randint(2, 15)
        mat.append(ex(rng.choice(["Quanto é {} ao quadrado?", "Quanto é {}²?"]).format(b), f"{b} ao quadrado é {b * b}."))
    for b, e in [(2, 3), (2, 4), (2, 5), (2, 10), (3, 3), (10, 3), (5, 3), (4, 3), (10, 2), (3, 4)]:
        mat.append(ex(f"Quanto é {b} elevado a {e}?", f"{b} elevado a {e} é {b ** e}."))
    for r in rng.sample(range(2, 16), 10):
        mat.append(ex(f"Qual é a raiz quadrada de {r * r}?", f"A raiz quadrada de {r * r} é {r}, porque {r} × {r} = {r * r}."))
    for _ in range(30):
        start, step = rng.randint(1, 20), rng.choice([2, 3, 5, 10, -1, -2, 4])
        seq = [start + step * k for k in range(4)]
        if min(seq) < 0:
            continue
        mat.append(ex(f"Qual é o próximo número da sequência: {', '.join(map(str, seq))}?",
                      f"O próximo número é {seq[-1] + step}, porque a sequência {'aumenta' if step > 0 else 'diminui'} de {abs(step)} em {abs(step)}."))
    for _ in range(15):
        preco = rng.randint(1, 45)
        nota = min(n for n in (2, 5, 10, 20, 50, 100) if n > preco)
        mat.append(ex(f"Comprei algo de {preco} reais e paguei com uma nota de {nota}. Quanto recebo de troco?",
                      f"Você recebe {nota - preco} reais de troco, porque {nota} - {preco} = {nota - preco}."))
    secs.append(("Matemática 2", mat))

    # --- Textos simples ---
    res = []
    for i, (titulo, texto, resumo, _, _) in enumerate(TEXTOS_SIMPLES):
        res.append(ex(PEDIDOS_RESUMO[i % len(PEDIDOS_RESUMO)].format(texto), resumo))
        if i % 2 == 0:
            res.append(ex(f"Resuma o texto {titulo[0].lower() + titulo[1:]}." if not titulo.startswith(("O ", "A ", "Os ", "As "))
                          else f"Faça um resumo do texto sobre {titulo[0].lower() + titulo[1:]}.", resumo))
    secs.append(("Textos simples: resumos", res))
    return secs


def leitura_simples():
    return [ex(rag_question(q, texto), a) for _, texto, _, q, a in TEXTOS_SIMPLES]


def write_simple_texts():
    for f in MODERN_DIR.glob("simples_*.txt"):
        f.unlink()
    for i, (titulo, texto, _, _, _) in enumerate(TEXTOS_SIMPLES, 1):
        (MODERN_DIR / f"simples_{i:03d}.txt").write_text(f"{titulo}\n\n{texto}\n", encoding="utf-8")


# =====================================================================
# PERGUNTAS GENÉRICAS (tools/genericas_*.py)
# =====================================================================
# Cada tema é (assunto com artigo, resposta curta, texto de um parágrafo). Daí saem: "O que é X?",
# pedidos de texto ("Faça um texto sobre X."), texto curto, "E X?", resumo do parágrafo e
# leitura com Contexto (vai para leitura.txt).
TEMAS = (TG1.TEMAS_ANIMAIS + TG1.TEMAS_PLANTAS + TG1.TEMAS_NATUREZA + TG1.TEMAS_ESPACO
         + TG2.TEMAS_CIENCIA + TG2.TEMAS_CORPO + TG2.TEMAS_TECNOLOGIA
         + TG3.TEMAS_SOCIEDADE + TG4.TEMAS_CULTURA + TG4.TEMAS_LUGARES + TG4.TEMAS_COTIDIANO
         + TG5.TEMAS_TERRA + TG5.TEMAS_ANIMAIS_2 + TG5.TEMAS_SAUDE_2 + TG5.TEMAS_ESPORTES_FESTAS
         + TG5.TEMAS_PROFISSOES)
TEMAS_PASSADO = TG3.TEMAS_HISTORIA  # "O que foi X?" em vez de "O que é X?"

PERGUNTA_CURTA = {
    "os povos indígenas do Brasil": "Quem são os povos indígenas do Brasil?",
    "os quilombos": "O que eram os quilombos?",
    "Zumbi dos Palmares": "Quem foi Zumbi dos Palmares?",
    "Tiradentes": "Quem foi Tiradentes?",
    "Dom Pedro II": "Quem foi Dom Pedro II?",
    "Brasília": "O que é Brasília?",
    "o SUS": "O que é o SUS?",
    "a ONU": "O que é a ONU?",
    "a Declaração Universal dos Direitos Humanos": "O que é a Declaração Universal dos Direitos Humanos?",
    "a Constituição de 1988": "O que é a Constituição de 1988?",
    "os vikings": "Quem foram os vikings?",
    "a invenção da escrita": "Quando a escrita foi inventada?",
    "a imigração no Brasil": "Como foi a imigração no Brasil?",
    "as pirâmides do Egito": "O que são as pirâmides do Egito?",
    "a chegada dos portugueses ao Brasil": "Como foi a chegada dos portugueses ao Brasil?",
    "a chegada do homem à Lua": "Quando o homem chegou à Lua?",
    "o Saci-Pererê": "Quem é o Saci-Pererê?",
    "o Curupira": "Quem é o Curupira?",
    "a Iara": "Quem é a Iara?",
    "a lenda do boto": "Qual é a lenda do boto?",
    "os professores": "O que faz um professor?",
    "as regiões do Brasil": "Quais são as regiões do Brasil?",
    "os continentes": "Quais são os continentes?",
    "os oceanos": "Quais são os oceanos?",
    "a energia elétrica em casa": "Como a energia elétrica chega às casas?",
    "a esquerda e a direita na política": "O que são esquerda e direita na política?",
    "o Brasil": "Como é o Brasil?",
    "as cidades": "O que é uma cidade?",
    "os mapas": "O que é um mapa?",
    "o clima do Brasil": "Como é o clima do Brasil?",
    "as Olimpíadas do Rio": "Como foram as Olimpíadas do Rio?",
    "o Dia das Mães": "Quando é o Dia das Mães?",
    "os médicos": "O que faz um médico?",
    "os enfermeiros": "O que faz um enfermeiro?",
    "os bombeiros": "O que fazem os bombeiros?",
    "os agricultores": "O que fazem os agricultores?",
    "os cientistas": "O que fazem os cientistas?",
    "os engenheiros": "O que fazem os engenheiros?",
    "os programadores": "O que faz um programador?",
    "os jornalistas": "O que fazem os jornalistas?",
    "a cozinha": "O que é cozinhar?",
    "o lixo": "O que é lixo?",
    "a água potável": "O que é água potável?",
    "o trabalho infantil": "O que é trabalho infantil?",
    "os estados da matéria": "Quais são os estados da matéria?",
    "as estações do ano": "Quais são as estações do ano?",
    "as fases da Lua": "Quais são as fases da Lua?",
    "os três poderes": "Quais são os três poderes?",
}

PEDIDOS_TEXTO = ["Faça um texto sobre {}.", "Escreva um texto sobre {}.", "Fale sobre {}.", "Me fale sobre {}.",
                 "Me conte sobre {}.", "O que você sabe sobre {}?", "Escreva um parágrafo sobre {}.",
                 "Fale um pouco sobre {}.", "Quero saber mais sobre {}.", "Me dê informações sobre {}.",
                 "Faça uma redação curta sobre {}.", "Conte o que você sabe sobre {}."]
PEDIDOS_CURTO = ["Escreva um texto curto sobre {}.", "Em duas frases, fale sobre {}.",
                 "Fale rapidamente sobre {}.", "Faça um resumo sobre {}."]
PEDIDOS_RESUMO_FRASE = ["Resuma em uma frase: {}", "Resuma este texto em uma frase: {}",
                        "Qual é a ideia principal deste texto? {}", "Faça um resumo curto: {}"]
# Pares óbvios demais para perguntar "X e Y são a mesma coisa?".
OPOSTOS = {"hemisfério norte", "Brasil Colônia", "Idade Média", "inflação", "importação", "débito", "salário bruto",
           "eclipse solar", "energia renovável", "presidente", "monarquia", "democracia", "lixo orgânico",
           "emprego formal", "país desenvolvido"}
NUMERAIS = {"dois", "duas", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"}
_FRASES = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")


def duas_frases(texto):
    return " ".join(_FRASES.split(texto)[:2])


def pergunta_curta(assunto, passado=False):
    if assunto in PERGUNTA_CURTA:
        return PERGUNTA_CURTA[assunto]
    art, _, resto = assunto.partition(" ")
    plural = art in ("os", "as")
    if not passado and plural and resto[:1].islower() and resto.split()[0] not in NUMERAIS:
        return f"O que são {resto}?"  # "O que são planárias?" soa melhor que "O que são as planárias?"
    verbo = ("foram" if plural else "foi") if passado else ("são" if plural else "é")
    return f"O que {verbo} {assunto}?"


def sem_artigo(assunto, i):
    """Em parte dos pedidos, tira o artigo do plural: "Faça um texto sobre planárias." (como o usuário escreve)."""
    art, _, resto = assunto.partition(" ")
    if art in ("os", "as") and resto[:1].islower() and resto.split()[0] not in NUMERAIS and i % 2 == 1:
        return resto
    return assunto


def de_artigo(x):
    art, _, resto = x.partition(" ")
    return {"o": "do", "a": "da", "os": "dos", "as": "das"}.get(art, "de " + art) + " " + resto if resto else "de " + x


def generic_sections():
    """Seções novas de perguntas genéricas e os exemplos com Contexto para o leitura.txt."""
    secs, leitura = [], []

    definicoes, textos, seguimentos, resumos = [], [], [], []
    temas = [(t, False) for t in TEMAS] + [(t, True) for t in TEMAS_PASSADO]
    for i, ((assunto, curta, texto), passado) in enumerate(temas):
        q = pergunta_curta(assunto, passado)
        definicoes.append((q, curta))
        textos.append((PEDIDOS_TEXTO[i % len(PEDIDOS_TEXTO)].format(sem_artigo(assunto, i)), texto))
        if i % 2 == 0:
            textos.append((PEDIDOS_CURTO[(i // 2) % len(PEDIDOS_CURTO)].format(assunto), duas_frases(texto)))
        if i % 3 == 0:
            seguimentos.append((f"E {assunto}?", curta))
        if i % 4 == 2:
            seguimentos.append((f"Você sabe algo sobre {assunto}?", "Sei, sim. " + curta))
        if i % 2 == 1:
            resumos.append((PEDIDOS_RESUMO_FRASE[(i // 2) % len(PEDIDOS_RESUMO_FRASE)].format(texto), curta))
        if i % 3 == 0:
            leitura.append(ex(rag_question(q, texto), curta))
        elif i % 3 == 1:
            leitura.append(ex(rag_question(PEDIDOS_CURTO[0].format(assunto), texto), duas_frases(texto)))
    secs += [("Genéricas: o que é", definicoes), ("Genéricas: pedidos de texto", textos),
             ("Genéricas: E X?", seguimentos), ("Genéricas: resumo em uma frase", resumos)]

    porque = []
    for i, (q, a) in enumerate(GP1.POR_QUE + GE.POR_QUE_2):
        porque.append((q, a))
        if i % 2 == 0:
            resto = q[len("Por que "):].rstrip("?")
            porque.append((["Você sabe por que {}?", "Me explique por que {}.", "Explique por que {}."][(i // 2) % 3]
                           .format(resto), a))
    secs.append(("Genéricas: por quê", porque))

    como = []
    for i, (q, a) in enumerate(GP1.COMO + GE.COMO_2):
        como.append((q, a))
        resto = q[len("Como "):].rstrip("?")
        if i % 2 == 0:
            forma = ["Me ensine a {}.", "Qual é a melhor forma de {}?", "Como eu faço para {}?"][(i // 2) % 3]
            if (forma.startswith("Como eu faço") and resto.startswith("fazer ")) or (forma.startswith("Qual") and "melhor" in resto):
                forma = "Me ensine a {}."
            if forma.startswith("Me ensine") and resto.startswith("aprender a "):
                resto = resto[len("aprender a "):]
            como.append((forma.format(resto), a))
    for i, (q, a) in enumerate(GP1.O_QUE_FAZER):
        como.append((q, a))
        if i % 2 == 0 and "a gente" not in q:
            como.append((f"O que eu devo fazer {q[len('O que fazer '):].rstrip('?')}?", a))
    secs.append(("Genéricas: como fazer e o que fazer", como))

    dif = []
    for i, (x, y, a) in enumerate(GP2.DIFERENCAS + GE.DIFERENCAS_2):
        dif.append((f"Qual é a diferença entre {x} e {y}?", a))
        if i % 3 == 2 and x not in OPOSTOS:
            dif.append((f"{cap(x)} e {y} são a mesma coisa?", "Não. " + a))
        elif i % 3 != 0:
            dif.append((f"Qual a diferença entre {y} e {x}?", a))
    secs.append(("Genéricas: diferenças", dif))

    serve = []
    for i, (q, a) in enumerate(GP2.PARA_QUE):
        serve.append((q, a))
        alvo = q.split(" ", 3)[3].rstrip("?")  # "Para que serve(m) X?" -> X
        if i % 2 == 0 and alvo.split()[0] in ("o", "a", "os", "as", "um", "uma"):
            serve.append((f"Qual é a função {de_artigo(alvo)}?", a))
    for i, (q, a) in enumerate(GP2.COMO_FUNCIONA):
        serve.append((q, a))
        if i % 2 == 0:
            serve.append((f"Me explique como funciona {q[len('Como funciona '):].rstrip('?')}.", a))
    secs.append(("Genéricas: para que serve e como funciona", serve))

    mito = []
    for i, (q, a) in enumerate(GP2.VERDADE_OU_MITO):
        mito.append((q, a))
        if i % 2 == 0:
            mito.append((f"Verdade ou mito: {q[len('É verdade que '):]}", a))
    secs.append(("Genéricas: verdade ou mito", mito))

    listas = []
    for i, (q, a) in enumerate(GP3.LISTAS + GE.LISTAS_2):
        listas.append((q, a))
        if q.startswith("Cite ") and i % 3 == 0:
            listas.append(("Diga " + q[len("Cite "):], a))
    secs.append(("Genéricas: listas", listas))

    pessoas = []
    for i, (q, a) in enumerate(GP3.PESSOAS_FAMOSAS + GE.PESSOAS_2):
        pessoas.append((q, a))
        if q.startswith(("Quem foi ", "Quem é ")) and i % 2 == 0:
            pessoas.append((f"Me fale sobre {q.split(' ', 2)[2].rstrip('?')}.", a))
    pessoas += GP3.QUANDO_ONDE
    secs.append(("Genéricas: pessoas, datas e lugares", pessoas))

    secs.append(("Genéricas: opiniões e conselhos", GP3.OPINIOES + GE.OPINIOES_2))
    secs.append(("Genéricas: conversa livre", list(GE.CONVERSA_LIVRE)))
    secs.append(("Genéricas: mensagens incompletas e pedidos de continuação", GC.INCOMPLETAS + GC.SEGUIMENTO))
    secs.append(("Genéricas: limites e apoio", GC.LIMITES + GC.APOIO))

    escrita = []
    for i, (q, a) in enumerate(GC.ESCRITA + GE.ESCRITA_2):
        escrita.append((q, a))
        if i % 3 == 0 and q.startswith(("Escreva um poema", "Faça um poema", "Escreva uma história", "Conte uma história")):
            troca = {"Escreva": "Crie", "Faça": "Escreva", "Conte": "Invente"}
            verbo, resto = q.split(" ", 1)
            escrita.append((f"{troca[verbo]} {resto}", a))
    secs.append(("Genéricas: escrita (poemas, histórias, mensagens)", escrita))
    secs.append(("Genéricas: curiosidades", GC.CURIOSIDADES + GE.CURIOSIDADES_2))
    return secs, leitura


MAIS = ["Me fale mais.", "Conte mais sobre isso.", "Explique melhor.", "Pode dar mais detalhes?", "Fale mais sobre isso."]
RESUMIR = ["Resuma isso em uma frase.", "Agora resuma em uma frase.", "Pode resumir?"]
NOMES_CONVERSA = ["Ana", "Bruna", "Carla", "Daniel", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Júlia",
         "Lucas", "Mariana", "Nicolas", "Olívia", "Pedro", "Rafaela", "Sofia", "Tiago", "Vitória", "Mateus"]


def conversas():
    """Conversas de várias trocas para a memória de IA (o chat põe as últimas mensagens no prompt).

    No fine-tuning, só a última resposta é treinada; as anteriores mostram por que ela faz sentido:
    "Qual é a capital da França?" ... "E da Itália?", "O que é X?" ... "Me fale mais.".
    """
    convs = []
    paises = [(p, prep, c) for p, prep, c, *_ in CAPITAIS + D3.CAPITAIS_2]
    for lista in (paises, ESTADOS):
        for i, (lugar, prep, capital) in enumerate(lista):
            outro, prep2, capital2 = lista[(i * 7 + 3) % len(lista)]
            if outro == lugar:
                continue
            convs.append([(f"Qual é a capital {prep} {lugar}?", f"A capital {prep} {lugar} é {capital}."),
                          (f"E {prep2} {outro}?", f"A capital {prep2} {outro} é {capital2}.")])
    temas = [(t, False) for t in TEMAS] + [(t, True) for t in TEMAS_PASSADO]
    for i, ((assunto, curta, texto), passado) in enumerate(temas):
        q = pergunta_curta(assunto, passado)
        convs.append([(q, curta), (MAIS[i % len(MAIS)], texto)])
        if i % 3 == 0:
            convs.append([(PEDIDOS_TEXTO[i % len(PEDIDOS_TEXTO)].format(assunto), texto),
                          (RESUMIR[i % len(RESUMIR)], curta)])
        if i % 4 == 1 and i + 1 < len(temas):
            (assunto2, curta2, _), _ = temas[i + 1]
            convs.append([(q, curta), (f"E {assunto2}?", curta2)])
        if i % 5 == 2:
            convs.append([(q, curta), ("Do que estávamos falando?", f"Estávamos falando sobre {assunto}.")])
        if i % 6 == 3:
            convs.append([(q, curta), ("Pode repetir?", curta)])
        if i % 7 == 4:
            convs.append([(q, curta), (MAIS[(i + 1) % len(MAIS)], texto),
                          ("Obrigado!", "De nada! Se quiser saber mais alguma coisa, é só perguntar.")])
    for i, nome in enumerate(NOMES_CONVERSA):
        pergunta = ["Qual é o meu nome?", "Como eu me chamo?", "Você lembra o meu nome?"][i % 3]
        resposta = [f"Seu nome é {nome}.", f"Você se chama {nome}.", f"Lembro, sim: seu nome é {nome}."][i % 3]
        convs.append([(f"Meu nome é {nome}.", f"Prazer, {nome}! Vou lembrar o seu nome."), (pergunta, resposta)])
    convs.append([("Qual é o seu nome?", "Meu nome é Laika."),
                  ("E o meu?", "Você ainda não me disse o seu nome. Como você se chama?")])
    convs.append([("Oi", "Olá! Eu sou a Laika. Como posso ajudar?"), ("Tudo bem?", "Tudo bem, e você?"),
                  ("Estou bem.", "Que bom! Em que posso ajudar hoje?")])
    return convs


# =====================================================================
# RESPOSTAS LONGAS, "POR QUÊ" E SIM OU NÃO (tools/longas*.py, porque*.py, simnao.py)
# =====================================================================
LONGAS = (longas1.LONGAS + longas2.LONGAS + longas3.LONGAS + longas4.LONGAS + longas5.LONGAS + longas6.LONGAS
          + longas7.LONGAS)
PORQUES = porque1.PORQUES + porque2.PORQUES + porque3.PORQUES + porque4.PORQUES
PEDIDOS_LONGO = ["Escreva um texto longo sobre {}.", "Escreva um texto completo sobre {}.", "Fale bastante sobre {}.",
                 "Me conte tudo o que você sabe sobre {}.", "Faça uma explicação detalhada sobre {}."]
PEDIDOS_HISTORIA = ["Escreva uma história sobre {}.", "Invente uma história sobre {}.", "Me conte uma história sobre {}."]
DETALHE = ["{} Explique com detalhes.", "{} Responda com detalhes.", "Explique com detalhes: {}",
           "{} Quero uma resposta completa."]
PASSO = ["Me explique o passo a passo: {}", "{} Explique com detalhes.", "Passo a passo, por favor: {}"]
PORQUE_FORMAS = ["Você sabe {}?", "Explique {}.", "Me diga {}."]
CONTINENTES = ["na Europa", "na Ásia", "na África", "na América do Sul", "na América do Norte", "na Oceania"]
ARTIGO_PAIS = {"do": "o ", "da": "a ", "dos": "os ", "de": ""}


# Resumos escritos à mão (tools/resumos*.py): o texto -> uma frase, duas frases ou três tópicos, com outras
# palavras. Antes, a maior parte dos resumos do fine-tuning era extrativa (uma frase do próprio texto), e o modelo
# aprendeu que resumir é copiar.
PEDIDOS_RESUMO_UMA = ["Resuma em uma frase: {}", "Resuma este texto em uma frase: {}",
                      "Qual é a ideia principal deste texto? {}", "Faça um resumo de uma frase: {}",
                      "Diga em uma frase do que trata este texto: {}", "{}\n\nResuma o texto acima em uma frase."]
PEDIDOS_RESUMO_CURTO = ["Resuma o texto: {}", "Resuma: {}", "Faça um resumo do texto: {}",
                        "Faça um resumo curto deste texto: {}", "Resuma em poucas palavras: {}",
                        "Resuma o texto abaixo.\n\n{}", "{}\n\nResuma o texto acima.", "Resuma em duas frases: {}"]
PEDIDOS_RESUMO_TOPICOS = ["Resuma em tópicos: {}", "Faça um resumo em tópicos: {}",
                          "Liste os pontos principais deste texto: {}", "Quais são os pontos principais do texto? {}",
                          "Resuma em três tópicos: {}", "{}\n\nQuais são os pontos principais desse texto?"]


def resumos_sections():
    """Três resumos de cada texto: os 176 textos longos (resumos1..3) e os textos novos (resumos4..7)."""
    longas = {pergunta: texto for _, pergunta, texto in LONGAS}
    textos = []
    for m in (resumos1, resumos2, resumos3):
        for pergunta, resumos in m.RESUMOS.items():
            if pergunta not in longas:
                raise SystemExit(f"resumo de um texto longo que não existe: {pergunta!r}")
            textos.append((longas[pergunta],) + resumos)
    for m in (resumos4, resumos5, resumos6, resumos7):
        textos += m.TEXTOS
    pares = []
    for i, (texto, frase, curto, topicos) in enumerate(textos):
        pares.append((PEDIDOS_RESUMO_UMA[i % len(PEDIDOS_RESUMO_UMA)].format(texto), frase))
        pares.append((PEDIDOS_RESUMO_CURTO[i % len(PEDIDOS_RESUMO_CURTO)].format(texto), curto))
        pares.append((PEDIDOS_RESUMO_TOPICOS[i % len(PEDIDOS_RESUMO_TOPICOS)].format(texto),
                      "\n".join("- " + t for t in topicos)))
    return [("Resumos escritos à mão", pares)]


def longas_sections(rng):
    """Respostas longas (2 parágrafos), "por quê" e sim ou não."""
    longas = []
    for i, (assunto, pergunta, texto) in enumerate(LONGAS):
        longas.append((pergunta, texto))
        if assunto is None:
            for k in range(2):
                longas.append((PASSO[(i + k) % len(PASSO)].format(pergunta), texto))
            continue
        historia = re.match(r"(Conte|Escreva) uma história", pergunta)
        formas = PEDIDOS_HISTORIA if historia else PEDIDOS_LONGO
        longas.append((formas[i % len(formas)].format(assunto), texto))
        if not historia:
            longas.append((DETALHE[i % len(DETALHE)].format(pergunta), texto))

    porques = []
    for i, (pergunta, resposta) in enumerate(PORQUES):
        porques.append((pergunta, resposta))
        miolo = pergunta[0].lower() + pergunta[1:].rstrip("?")
        porques.append((PORQUE_FORMAS[i % len(PORQUE_FORMAS)].format(miolo), resposta))

    sim = list(SN.SIMNAO) + list(SN2.SIMNAO) + list(SN3.SIMNAO)
    # Capitais e continentes: uma pergunta certa e uma errada de cada.
    caps = CAPITAIS
    for i, (pais, prep, capital, continente, _) in enumerate(caps):
        outro = caps[(i * 7 + 3) % len(caps)]
        if outro[2] == capital:
            outro = caps[(i + 1) % len(caps)]
        sim.append((f"A capital {prep} {pais} é {capital}?", f"Sim. A capital {prep} {pais} é {capital}."))
        sim.append((f"A capital {prep} {pais} é {outro[2]}?",
                    f"Não. A capital {prep} {pais} é {capital}. {outro[2]} é a capital {outro[1]} {outro[0]}."))
        art = ARTIGO_PAIS[prep]
        verbo = "ficam" if prep == "dos" else "fica"
        nome = (art + pais)[0].upper() + (art + pais)[1:]
        sim.append((f"{nome} {verbo} {continente}?", f"Sim. {nome} {verbo} {continente}."))
        outros = [c for c in CONTINENTES if c not in continente]
        errado = outros[i % len(outros)]
        sim.append((f"{nome} {verbo} {errado}?", f"Não. {nome} {verbo} {continente}, e não {errado}."))
    falam = [(c[0], c[1], c[4]) for c in caps if c[4]]
    for i, (pais, prep, lingua) in enumerate(falam):
        em = {"do": "No", "da": "Na", "dos": "Nos", "de": "Em"}[prep]
        outra = next((l for _, _, l in falam[i + 1:] + falam[:i] if l != lingua), None)
        sim.append((f"{em} {pais} se fala {lingua}?", f"Sim. {em} {pais} a língua oficial é o {lingua}."
                    if lingua.islower() and " " not in lingua else f"Sim. {em} {pais} se fala {lingua}."))
        if outra:
            sim.append((f"{em} {pais} se fala {outra}?", f"Não. {em} {pais} se fala {lingua}."))
    for i, (estado, prep, capital) in enumerate(ESTADOS):
        outro = ESTADOS[(i * 5 + 2) % len(ESTADOS)]
        if outro[2] == capital:
            outro = ESTADOS[(i + 1) % len(ESTADOS)]
        sim.append((f"A capital {prep} {estado} é {capital}?", f"Sim. A capital {prep} {estado} é {capital}."))
        sim.append((f"A capital {prep} {estado} é {outro[2]}?",
                    f"Não. A capital {prep} {estado} é {capital}. {outro[2]} é a capital {outro[1]} {outro[0]}."))
    for i, (obra, autor) in enumerate(LIVROS):
        outro = next(a for _, a in LIVROS[i + 1:] + LIVROS[:i] if a != autor)
        sim.append((f"{obra} foi escrito por {autor}?", f"Sim. {obra} foi escrito por {autor}."))
        sim.append((f"{obra} foi escrito por {outro}?", f"Não. {obra} foi escrito por {autor}, e não por {outro}."))
    # Animais: a classe certa e uma com que costuma ser confundido.
    for i, (animal, classe, motivo) in enumerate(SN.ANIMAIS):
        nome = animal[0].upper() + animal[1:]
        pron = "ela" if animal.startswith("a ") else "ele"
        art = SN.ARTIGO_CLASSE[classe]
        sim.append((f"{nome} é {art} {classe}?", f"Sim. {nome} é {art} {classe}: {pron} {motivo}."))
        confusoes = SN.CONFUSOES[classe]
        for k in range(min(2, len(confusoes))):  # até duas classes erradas por animal
            errada = confusoes[(i + k) % len(confusoes)]
            art2 = SN.ARTIGO_CLASSE[errada]
            sim.append((f"{nome} é {art2} {errada}?",
                        f"Não. {nome} é {art} {classe}, e não {art2} {errada}: {pron} {motivo}."))
    for i, (planeta, pos, tipo, carac) in enumerate(SN.PLANETAS):
        outro_tipo = "gasoso" if tipo == "rochoso" else "rochoso"
        sim.append((f"{planeta} {carac}?", f"Sim. {planeta} {carac}."))
        sim.append((f"{planeta} é um planeta {tipo}?", f"Sim. {planeta} é um planeta {tipo}."))
        sim.append((f"{planeta} é um planeta {outro_tipo}?", f"Não. {planeta} é um planeta {tipo}, e não {outro_tipo}."))
        if pos == 1:
            sim.append((f"{planeta} é o planeta mais próximo do Sol?", f"Sim. {planeta} é o planeta mais próximo do Sol."))
        else:
            sim.append((f"{planeta} é o planeta mais próximo do Sol?",
                        f"Não. O planeta mais próximo do Sol é Mercúrio. {planeta} é o {ORDINAIS[pos - 1]} planeta "
                        f"a partir do Sol."))
    # Contas, pares e ímpares, maior e menor.
    for _ in range(60):
        a, b = rng.randint(2, 30), rng.randint(2, 20)
        op, r = rng.choice([("+", a + b), ("-", a - b), ("×", a * b)]) if a > b else ("+", a + b)
        if op == "×":
            a, b = rng.randint(2, 10), rng.randint(2, 10)
            r = a * b
        certo = rng.random() < 0.5
        dado = r if certo else r + rng.choice([-3, -2, -1, 1, 2, 3])
        sim.append((f"{a} {op} {b} é igual a {dado}?",
                    f"Sim. {a} {op} {b} = {r}." if certo else f"Não. {a} {op} {b} = {r}, e não {dado}."))
    for _ in range(50):  # tabuada
        a, b = rng.randint(2, 10), rng.randint(2, 10)
        dado = a * b if rng.random() < 0.5 else a * b + rng.choice([-2, -1, 1, 2, a, -b])
        sim.append((f"{a} vezes {b} é {dado}?", f"Sim. {a} vezes {b} é {a * b}." if dado == a * b
                    else f"Não. {a} vezes {b} é {a * b}, e não {dado}."))
    for n in range(1, 41):
        if n % 2 == 0:
            sim.append((f"{n} é um número par?", f"Sim. {n} é par, porque pode ser dividido por 2 sem sobrar resto."))
        else:
            sim.append((f"{n} é um número par?", f"Não. {n} é ímpar: dividido por 2, sobra 1."))
    for n in range(2, 51):
        divisor = next((d for d in range(2, n) if n % d == 0), None)
        if divisor is None:
            sim.append((f"{n} é um número primo?", f"Sim. {n} é primo: só pode ser dividido por 1 e por ele mesmo."))
        else:
            sim.append((f"{n} é um número primo?",
                        f"Não. {n} não é primo, porque também pode ser dividido por {divisor}: {n} ÷ {divisor} = "
                        f"{n // divisor}."))
    for _ in range(30):
        a, b = rng.sample(range(1, 200), 2)
        sim.append((f"{a} é maior que {b}?",
                    f"Sim. {a} é maior que {b}." if a > b else f"Não. {a} é menor que {b}."))
    return [("Respostas longas", longas + contas_explicadas(rng)), ("Por quê", porques), ("Sim ou não", sim)]


def contas_explicadas(rng):
    """Contas com o passo a passo (respostas mais longas, com o raciocínio)."""
    pares, vistos = [], set()
    while len(pares) < 150:
        tipo = len(pares) % 3
        if tipo == 0:  # multiplicação de dois algarismos por um
            a, b = rng.randint(12, 99), rng.randint(2, 9)
            if (a, b, "x") in vistos or a % 10 == 0:
                continue
            vistos.add((a, b, "x"))
            d, u = a - a % 10, a % 10
            q = rng.choice(["Explique passo a passo: quanto é {} × {}?", "Como calcular {} × {}? Explique.",
                            "Me mostre como fazer a conta {} × {}."]).format(a, b)
            r = (f"Para multiplicar {a} por {b}, dá para separar o {a} em {d} + {u}. Primeiro, {d} × {b} = {d * b}. "
                 f"Depois, {u} × {b} = {u * b}. Por fim, somamos os dois resultados: {d * b} + {u * b} = {a * b}. "
                 f"Então, {a} × {b} = {a * b}.")
        elif tipo == 1:  # soma com "vai um"
            a, b = rng.randint(15, 89), rng.randint(15, 89)
            if (a, b, "+") in vistos or (a % 10) + (b % 10) < 10:
                continue
            vistos.add((a, b, "+"))
            su = a % 10 + b % 10
            q = rng.choice(["Explique passo a passo: quanto é {} + {}?", "Como somar {} + {}? Explique.",
                            "Me ensine a fazer a conta {} + {}."]).format(a, b)
            r = (f"Somamos primeiro as unidades: {a % 10} + {b % 10} = {su}. Escrevemos o {su % 10} e passamos 1 "
                 f"para a casa das dezenas, o famoso vai um. Depois, somamos as dezenas: {a // 10} + {b // 10} + 1 = "
                 f"{a // 10 + b // 10 + 1}. Juntando, o resultado é {a + b}. Então, {a} + {b} = {a + b}.")
        else:  # divisão exata
            b, r_ = rng.randint(2, 9), rng.randint(11, 30)
            a = b * r_
            if (a, b, "/") in vistos:
                continue
            vistos.add((a, b, "/"))
            q = rng.choice(["Explique passo a passo: quanto é {} ÷ {}?", "Como dividir {} por {}? Explique.",
                            "Me mostre como fazer a conta {} ÷ {}."]).format(a, b)
            d = (a // (b * 10)) * b * 10
            if d:
                r = (f"Dividir {a} por {b} é descobrir quantas vezes o {b} cabe no {a}. Dá para separar o {a} em "
                     f"{d} + {a - d}. {d} ÷ {b} = {d // b}, e {a - d} ÷ {b} = {(a - d) // b}. Somando, "
                     f"{d // b} + {(a - d) // b} = {r_}. Então, {a} ÷ {b} = {r_}. Para conferir, {r_} × {b} = {a}.")
            else:
                r = (f"Dividir {a} por {b} é descobrir quantas vezes o {b} cabe no {a}. Como {r_} × {b} = {a}, o "
                     f"resultado é {r_}. Então, {a} ÷ {b} = {r_}.")
        pares.append((q, r))
    return pares


# =====================================================================
# PESSOAS, DATAS, SÉCULOS, CONCEITOS E O GATILHO DE RESPOSTA LONGA
# (tools/pessoas*.py, eventos.py, conceitos*.py)
# =====================================================================
PESSOAS_V = pessoas1.PESSOAS + pessoas2.PESSOAS + pessoas3.PESSOAS
CONCEITOS = conceitos1.CONCEITOS + conceitos2.CONCEITOS
# Formas do gatilho (data_utils.LONG_TRIGGER e _LONG_TRIGGERS). A primeira é a que o app e o chat.py acrescentam.
GATILHOS = ["{} Resposta longa.", "{} Explique melhor.", "Resposta longa: {}", "{} Responda com detalhes.",
            "Explique melhor: {}", "{} Resposta longa, por favor."]


def ano_extenso(n):
    """1822 -> "mil oitocentos e vinte e dois", 1500 -> "mil e quinhentos", 2002 -> "dois mil e dois"."""
    if n < 1000:
        return por_extenso(n)
    m, r = divmod(n, 1000)
    mil = "mil" if m == 1 else por_extenso(m) + " mil"
    if r == 0:
        return mil
    return f"{mil}{' e ' if r < 100 or r % 100 == 0 else ' '}{por_extenso(r)}"


def seculo(ano):
    return (ano - 1) // 100 + 1


def nome_seculo(s, extenso=False):
    # Sem o "(quinze)" por padrão: o modelo copiava o molde com o número errado ("século XIV (doze)").
    return f"século {romano(s)} ({por_extenso(s)})" if extenso else f"século {romano(s)}"


def data_curta(d, m, a):
    return f"{'1º' if d == 1 else d} de {MESES[m - 1][0]} de {a}"


def data_extenso(d, m, a):
    return f"{'primeiro' if d == 1 else por_extenso(d)} de {MESES[m - 1][0]} de {ano_extenso(a)}"


def minuscula(texto):
    """Primeira letra minúscula, a não ser que a palavra pareça nome próprio (ex.: "A princesa" -> "a princesa")."""
    primeira = texto.split(" ", 1)[0]
    return texto[0].lower() + texto[1:] if primeira in ("O", "A", "Os", "As") else texto


def com_gatilho(i, pergunta):
    forma = GATILHOS[i % len(GATILHOS)]
    if forma.startswith(("Resposta longa:", "Explique melhor:")):
        pergunta = minuscula(pergunta)
    return forma.format(pergunta)


def pergunta_conceito(assunto):
    """"a pedra" -> "O que é pedra?" (como o usuário pergunta); nomes próprios ficam com o artigo ("O que é o Sol?")."""
    art, _, resto = assunto.partition(" ")
    return f"O que é {resto}?" if art in ("o", "a") and resto[:1].islower() else pergunta_curta(assunto)


def pessoas_sections():
    """"Quem foi X?", "O que X fez?", século, nascimento com o ano por extenso, sim ou não e o gatilho."""
    quem, fez, datas, sim = [], [], [], []
    for i, (nome, g, nasc, morte, q_foi, o_que) in enumerate(PESSOAS_V):
        plural = g == "p"
        Nome = cap(nome)
        foi, fizeram = ("foram", "fizeram") if plural else ("foi", "fez")
        fim = {"m": "o", "f": "a", "p": "os"}[g]
        quem.append((f"Quem {foi} {nome}?", q_foi))
        fez.append((f"O que {nome} {fizeram}?", o_que))
        fez.append(([f"Por que {nome} {'são' if plural else 'é'} famos{fim}?",
                     f"Pelo que {nome} {'ficaram' if plural else 'ficou'} conhecid{fim}?",
                     f"Qual é a importância {de_artigo(nome)}?"][i % 3], o_que))
        pron = {"m": "ele", "f": "ela", "p": "eles"}[g]
        quem.append(([f"Quem {foi} {nome} e o que {pron} {fizeram}?", f"Me fale sobre {nome}.",
                      f"O que você sabe sobre {nome}?"][i % 3], f"{q_foi} {o_que}"))
        vida = ""
        if nasc and morte:
            s1, s2 = seculo(nasc), seculo(morte)
            vida = (f"{Nome} viveu no {nome_seculo(s1)}: nasceu em {nasc} e morreu em {morte}." if s1 == s2 else
                    f"{Nome} viveu entre os séculos {romano(s1)} e {romano(s2)}: nasceu em {nasc} e morreu em {morte}.")
            datas.append(([f"Em que século viveu {nome}?", f"{Nome} viveu em que século?",
                           f"Em que época viveu {nome}?"][i % 3], vida))
            datas.append((f"Quando {nome} nasceu?",
                          f"{Nome} nasceu em {nasc}, no {nome_seculo(s1)}."))
            datas.append((f"Quando {nome} morreu?", f"{Nome} morreu em {morte}, no {nome_seculo(s2)}."))
            datas.append((f"Quantos anos {nome} viveu?",
                          f"{Nome} viveu cerca de {morte - nasc} anos: nasceu em {nasc} e morreu em {morte}."))
            errado = nasc + [12, -9, 23, -17, 31][i % 5]
            if i % 2 == 0:
                sim.append((f"{Nome} nasceu em {ano_extenso(nasc)}?",
                            f"Sim. {Nome} nasceu em {nasc}."))
            else:
                sim.append((f"{Nome} nasceu em {ano_extenso(errado)}?",
                            f"Não. {Nome} nasceu em {nasc}, e não em {errado}."))
            outro = s1 + (1 if i % 4 < 2 else -1)
            if i % 2 == 1 or outro in (s1, s2):
                sim.append((f"{Nome} viveu no século {romano(s1)}?", f"Sim. {vida}"))
            else:
                sim.append((f"{Nome} viveu no século {romano(outro)}?", f"Não. {vida}"))
            if i % 2 == 1:
                sim.append((f"{Nome} morreu em {ano_extenso(morte)}?", f"Sim. {Nome} morreu em {morte}."))
            else:
                sim.append((f"{Nome} morreu em {ano_extenso(morte + 14)}?",
                            f"Não. {Nome} morreu em {morte}, e não em {morte + 14}."))
        longa = f"{q_foi} {o_que}" + (f" {vida}" if vida else "")
        quem.append((com_gatilho(i, f"Quem {foi} {nome}?"), longa))
        fez.append((com_gatilho(i + 3, f"O que {nome} {fizeram}?"), longa))
    return [("Pessoas: quem foi", quem), ("Pessoas: o que fez", fez), ("Pessoas: datas e séculos", datas),
            ("Pessoas: sim ou não", sim)]


def datas_sections(rng):
    """Acontecimentos com a data em algarismos e por extenso, séculos em algarismos romanos e anos por extenso."""
    quando, aconteceu, sim = [], [], []
    por_ano = {}
    for i, (nome, d, m, a, fato, mais) in enumerate(EV.EVENTOS):
        Nome, s = cap(nome), seculo(a)
        por_ano.setdefault(a, []).append(fato)
        quando_foi = f"Foi em {data_curta(d, m, a)}." if d else f"Foi em {a}, no {nome_seculo(s)}."
        quando.append((f"Quando foi {nome}?", f"{quando_foi} {'Nesse dia' if d else 'Nesse ano'}, {fato}."))
        quando.append((f"Em que ano foi {nome}?", f"{Nome} foi em {a}, no {nome_seculo(s)}."))
        quando.append(([f"Em que século foi {nome}?", f"{Nome} aconteceu em que século?"][i % 2],
                        f"{Nome} foi no {nome_seculo(s)}, em {a}."))
        texto = f"{Nome} foi em {data_curta(d, m, a) if d else a}. {cap(fato)}. {mais}"
        aconteceu.append(([f"Me fale sobre {nome}.", f"O que foi {nome}?", f"Explique o que foi {nome}."][i % 3], texto))
        aconteceu.append((com_gatilho(i, f"Quando foi {nome}?"), f"{texto} Isso foi no {nome_seculo(s)}."))
        if d:
            quando.append(([f"Em que dia foi {nome}?", f"Qual foi a data {de_artigo(nome)}?"][i % 2],
                           f"{Nome} foi no dia {data_curta(d, m, a)}."))
            resposta = f"Em {data_curta(d, m, a)}, {fato}. {mais}"
            aconteceu.append((f"O que aconteceu em {data_extenso(d, m, a)}?", resposta))
            aconteceu.append(([f"O que aconteceu no dia {d:02d}/{m:02d}/{a}?", f"O que aconteceu em {d}/{m}/{a}?"][i % 2],
                              resposta))
            aconteceu.append((f"O que aconteceu em {data_curta(d, m, a)}?", resposta))
        outro = s + (1 if i % 3 else -1)
        if i % 2 == 0:
            sim.append((f"{Nome} foi no século {romano(s)}?", f"Sim. {Nome} foi em {a}, no {nome_seculo(s)}."))
        else:
            sim.append((f"{Nome} foi no século {romano(outro)}?",
                        f"Não. {Nome} foi em {a}, no {nome_seculo(s)}, e não no século {romano(outro)}."))
        if d and i % 2 == 1:
            sim.append((f"{Nome} foi em {ano_extenso(a)}?", f"Sim. {quando_foi}"))
    for a, fatos in por_ano.items():
        if len(fatos) == 1:
            resposta = f"Em {a}, {fatos[0]}."
        else:
            resposta = f"Em {a}, aconteceram várias coisas: " + "; ".join(fatos[:-1]) + f"; e {fatos[-1]}."
        aconteceu.append(([f"O que aconteceu em {ano_extenso(a)}?", f"O que aconteceu no ano de {ano_extenso(a)}?"]
                          [a % 2], resposta))
        aconteceu.append((f"O que aconteceu em {a}?", resposta))

    secs = []
    for s in range(1, 22):
        ini, fim = 100 * (s - 1) + 1, 100 * s
        R, ext = romano(s), por_extenso(s)
        secs.append((f"Quais anos fazem parte do século {R}?", f"O século {R} ({ext}) vai do ano {ini} ao ano {fim}."))
        secs.append((f"O que quer dizer século {R}?",
                     f"Século {R} quer dizer século {ext}: o período de cem anos que vai de {ini} a {fim}."))
        secs.append((f"Como se lê século {R}?", f"Século {R} se lê século {ext}."))
        secs.append((f"Como se escreve século {ext} em algarismos romanos?", f"Século {ext} se escreve século {R}."))
        secs.append((f"Quando começou o século {R}?", f"O século {R} começou no ano {ini} e terminou no ano {fim}."
                     if s < 21 else f"O século XXI começou em 1º de janeiro de 2001 e vai até o fim de 2100."))
    anos = sorted(rng.sample(range(1000, 2026), 230) + rng.sample(range(101, 1000), 50)
                  + [1500, 1600, 1700, 1800, 1900, 2000, 1501, 1801, 1901, 2001])
    for i, a in enumerate(dict.fromkeys(anos)):
        s = seculo(a)
        resposta = (f"O ano {a} fica no {nome_seculo(s)}, que vai de {100 * (s - 1) + 1} a {100 * s}."
                    + (f" Como {a} termina em 00, ele é o último ano desse século." if a % 100 == 0 else ""))
        secs.append(([f"Em que século fica o ano {a}?", f"O ano {a} é de que século?", f"{a} é de que século?"][i % 3],
                      resposta))
        secs.append(([f"O ano de {ano_extenso(a)} fica em que século?", f"Em que século fica o ano {ano_extenso(a)}?"][i % 2],
                     resposta))
        if i % 3 == 0:
            secs.append((f"Como se escreve o ano {a} por extenso?", f"O ano {a} por extenso é {ano_extenso(a)}."))
        elif i % 3 == 1:
            secs.append((f"Como se escreve {ano_extenso(a)} com algarismos?", f"{cap(ano_extenso(a))} se escreve {a}."))
    for n in list(range(1, 51)) + [60, 70, 80, 90, 99, 100, 200, 400, 500, 900, 1000, 1500, 1822, 1888, 1889, 1922, 2000, 2024]:
        R = romano(n)
        secs.append(([f"Quanto vale {R} em algarismos romanos?", f"Que número é {R} em algarismos romanos?",
                      f"Quanto é {R} em números?"][n % 3], f"{R} vale {n}."))
    return [("Datas: quando foi", quando), ("Datas: o que aconteceu", aconteceu), ("Datas: sim ou não", sim),
            ("Séculos, anos por extenso e algarismos romanos", secs)]


def conceitos_sections():
    """"O que é pedra/rocha/água...?" com resposta curta, e a resposta longa com o gatilho."""
    curtas, longas = [], []
    for i, (assunto, curta, longa) in enumerate(CONCEITOS):
        q = pergunta_conceito(assunto)
        curtas.append((q, curta))
        if q != pergunta_curta(assunto):
            curtas.append((pergunta_curta(assunto), curta))
        curtas.append(([f"Me explique o que é {assunto}.", f"Você sabe o que é {assunto}?", f"Defina {assunto}."][i % 3],
                       curta))
        longas.append((com_gatilho(0, q), longa))
        longas.append((com_gatilho(1 + i % (len(GATILHOS) - 1), q), longa))
        longas.append((PEDIDOS_TEXTO[i % len(PEDIDOS_TEXTO)].format(assunto), longa.split("\n\n")[0]))
        longas.append((com_gatilho(0, PEDIDOS_TEXTO[(i + 3) % len(PEDIDOS_TEXTO)].format(assunto)), longa))
        if i % 2 == 0:
            longas.append((PEDIDOS_LONGO[i % len(PEDIDOS_LONGO)].format(assunto), longa))
    return [("Conceitos: o que é", curtas), ("Conceitos: resposta longa", longas)]


def gatilho_sections():
    """O gatilho nos temas genéricos (resposta curta -> parágrafo) e nas respostas longas já escritas."""
    temas, longas = [], []
    for i, ((assunto, curta, texto), passado) in enumerate([(t, False) for t in TEMAS] + [(t, True) for t in TEMAS_PASSADO]):
        q = pergunta_curta(assunto, passado)
        temas.append((com_gatilho(i, q), texto))
        if i % 2 == 0:
            temas.append((com_gatilho(0, PEDIDOS_TEXTO[i % len(PEDIDOS_TEXTO)].format(sem_artigo(assunto, i))), texto))
    for i, (assunto, pergunta, texto) in enumerate(LONGAS):
        longas.append((com_gatilho(0, pergunta), texto))
        if i % 2 == 1:
            longas.append((com_gatilho(i, pergunta), texto))
    return [("Gatilho de resposta longa: temas", temas), ("Gatilho de resposta longa: textos longos", longas)]


def novas_conversas():
    """"Quem foi X?" -> "E o que ele fez?", "O que é X?" -> "Explique melhor." e datas em sequência."""
    convs = []
    for i, (nome, g, nasc, morte, q_foi, o_que) in enumerate(PESSOAS_V):
        plural = g == "p"
        foi = "foram" if plural else "foi"
        pron = {"m": "ele", "f": "ela", "p": "eles"}[g]
        fez = "fizeram" if plural else "fez"
        seguinte = [f"E o que {pron} {fez}?", f"O que {pron} {fez}?", f"E o que {pron} {fez} de importante?",
                    f"Por que {pron} {'são' if plural else 'é'} {'famosos' if plural else 'famosa' if g == 'f' else 'famoso'}?"][i % 4]
        conv = [(f"Quem {foi} {nome}?", q_foi), (seguinte, o_que)]
        if nasc and morte and i % 3 == 0:
            Nome = cap(nome)
            conv.append(([f"Em que século {pron} viveu?", f"E quando {pron} nasceu?"][i % 2],
                         f"{Nome} viveu entre {nasc} e {morte}, no {nome_seculo(seculo(nasc))}." if i % 2 == 0
                         else f"{cap(pron)} nasceu em {nasc}."))
        convs.append(conv)
        if i % 4 == 1:
            convs.append([(f"Quem {foi} {nome}?", q_foi), ("Explique melhor.", f"{q_foi} {o_que}")])
    for i, (assunto, curta, longa) in enumerate(CONCEITOS):
        q = pergunta_conceito(assunto)
        convs.append([(q, curta), (["Explique melhor.", "Resposta longa.", "Explique melhor, por favor.",
                                    "Pode dar uma resposta longa?"][i % 4], longa)])
        if i % 5 == 2:
            j = (i * 7 + 3) % len(CONCEITOS)
            convs.append([(q, curta), (f"E {CONCEITOS[j][0]}?", CONCEITOS[j][1])])
    for i, (nome, d, m, a, fato, mais) in enumerate(EV.EVENTOS):
        if d and i % 2 == 0:
            convs.append([(f"Quando foi {nome}?", f"Foi em {data_curta(d, m, a)}."),
                          (["E em que século?", "E em que século foi isso?"][i % 4 // 2],
                           f"No {nome_seculo(seculo(a))}: {a} fica entre {100 * (seculo(a) - 1) + 1} e {100 * seculo(a)}.")])
        elif d:
            convs.append([(f"O que aconteceu em {data_extenso(d, m, a)}?", f"Em {data_curta(d, m, a)}, {fato}."),
                          ("Explique melhor.", f"Em {data_curta(d, m, a)}, {fato}. {mais}")])
    return convs


# =====================================================================
# ACONTECIMENTOS: QUEM FEZ, POR QUÊ, LÍDER, MÊS (tools/eventos2.py) E O NOME DO USUÁRIO / DA LAIKA
# =====================================================================
def _com_artigo(x, contracoes):
    art, _, resto = x.partition(" ")
    return f"{contracoes[art]} {resto}" if art in contracoes and resto else f"{contracoes['']} {x}"


def em_artigo(x):
    """"a queda de Constantinopla" -> "na queda de Constantinopla"."""
    return _com_artigo(x, {"o": "no", "a": "na", "os": "nos", "as": "nas", "": "em"})


def por_artigo(x):
    """"a queda de Constantinopla" -> "pela queda de Constantinopla"."""
    return _com_artigo(x, {"o": "pelo", "a": "pela", "os": "pelos", "as": "pelas", "": "por"})


def _quando(d, m, a):
    return f"Foi em {data_curta(d, m, a)}." if d else f"Foi em {a}."


def detalhes_sections():
    """Quem fez, por que aconteceu, quem estava no poder, o mês, e perguntas que juntam duas coisas."""
    quem, porque, lider, juntas, meses = [], [], [], [], []
    for i, (nome, d, m, a, fato, mais) in enumerate(EV.EVENTOS):
        Nome = cap(nome)
        if d:
            mes = MESES[m - 1][0]
            resp_mes = f"{Nome} foi em {mes} de {a}, no dia {d}."
            meses.append(([f"Em que mês foi {nome}?", f"{Nome} foi em que mês?", f"Em que mês aconteceu {nome}?",
                           f"{Nome} aconteceu em que mês?"][i % 4], resp_mes))
            meses.append(([f"Em que mês e ano foi {nome}?", f"Foi em que mês {nome}?", f"Qual foi o mês {de_artigo(nome)}?"]
                          [i % 3], resp_mes))
        if nome not in EV2.DETALHES:
            continue
        q, pq, lq, la = EV2.DETALHES[nome]
        quem.append(([f"Quem foi o responsável {por_artigo(nome)}?", f"Quem liderou {nome}?",
                      f"Quem esteve à frente {de_artigo(nome)}?", f"Quem fez {nome}?"][i % 4], q))
        porque.append(([f"Por que aconteceu {nome}?", f"Qual foi o motivo {de_artigo(nome)}?",
                        f"Por que {nome} aconteceu?", f"O que causou {nome}?"][i % 4], pq))
        if i % 2 == 0:
            porque.append(([f"Qual foi a causa {de_artigo(nome)}?", f"Por que houve {nome}?"][i % 4 // 2], pq))
        if lq:
            lider.append((lq, la))
            lider.append((f"{lq[:-1]}, e em que ano foi isso?", f"{la} Isso foi em {a}."))
        juntas.append((f"O que foi {nome} e por que aconteceu?", f"{cap(fato)}. {pq}"))
        juntas.append(([f"O que aconteceu {em_artigo(nome)}, quando?", f"O que aconteceu {em_artigo(nome)} e quando foi?",
                        f"O que aconteceu {em_artigo(nome)}, e quando?"][i % 3],
                       f"Em {data_curta(d, m, a) if d else a}, {fato}."))
        juntas.append(([f"Quando foi {nome} e quem fez isso?", f"Quando aconteceu {nome} e quem participou?"][i % 2],
                       f"{_quando(d, m, a)} {q}"))
        juntas.append((f"Quem foi o responsável {por_artigo(nome)} e por quê?", f"{q} {pq}"))
    return [("Acontecimentos: quem fez", quem), ("Acontecimentos: por quê", porque),
            ("Acontecimentos: quem estava no poder", lider), ("Acontecimentos: duas perguntas em uma", juntas),
            ("Acontecimentos: em que mês", meses)]


def detalhes_conversas():
    """"O que foi X e por que aconteceu?" -> "Mas quando?", "O que aconteceu em X, quando?" -> "Mas quem fez isso?",
    "Quando foi X?" -> "Mas em que mês foi?" -> "E o dia?" e outras."""
    convs = []
    for i, (nome, d, m, a, fato, mais) in enumerate(EV.EVENTOS):
        quando = _quando(d, m, a)
        if d:
            mes = MESES[m - 1][0]
            conv = [(["Quando foi {}?", "Em que ano foi {}?", "Quando aconteceu {}?"][i % 3].format(nome), f"Foi em {a}."),
                    (["Mas em que mês foi?", "Foi em que mês?", "E em que mês?", "Em que mês foi isso?", "E o mês?",
                      "Mas foi em que mês?"][i % 6], f"Foi em {mes} de {a}.")]
            if i % 2 == 0:
                conv.append((["E o dia?", "Em que dia?", "Foi em que dia?", "E em que dia foi?"][i % 4],
                             f"Foi no dia {d} de {mes}."))
            convs.append(conv)
        if nome not in EV2.DETALHES:
            continue
        q, pq, lq, la = EV2.DETALHES[nome]
        convs.append([(f"O que foi {nome} e por que aconteceu?", f"{cap(fato)}. {pq}"),
                      (["Mas quando?", "E quando foi isso?", "Mas quando foi?", "Quando foi isso?"][i % 4], quando)])
        convs.append([([f"O que aconteceu {em_artigo(nome)}, quando?", f"O que aconteceu {em_artigo(nome)}, e quando?"][i % 2],
                       f"Em {data_curta(d, m, a) if d else a}, {fato}."),
                      (["Mas quem fez isso?", "E quem fez isso?", "Quem foi o responsável?", "Mas quem estava por trás disso?"]
                       [i % 4], q)])
        convs.append([(f"Por que aconteceu {nome}?", pq),
                      (["E quem fez isso?", "Mas quem liderou?", "Quem foi o responsável?"][i % 3], q)])
        convs.append([(f"Quem foi o responsável {por_artigo(nome)}?", q),
                      (["E por quê?", "Mas por quê?", "Por que fizeram isso?"][i % 3], pq)])
        if lq:
            convs.append([(lq, la), (["Mas quando foi isso?", "E em que ano foi?", "Quando foi isso?"][i % 3], quando)])
            convs.append([(f"O que foi {nome}?", f"{cap(fato)}."),
                          (["Quem era o líder na época?", "E quem governava na época?", "Quem estava no poder?"][i % 3], la)])
    return convs


NOMES_USUARIO = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Heitor", "Isabela", "João",
                 "Larissa", "Marcos", "Natália", "Otávio", "Paula", "Rafael", "Sara", "Thiago", "Valéria", "Yuri",
                 "Ana Maria", "José Carlos"]
FRASES_NOME = ["{n} é uma pessoa muito especial.", "{n} acordou cedo e foi caminhar no parque.",
               "Hoje é um ótimo dia para {n} aprender algo novo.", "{n} gosta de ler um bom livro antes de dormir.",
               "Todos ficaram felizes quando {n} chegou à festa.", "{n}, você é capaz de conseguir tudo o que quiser!",
               "O sorriso de {n} ilumina qualquer lugar.", "{n} tem muitos amigos e adora conversar."]
PEDIDOS_NOME = ["Faça uma frase usando o meu nome.", "Escreva uma frase com o meu nome.", "Use o meu nome numa frase.",
                "Crie uma frase com o meu nome.", "Faça uma frase bonita com o meu nome.", "Me escreva uma frase com meu nome."]


def nomes_sections():
    """Pedidos com o nome do usuário (que a memória põe no Contexto) e com o nome da Laika."""
    usuario, laika = [], []
    for i, n in enumerate(NOMES_USUARIO):
        ctx = f"O nome do usuário é {n}."
        for k in range(2):
            usuario.append((rag_question(PEDIDOS_NOME[(i + k) % len(PEDIDOS_NOME)], ctx),
                            FRASES_NOME[(i + 3 * k) % len(FRASES_NOME)].format(n=n)))
        letras = sum(c.isalpha() for c in n)
        extras = [("Quantas letras tem o meu nome?", f"O seu nome, {n}, tem {letras} letras."),
                  ("Qual é a primeira letra do meu nome?", f"A primeira letra do seu nome é {n[0]}."),
                  ("Escreva uma mensagem de bom dia com o meu nome.", f"Bom dia, {n}! Que o seu dia seja leve e cheio de coisas boas."),
                  ("Faça um poema curto com o meu nome.", f"{n}, nome de gente querida,\nque deixa mais bonita a vida.\nCom um sorriso no olhar,\n{n} faz o mundo brilhar."),
                  ("Me deseje boa noite usando o meu nome.", f"Boa noite, {n}! Durma bem e tenha bons sonhos."),
                  ("Escreva o meu nome ao contrário.", f"O seu nome ao contrário fica {n[::-1].capitalize()}.")]
        for q, a in [extras[i % len(extras)], extras[(i + 2) % len(extras)]]:
            usuario.append((rag_question(q, ctx), a))
    ctx_laika = "O nome da assistente é Laika."
    for q, a in [("Faça uma frase com o seu nome.", "Meu nome é Laika, e eu adoro aprender coisas novas."),
                 ("Escreva uma frase usando o seu nome.", "A Laika está sempre pronta para ajudar."),
                 ("Use o seu nome numa frase.", "Laika é o nome de uma cadela que foi ao espaço em 1957, e hoje também é o meu."),
                 ("Quantas letras tem o seu nome?", "O meu nome, Laika, tem 5 letras."),
                 ("Qual é a primeira letra do seu nome?", "A primeira letra do meu nome é L, de Laika."),
                 ("Faça um poema curto com o seu nome.", "Laika, nome de estrela,\nque viajou pelo céu.\nHoje sou eu quem conversa,\ncom você, aqui, sem véu.")]:
        laika.append((rag_question(q, ctx_laika), a))
        laika.append((q, a))
    return [("Nome do usuário (Contexto da memória)", usuario), ("Nome da Laika", laika)]


def nomes_conversas():
    """"Faça uma frase com o nome dele" depois de "Quem foi X?", o nome de um amigo e o do próprio usuário."""
    convs = []
    for i, (nome, g, nasc, morte, q_foi, o_que) in enumerate(PESSOAS_V):
        if g == "p":
            continue
        frase = _FRASES.split(o_que)[0]
        sobrenome = nome.split()[-1]
        if sobrenome not in frase:
            continue
        pron = "dele" if g == "m" else "dela"
        pedido = [f"Faça uma frase com o nome {pron}.", f"Escreva uma frase usando o nome {pron}.",
                  f"Use o nome {pron} numa frase.", "Crie uma frase com esse nome."][i % 4]
        convs.append([(f"Quem foi {nome}?", q_foi), (pedido, frase)])
    amigos = [("Minha amiga se chama Júlia.", "dela", "Júlia"), ("Meu irmão se chama Pedro.", "dele", "Pedro"),
              ("Minha mãe se chama Teresa.", "dela", "Teresa"), ("Meu cachorro se chama Thor.", "dele", "Thor"),
              ("Minha professora se chama Helena.", "dela", "Helena"), ("Meu avô se chama Antônio.", "dele", "Antônio"),
              ("Minha gata se chama Mel.", "dela", "Mel"), ("Meu melhor amigo se chama Lucas.", "dele", "Lucas")]
    for i, (msg, pron, n) in enumerate(amigos):
        convs.append([(msg, f"Que nome bonito! {n} parece ser alguém muito querido."),
                      ([f"Faça uma frase com o nome {pron}.", f"Escreva uma frase usando o nome {pron}."][i % 2],
                       FRASES_NOME[i % len(FRASES_NOME)].format(n=n).replace("pessoa", "companhia" if "cachorro" in msg or "gata" in msg else "pessoa"))])
    for i, n in enumerate(NOMES_USUARIO[:12]):
        convs.append([(f"Meu nome é {n}.", f"Prazer, {n}! Vou lembrar o seu nome."),
                      (PEDIDOS_NOME[i % len(PEDIDOS_NOME)], FRASES_NOME[i % len(FRASES_NOME)].format(n=n))])
    convs.append([("Qual é o seu nome?", "Meu nome é Laika."),
                  ("Faça uma frase com ele.", "Laika é o nome de uma cadela que foi ao espaço em 1957, e hoje também é o meu.")])
    convs.append([("Como você se chama?", "Eu me chamo Laika."),
                  ("Use esse nome numa frase.", "A Laika adora conversar e aprender coisas novas.")])
    return convs


def identidade_conversas():
    """Perguntas sobre ela depois de perguntas sobre reis e pessoas: o assunto anterior não muda quem ela é."""
    convs, k = [], 0
    for nome, (q, pq, lq, la) in EV2.DETALHES.items():
        if lq:
            convs.append([(lq, la), ID4.DEPOIS_DO_ASSUNTO[k % len(ID4.DEPOIS_DO_ASSUNTO)]])
            k += 1
    for i, (nome, g, nasc, morte, q_foi, o_que) in enumerate(PESSOAS_V):
        if i % 3 == 0:
            convs.append([(f"Quem foi {nome}?", q_foi), ID4.DEPOIS_DO_ASSUNTO[k % len(ID4.DEPOIS_DO_ASSUNTO)]])
            k += 1
    return convs


# =====================================================================
# TÍTULOS DE CHAT (app 1.10): o app pede "Dê um título curto para esta conversa: <1ª mensagem>"
# (android/core Texto.PEDIDO_TITULO) depois da primeira resposta de cada chat.
# =====================================================================
PEDIDO_TITULO = "Dê um título curto para esta conversa: "
TITULOS_FIXOS = [
    ("Oi, tudo bem?", "Cumprimento"), ("Bom dia, Laika!", "Bom dia"), ("Olá! Como você está?", "Conversa"),
    ("Meu nome é Ana.", "Apresentação"), ("Me ajude a estudar para a prova de matemática.", "Estudo de matemática"),
    ("Escreva um poema sobre o mar.", "Poema sobre o mar"), ("Conte uma história curta.", "História curta"),
    ("Quanto é 25 vezes 4?", "Conta de multiplicação"), ("Quanto é 120 dividido por 8?", "Conta de divisão"),
    ("Corrija esta frase: eu fui na escola ontem.", "Correção de frase"),
    ("Resuma em uma frase: O menino acordou cedo e foi para a escola.", "Resumo de texto"),
    ("Me dê dicas para dormir melhor.", "Dicas para dormir"), ("Como fazer um bolo simples?", "Receita de bolo"),
    ("Escreva uma mensagem de aniversário para minha mãe.", "Mensagem de aniversário"),
    ("Quem é você?", "Sobre a Laika"), ("Qual é o seu nome?", "Nome da Laika"),
    ("Complete a frase: Quem espera", "Completar frase"), ("Traduza bom dia para o inglês.", "Tradução"),
    ("Estou triste hoje.", "Conversa de apoio"), ("Lembre que amanhã tenho dentista.", "Lembrete"),
]
CAPITAIS_TITULO = ["da França", "da Itália", "do Japão", "da Argentina", "de Portugal", "da Alemanha", "do Canadá",
                   "do Egito", "do Peru", "da Austrália", "do Chile", "do México", "da Espanha", "da Índia", "da China"]


def _sem_artigo_titulo(x):
    art, _, resto = x.partition(" ")
    return cap(resto if art in ("o", "a", "os", "as") and resto else x)


def titulos_sections():
    """Pares (primeira mensagem -> título curto): o assunto, sem "O que é", em 1 a 5 palavras."""
    pares = list(TITULOS_FIXOS)
    for pais in CAPITAIS_TITULO:
        pares.append((f"Qual é a capital {pais}?", f"Capital {pais}"))
    temas = [(t, False) for t in TEMAS] + [(t, True) for t in TEMAS_PASSADO]
    for i, ((assunto, curta, texto), passado) in enumerate(temas):
        x = sem_artigo(assunto, i)
        if i % 3 == 0:
            art, _, resto = assunto.partition(" ")
            pares.append((f"Faça um texto sobre {x}.",
                          "Texto sobre " + (resto if art in ("o", "a", "os", "as") and resto else assunto)))
        elif i % 3 == 1:
            verbo = "foi" if passado else ("são" if assunto.split(" ", 1)[0] in ("os", "as") else "é")
            pares.append((f"O que {verbo} {assunto}?", _sem_artigo_titulo(assunto)))
        else:
            pares.append((f"Me fale sobre {x}.", _sem_artigo_titulo(assunto)))
    for i, (nome, g, nasc, morte, q_foi, o_que) in enumerate(PESSOAS_V):
        pares.append(([f"Quem foi {nome}?", f"O que {nome} fez?", f"Me conte sobre {nome}."][i % 3], nome))
    for i, (nome, d, m, a, fato, mais) in enumerate(EV.EVENTOS):
        pares.append(([f"Quando foi {nome}?", f"O que foi {nome}?", f"Por que aconteceu {nome}?"][i % 3],
                      _sem_artigo_titulo(nome)))
    # O app só aceita títulos de até 6 palavras e 40 letras (Texto.limparTitulo).
    pares = [(q, a) for q, a in pares if len(a) <= 40 and len(a.split()) <= 6]
    return [("Títulos de chat", [(PEDIDO_TITULO + q, a) for q, a in pares])]


def _chave(question):
    return " ".join(re.sub(r"[^\w\s]", " ", question.lower()).split())


def build():
    rng = random.Random(42)
    sections = []

    sections.append(("Conversa", [ex(q, a) for q, a in CONVERSA]))

    defs = []
    for i, (q, a) in enumerate(DEFINICOES):
        defs.append(ex(f"O que é {q}?", a))
        if i % 3 == 0:  # uma pergunta alternativa a cada três
            word = q.split(" ", 1)[1] if q.split(" ", 1)[0] in {"o", "a", "um", "uma"} else q
            defs.append(ex(ALT_DEF[(i // 3) % len(ALT_DEF)].format(w=word, q=q), a))
    sections.append(("Definições", defs))

    caps = []
    forms = ["Qual é a capital {p} {c}?", "Qual a capital {p} {c}?", "Me diga a capital {p} {c}.",
             "Qual cidade é a capital {p} {c}?"]
    for i, (pais, prep, capital, continente, lingua) in enumerate(CAPITAIS):
        caps.append(ex(forms[i % len(forms)].format(p=prep, c=pais), f"A capital {prep} {pais} é {capital}."))
        caps.append(ex(f"De que país {capital} é a capital?", f"{capital} é a capital {prep} {pais}."))
        if i % 2 == 0:
            caps.append(ex(f"Em que continente fica {'o ' if prep in ('do',) else 'a ' if prep == 'da' else 'os ' if prep == 'dos' else ''}{pais}?",
                           f"{'O ' if prep == 'do' else 'A ' if prep == 'da' else 'Os ' if prep == 'dos' else ''}{pais} fica {continente}."))
        if lingua and i % 2 == 1:
            caps.append(ex(f"Que língua se fala {'no' if prep == 'do' else 'na' if prep == 'da' else 'nos' if prep == 'dos' else 'em'} {pais}?",
                           f"{'No' if prep == 'do' else 'Na' if prep == 'da' else 'Nos' if prep == 'dos' else 'Em'} {pais} se fala {lingua}."))
    for i, (estado, prep, capital) in enumerate(ESTADOS):
        caps.append(ex(f"Qual é a capital {prep} {estado}?", f"A capital {prep} {estado} é {capital}."))
    sections.append(("Países, capitais e estados", caps))

    obras = []
    for i, (obra, autor) in enumerate(LIVROS):
        q = ["Quem escreveu {}?", "Quem é o autor de {}?", "Qual escritor escreveu {}?"][i % 3]
        obras.append(ex(q.format(obra), f"{obra} foi escrito por {autor}."))
    for nome, desc in PESSOAS:
        obras.append(ex(f"Quem foi {nome}?", desc))
    sections.append(("Livros e pessoas", obras))

    sections.append(("Conhecimentos gerais", [ex(q, a) for q, a in FATOS]))

    ling = []
    for i, (a, b) in enumerate(ANTONIMOS):
        q = ["Qual é o contrário de {}?", "Qual é o antônimo de {}?", "O que é o oposto de {}?"][i % 3]
        ling.append(ex(q.format(a), f"O contrário de {a} é {b}."))
    for a, b in PLURAIS:
        ling.append(ex(f"Qual é o plural de {a}?", f"O plural de {a} é {b}."))
    for a, b in FEMININOS:
        ling.append(ex(f"Qual é o feminino de {a}?", f"O feminino de {a} é {b}."))
    for a, b in SINONIMOS:
        ling.append(ex(f"Me dê um sinônimo de {a}.", f"Um sinônimo de {a} é {b}."))
    for n, palavra in EXTENSO.items():
        if n % 3 == 0 or n >= 20:
            ling.append(ex(f"Como se escreve {n} por extenso?", f"{n} por extenso é {palavra}."))
    sections.append(("Linguagem", ling))

    mat = []
    for _ in range(45):
        op = rng.choice("+-x÷")
        a, b = rng.randint(1, 20), rng.randint(1, 12)
        if op == "+":
            q, r, nome = f"{a} + {b}", a + b, "mais"
        elif op == "-":
            a, b = max(a, b), min(a, b)
            q, r, nome = f"{a} - {b}", a - b, "menos"
        elif op == "x":
            a = rng.randint(1, 10)
            q, r, nome = f"{a} × {b}", a * b, "vezes"
        else:
            r = rng.randint(1, 10)
            a = r * b
            q, nome = f"{a} ÷ {b}", "dividido por"
        form = rng.choice(["Quanto é {}?", "Quanto dá {}?", "Calcule {}.", "Qual é o resultado de {}?"])
        mat.append(ex(form.format(q), f"{q} = {r}."))
    for a, b in [(2, 2), (3, 3), (5, 5), (10, 10), (4, 3), (6, 2)]:
        mat.append(ex(f"Quanto é {EXTENSO[a]} mais {EXTENSO[b]}?",
                      f"{EXTENSO[a].capitalize()} mais {EXTENSO[b]} é igual a {EXTENSO.get(a + b, a + b)}."))
    sections.append(("Matemática", mat))

    comp = []
    for i, (inicio, fim) in enumerate(DITADOS):
        q = ["Complete o ditado: {}", "Complete a frase: {}", "Complete: {}", "Termine o ditado: {}"][i % 4]
        comp.append(ex(q.format(inicio), fim))
    for i, (inicio, fim) in enumerate(FRASES):
        q = ["Complete a frase: {}", "Complete: {}", "Termine a frase: {}"][i % 3]
        comp.append(ex(q.format(inicio), fim))
    for i, (inicio, fim) in enumerate(HISTORIAS):
        q = ["Continue a história: {}", "Complete a frase: {}", "Continue: {}"][i % 3]
        comp.append(ex(q.format(inicio), fim))
    sections.append(("Complete a frase", comp))

    res = []
    for i, (name, idx, resumo) in enumerate(RESUMOS):
        trecho = paragraphs(name)[idx]
        words = len(trecho.split())
        if words > 120:
            print(f"aviso: trecho longo ({words} palavras) em {name}#{idx}")
        res.append(ex(PEDIDOS_RESUMO[i % len(PEDIDOS_RESUMO)].format(trecho), resumo))
    res += [ex(q, a) for q, a in RESUMOS_HISTORIA]
    sections.append(("Resumos (textos de data/modern)", res))
    sections += extra_sections(rng)
    sections += extra_sections_3(rng)
    write_simple_texts()

    # Perguntas genéricas: só entram as que ainda não existem (mesma pergunta, ignorando pontuação).
    identidade = IDENTIDADE + D3.IDENTIDADE_2
    vistas = {_chave(q) for q, _ in identidade}
    novas_id = [(q, a) for q, a in GC.IDENTIDADE_3 if _chave(q) not in vistas]
    identidade = identidade + novas_id
    vistas |= {_chave(q) for q, _ in novas_id}
    # 1.9: mais formas de perguntar quem ela é e negações de personagem ("Você é o rei do Reino Unido?").
    novas_id = [(q, a) for q, a in ID4.pares() if _chave(q) not in vistas]
    # As mesmas perguntas com o Contexto da memória também respondem "Laika" (o app antigo ainda o põe).
    novas_id += [(rag_question(q, "O nome da assistente é Laika."), a) for q, a in
                 [("Qual é o seu nome?", "Meu nome é Laika."), ("Como você se chama?", "Eu me chamo Laika."),
                  ("Quem é você?", ID4.QUEM[0]), ("Seu nome?", "Meu nome é Laika.")]]
    identidade = identidade + novas_id
    vistas |= {_chave(q) for q, _ in novas_id}
    vistas |= {_chave(item.split("<|user|>", 1)[1].split("<|assistant|>", 1)[0]) for _, items in sections for item in items}
    genericas, leitura_genericas = generic_sections()
    genericas += longas_sections(rng)
    novas_secoes = pessoas_sections() + datas_sections(rng) + conceitos_sections() + gatilho_sections() + detalhes_sections() + nomes_sections() + titulos_sections() + resumos_sections()
    genericas += novas_secoes
    repetidas = 0
    for title, pares in genericas:
        novos = []
        for q, a in pares:
            if _chave(q) in vistas:
                repetidas += 1
                continue
            vistas.add(_chave(q))
            novos.append(ex(q, a))
        sections.append((title, novos))
    novas = sum(len(items) for title, items in sections if title.startswith("Genéricas"))
    titulos = {title for title, _ in novas_secoes}
    print(f"Pessoas, datas, conceitos e gatilho: {sum(len(i) for t, i in sections if t in titulos)} novas no pergeresp")
    print(f"Perguntas genéricas: {novas} novas no pergeresp + {len(novas_id)} de identidade + "
          f"{len(leitura_genericas)} com Contexto ({repetidas} repetidas foram puladas)")

    header = ("# Gerado por tools/gerar_pergeresp.py. Linhas começando com # são comentários.\n"
              "# Para adicionar exemplos seus, crie outro .txt em data/qa/.\n\n")
    total = 0
    with open(QA_DIR / "pergeresp.txt", "w", encoding="utf-8") as f:
        f.write(header)
        for title, items in sections:
            f.write(f"# ===== {title} ({len(items)}) =====\n\n")
            f.write("\n".join(items) + "\n")
            total += len(items)
            print(f"{title}: {len(items)}")
    with open(QA_DIR / "identidade.txt", "w", encoding="utf-8") as f:
        f.write("# Quem é a Laika. Este arquivo tem peso maior no fine-tuning.\n\n")
        f.write("\n".join(ex(q, a) for q, a in identidade) + "\n")
    convs = conversas() + novas_conversas() + detalhes_conversas() + nomes_conversas() + identidade_conversas()
    with open(QA_DIR / "conversas.jsonl", "w", encoding="utf-8") as f:
        for c in convs:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"conversas.jsonl: {len(convs)} conversas de várias trocas (memória de IA)")
    leitura, _ = leitura_examples()
    leitura += leitura_simples() + leitura_genericas
    with open(QA_DIR / "leitura.txt", "w", encoding="utf-8") as f:
        f.write("# Interpretação de texto: Contexto + Pergunta, no mesmo formato que o RAG usa.\n\n")
        f.write("\n".join(leitura) + "\n")
    print(f"pergeresp.txt: {total} exemplos | identidade.txt: {len(identidade)} | leitura.txt: {len(leitura)}")


if __name__ == "__main__":
    build()
