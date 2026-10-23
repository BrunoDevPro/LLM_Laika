"""Temas para pedidos genéricos (parte 1: animais, plantas, natureza e espaço).

Cada tema: (assunto com artigo, resposta curta, texto). O gerador monta perguntas como
"Faça um texto sobre as planárias.", "O que são as planárias?" e "E as planárias?".
"""

TEMAS_ANIMAIS = [
    ("as planárias",
     "As planárias são pequenos vermes de corpo achatado que vivem em água doce, no mar ou em lugares úmidos.",
     "As planárias são vermes de corpo achatado, quase sempre com menos de dois centímetros, que vivem em rios, "
     "lagos e lugares úmidos. Na cabeça, elas têm duas manchas que funcionam como olhos simples e percebem a luz. "
     "São famosas pela regeneração: se uma planária for cortada em pedaços, cada parte pode formar um animal "
     "inteiro. Por isso, os cientistas as estudam para entender como o corpo se refaz."),
    ("as águas-vivas",
     "As águas-vivas são animais marinhos de corpo gelatinoso, com tentáculos que podem queimar a pele.",
     "As águas-vivas são animais marinhos de corpo mole e transparente, formado quase todo por água. Elas não têm "
     "cérebro nem ossos e nadam contraindo o corpo em forma de sino. Os tentáculos têm células que soltam uma "
     "substância urticante, usada para capturar pequenos animais. Por isso, encostar numa água-viva na praia pode "
     "causar ardência e vermelhidão."),
    ("os polvos",
     "Os polvos são moluscos marinhos com oito braços cheios de ventosas e um corpo mole, sem ossos.",
     "Os polvos são moluscos que vivem no mar. Eles têm oito braços com ventosas, três corações e sangue azulado. "
     "Como não têm ossos, conseguem passar por buracos muito pequenos. São animais muito inteligentes: aprendem a "
     "abrir potes, mudam de cor para se camuflar e soltam tinta para fugir dos predadores."),
    ("os tubarões",
     "Os tubarões são peixes marinhos com esqueleto de cartilagem e várias fileiras de dentes.",
     "Os tubarões são peixes que vivem em mares e oceanos do mundo todo. O esqueleto deles é de cartilagem, um "
     "material mais flexível que o osso, e os dentes caem e são trocados muitas vezes ao longo da vida. Há tubarões "
     "pequenos e enormes, como o tubarão-baleia, o maior peixe do mundo, que se alimenta de plâncton. Ataques a "
     "pessoas são raros."),
    ("os golfinhos",
     "Os golfinhos são mamíferos aquáticos inteligentes, que respiram ar e vivem em grupos.",
     "Os golfinhos são mamíferos que vivem no mar e em alguns rios. Mesmo morando na água, eles respiram ar por um "
     "orifício no alto da cabeça. Vivem em grupos, se comunicam com assobios e cliques e usam o eco dos sons para "
     "achar peixes, o que se chama ecolocalização. Na Amazônia vive o boto-cor-de-rosa, um golfinho de rio."),
    ("os morcegos",
     "Os morcegos são os únicos mamíferos capazes de voar de verdade.",
     "Os morcegos são mamíferos que voam com asas formadas por uma pele fina entre os dedos. A maioria sai à noite "
     "e se orienta pelo eco dos sons que emite. Muitos comem insetos; outros comem frutas e ajudam a espalhar "
     "sementes e a polinizar flores. Só poucas espécies se alimentam de sangue."),
    ("as corujas",
     "As corujas são aves de rapina, em geral noturnas, com olhos grandes e uma audição muito boa.",
     "As corujas são aves de rapina que costumam caçar à noite. Têm olhos grandes voltados para a frente e "
     "conseguem girar a cabeça muito mais do que nós. O voo delas é silencioso, o que ajuda a surpreender ratos, "
     "insetos e outros pequenos animais. Por isso, as corujas ajudam a controlar pragas nas plantações."),
    ("os pinguins",
     "Os pinguins são aves que não voam, mas nadam muito bem, e vivem principalmente no hemisfério sul.",
     "Os pinguins são aves que não voam: as asas viraram nadadeiras, e eles nadam rápido para pegar peixes, lulas e "
     "pequenos crustáceos. Vivem principalmente no hemisfério sul, em lugares frios como a Antártida, mas algumas "
     "espécies vivem em regiões mais quentes. Uma camada de gordura e as penas bem juntas protegem o corpo do frio."),
    ("os flamingos",
     "Os flamingos são aves de pernas longas e penas cor-de-rosa, que vivem em lagoas rasas.",
     "Os flamingos são aves altas, de pernas e pescoço compridos, que vivem em lagoas rasas e salgadas. A cor "
     "rosada das penas vem da comida: eles comem pequenos crustáceos e algas que têm pigmentos chamados "
     "carotenoides. Costumam descansar apoiados numa perna só e vivem em grandes bandos."),
    ("os papagaios",
     "Os papagaios são aves coloridas e inteligentes, conhecidas por imitar sons e até palavras.",
     "Os papagaios são aves de bico curvo e forte, capaz de quebrar sementes duras. Muitas espécies vivem nas "
     "florestas tropicais, inclusive no Brasil. Eles são inteligentes e alguns imitam a voz humana. Muitos papagaios "
     "são capturados para o comércio ilegal, o que ameaça várias espécies na natureza."),
    ("os tucanos",
     "O tucano é uma ave das florestas tropicais das Américas, famosa pelo bico enorme e colorido.",
     "O tucano é uma ave das florestas da América Central e da América do Sul. Seu bico é grande, mas leve, porque "
     "por dentro é cheio de espaços com ar. O bico ajuda a alcançar frutas nos galhos e também a perder calor nos "
     "dias quentes. Os tucanos comem principalmente frutas e espalham as sementes pela floresta."),
    ("os beija-flores",
     "O beija-flor é uma ave muito pequena que bate as asas tão rápido que consegue ficar parada no ar.",
     "O beija-flor é uma das menores aves do mundo. Ele bate as asas dezenas de vezes por segundo, consegue pairar "
     "no ar e até voar para trás. Alimenta-se principalmente do néctar das flores, usando o bico fino e a língua "
     "comprida, e também come pequenos insetos. Ao visitar as flores, ajuda a polinizar as plantas."),
    ("a onça-pintada",
     "A onça-pintada é o maior felino das Américas, de pelagem amarelada com manchas pretas.",
     "A onça-pintada é o maior felino do continente americano. Vive em florestas e áreas alagadas, como a Amazônia "
     "e o Pantanal. Tem uma mordida fortíssima, nada bem e caça animais como capivaras, queixadas e jacarés. Está "
     "ameaçada principalmente pelo desmatamento e pela caça."),
    ("o lobo-guará",
     "O lobo-guará é um canídeo de pernas longas e pelagem alaranjada, típico do Cerrado brasileiro.",
     "O lobo-guará é o maior canídeo da América do Sul. As pernas longas ajudam a enxergar por cima do capim alto do "
     "Cerrado, e a pelagem é alaranjada. Apesar do nome, não é um lobo de verdade. Come pequenos animais e muitas "
     "frutas, como a lobeira, e por isso espalha sementes. Ele aparece na nota de duzentos reais."),
    ("as capivaras",
     "A capivara é o maior roedor do mundo e vive perto de rios e lagos.",
     "A capivara é o maior roedor do mundo e vive em grupos perto de rios, lagos e áreas alagadas da América do Sul. "
     "É ótima nadadora e consegue ficar alguns minutos debaixo d'água para fugir de predadores. Come capim e plantas "
     "aquáticas. Em muitas cidades brasileiras, é comum ver capivaras em parques à beira dos rios."),
    ("o tamanduá-bandeira",
     "O tamanduá-bandeira é um mamífero sem dentes que come formigas e cupins com uma língua muito comprida.",
     "O tamanduá-bandeira vive em campos e savanas da América do Sul, como o Cerrado. Ele não tem dentes: abre "
     "cupinzeiros e formigueiros com as garras fortes e captura os insetos com a língua longa e pegajosa. A cauda "
     "peluda lembra uma bandeira, daí o nome. É uma espécie ameaçada."),
    ("o bicho-preguiça",
     "O bicho-preguiça é um mamífero que vive nas árvores e se move muito devagar.",
     "O bicho-preguiça vive nas florestas tropicais das Américas e passa quase a vida toda pendurado nas árvores. Ele "
     "se move devagar porque come folhas, que dão pouca energia, e assim economiza esforço. Desce ao chão mais ou "
     "menos uma vez por semana para fazer as necessidades. Na água, nada razoavelmente bem."),
    ("os tatus",
     "O tatu é um mamífero com o corpo protegido por uma carapaça de placas, que cava tocas no chão.",
     "O tatu tem o corpo coberto por uma carapaça formada por placas. Com as garras, cava tocas e procura insetos, "
     "minhocas e raízes. O tatu-bola consegue se enrolar e virar uma bola para se proteger. Um tatu-bola chamado "
     "Fuleco foi o mascote da Copa do Mundo de 2014, no Brasil."),
    ("os elefantes",
     "Os elefantes são os maiores animais terrestres e usam a tromba como se fosse uma mão.",
     "Os elefantes são os maiores animais que vivem em terra. Existem elefantes africanos e asiáticos. A tromba é o "
     "nariz unido ao lábio de cima: com ela, eles respiram, cheiram, pegam comida e bebem água. Vivem em grupos "
     "liderados pelas fêmeas mais velhas e têm ótima memória. As presas de marfim fazem deles alvo de caçadores."),
    ("as girafas",
     "A girafa é o animal mais alto do mundo, com pescoço e pernas muito compridos.",
     "A girafa vive nas savanas da África e é o animal mais alto do mundo. O pescoço comprido permite comer folhas no "
     "alto das árvores, como as da acácia, que ela puxa com a língua longa. Mesmo com o pescoço enorme, a girafa tem "
     "sete vértebras no pescoço, a mesma quantidade que nós. Cada girafa tem um desenho de manchas diferente."),
    ("os leões",
     "O leão é um grande felino que vive em grupos, chamados alcateias, nas savanas da África.",
     "O leão é um grande felino que vive principalmente nas savanas da África. Diferente de outros felinos, vive em "
     "grupos, que reúnem fêmeas, filhotes e alguns machos. Em geral, as leoas fazem a maior parte da caça. O macho "
     "adulto tem uma juba, e o rugido do leão pode ser ouvido a quilômetros de distância."),
    ("os tigres",
     "O tigre é o maior felino do mundo, com pelagem laranja e listras pretas.",
     "O tigre é o maior felino do mundo e vive em florestas e pântanos da Ásia. As listras ajudam a se esconder entre "
     "a vegetação, e cada tigre tem um desenho de listras único. Diferente de muitos gatos, gosta de água e nada bem. "
     "É uma espécie ameaçada de extinção por causa da caça e da perda de habitat."),
    ("os ursos-polares",
     "O urso-polar é um grande urso branco que vive no gelo do Ártico e caça focas.",
     "O urso-polar vive no Ártico, perto do Polo Norte. Ele é um dos maiores carnívoros terrestres e caça "
     "principalmente focas, esperando por elas perto de buracos no gelo. A pelagem parece branca, mas a pele "
     "por baixo é escura, o que ajuda a absorver calor. Com o derretimento do gelo do mar, ele tem cada vez mais "
     "dificuldade para caçar."),
    ("os pandas",
     "O panda-gigante é um urso preto e branco da China que se alimenta quase só de bambu.",
     "O panda-gigante vive nas montanhas do centro da China. Mesmo sendo um urso, passa boa parte do dia comendo "
     "bambu, que é pouco nutritivo. Tem um osso do pulso que funciona como um polegar e ajuda a segurar os galhos. "
     "É um símbolo da conservação da natureza, e os esforços de proteção fizeram a população aumentar."),
    ("os cangurus",
     "O canguru é um marsupial da Austrália que se move aos saltos e carrega o filhote numa bolsa.",
     "O canguru é um marsupial que vive na Austrália. As patas de trás são fortes e ele se move aos saltos, usando a "
     "cauda para se equilibrar. O filhote nasce muito pequeno e termina de se desenvolver dentro de uma bolsa na "
     "barriga da mãe, chamada marsúpio. Os cangurus comem capim e outras plantas."),
    ("os camelos",
     "O camelo é um mamífero do deserto que aguenta muitos dias sem beber água.",
     "O camelo vive em regiões secas da Ásia e da África. As corcovas guardam gordura, não água, e servem como "
     "reserva de energia. Ele aguenta vários dias sem beber e, quando encontra água, bebe muito de uma vez. Cílios "
     "longos e narinas que se fecham protegem dos ventos de areia. O dromedário tem uma corcova; o camelo-bactriano, duas."),
    ("os cavalos",
     "O cavalo é um mamífero herbívoro e veloz, domesticado pelo ser humano há milhares de anos.",
     "O cavalo é um mamífero herbívoro que come capim e feno. Foi domesticado há milhares de anos e, por muito tempo, "
     "foi o principal meio de transporte e de trabalho no campo. Os cavalos conseguem cochilar em pé, e o potro, "
     "o filhote, fica de pé e anda poucas horas depois de nascer."),
    ("as vacas",
     "A vaca é um mamífero ruminante criado pelo ser humano para produzir leite e carne.",
     "A vaca é um mamífero herbívoro e ruminante: o estômago tem quatro partes, e ela engole o capim, depois o devolve "
     "à boca para mastigar de novo. Vacas são criadas para dar leite, carne e couro. O macho é o boi ou o touro, e o "
     "filhote se chama bezerro. O Brasil tem um dos maiores rebanhos bovinos do mundo."),
    ("as galinhas",
     "A galinha é uma ave doméstica criada para botar ovos e fornecer carne.",
     "A galinha é uma ave doméstica que vive em quase todo o mundo. Ela consegue voar só pequenas distâncias. É "
     "criada para botar ovos e para o consumo da carne. O macho é o galo, famoso por cantar de manhã, e o filhote é "
     "o pintinho. As galinhas comem grãos, insetos e restos de comida."),
    ("os cupins",
     "Os cupins são insetos que vivem em colônias e se alimentam de madeira e restos de plantas.",
     "Os cupins são insetos sociais que vivem em colônias com rainha, rei, operários e soldados. Eles comem madeira e "
     "folhas mortas, com a ajuda de micróbios que vivem no intestino e quebram a celulose. Na natureza, ajudam a "
     "reciclar a matéria das plantas, mas dentro de casa podem destruir móveis e portas. Os cupinzeiros podem ser "
     "bem altos."),
    ("as minhocas",
     "A minhoca é um animal de corpo mole e alongado que vive debaixo da terra.",
     "A minhoca é um anelídeo, um animal de corpo mole dividido em anéis. Ela vive na terra úmida e respira pela "
     "pele. Ao cavar túneis e comer restos de plantas, a minhoca afofa e aduba o solo, o que ajuda as plantas a "
     "crescer. Por isso, é uma grande amiga dos agricultores e de quem cuida de hortas."),
    ("as aranhas",
     "As aranhas são animais de oito patas que produzem seda e caçam insetos.",
     "As aranhas não são insetos: são aracnídeos, com oito patas e o corpo dividido em duas partes. Muitas fazem "
     "teias de seda para capturar insetos, e outras caçam correndo atrás das presas. A maioria é inofensiva para as "
     "pessoas, mas algumas, como a armadeira e a aranha-marrom, têm veneno perigoso."),
    ("os escorpiões",
     "O escorpião é um aracnídeo com pinças e um ferrão venenoso na ponta da cauda.",
     "O escorpião é um aracnídeo de oito patas, com duas pinças na frente e uma cauda que termina num ferrão com "
     "veneno. Ele caça insetos e costuma sair à noite. No Brasil, o escorpião-amarelo é o mais perigoso e aparece "
     "em cidades, perto de entulho e de esgoto. Em caso de picada, é preciso procurar atendimento médico logo."),
    ("os mosquitos",
     "Os mosquitos são insetos pequenos de asas finas; as fêmeas de muitas espécies picam para se alimentar de sangue.",
     "Os mosquitos são insetos de asas finas e pernas longas. Só as fêmeas picam, porque precisam do sangue para "
     "produzir os ovos, que são postos na água parada. Alguns mosquitos transmitem doenças: o Aedes aegypti "
     "transmite dengue, zika e chikungunya. Por isso, é importante não deixar água acumulada em vasos, pneus e garrafas."),
    ("as joaninhas",
     "A joaninha é um besouro pequeno e arredondado, geralmente vermelho com pintas pretas.",
     "A joaninha é um pequeno besouro de corpo arredondado e colorido. As cores fortes avisam os predadores que ela "
     "tem gosto ruim. As joaninhas comem pulgões e outras pragas das plantas, por isso são muito úteis nas hortas e "
     "nos jardins. Existem joaninhas de várias cores, não só vermelhas."),
    ("os vaga-lumes",
     "O vaga-lume é um besouro que produz luz no próprio corpo.",
     "O vaga-lume é um besouro capaz de produzir luz, um fenômeno chamado bioluminescência. A luz vem de uma reação "
     "química no abdômen e quase não produz calor. Os vaga-lumes piscam para se comunicar e atrair parceiros. Eles "
     "precisam de lugares escuros e sem poluição, por isso estão ficando raros perto das cidades."),
    ("os caracóis",
     "O caracol é um molusco de corpo mole que carrega uma concha em espiral nas costas.",
     "O caracol é um molusco que vive em lugares úmidos e carrega uma concha em espiral, onde se esconde quando se "
     "sente ameaçado. Ele se move devagar, deslizando sobre uma gosma que produz. Tem antenas na cabeça, e os olhos "
     "ficam na ponta de duas delas. Muitos caracóis comem folhas e podem estragar hortas."),
    ("os jacarés",
     "O jacaré é um réptil grande, de pele com placas duras, que vive em rios, lagos e pântanos.",
     "O jacaré é um réptil que vive em rios, lagos e áreas alagadas das Américas, como o Pantanal. Tem a pele coberta "
     "de placas duras e passa boa parte do tempo tomando sol, porque não produz o próprio calor. Come peixes, aves e "
     "outros animais. O jacaré tem o focinho mais largo e arredondado que o do crocodilo."),
    ("as tartarugas marinhas",
     "As tartarugas marinhas são répteis que vivem no mar e voltam à praia para botar ovos.",
     "As tartarugas marinhas são répteis que vivem nos oceanos e nadam milhares de quilômetros. As fêmeas voltam às "
     "praias para cavar ninhos na areia e botar os ovos. Quando os filhotes nascem, correm para o mar. O lixo de "
     "plástico, a pesca e as luzes nas praias ameaçam essas tartarugas, e no Brasil o Projeto Tamar ajuda a protegê-las."),
    ("as cobras",
     "As cobras são répteis sem patas, de corpo alongado e coberto de escamas.",
     "As cobras, ou serpentes, são répteis sem patas que se movem rastejando. Elas sentem os cheiros com a língua e "
     "engolem as presas inteiras, porque a mandíbula se abre muito. Algumas são venenosas, como a jararaca, a "
     "cascavel e a coral-verdadeira, e outras não têm veneno, como a jiboia. Em caso de picada, é preciso procurar "
     "um hospital, que tem o soro certo."),
    ("os camaleões",
     "O camaleão é um lagarto que muda de cor e tem uma língua longa para capturar insetos.",
     "O camaleão é um lagarto que vive principalmente na África e em Madagascar. Ele muda de cor conforme o humor, a "
     "temperatura e a luz. Os olhos se movem cada um para um lado, e a língua comprida é lançada muito rápido para "
     "pegar insetos. As patas e a cauda ajudam a se segurar nos galhos."),
    ("os dinossauros",
     "Os dinossauros foram répteis que dominaram a Terra por milhões de anos e foram extintos há cerca de 66 milhões de anos.",
     "Os dinossauros foram um grupo de répteis que viveu na Terra por mais de 160 milhões de anos. Havia dinossauros "
     "enormes e pequenos, carnívoros como o tiranossauro e herbívoros como o tricerátopo. A maioria foi extinta há "
     "cerca de 66 milhões de anos, provavelmente depois da queda de um grande asteroide. As aves de hoje são "
     "descendentes de dinossauros."),
    ("os lobos",
     "O lobo é um canídeo selvagem que vive e caça em grupos chamados alcateias.",
     "O lobo é um canídeo selvagem que vive em florestas, montanhas e planícies do hemisfério norte. Vive em grupos, "
     "as alcateias, que caçam juntos animais como cervos. Os lobos uivam para se comunicar e marcar território. Os "
     "cachorros descendem de lobos domesticados pelo ser humano há milhares de anos."),
    ("as raposas",
     "A raposa é um canídeo pequeno, de focinho fino e cauda peluda, conhecida pela esperteza.",
     "A raposa é um canídeo de porte pequeno, com focinho fino, orelhas grandes e cauda peluda. Vive em muitos lugares "
     "do mundo e come pequenos animais, insetos e frutas. Nas fábulas e histórias populares, a raposa costuma "
     "aparecer como um bicho esperto e enganador."),
    ("os macacos",
     "Os macacos são primatas, em geral ágeis e sociais, que vivem principalmente em florestas tropicais.",
     "Os macacos são primatas que vivem principalmente em florestas tropicais da América, da África e da Ásia. Usam as "
     "mãos para pegar comida e se segurar nos galhos, e muitos têm cauda. Vivem em grupos e se comunicam com sons e "
     "gestos. No Brasil, há espécies como o bugio, o macaco-prego e o mico-leão-dourado."),
    ("os gorilas",
     "O gorila é o maior primata do mundo e vive nas florestas da África.",
     "O gorila é o maior primata do mundo e vive nas florestas da região central da África. Apesar do tamanho, é "
     "calmo e come principalmente folhas, brotos e frutas. Vive em grupos liderados por um macho adulto, chamado "
     "costas-prateadas. Os gorilas estão ameaçados pela caça e pelo desmatamento."),
    ("o peixe-boi",
     "O peixe-boi é um mamífero aquático grande e tranquilo que se alimenta de plantas.",
     "O peixe-boi é um mamífero aquático, parente distante dos elefantes. É grande, lento e tranquilo, e come plantas "
     "aquáticas e capim marinho. No Brasil vivem o peixe-boi-marinho, no litoral do Nordeste, e o peixe-boi-da-"
     "amazônia, nos rios. As duas espécies estão ameaçadas."),
    ("a arara-azul",
     "A arara-azul é uma grande ave de penas azuis que vive principalmente no Pantanal.",
     "A arara-azul-grande é a maior arara do mundo, com penas de um azul forte e um anel amarelo em volta dos olhos. "
     "Vive principalmente no Pantanal e se alimenta de cocos de palmeiras, que quebra com o bico poderoso. Já esteve "
     "muito ameaçada pelo tráfico de animais, e projetos de conservação ajudaram a população a crescer."),
    ("o mico-leão-dourado",
     "O mico-leão-dourado é um macaco pequeno, de pelagem alaranjada, que só existe na Mata Atlântica.",
     "O mico-leão-dourado é um pequeno primata de pelagem dourada, com uma juba que lembra a de um leão. Vive apenas "
     "na Mata Atlântica do estado do Rio de Janeiro. Quase foi extinto por causa do desmatamento, mas programas de "
     "proteção e reflorestamento ajudaram a salvar a espécie. Ele aparece na nota de vinte reais."),
    ("os corais",
     "Os corais são pequenos animais marinhos que vivem em colônias e formam os recifes.",
     "Os corais são animais marinhos pequenos que vivem em colônias. Muitos produzem um esqueleto de calcário que, ao "
     "longo de muito tempo, forma os recifes de coral. Os recifes abrigam uma enorme variedade de peixes e outros "
     "seres. Com o aquecimento dos oceanos, muitos corais ficam brancos e podem morrer, o que se chama branqueamento."),
    ("as baleias-jubarte",
     "A baleia-jubarte é uma grande baleia conhecida pelos saltos e pelos cantos.",
     "A baleia-jubarte é uma baleia grande, de nadadeiras peitorais muito longas. Ela é famosa pelos saltos fora da "
     "água e pelos cantos dos machos, que podem durar horas. Todo ano, migra das águas frias, onde se alimenta, para "
     "águas quentes, onde nascem os filhotes. No Brasil, pode ser vista no litoral da Bahia, como em Abrolhos."),
    ("as abelhas sem ferrão",
     "As abelhas sem ferrão são abelhas nativas do Brasil que produzem mel e não picam.",
     "As abelhas sem ferrão, como a jataí e a mandaçaia, são nativas das Américas e não conseguem picar. Elas "
     "produzem um mel mais líquido e são importantes polinizadoras das plantas nativas. Criar essas abelhas, a "
     "meliponicultura, é uma atividade que ajuda a conservar a natureza e pode ser feita até em quintais."),
    ("as formigas-cortadeiras",
     "As formigas-cortadeiras cortam folhas, não para comer, mas para cultivar um fungo que lhes serve de alimento.",
     "As formigas-cortadeiras, como as saúvas, cortam pedaços de folhas e os levam para o formigueiro. Lá dentro, as "
     "folhas servem de base para cultivar um fungo, que é o verdadeiro alimento da colônia. Os formigueiros podem ser "
     "enormes, com milhões de formigas, e às vezes causam prejuízo às plantações."),
]

