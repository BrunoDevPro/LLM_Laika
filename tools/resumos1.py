"""Resumos escritos à mão (parte 1): resumos dos textos longos de tools/longas1..3.py.

Cada item: pergunta do texto em LONGAS -> (resumo em uma frase, resumo curto em duas frases, três tópicos).
Os resumos dizem a ideia principal com outras palavras: não copiam frases do texto (os resumos extrativos,
que copiavam uma frase, ensinavam o modelo a copiar). O gerador monta "Resuma em uma frase: <texto>",
"Resuma o texto: <texto>", "Resuma em tópicos: <texto>" e outras formas (gerar_pergeresp.resumos_sections).
"""

RESUMOS = {
    "Como funcionam os vulcões?": (
        "Os vulcões soltam lava, cinzas e gases quando a pressão do magma fica grande demais, e a maioria deles "
        "fica nas bordas das placas tectônicas.",
        "Os vulcões entram em erupção quando o magma, cheio de gases, sobe e rompe a crosta. As erupções podem ser "
        "calmas ou explosivas, e o solo fértil das cinzas atrai moradores para perto deles.",
        ["O magma sobe e sai quando a pressão dos gases aumenta.",
         "Há erupções calmas e explosivas.",
         "As cinzas deixam o solo fértil."]),
    "Como funciona o ciclo da água?": (
        "A água circula sem parar entre o mar, o ar e a terra, evaporando, formando nuvens e voltando como chuva.",
        "Com o calor do Sol, a água evapora, vira nuvem e cai como chuva. Depois volta aos rios e ao mar ou entra "
        "no solo, num ciclo que o desmatamento e a poluição prejudicam.",
        ["O Sol faz a água evaporar e formar nuvens.",
         "A chuva devolve a água aos rios e ao solo.",
         "Desmatar e poluir atrapalham o ciclo."]),
    "O que é a fotossíntese?": (
        "Na fotossíntese, as plantas usam a luz do Sol para transformar água e gás carbônico em alimento, "
        "liberando o oxigênio que respiramos.",
        "As plantas e as algas fabricam o próprio alimento com luz, água e gás carbônico. O processo solta "
        "oxigênio e sustenta quase todas as cadeias alimentares.",
        ["A clorofila captura a luz do Sol.",
         "A planta produz glicose e libera oxigênio.",
         "Quase toda a vida depende desse processo."]),
    "Como é o Sistema Solar?": (
        "O Sistema Solar é o Sol com oito planetas e outros corpos menores girando em volta dele, presos pela "
        "sua gravidade.",
        "O Sol segura com a gravidade planetas, luas, asteroides e cometas. Os quatro planetas de dentro são "
        "rochosos, os de fora são gigantes de gás e gelo, e só a Terra tem vida conhecida.",
        ["O Sol tem quase toda a massa do sistema.",
         "Os planetas internos são rochosos e os externos, gigantes.",
         "A Terra é o único planeta com vida conhecida."]),
    "O que é um buraco negro?": (
        "Um buraco negro é uma região com gravidade tão forte que nem a luz escapa, formada muitas vezes pelo "
        "colapso de uma estrela enorme.",
        "Buracos negros surgem quando estrelas gigantes desabam no fim da vida. Eles não podem ser vistos "
        "diretamente, mas se revelam pelo efeito no que está em volta, e a Via Láctea tem um no centro.",
        ["Nem a luz escapa de um buraco negro.",
         "Muitos nascem do colapso de estrelas grandes.",
         "São percebidos pelo efeito no que está perto."]),
    "Como nascem e morrem as estrelas?": (
        "As estrelas nascem em nuvens de gás quando começa a fusão nuclear, e o fim de cada uma depende do seu "
        "tamanho.",
        "A gravidade junta gás e poeira até o centro esquentar e iniciar a fusão, e assim nasce uma estrela. As "
        "parecidas com o Sol viram anãs brancas, e as muito grandes explodem como supernovas.",
        ["Estrelas se formam em nuvens de gás e poeira.",
         "A fusão do hidrogênio produz a energia delas.",
         "O tamanho decide se viram anãs brancas ou explodem."]),
    "O que sabemos sobre a Lua?": (
        "A Lua, único satélite natural da Terra, provavelmente surgiu de uma grande colisão e reflete a luz do "
        "Sol, o que cria as suas fases.",
        "A Lua deve ter se formado com os pedaços de um choque entre a Terra e um corpo do tamanho de Marte. Ela "
        "mostra sempre a mesma face, provoca as marés e foi visitada por astronautas entre 1969 e 1972.",
        ["A Lua veio provavelmente de uma colisão com a Terra.",
         "As fases vêm da luz do Sol refletida.",
         "Ela causa as marés e já foi visitada por astronautas."]),
    "Quem foram os dinossauros?": (
        "Os dinossauros foram répteis que dominaram a Terra por milhões de anos e quase todos sumiram depois da "
        "queda de um asteroide.",
        "Havia dinossauros de todos os tamanhos, e os conhecemos pelos fósseis. A maioria desapareceu há cerca de "
        "66 milhões de anos, depois de um asteroide, mas as aves descendem deles.",
        ["Dominaram a Terra por mais de 160 milhões de anos.",
         "Um asteroide causou o fim da maioria.",
         "As aves são suas descendentes."]),
    "O que é a evolução das espécies?": (
        "A evolução é a mudança lenta dos seres vivos ao longo das gerações, guiada pela seleção natural.",
        "Os indivíduos com características mais vantajosas sobrevivem e deixam mais filhos, e assim a espécie muda. "
        "Darwin e Wallace explicaram esse mecanismo, e o DNA mostra que todos os seres vivos são parentes.",
        ["As espécies mudam devagar ao longo de gerações.",
         "A seleção natural favorece quem se adapta melhor.",
         "Todos os seres vivos têm parentesco."]),
    "O que é o DNA?": (
        "O DNA é a molécula que guarda, num código de quatro letras, as instruções para formar e fazer funcionar "
        "um ser vivo.",
        "Em forma de dupla hélice, o DNA tem genes que ensinam a célula a fabricar proteínas. Herdamos metade da "
        "mãe e metade do pai, e o seu estudo ajuda a medicina e a identificar pessoas.",
        ["O DNA é um código escrito com A, T, C e G.",
         "Os genes comandam a produção de proteínas.",
         "Metade vem da mãe e metade do pai."]),
    "O que são as células?": (
        "As células são as menores unidades vivas, e todos os seres vivos são formados por uma ou por muitas delas.",
        "Algumas criaturas têm uma célula só, e o corpo humano tem trilhões. Elas se especializam em funções "
        "diferentes e se dividem para o corpo crescer e se renovar.",
        ["A célula é a menor parte viva de um ser vivo.",
         "Elas se especializam, como as dos músculos e do sangue.",
         "Dividindo-se, elas permitem o crescimento."]),
    "O que são as bactérias?": (
        "As bactérias são seres de uma única célula, presentes em quase todo lugar, e a maioria é inofensiva ou útil.",
        "Elas ajudam na digestão, decompõem restos na natureza e servem para fazer iogurte e queijo. Algumas causam "
        "doenças, e o uso errado de antibióticos cria bactérias resistentes.",
        ["Bactérias são microscópicas e estão em toda parte.",
         "Muitas são úteis para o corpo e a natureza.",
         "Antibiótico sem necessidade gera resistência."]),
    "O que são os vírus?": (
        "Os vírus são partículas que só se multiplicam dentro de células vivas e causam doenças que os "
        "antibióticos não curam.",
        "Formados por material genético numa capa de proteína, os vírus usam as células para se copiar. Vacinas e "
        "hábitos como lavar as mãos são as melhores formas de se proteger.",
        ["Vírus precisam de uma célula para se reproduzir.",
         "Causam gripe, sarampo e dengue, entre outras doenças.",
         "Vacinas e higiene ajudam a evitá-los."]),
    "O que é a gravidade?": (
        "A gravidade é a atração entre tudo o que tem massa, a força que nos prende ao chão e mantém os planetas "
        "em órbita.",
        "Quanto mais massa, mais forte a atração, que diminui com a distância. Newton a descreveu como uma força e "
        "Einstein, como uma curvatura do espaço e do tempo.",
        ["Tudo o que tem massa se atrai.",
         "Ela segura os planetas em volta do Sol.",
         "Newton e Einstein a explicaram."]),
    "O que é a eletricidade?": (
        "A eletricidade é a energia do movimento de cargas elétricas, gerada nas usinas e usada para fazer "
        "funcionar quase todos os aparelhos.",
        "A corrente elétrica passa bem pelos condutores e é bloqueada pelos isolantes. As usinas a produzem girando "
        "ímãs em bobinas, e é preciso cuidado porque ela pode causar choques graves.",
        ["A corrente é o movimento organizado de elétrons.",
         "Usinas geram eletricidade girando ímãs.",
         "Fios e aparelhos molhados podem dar choque."]),
    "O que é o magnetismo?": (
        "O magnetismo é a força com que os ímãs atraem ou repelem outros materiais, e a própria Terra se comporta "
        "como um ímã gigante.",
        "Polos diferentes se atraem e polos iguais se repelem. O campo magnético da Terra orienta a bússola, nos "
        "protege das partículas do Sol e forma as auroras.",
        ["Todo ímã tem polo norte e polo sul.",
         "A Terra é um grande ímã e guia a bússola.",
         "Magnetismo e eletricidade movem motores e geradores."]),
    "O que é a luz?": (
        "A luz é uma forma de energia muito rápida que atravessa até o vácuo, e a luz branca é a mistura de todas "
        "as cores.",
        "Ela viaja a cerca de 300 mil quilômetros por segundo e chega do Sol em oito minutos. As cores dos objetos "
        "vêm da luz que eles refletem, e existem ondas parecidas que não vemos, como os raios X.",
        ["A luz é a coisa mais rápida que existe.",
         "A luz branca mistura todas as cores.",
         "Há luz invisível, como o ultravioleta."]),
    "Como o som funciona?": (
        "O som é uma vibração que se espalha pelo ar, pela água ou por sólidos até chegar aos nossos ouvidos.",
        "Um objeto vibra, empurra o ar e forma uma onda que faz o tímpano vibrar. Vibrações rápidas dão sons "
        "agudos, as lentas dão sons graves, e no espaço não há som.",
        ["O som é uma onda de vibração.",
         "A velocidade da vibração define se ele é agudo ou grave.",
         "Sem matéria, como no espaço, o som não passa."]),
    "Qual é a importância dos oceanos?": (
        "Os oceanos cobrem a maior parte da Terra, abrigam muita vida e são essenciais para o clima e para o "
        "oxigênio do planeta.",
        "Eles guardam quase toda a água, absorvem calor e gás carbônico e têm algas que produzem oxigênio. A "
        "poluição, a pesca exagerada e o aquecimento ameaçam esse ambiente.",
        ["Os oceanos cobrem cerca de 70% da Terra.",
         "Regulam o clima e produzem oxigênio.",
         "Plástico e pesca exagerada os ameaçam."]),
    "Por que as florestas tropicais são importantes?": (
        "As florestas tropicais guardam a maior parte das espécies do planeta e ajudam a controlar o clima e as "
        "chuvas.",
        "Mesmo ocupando pouco espaço, elas abrigam mais da metade das espécies conhecidas e guardam muito carbono. "
        "Na Amazônia, formam os rios voadores, mas o desmatamento as ameaça.",
        ["Abrigam mais da metade das espécies conhecidas.",
         "Guardam carbono e levam chuva para outras regiões.",
         "O desmatamento é a maior ameaça."]),
    "O que é o aquecimento global?": (
        "O aquecimento global é a subida da temperatura da Terra causada principalmente pela queima de "
        "combustíveis fósseis e pelo desmatamento.",
        "Os gases lançados no ar reforçam o efeito estufa e seguram mais calor. Isso derrete geleiras e aumenta "
        "secas e tempestades, e os países tentam reduzir as emissões.",
        ["A queima de petróleo, carvão e gás aquece a Terra.",
         "O clima fica mais extremo e o mar sobe.",
         "Energia limpa e florestas ajudam a frear o problema."]),
    "O que é o efeito estufa?": (
        "O efeito estufa é o fenômeno natural em que alguns gases seguram o calor e mantêm a Terra quente o "
        "bastante para a vida.",
        "Sem ele, a Terra seria muito gelada. Desde a Revolução Industrial, porém, as pessoas aumentaram esses "
        "gases, e o efeito ficou forte demais, aquecendo o planeta.",
        ["Gases da atmosfera seguram parte do calor.",
         "Sem o efeito estufa, quase não haveria vida.",
         "O excesso causado pelas pessoas aquece a Terra."]),
    "O que são as placas tectônicas?": (
        "A crosta da Terra é dividida em placas que se movem devagar e causam terremotos, vulcões e montanhas.",
        "As placas se afastam, se chocam ou deslizam umas ao lado das outras. Esse movimento separou a Pangeia e "
        "explica por que a América do Sul e a África se encaixam.",
        ["A crosta é feita de grandes placas.",
         "O movimento delas forma montanhas e causa terremotos.",
         "Os continentes já foram um bloco só, a Pangeia."]),
    "Qual é a importância das abelhas?": (
        "As abelhas fazem mel, mas a sua maior importância é polinizar as plantas que dão grande parte da nossa "
        "comida.",
        "Elas vivem em colônias organizadas e levam o pólen de flor em flor, o que permite formar frutos e sementes. "
        "Agrotóxicos, doenças e a destruição de habitats estão diminuindo as abelhas.",
        ["As abelhas vivem em colônias e produzem mel.",
         "A polinização garante muitos alimentos.",
         "As populações estão diminuindo."]),
    "Como vivem os golfinhos?": (
        "Os golfinhos são mamíferos marinhos inteligentes que vivem em grupos e se orientam pelo eco dos sons "
        "que emitem.",
        "Eles respiram ar, amamentam os filhotes e caçam em equipe. Comunicam-se com assobios e usam a "
        "ecolocalização, mas sofrem com a poluição e com as redes de pesca.",
        ["Golfinhos são mamíferos e respiram ar.",
         "Vivem e caçam em bandos.",
         "Usam o eco para perceber o ambiente."]),
    "Como são os tubarões?": (
        "Os tubarões são peixes muito antigos, de esqueleto de cartilagem, que raramente atacam pessoas e hoje "
        "estão ameaçados pela pesca.",
        "Eles existem há mais de 400 milhões de anos, trocam os dentes a vida toda e têm sentidos muito apurados. "
        "Existem centenas de espécies, e milhões de tubarões são pescados por ano.",
        ["Tubarões existem desde antes dos dinossauros.",
         "O esqueleto deles é de cartilagem.",
         "Correm mais perigo de nós do que nós deles."]),
    "Como vivem as formigas?": (
        "As formigas vivem em colônias organizadas, com rainhas e operárias, e se comunicam principalmente por "
        "cheiros.",
        "As operárias buscam comida, cuidam das larvas e defendem o formigueiro, guiadas por rastros de feromônio. "
        "Algumas cultivam fungos, e todas ajudam o solo e as plantas.",
        ["Cada colônia tem rainhas e muitas operárias.",
         "Elas seguem rastros de cheiro.",
         "As saúvas cultivam fungos com folhas."]),
    "Como as borboletas se desenvolvem?": (
        "As borboletas passam pela metamorfose: ovo, lagarta, crisálida e adulto.",
        "A lagarta come e cresce até formar a crisálida, onde o corpo se transforma por completo. A borboleta "
        "adulta se alimenta de néctar e ajuda a polinizar as flores.",
        ["A metamorfose tem quatro fases.",
         "Na crisálida, a lagarta vira borboleta.",
         "Adultas, elas polinizam flores."]),
    "O que você sabe sobre a onça-pintada?": (
        "A onça-pintada é o maior felino das Américas, uma caçadora poderosa que hoje está ameaçada pela "
        "destruição do seu ambiente.",
        "Ela vive em lugares como a Amazônia e o Pantanal, tem a mordida mais forte entre os felinos e nada muito "
        "bem. Desmatamento, queimadas e caça põem a espécie em risco.",
        ["É o maior felino das Américas.",
         "Caça sozinha e gosta de água.",
         "Está ameaçada pelo desmatamento e pela caça."]),
    "Como uma árvore cresce?": (
        "A árvore nasce de uma semente e cresce para cima e para os lados durante anos, formando anéis de madeira.",
        "A semente germina, solta a raiz e o caule, e as folhas começam a fazer fotossíntese. Com o tempo, a "
        "árvore engrossa, e algumas vivem milhares de anos.",
        ["Tudo começa com a germinação da semente.",
         "Cada ano forma uma nova camada de madeira.",
         "As árvores dão sombra, frutos e abrigo."]),
    "Como acontecem as estações do ano?": (
        "As estações acontecem porque o eixo da Terra é inclinado, e cada hemisfério fica mais virado para o Sol "
        "numa época do ano.",
        "O hemisfério mais exposto recebe luz mais direta e tem verão, enquanto o outro tem inverno. Perto do "
        "Equador, as estações se notam mais pelas chuvas do que pela temperatura.",
        ["A inclinação da Terra causa as estações.",
         "Verão no Brasil é inverno na Europa.",
         "Perto do Equador, a diferença está nas chuvas."]),
    "O que é a camada de ozônio?": (
        "A camada de ozônio filtra os raios ultravioleta do Sol e está se recuperando desde que os países "
        "proibiram os gases que a destruíam.",
        "Ela protege contra queimaduras e câncer de pele. O buraco descoberto nos anos 1980 levou ao Protocolo de "
        "Montreal, um acordo mundial que deu certo.",
        ["O ozônio absorve os raios ultravioleta.",
         "Os CFCs abriram um buraco sobre a Antártida.",
         "O Protocolo de Montreal ajudou a recuperá-la."]),
    "Qual é a importância dos rios?": (
        "Os rios levam água doce para beber, plantar, pescar, transportar e gerar energia, e por isso precisam "
        "ser protegidos.",
        "Eles nascem em nascentes ou geleiras e recebem afluentes até o mar. O Brasil tem bacias enormes, mas o "
        "esgoto, o lixo e o desmatamento das margens poluem os rios.",
        ["Os rios fornecem água e energia.",
         "Muitas cidades nasceram às suas margens.",
         "Esgoto e lixo os poluem."]),
    "Como acontecem os terremotos?": (
        "Os terremotos acontecem quando a tensão acumulada entre as placas tectônicas se solta de repente e faz o "
        "chão tremer.",
        "As rochas travadas se rompem e espalham ondas de vibração, que podem derrubar prédios e causar tsunamis. "
        "Não dá para prever o momento exato, mas construções resistentes salvam vidas.",
        ["Placas travadas acumulam tensão.",
         "A ruptura espalha ondas pelo chão.",
         "Construções firmes reduzem os danos."]),
    "O que são os cometas?": (
        "Os cometas são corpos de gelo e poeira que, perto do Sol, formam uma nuvem brilhante e caudas enormes.",
        "Eles vêm das partes mais distantes do Sistema Solar e passam quase todo o tempo congelados. Com o calor do "
        "Sol, o gelo vira gás, e o Halley volta a cada 76 anos.",
        ["Cometas são feitos de gelo, poeira e rocha.",
         "O Sol forma a coma e as caudas.",
         "O Halley passa perto da Terra a cada 76 anos."]),
    "Por que a água é tão importante para o corpo?": (
        "A água forma boa parte do corpo e participa de quase todas as suas funções, por isso precisa ser reposta "
        "todos os dias.",
        "Ela transporta nutrientes, ajuda a digestão, protege os órgãos e controla a temperatura pelo suor. Como "
        "perdemos água o tempo todo, sede e urina escura são sinais de que falta beber.",
        ["A água é cerca de 60% do peso de um adulto.",
         "Ela controla a temperatura e leva nutrientes.",
         "É preciso repô-la diariamente."]),
    "Como funciona o coração?": (
        "O coração é um músculo que bombeia o sangue para os pulmões e para o corpo inteiro, sem parar.",
        "O lado direito manda o sangue pobre em oxigênio para os pulmões, e o esquerdo manda o sangue oxigenado "
        "para o corpo. Exercícios e hábitos saudáveis o mantêm forte.",
        ["O coração é uma bomba dupla.",
         "Tem quatro cavidades separadas por válvulas.",
         "Bons hábitos o protegem."]),
    "Como funcionam os pulmões?": (
        "Nos pulmões, o ar que respiramos entrega oxigênio ao sangue e leva embora o gás carbônico.",
        "O diafragma faz o ar entrar e descer até os alvéolos, onde acontece a troca de gases. Cigarro e poluição "
        "prejudicam os pulmões, e o exercício ajuda a mantê-los saudáveis.",
        ["O diafragma faz o ar entrar.",
         "Nos alvéolos, o oxigênio passa para o sangue.",
         "Fumar prejudica os pulmões."]),
    "Como funciona o cérebro?": (
        "O cérebro comanda o corpo com uma rede de bilhões de neurônios, onde nascem pensamentos, memórias e "
        "movimentos.",
        "Cada parte cuida de uma tarefa, e as ligações entre os neurônios se fortalecem quando aprendemos. Dormir, "
        "comer bem, ler e conviver ajudam a manter o cérebro saudável.",
        ["O cérebro tem cerca de 86 bilhões de neurônios.",
         "Aprender fortalece as ligações entre eles.",
         "Ele gasta cerca de 20% da energia do corpo."]),
    "Como funciona a digestão?": (
        "A digestão quebra a comida em partes pequenas que o corpo consegue absorver, da boca até o intestino.",
        "O alimento é mastigado, digerido no estômago e absorvido no intestino delgado, e o resto vira fezes no "
        "intestino grosso. Comer devagar e consumir fibras ajudam o processo.",
        ["A digestão começa na boca.",
         "Os nutrientes são absorvidos no intestino delgado.",
         "Água e fibras ajudam a digestão."]),
    "Como funciona o sistema imunológico?": (
        "O sistema imunológico defende o corpo contra micróbios e guarda memória dos invasores que já enfrentou.",
        "A pele é a primeira barreira, e os glóbulos brancos atacam o que consegue entrar. As vacinas aproveitam a "
        "memória dessas células para ensinar o corpo a se defender.",
        ["A pele e o muco são as primeiras barreiras.",
         "Glóbulos brancos atacam os invasores.",
         "As vacinas usam a memória das defesas."]),
    "Para que servem os ossos?": (
        "Os ossos sustentam e protegem o corpo, permitem os movimentos e produzem as células do sangue.",
        "O adulto tem cerca de 206 ossos, que protegem órgãos como o cérebro e o coração. Eles são vivos e se "
        "renovam, e cálcio, sol e exercício os mantêm fortes.",
        ["O esqueleto sustenta e protege o corpo.",
         "A medula óssea produz o sangue.",
         "Cálcio e exercício fortalecem os ossos."]),
    "Como funcionam os músculos?": (
        "Os músculos se contraem e relaxam para mover o corpo, e alguns, como o coração, trabalham sozinhos.",
        "Os músculos presos aos ossos puxam as partes do corpo quando se contraem. Eles usam energia e oxigênio, e "
        "exercícios e proteínas os deixam mais fortes.",
        ["O corpo tem mais de 600 músculos.",
         "Alguns funcionam sem a nossa vontade.",
         "O exercício os fortalece."]),
    "Qual é a função da pele?": (
        "A pele é o maior órgão do corpo e o protege, controla a temperatura e permite sentir o toque.",
        "Ela é uma barreira contra micróbios e perda de água e esfria o corpo com o suor. Também produz melanina e "
        "vitamina D, e protetor solar e cuidados com manchas a mantêm saudável.",
        ["A pele protege contra micróbios e pancadas.",
         "Ajuda a controlar a temperatura.",
         "Protetor solar evita danos."]),
    "Como cuidar bem dos dentes?": (
        "Para evitar cáries, é preciso escovar os dentes, usar fio dental, comer menos doce e ir ao dentista.",
        "As cáries surgem quando bactérias se alimentam de açúcar e soltam ácidos que atacam o esmalte. Como os "
        "dentes permanentes precisam durar a vida toda, a higiene diária é essencial.",
        ["Temos dentes de leite e dentes permanentes.",
         "O açúcar alimenta as bactérias das cáries.",
         "Escova, fio dental e dentista previnem problemas."]),
    "Por que o sono é tão importante?": (
        "Enquanto dormimos, o cérebro organiza as memórias e o corpo se recupera, por isso dormir pouco faz mal.",
        "O sono passa por ciclos de sono leve, profundo e REM, e adultos precisam de sete a nove horas. Horários "
        "regulares e menos telas antes de deitar ajudam a dormir melhor.",
        ["O sono fixa o que aprendemos.",
         "Adultos precisam de sete a nove horas.",
         "Dormir pouco deixa a pessoa desatenta e doente."]),
    "Como ter uma alimentação saudável?": (
        "Comer bem é ter uma alimentação variada, com alimentos naturais e pouco processados, e evitar o excesso "
        "de ultraprocessados.",
        "Cada grupo de alimentos traz nutrientes diferentes, como energia, proteínas e vitaminas. O prato de arroz, "
        "feijão, carne e salada é um bom exemplo de refeição equilibrada.",
        ["Prefira alimentos naturais e variados.",
         "Evite refrigerantes e salgadinhos em excesso.",
         "Arroz, feijão e salada formam um prato equilibrado."]),
    "O que são as vitaminas?": (
        "As vitaminas são substâncias de que o corpo precisa em pouca quantidade e que, em geral, vêm da "
        "alimentação.",
        "Cada vitamina tem uma função, como ajudar a visão, as defesas ou os ossos. Uma dieta variada costuma "
        "bastar, e suplementos só devem ser tomados com orientação médica.",
        ["O corpo quase não produz vitaminas sozinho.",
         "Cada uma tem uma função diferente.",
         "Suplementos só com orientação médica."]),
    "O que é a diabetes?": (
        "A diabetes é uma doença em que o açúcar do sangue fica alto porque a insulina falta ou não funciona bem.",
        "No tipo 1, o corpo quase não produz insulina, e no tipo 2 ela não age direito, muitas vezes por excesso de "
        "peso. Com tratamento e bons hábitos, a doença pode ser controlada.",
        ["A insulina deixa o açúcar entrar nas células.",
         "Existem os tipos 1 e 2.",
         "Tratamento e exercícios controlam a doença."]),
    "O que é a pressão alta?": (
        "A pressão alta é a força excessiva do sangue nas artérias, um problema silencioso que aumenta o risco de "
        "infarto e derrame.",
        "Ela quase nunca dá sintomas, então muita gente só descobre medindo. Menos sal, exercícios e o tratamento "
        "certo ajudam a mantê-la sob controle.",
        ["A hipertensão quase não dá sintomas.",
         "Ela sobrecarrega o coração e as artérias.",
         "Medir e reduzir o sal ajudam."]),
    "O que é a ansiedade?": (
        "A ansiedade é uma reação natural de alerta, mas pode virar um problema quando fica forte demais ou não "
        "passa.",
        "Em doses moderadas, ela ajuda a se preparar para desafios. Quando atrapalha a vida, respirar devagar, se "
        "exercitar e buscar ajuda, como o CVV no 188, fazem diferença.",
        ["A ansiedade prepara o corpo para desafios.",
         "Em excesso, vira um transtorno.",
         "Conversar e buscar um profissional ajudam."]),
    "Quais são os benefícios do exercício físico?": (
        "O exercício físico fortalece o corpo, previne doenças e também melhora o humor e o sono.",
        "Ele faz bem ao coração, aos músculos e aos ossos e ajuda a controlar peso, pressão e açúcar. Não é preciso "
        "ser atleta: caminhar ou dançar com frequência já ajuda.",
        ["O exercício fortalece coração, músculos e ossos.",
         "Reduz o estresse e melhora o sono.",
         "O importante é se mexer com frequência."]),
    "O que são os primeiros socorros?": (
        "Os primeiros socorros são os cuidados dados a uma vítima até chegar a ajuda profissional, começando por "
        "manter a calma e chamar socorro.",
        "É preciso ver se o local é seguro e ligar para o SAMU, no 192, ou para os bombeiros, no 193. Atitudes "
        "simples, como comprimir um sangramento, podem salvar vidas.",
        ["Mantenha a calma e veja se o local é seguro.",
         "Chame o SAMU (192) ou os bombeiros (193).",
         "Não mova quem pode ter machucado a coluna."]),
    "O açúcar faz mal à saúde?": (
        "O açúcar dá energia, mas o excesso de açúcar adicionado aumenta o risco de cáries, obesidade e diabetes.",
        "O açúcar das frutas vem com fibras e vitaminas, e o problema está nos refrigerantes e doces. Trocar o "
        "refrigerante por água e ler os rótulos ajuda a comer menos açúcar.",
        ["O corpo usa a glicose como combustível.",
         "O excesso de açúcar adicionado faz mal.",
         "Água no lugar de refrigerante é uma boa troca."]),
    "Como funciona a visão?": (
        "Enxergamos porque a luz entra nos olhos, forma uma imagem na retina e vira sinais que o cérebro "
        "interpreta.",
        "A córnea, a pupila e o cristalino levam a luz até a retina, onde cones e bastonetes a captam. Miopia e "
        "hipermetropia são corrigidas com óculos.",
        ["A luz é focalizada na retina.",
         "Cones percebem as cores e bastonetes, a pouca luz.",
         "O cérebro monta a imagem."]),
    "Como funciona a audição?": (
        "Ouvimos porque o som faz o tímpano vibrar, e essa vibração vira sinais elétricos que vão ao cérebro.",
        "Três ossinhos levam a vibração até a cóclea, onde células com cílios a transformam em sinais. Sons muito "
        "altos podem danificar essas células para sempre.",
        ["O tímpano vibra com o som.",
         "A cóclea transforma vibração em sinal elétrico.",
         "Volume alto pode causar perda de audição."]),
    "Para que serve o sangue?": (
        "O sangue leva oxigênio e nutrientes a todo o corpo, recolhe os resíduos e ajuda a defendê-lo.",
        "Ele é formado por plasma, glóbulos vermelhos, glóbulos brancos e plaquetas. Também distribui hormônios, e "
        "doar sangue é um gesto simples que salva vidas.",
        ["Glóbulos vermelhos carregam oxigênio.",
         "Glóbulos brancos defendem o corpo.",
         "Doar sangue salva vidas."]),
    "Qual é a função dos rins?": (
        "Os rins filtram o sangue, tiram o que o corpo não usa e formam a urina.",
        "Além de filtrar, eles ajudam a controlar a pressão e produzem hormônios para o sangue e os ossos. Beber "
        "água e evitar excesso de sal protegem os rins.",
        ["Os rins funcionam como filtros.",
         "A urina vai para a bexiga.",
         "Eles também ajudam a controlar a pressão."]),
    "O que é a gripe e como se proteger?": (
        "A gripe é uma infecção pelo vírus influenza, e a vacina anual e a higiene são as principais formas de "
        "proteção.",
        "Ela começa de repente, com febre, dor no corpo e tosse, e é mais forte que o resfriado. O vírus passa "
        "pela tosse e pelas mãos, e quem fica gripado deve descansar e beber líquidos.",
        ["A gripe é causada pelo vírus influenza.",
         "Passa por gotículas e mãos contaminadas.",
         "Vacina todo ano e lavar as mãos protegem."]),
    "O que é a dengue?": (
        "A dengue é uma doença viral transmitida pelo mosquito Aedes aegypti, e a melhor prevenção é acabar com a "
        "água parada.",
        "Ela causa febre alta, dores no corpo e manchas na pele e pode se agravar. Como o mosquito põe ovos em água "
        "parada, é preciso cuidar de vasos, pneus e caixas-d'água.",
        ["O Aedes aegypti transmite a dengue.",
         "Dor forte na barriga e sangramento são sinais de alerta.",
         "Eliminar água parada previne a doença."]),
    "Por que a higiene pessoal é importante?": (
        "A higiene pessoal remove sujeira e micróbios, evita doenças e melhora o bem-estar e a convivência.",
        "Banho, dentes escovados e unhas cortadas fazem parte desses cuidados. Lavar as mãos com água e sabão é "
        "uma das formas mais simples de evitar doenças.",
        ["A higiene evita doenças e mau cheiro.",
         "Lavar as mãos é muito eficaz.",
         "Cuidar do corpo também é respeito pelos outros."]),
    "O que são as proteínas e para que servem?": (
        "As proteínas são nutrientes que constroem e reparam o corpo e vêm de alimentos animais e vegetais.",
        "Elas formam músculos, pele, enzimas e anticorpos. Carnes, ovos e leite têm proteína, assim como o feijão, "
        "e arroz com feijão juntos formam uma boa combinação.",
        ["Proteínas são feitas de aminoácidos.",
         "Constroem músculos e defesas do corpo.",
         "Arroz e feijão se completam."]),
    "Como foi a chegada dos portugueses ao Brasil?": (
        "Em 1500, a esquadra de Pedro Álvares Cabral chegou à Bahia, numa terra já habitada por milhões de "
        "indígenas.",
        "Pero Vaz de Caminha contou o encontro numa carta ao rei. Como os indígenas já viviam aqui, muitos "
        "historiadores falam em chegada, e não em descobrimento, e a colonização trouxe doenças e violência.",
        ["Cabral chegou à Bahia em abril de 1500.",
         "Milhões de indígenas já viviam na terra.",
         "A colonização trouxe guerras e escravização."]),
    "Como aconteceu a independência do Brasil?": (
        "Depois de anos de mudanças trazidas pela família real, Dom Pedro declarou a independência do Brasil em "
        "7 de setembro de 1822.",
        "A vinda da corte em 1808 deu importância ao Brasil, e Portugal depois tentou fazê-lo voltar a ser colônia. "
        "Dom Pedro resistiu, virou imperador, e ainda houve lutas, como na Bahia.",
        ["A família real chegou ao Rio em 1808.",
         "Dom Pedro proclamou a independência em 1822.",
         "Houve lutas em províncias como a Bahia."]),
    "Como foi a abolição da escravidão no Brasil?": (
        "A escravidão no Brasil durou séculos, enfrentou a resistência dos escravizados e só acabou com a Lei "
        "Áurea, em 1888.",
        "Os africanos escravizados resistiram com fugas, revoltas e quilombos. Depois de leis graduais, a princesa "
        "Isabel assinou a abolição, mas os libertos ficaram sem apoio, e as desigualdades continuam.",
        ["Milhões de africanos foram escravizados.",
         "A Lei Áurea acabou com a escravidão em 1888.",
         "Faltaram políticas para os libertos."]),
    "Como o Brasil virou uma república?": (
        "O Império perdeu apoio, e em 15 de novembro de 1889 um movimento militar liderado por Deodoro da "
        "Fonseca proclamou a República.",
        "Militares, fazendeiros e republicanos se afastaram de Dom Pedro II. A família imperial foi exilada, e a "
        "Constituição de 1891 separou o Estado da Igreja.",
        ["O Império perdeu o apoio de grupos importantes.",
         "Deodoro proclamou a República em 1889.",
         "A família imperial foi para o exílio."]),
    "Por que e como Brasília foi construída?": (
        "Brasília foi construída no governo de Juscelino Kubitschek para levar a capital ao centro do país e foi "
        "inaugurada em 1960.",
        "A cidade foi planejada por Lúcio Costa, com prédios de Oscar Niemeyer, e erguida por milhares de "
        "candangos. A ideia era desenvolver o interior, e hoje ela é patrimônio da humanidade.",
        ["O objetivo era ocupar o centro do Brasil.",
         "Lúcio Costa e Niemeyer planejaram a cidade.",
         "Foi inaugurada em 21 de abril de 1960."]),
    "O que foram as Grandes Navegações?": (
        "As Grandes Navegações foram as viagens dos europeus nos séculos XV e XVI em busca de novas rotas de "
        "comércio, com Portugal na frente.",
        "Com caravelas e instrumentos como o astrolábio, navegadores chegaram à Índia, à América e ao Brasil. As "
        "viagens ligaram continentes, mas abriram caminho para a colonização.",
        ["Os europeus buscavam as especiarias da Ásia.",
         "Portugal foi pioneiro.",
         "As viagens levaram à colonização de outros povos."]),
    "O que foi a Revolução Industrial?": (
        "A Revolução Industrial foi a passagem da produção manual para as máquinas e fábricas, começando na "
        "Inglaterra no século XVIII.",
        "Máquinas como a de vapor deixaram a produção rápida e barata, e as cidades cresceram. Os operários, porém, "
        "sofriam com jornadas longas e salários baixos, o que gerou os sindicatos.",
        ["A produção passou das oficinas para as fábricas.",
         "As cidades cresceram e surgiram as ferrovias.",
         "As condições de trabalho eram duras."]),
}
