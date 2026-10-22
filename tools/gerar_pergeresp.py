"""Gera data/qa/pergeresp.txt e data/qa/identidade.txt.

Rode:  python tools/gerar_pergeresp.py
ATENÇÃO: sobrescreve esses dois arquivos. Para adicionar perguntas suas sem perder nada,
crie outro arquivo em data/qa/ (por exemplo data/qa/meus_exemplos.txt).
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_utils import rag_question, content_words  # noqa: E402
import dados_extra as D1  # noqa: E402
import dados_extra2 as D2  # noqa: E402
import leitura as L  # noqa: E402
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
        f.write("\n".join(ex(q, a) for q, a in IDENTIDADE) + "\n")
    leitura, _ = leitura_examples()
    with open(QA_DIR / "leitura.txt", "w", encoding="utf-8") as f:
        f.write("# Interpretação de texto: Contexto + Pergunta, no mesmo formato que o RAG usa.\n\n")
        f.write("\n".join(leitura) + "\n")
    print(f"pergeresp.txt: {total} exemplos | identidade.txt: {len(IDENTIDADE)} | leitura.txt: {len(leitura)}")


if __name__ == "__main__":
    build()