TEMAS_PLANTAS = [
    ("os cactos",
     "Os cactos são plantas de regiões secas, com caule grosso que guarda água e espinhos no lugar das folhas.",
     "Os cactos são plantas adaptadas a lugares secos. O caule é grosso e guarda água, e as folhas viraram espinhos, "
     "que perdem pouca água e protegem a planta dos animais. Muitos cactos dão flores bonitas. No Nordeste "
     "brasileiro, o mandacaru e o xique-xique são cactos típicos da Caatinga."),
    ("as samambaias",
     "As samambaias são plantas sem flores nem sementes, que se reproduzem por esporos.",
     "As samambaias são plantas que gostam de lugares úmidos e sombreados. Elas não têm flores nem sementes: se "
     "reproduzem por esporos, que ficam em pontinhos marrons embaixo das folhas. As folhas novas nascem enroladas, "
     "como um caracol. São plantas muito antigas, que já existiam no tempo dos dinossauros."),
    ("os cogumelos",
     "Os cogumelos são as partes visíveis de certos fungos, que nascem em lugares úmidos.",
     "Os cogumelos não são plantas: são fungos. O cogumelo é só a parte que aparece; o resto do fungo fica escondido "
     "na terra ou na madeira, formando fios finos. Os fungos decompõem restos de plantas e animais e devolvem "
     "nutrientes ao solo. Alguns cogumelos são comestíveis, como o champignon, mas outros são venenosos, por isso "
     "nunca se deve comer cogumelos colhidos na natureza sem conhecer bem."),
    ("as orquídeas",
     "As orquídeas são uma grande família de plantas com flores, muitas delas bonitas e perfumadas.",
     "As orquídeas formam uma das maiores famílias de plantas com flores, com milhares de espécies. Muitas vivem "
     "presas no tronco das árvores, sem prejudicá-las. As flores têm formas variadas e às vezes imitam insetos para "
     "atrair os polinizadores. A baunilha, usada para dar sabor a doces, vem de uma orquídea."),
    ("os girassóis",
     "O girassol é uma planta de flor grande e amarela, cujas sementes dão óleo e servem de alimento.",
     "O girassol é uma planta alta, de flor grande e amarela. Quando é jovem, a planta acompanha o movimento do Sol "
     "durante o dia. O miolo da flor tem centenas de sementes, usadas para fazer óleo de cozinha e como alimento "
     "para pessoas e pássaros. O girassol também é muito usado como flor de enfeite."),
    ("os ipês",
     "Os ipês são árvores brasileiras que se cobrem de flores amarelas, roxas, rosas ou brancas.",
     "Os ipês são árvores nativas do Brasil famosas pela florada. No fim do inverno, muitas perdem as folhas e ficam "
     "cobertas de flores amarelas, roxas, rosas ou brancas, colorindo ruas e campos. A flor do ipê-amarelo é "
     "considerada a flor-símbolo do Brasil. A madeira dos ipês é muito dura e resistente."),
    ("as araucárias",
     "A araucária é um pinheiro nativo do Sul do Brasil, cuja semente é o pinhão.",
     "A araucária, ou pinheiro-do-paraná, é uma árvore alta, com galhos que lembram uma taça no topo. Vive nas regiões "
     "frias e altas do Sul do Brasil. A semente é o pinhão, comido cozido no inverno e muito apreciado também por "
     "animais como a gralha-azul. A floresta de araucárias foi muito derrubada e hoje é protegida."),
    ("as plantas carnívoras",
     "As plantas carnívoras capturam pequenos insetos para conseguir nutrientes que faltam no solo.",
     "As plantas carnívoras vivem em solos pobres e completam a alimentação capturando insetos. Algumas têm folhas que "
     "se fecham como uma armadilha, como a dioneia; outras têm folhas em forma de jarro, onde o inseto cai, ou pelos "
     "grudentos. Depois, a planta digere o inseto. Elas também fazem fotossíntese, como as outras plantas."),
    ("as algas",
     "As algas são seres que fazem fotossíntese e vivem principalmente na água.",
     "As algas são seres que vivem na água ou em lugares muito úmidos e fazem fotossíntese, como as plantas. Há algas "
     "microscópicas e algas grandes, que formam florestas no fundo do mar. As algas do oceano produzem uma parte "
     "enorme do oxigênio do planeta e são a base da alimentação de muitos animais marinhos."),
    ("as sementes",
     "A semente é a parte da planta que guarda o embrião, de onde nasce uma planta nova.",
     "A semente guarda um pequeno embrião e uma reserva de alimento, protegidos por uma casca. Com água, calor e ar, "
     "ela germina e a plantinha começa a crescer. As sementes se espalham de muitas formas: pelo vento, pela água ou "
     "levadas por animais que comem os frutos. Feijão, milho e arroz são sementes que comemos."),
    ("as árvores frutíferas",
     "As árvores frutíferas são as que dão frutos comestíveis, como a mangueira e a laranjeira.",
     "As árvores frutíferas são árvores que produzem frutos que podemos comer, como a mangueira, a laranjeira, o "
     "cajueiro e a goiabeira. Elas dão sombra, alimentam pessoas e animais e embelezam quintais e praças. Plantar uma "
     "árvore frutífera exige um lugar com sol, água na medida certa e paciência, porque algumas levam anos para dar frutos."),
    ("as plantas medicinais",
     "Plantas medicinais são plantas usadas para tratar ou aliviar problemas de saúde, como a camomila e a hortelã.",
     "Plantas medicinais são aquelas usadas tradicionalmente para aliviar sintomas, como a camomila, o boldo, a "
     "hortelã e a erva-cidreira. Muitos remédios modernos foram descobertos a partir de plantas. Mesmo sendo "
     "naturais, elas podem fazer mal em excesso ou junto com outros remédios, por isso é bom conversar com um "
     "profissional de saúde antes de usar."),
]

TEMAS_NATUREZA = [
    ("os manguezais",
     "O manguezal é um ambiente de transição entre o rio e o mar, com lama, água salobra e árvores de raízes aéreas.",
     "O manguezal fica onde os rios encontram o mar, em áreas protegidas das ondas. A água é salobra, o solo é uma "
     "lama mole e as árvores têm raízes que saem do chão para respirar e se firmar. É um berçário de peixes, "
     "caranguejos e camarões, e protege o litoral da erosão. O Brasil tem uma das maiores áreas de manguezal do mundo."),
    ("os recifes de coral",
     "Os recifes de coral são estruturas no mar formadas pelo esqueleto de corais, cheias de vida.",
     "Os recifes de coral são construídos ao longo de muitos anos pelo esqueleto de calcário de pequenos animais, os "
     "corais. Ocupam uma parte pequena do oceano, mas abrigam uma enorme variedade de peixes e outros seres. Eles "
     "protegem as praias das ondas e atraem turistas. O aquecimento da água e a poluição ameaçam os recifes."),
    ("o Cerrado",
     "O Cerrado é a savana brasileira, com árvores tortas, capim e muita biodiversidade, no centro do país.",
     "O Cerrado é o segundo maior bioma do Brasil e ocupa principalmente a região central do país. Tem árvores de "
     "troncos tortos e casca grossa, arbustos e capim, com uma estação seca e outra chuvosa. Muitos rios importantes "
     "nascem no Cerrado, que por isso é chamado de berço das águas. Grande parte dele já foi transformada em plantações e pastos."),
    ("a Caatinga",
     "A Caatinga é o bioma do semiárido nordestino, com plantas adaptadas à seca, como os cactos.",
     "A Caatinga é um bioma que só existe no Brasil e ocupa boa parte do Nordeste. O clima é quente e seco, com chuvas "
     "irregulares. Na seca, muitas plantas perdem as folhas e a paisagem fica acinzentada; quando chove, tudo fica "
     "verde em poucos dias. Mandacaru, juazeiro e umbuzeiro são plantas típicas da Caatinga."),
    ("o Pantanal",
     "O Pantanal é a maior planície alagável do mundo, no Centro-Oeste do Brasil.",
     "O Pantanal fica principalmente em Mato Grosso e Mato Grosso do Sul e é uma das maiores áreas alagáveis do mundo. "
     "Na época das chuvas, os rios transbordam e grande parte da planície fica coberta de água; na seca, a água "
     "baixa. É famoso pela fauna fácil de observar, como jacarés, capivaras, tuiuiús, araras e onças-pintadas."),
    ("a Mata Atlântica",
     "A Mata Atlântica é a floresta tropical que se estendia por grande parte do litoral brasileiro.",
     "A Mata Atlântica é uma floresta tropical que cobria boa parte da costa do Brasil. Foi o primeiro bioma explorado "
     "pelos colonizadores, a partir da extração do pau-brasil, e hoje resta só uma pequena parte da área original. "
     "Mesmo assim, abriga uma enorme variedade de plantas e animais, muitos que só existem lá, como o mico-leão-dourado."),
    ("a Floresta Amazônica",
     "A Floresta Amazônica é a maior floresta tropical do mundo e fica na região norte da América do Sul.",
     "A Floresta Amazônica é a maior floresta tropical do planeta e ocupa vários países da América do Sul, a maior "
     "parte no Brasil. Ela abriga uma imensa variedade de plantas e animais e é cortada pelo rio Amazonas e seus "
     "afluentes. A floresta ajuda a regular o clima e as chuvas de outras regiões. O desmatamento e as queimadas são "
     "as maiores ameaças a ela."),
    ("o Pampa",
     "O Pampa é o bioma dos campos do Sul do Brasil, com vegetação baixa e rasteira.",
     "O Pampa ocupa a metade sul do Rio Grande do Sul e se estende pelo Uruguai e pela Argentina. É formado por campos "
     "de vegetação baixa, com poucas árvores, e tem invernos frios. A criação de gado nesses campos faz parte da "
     "cultura gaúcha, com o churrasco e o chimarrão."),
    ("as geleiras",
     "Geleiras são grandes massas de gelo que se formam com o acúmulo de neve ao longo de muitos anos.",
     "As geleiras se formam quando a neve se acumula por muitos anos e vai sendo compactada até virar gelo. Elas "
     "existem nas regiões polares e no alto de montanhas e se movem muito devagar, como rios de gelo. As geleiras "
     "guardam uma grande parte da água doce do planeta. Com o aquecimento global, muitas estão derretendo e diminuindo."),
    ("as cavernas",
     "Cavernas são buracos naturais grandes na rocha, muitas vezes formados pela água ao longo de milhares de anos.",
     "Muitas cavernas se formam quando a água da chuva, levemente ácida, vai dissolvendo rochas como o calcário ao "
     "longo de milhares de anos. Dentro delas aparecem formações como as estalactites, que pendem do teto, e as "
     "estalagmites, que crescem do chão. Algumas cavernas guardam pinturas feitas por povos antigos. O estudo das "
     "cavernas se chama espeleologia."),
    ("as cachoeiras",
     "Cachoeira é uma queda d'água que acontece quando um rio passa por um desnível do terreno.",
     "Uma cachoeira se forma quando a água de um rio cai de um ponto mais alto para um mais baixo do terreno. As "
     "Cataratas do Iguaçu, na fronteira do Brasil com a Argentina, são um conjunto enorme de quedas d'água e um dos "
     "lugares mais visitados do país. Nadar perto de cachoeiras exige cuidado, porque o nível da água pode subir "
     "rápido depois de chuvas."),
    ("os terremotos",
     "Terremoto é um tremor da superfície da Terra causado pelo movimento das placas tectônicas.",
     "Os terremotos acontecem quando as grandes placas que formam a crosta da Terra se movem e liberam de repente a "
     "energia acumulada. O chão treme e, nos casos fortes, prédios e estradas podem desabar. A intensidade é medida "
     "por escalas, como a de magnitude. O Brasil fica no meio de uma placa, por isso aqui os terremotos fortes são raros."),
    ("os tsunamis",
     "Tsunami é uma série de ondas gigantes no mar, causada em geral por um terremoto no fundo do oceano.",
     "Um tsunami é uma sequência de ondas enormes provocada principalmente por terremotos no fundo do mar, mas também "
     "por erupções ou deslizamentos. Em alto-mar, as ondas são baixas e muito rápidas; perto da costa, crescem e "
     "invadem a terra com muita força. Um sinal de alerta é o mar recuar de repente: nesse caso, é preciso correr "
     "para um lugar alto."),
    ("os furacões",
     "Furacão é uma tempestade enorme, com ventos muito fortes girando em volta de um centro calmo, o olho.",
     "Os furacões se formam sobre mares quentes, quando a água evaporada sobe e forma nuvens que começam a girar. "
     "Os ventos podem passar de duzentos quilômetros por hora e vêm acompanhados de chuva forte e ressaca no mar. "
     "No meio do furacão há o olho, uma região calma. No oeste do Pacífico, essas tempestades se chamam tufões."),
    ("os tornados",
     "Tornado é uma coluna de ar girando com muita força, que desce de uma nuvem de tempestade até o chão.",
     "O tornado é um redemoinho de vento muito forte que liga uma nuvem de tempestade ao chão. Ele é bem menor que um "
     "furacão, mas os ventos podem ser ainda mais violentos e destruir casas no caminho. Os Estados Unidos têm muitos "
     "tornados, e no Brasil eles acontecem principalmente no Sul."),
    ("os raios",
     "O raio é uma descarga elétrica enorme entre as nuvens e o chão, ou dentro das próprias nuvens.",
     "Os raios acontecem durante tempestades, quando as nuvens acumulam cargas elétricas. A descarga aquece o ar de "
     "repente e produz o estrondo do trovão. Como a luz chega antes do som, vemos o clarão antes de ouvir o barulho. "
     "Em tempestades, o mais seguro é ficar dentro de casa ou do carro e longe de árvores isoladas e de piscinas."),
    ("o arco-íris",
     "O arco-íris é um arco colorido que aparece no céu quando a luz do Sol atravessa gotas de chuva.",
     "O arco-íris aparece quando a luz do Sol passa pelas gotinhas de água no ar e se separa em várias cores, como "
     "num prisma. Por isso, ele surge quando chove e faz sol ao mesmo tempo, com o Sol atrás de quem olha. As cores "
     "costumam ser descritas como vermelho, laranja, amarelo, verde, azul, anil e violeta."),
    ("as auroras polares",
     "As auroras são luzes coloridas que aparecem no céu perto dos polos da Terra.",
     "As auroras polares são luzes verdes, roxas ou avermelhadas que dançam no céu das regiões perto dos polos. Elas "
     "aparecem quando partículas lançadas pelo Sol chegam à Terra e são guiadas pelo campo magnético até os polos, "
     "onde fazem os gases do ar brilhar. No norte, são chamadas de aurora boreal; no sul, de aurora austral."),
    ("as marés",
     "Maré é a subida e a descida do nível do mar ao longo do dia, causada principalmente pela atração da Lua.",
     "As marés são o sobe e desce do nível do mar, que acontece em geral duas vezes por dia. Elas são causadas "
     "principalmente pela atração da gravidade da Lua e, em menor parte, do Sol. Na maré alta, a água avança sobre a "
     "praia; na maré baixa, recua. Pescadores e navegadores acompanham as tábuas de marés."),
    ("os eclipses",
     "Eclipse é quando um astro fica escondido pela sombra de outro, como no eclipse do Sol e no da Lua.",
     "Num eclipse solar, a Lua passa entre a Terra e o Sol e esconde o Sol, total ou parcialmente. Num eclipse lunar, "
     "a Terra fica entre o Sol e a Lua, e a sombra da Terra cobre a Lua, que pode ficar avermelhada. Nunca se deve "
     "olhar para o Sol diretamente, nem durante um eclipse, sem óculos de proteção próprios."),
    ("o efeito estufa",
     "O efeito estufa é o aquecimento natural da Terra causado por gases que seguram parte do calor na atmosfera.",
     "O efeito estufa é natural e importante: gases como o gás carbônico e o vapor d'água seguram parte do calor do "
     "Sol perto da superfície, e sem eles a Terra seria fria demais para a vida. O problema é que a queima de "
     "petróleo, carvão e gás e o desmatamento aumentam esses gases, o efeito fica mais forte e o planeta esquenta além da conta."),
    ("o aquecimento global",
     "O aquecimento global é o aumento da temperatura média da Terra causado principalmente pelas atividades humanas.",
     "O aquecimento global é o aumento da temperatura média do planeta nas últimas décadas. A principal causa é a "
     "emissão de gases do efeito estufa pela queima de combustíveis fósseis e pelo desmatamento. As consequências "
     "incluem derretimento de geleiras, subida do nível do mar e mais secas, ondas de calor e tempestades fortes. "
     "Usar energia limpa e proteger as florestas ajuda a reduzir o problema."),
    ("a camada de ozônio",
     "A camada de ozônio é uma faixa da atmosfera que filtra boa parte dos raios ultravioleta do Sol.",
     "A camada de ozônio fica no alto da atmosfera e protege a vida na Terra filtrando boa parte dos raios "
     "ultravioleta do Sol, que podem causar queimaduras e câncer de pele. Gases usados antigamente em geladeiras e "
     "sprays abriram um buraco nessa camada. Um acordo internacional proibiu esses gases, e a camada está se recuperando aos poucos."),
    ("o desmatamento",
     "Desmatamento é a derrubada de florestas e outras vegetações nativas.",
     "O desmatamento é o corte ou a queima da vegetação nativa, muitas vezes para abrir pastos, plantações, estradas "
     "ou para vender madeira. Ele destrói o lar de muitos animais e plantas, deixa o solo mais pobre, diminui as "
     "chuvas e solta gás carbônico, que piora o aquecimento global. Fiscalização, reflorestamento e consumo "
     "consciente ajudam a combatê-lo."),
    ("as queimadas",
     "Queimadas são incêndios na vegetação, muitas vezes provocados para limpar terrenos.",
     "As queimadas são incêndios em florestas, campos e cerrados. Muitas são provocadas para limpar terrenos e acabam "
     "fugindo do controle, principalmente na época seca. Elas matam animais e plantas, empobrecem o solo e enchem o ar "
     "de fumaça, o que faz mal à saúde. Nunca se deve soltar balões ou jogar bitucas de cigarro na beira das estradas."),
    ("a poluição",
     "Poluição é a sujeira ou a contaminação do ar, da água ou do solo, que faz mal aos seres vivos.",
     "A poluição acontece quando lixo, esgoto, fumaça ou produtos químicos contaminam o ar, a água ou o solo. A "
     "poluição do ar vem de carros, fábricas e queimadas; a dos rios, principalmente do esgoto sem tratamento e do "
     "lixo. Ela causa doenças e prejudica os animais e as plantas. Tratar o esgoto, reciclar e usar transporte "
     "público são formas de diminuir a poluição."),
    ("a compostagem",
     "Compostagem é transformar restos de comida e folhas em adubo, com a ajuda de micróbios e minhocas.",
     "A compostagem transforma restos orgânicos, como cascas de frutas, folhas secas e borra de café, em adubo. Os "
     "micróbios e as minhocas decompõem esse material, que vira um composto escuro e rico em nutrientes, ótimo para "
     "hortas e vasos. Assim, sobra menos lixo para os aterros. Dá para fazer compostagem até em apartamento, numa "
     "composteira pequena."),
    ("a biodiversidade",
     "Biodiversidade é a variedade de seres vivos de um lugar ou de todo o planeta.",
     "Biodiversidade é a variedade de vida: as diferentes espécies de plantas, animais, fungos e micróbios e os "
     "ambientes onde vivem. O Brasil é um dos países com maior biodiversidade do mundo, por causa de biomas como a "
     "Amazônia e a Mata Atlântica. Proteger a biodiversidade garante alimentos, remédios, água limpa e um clima equilibrado."),
    ("as nascentes",
     "Nascente é o lugar onde a água subterrânea brota na superfície e dá origem a um rio ou córrego.",
     "As nascentes, ou olhos d'água, são pontos onde a água guardada debaixo da terra aflora e começa a correr. Elas "
     "alimentam córregos e rios. Para que continuem existindo, é preciso manter a vegetação ao redor, que ajuda a "
     "chuva a se infiltrar no solo. Nascentes desprotegidas podem secar ou ficar poluídas."),
    ("as estações do ano",
     "As estações do ano são primavera, verão, outono e inverno.",
     "As estações do ano existem porque o eixo da Terra é inclinado: enquanto o planeta gira em volta do Sol, cada "
     "hemisfério recebe mais ou menos luz em épocas diferentes. Por isso, quando é verão no Brasil, é inverno na "
     "Europa. Perto da linha do Equador, as diferenças entre as estações são pequenas, e fala-se mais em época de chuva e de seca."),
]

TEMAS_ESPACO = [
    ("os buracos negros",
     "Buraco negro é uma região do espaço com gravidade tão forte que nem a luz consegue escapar.",
     "Um buraco negro se forma, por exemplo, quando uma estrela muito grande acaba o combustível e desaba sobre si "
     "mesma. A matéria fica tão concentrada que a gravidade não deixa nada sair, nem a luz. Por isso, os buracos "
     "negros não podem ser vistos diretamente: os astrônomos os percebem pelo efeito que causam no gás e nas estrelas "
     "em volta. No centro da Via Láctea há um buraco negro gigante."),
    ("os cometas",
     "Cometa é um corpo de gelo, poeira e rocha que forma uma cauda brilhante quando chega perto do Sol.",
     "Os cometas são feitos de gelo, poeira e rocha e giram em volta do Sol em órbitas muito alongadas. Quando se "
     "aproximam do Sol, o gelo vira gás e forma uma cabeleira e uma cauda brilhantes, que sempre apontam para o lado "
     "oposto ao Sol. O cometa Halley é o mais famoso e volta a passar perto da Terra a cada 76 anos, mais ou menos."),
    ("os asteroides",
     "Asteroides são rochas que giram em volta do Sol, menores que os planetas.",
     "Os asteroides são corpos rochosos ou metálicos que giram em volta do Sol. A maioria fica no cinturão de "
     "asteroides, entre Marte e Júpiter. Alguns são pequenos como uma casa, outros têm centenas de quilômetros. Os "
     "cientistas vigiam os que passam perto da Terra, porque a queda de um asteroide grande pode causar muita destruição."),
    ("as estrelas cadentes",
     "Estrela cadente é o risco de luz que um pedaço de rocha espacial faz ao queimar na atmosfera.",
     "Apesar do nome, estrela cadente não é uma estrela. É um meteoro: um pedacinho de rocha ou poeira do espaço que "
     "entra na atmosfera muito rápido, esquenta e brilha por alguns segundos. Quando sobra um pedaço que chega ao "
     "chão, ele se chama meteorito. Em certas épocas do ano há chuvas de meteoros."),
    ("Marte",
     "Marte é o quarto planeta a partir do Sol, conhecido como planeta vermelho.",
     "Marte é o quarto planeta do Sistema Solar. A cor avermelhada vem do óxido de ferro, a ferrugem, que cobre o "
     "solo. É um planeta frio, com uma atmosfera muito fina, e tem o maior vulcão conhecido do Sistema Solar, o Monte "
     "Olimpo. Robôs enviados pela Terra exploram a superfície em busca de sinais de água e de vida no passado."),
    ("Júpiter",
     "Júpiter é o maior planeta do Sistema Solar, um gigante gasoso.",
     "Júpiter é o quinto planeta a partir do Sol e o maior do Sistema Solar: caberiam mais de mil Terras dentro dele. "
     "É formado principalmente por gases e não tem uma superfície sólida como a da Terra. Tem uma tempestade gigante "
     "chamada Grande Mancha Vermelha e dezenas de luas, como Io, Europa, Ganimedes e Calisto."),
    ("Saturno",
     "Saturno é o sexto planeta a partir do Sol, famoso pelos anéis.",
     "Saturno é um gigante gasoso e o segundo maior planeta do Sistema Solar. É famoso pelos anéis, formados por "
     "bilhões de pedaços de gelo e rocha que giram em volta dele. Ele é tão pouco denso que, se houvesse uma banheira "
     "grande o bastante, flutuaria. Titã, sua maior lua, tem uma atmosfera espessa."),
    ("Vênus",
     "Vênus é o segundo planeta a partir do Sol e o mais quente do Sistema Solar.",
     "Vênus é o segundo planeta a partir do Sol e tem tamanho parecido com o da Terra. É coberto por nuvens grossas e "
     "tem uma atmosfera de gás carbônico que prende o calor, por isso é o planeta mais quente do Sistema Solar, mais "
     "até que Mercúrio. Visto da Terra, é o astro mais brilhante do céu depois do Sol e da Lua e é chamado de "
     "estrela-d'alva."),
    ("Mercúrio",
     "Mercúrio é o menor planeta do Sistema Solar e o mais próximo do Sol.",
     "Mercúrio é o planeta mais perto do Sol e o menor do Sistema Solar. Quase não tem atmosfera, por isso o dia é "
     "muito quente e a noite é muito fria. A superfície é cheia de crateras, parecida com a da Lua. Ele dá a volta em "
     "torno do Sol em apenas 88 dias."),
    ("Netuno",
     "Netuno é o oitavo e mais distante planeta do Sistema Solar, um gigante azulado.",
     "Netuno é o planeta mais distante do Sol. É um gigante gelado, de cor azulada por causa do gás metano, e tem os "
     "ventos mais fortes do Sistema Solar. Foi descoberto com a ajuda de cálculos matemáticos antes de ser visto no "
     "telescópio. Ele leva cerca de 165 anos para dar uma volta em torno do Sol."),
    ("Plutão",
     "Plutão é um planeta-anão que fica além de Netuno.",
     "Plutão foi considerado o nono planeta até 2006, quando os astrônomos o reclassificaram como planeta-anão. Ele é "
     "menor que a nossa Lua e fica numa região gelada além de Netuno, cheia de outros corpos pequenos. Em 2015, a "
     "sonda New Horizons passou perto de Plutão e mostrou uma grande área clara em forma de coração."),
    ("a Via Láctea",
     "A Via Láctea é a galáxia onde fica o Sistema Solar.",
     "A Via Láctea é a nossa galáxia, um conjunto de centenas de bilhões de estrelas, além de gás e poeira. Ela tem a "
     "forma de um disco com braços em espiral, e o Sistema Solar fica num desses braços. Em noites escuras, longe das "
     "luzes da cidade, dá para ver a Via Láctea como uma faixa esbranquiçada no céu."),
    ("as constelações",
     "Constelações são grupos de estrelas que, vistos da Terra, parecem formar desenhos no céu.",
     "As constelações são grupos de estrelas que os povos imaginaram formando figuras, como animais e heróis. As "
     "estrelas de uma constelação podem estar a distâncias muito diferentes da Terra. Hoje os astrônomos reconhecem 88 "
     "constelações. O Cruzeiro do Sul, que aparece na bandeira do Brasil, ajuda a encontrar a direção sul."),
    ("a Estação Espacial Internacional",
     "A Estação Espacial Internacional é um laboratório que gira em volta da Terra, onde astronautas vivem e trabalham.",
     "A Estação Espacial Internacional é um grande laboratório em órbita da Terra, construído por vários países. Ela "
     "dá uma volta no planeta em cerca de uma hora e meia. Os astronautas que vivem lá fazem experiências sobre como "
     "a falta de peso afeta o corpo, as plantas e os materiais. Às vezes, dá para ver a estação passando no céu como um ponto brilhante."),
    ("os astronautas",
     "Astronauta é a pessoa treinada para viajar e trabalhar no espaço.",
     "Os astronautas passam por um treinamento longo, com estudo, exercícios físicos e simulações. No espaço, flutuam "
     "por causa da falta de peso, comem alimentos preparados especialmente e precisam se exercitar todos os dias para "
     "não perder músculos e ossos. O primeiro ser humano no espaço foi Iuri Gagarin, em 1961, e o primeiro brasileiro "
     "foi Marcos Pontes, em 2006."),
    ("os foguetes",
     "Foguete é um veículo que sobe ao espaço empurrado pelos gases que solta para trás.",
     "Os foguetes funcionam pelo princípio da ação e reação: queimam combustível e soltam gases muito rápido para "
     "baixo, o que empurra o foguete para cima. Eles levam satélites, sondas e astronautas ao espaço. Muitos têm "
     "partes, chamadas estágios, que se soltam quando o combustível acaba. Hoje, alguns foguetes voltam e pousam para "
     "serem usados de novo."),
    ("os telescópios",
     "Telescópio é um instrumento que aumenta a imagem de objetos distantes, como estrelas e planetas.",
     "Os telescópios recolhem a luz de objetos distantes e formam imagens aumentadas. Galileu Galilei foi um dos "
     "primeiros a usá-los para estudar o céu e viu as luas de Júpiter. Há telescópios em montanhas, longe das luzes "
     "das cidades, e no espaço, como o Hubble e o James Webb, que mostram galáxias muito distantes."),
    ("a gravidade",
     "Gravidade é a força que faz os corpos se atraírem; é ela que faz as coisas caírem e nos prende ao chão.",
     "A gravidade é a força de atração entre corpos que têm massa. É por causa dela que as coisas caem, que nós ficamos "
     "presos ao chão e que a Lua gira em volta da Terra. Quanto maior a massa de um corpo, mais forte é a gravidade "
     "dele: na Lua, que é menor, uma pessoa pesaria cerca de seis vezes menos. Isaac Newton descreveu a gravidade no século dezessete."),
    ("o Big Bang",
     "O Big Bang é a teoria de que o universo começou muito quente e concentrado e vem se expandindo há bilhões de anos.",
     "A teoria do Big Bang diz que, há cerca de 13,8 bilhões de anos, todo o universo estava muito quente e "
     "concentrado e começou a se expandir. Com o tempo, ele esfriou e se formaram os átomos, as estrelas e as galáxias. "
     "Uma das provas é que as galáxias estão se afastando umas das outras. Outra é uma radiação fraca que vem de todas as direções do céu."),
    ("as fases da Lua",
     "As fases da Lua são nova, crescente, cheia e minguante.",
     "As fases da Lua mudam porque, ao girar em volta da Terra, a Lua mostra para nós partes diferentes do seu lado "
     "iluminado pelo Sol. Na lua nova, quase não a vemos; depois vêm a crescente, a cheia e a minguante. O ciclo "
     "completo dura cerca de 29 dias e meio."),
    ("os satélites artificiais",
     "Satélites artificiais são aparelhos lançados ao espaço que giram em volta da Terra.",
     "Os satélites artificiais são levados ao espaço por foguetes e ficam girando em volta da Terra. Eles servem para "
     "comunicações, televisão, internet, previsão do tempo, localização por GPS e observação do planeta, como o "
     "monitoramento do desmatamento. O primeiro satélite artificial foi o Sputnik 1, lançado pela União Soviética em 1957."),
]
