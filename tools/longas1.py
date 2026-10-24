"""Respostas longas (parte 1: ciência, natureza e espaço).

Cada item: (assunto com artigo ou None, pergunta, texto). O texto tem 2 parágrafos (~100 a 150 palavras).
O gerador monta a pergunta original, "Escreva um texto longo sobre <assunto>." e "<pergunta> Explique com
detalhes." (ver gerar_pergeresp.longas_sections).
"""

LONGAS = [
    ("os vulcões", "Como funcionam os vulcões?",
     "Os vulcões são aberturas na crosta da Terra por onde sai o magma, a rocha derretida que fica lá embaixo. O "
     "magma é mais leve que as rochas em volta e vai subindo, acumulando-se em câmaras abaixo da superfície. Ele "
     "carrega muitos gases dissolvidos, como vapor de água e gás carbônico, e, quando a pressão desses gases fica "
     "grande demais, o magma rompe o caminho e sai como lava, cinzas e fumaça.\n\n"
     "Existem erupções calmas, em que a lava escorre devagar, como no Havaí, e erupções explosivas, que lançam "
     "nuvens de cinzas a quilômetros de altura. A maior parte dos vulcões fica nas bordas das placas tectônicas, "
     "como no chamado Círculo de Fogo do Pacífico. Apesar do perigo, as cinzas vulcânicas deixam o solo muito "
     "fértil, e por isso muitas pessoas vivem perto deles."),
    ("o ciclo da água", "Como funciona o ciclo da água?",
     "O ciclo da água é o caminho que a água faz sem parar entre o mar, o ar e a terra. Com o calor do Sol, a água "
     "de oceanos, rios e lagos evapora e sobe como vapor. As plantas também soltam vapor pelas folhas, na "
     "transpiração. Lá no alto, o ar é mais frio, e o vapor se condensa em gotinhas que formam as nuvens.\n\n"
     "Quando as gotinhas se juntam e ficam pesadas, caem como chuva, neve ou granizo. Parte dessa água escorre para "
     "os rios e volta ao mar; outra parte se infiltra no solo e forma os lençóis subterrâneos, que abastecem poços e "
     "nascentes. Assim, a mesma água circula pelo planeta há bilhões de anos. Desmatar e poluir atrapalham esse "
     "ciclo e afetam as chuvas e o abastecimento das cidades."),
    ("a fotossíntese", "O que é a fotossíntese?",
     "A fotossíntese é o processo que as plantas, as algas e algumas bactérias usam para fabricar o próprio "
     "alimento. Nas folhas, existe um pigmento verde chamado clorofila, que captura a energia da luz do Sol. Com "
     "essa energia, a planta junta a água que vem das raízes e o gás carbônico que entra pelas folhas e produz "
     "glicose, um açúcar que serve de energia e de matéria-prima para crescer.\n\n"
     "Nesse processo, a planta libera oxigênio para o ar. Quase todo o oxigênio que respiramos foi produzido por "
     "plantas e algas, e boa parte dele vem das algas microscópicas dos oceanos. A fotossíntese também está na base "
     "de quase todas as cadeias alimentares: os animais comem as plantas, ou comem animais que comeram plantas. Sem "
     "ela, a vida na Terra seria muito diferente."),
    ("o Sistema Solar", "Como é o Sistema Solar?",
     "O Sistema Solar é formado pelo Sol e por tudo o que gira em volta dele: oito planetas, seus satélites, "
     "planetas anões como Plutão, asteroides, cometas e muita poeira. O Sol concentra quase toda a massa do sistema, "
     "e é a gravidade dele que mantém os planetas em suas órbitas.\n\n"
     "Os quatro planetas mais próximos do Sol, Mercúrio, Vênus, Terra e Marte, são rochosos e pequenos. Depois do "
     "cinturão de asteroides vêm os gigantes Júpiter e Saturno, feitos principalmente de gás, e Urano e Netuno, "
     "mais distantes e gelados. Júpiter é o maior de todos, e Saturno é famoso pelos anéis. A Terra é o único "
     "planeta onde se conhece vida, graças à água líquida e à distância certa do Sol."),
    ("os buracos negros", "O que é um buraco negro?",
     "Um buraco negro é uma região do espaço onde a gravidade é tão forte que nada consegue escapar, nem mesmo a "
     "luz. Por isso ele é escuro. Muitos buracos negros se formam quando uma estrela muito grande chega ao fim da "
     "vida: o núcleo dela desaba sobre si mesmo e a matéria fica espremida num espaço minúsculo.\n\n"
     "Não dá para ver um buraco negro diretamente, mas os astrônomos percebem o efeito dele no que está em volta, "
     "como estrelas girando muito rápido ou gás superaquecido brilhando antes de cair. No centro da nossa galáxia, a "
     "Via Láctea, existe um buraco negro gigante, milhões de vezes mais pesado que o Sol. Em 2019, cientistas "
     "divulgaram a primeira imagem da sombra de um buraco negro, numa galáxia distante."),
    ("as estrelas", "Como nascem e morrem as estrelas?",
     "As estrelas nascem em grandes nuvens de gás e poeira no espaço. Em alguma parte da nuvem, a gravidade junta "
     "a matéria, que vai ficando cada vez mais densa e quente. Quando o centro chega a milhões de graus, começa a "
     "fusão nuclear: átomos de hidrogênio se unem formando hélio e liberando muita energia. Nesse momento, nasce uma "
     "estrela.\n\n"
     "O destino da estrela depende do tamanho dela. Estrelas como o Sol brilham por bilhões de anos, depois incham "
     "e viram gigantes vermelhas, soltam as camadas de fora e terminam como anãs brancas, pequenas e quentes. "
     "Estrelas muito maiores vivem menos e explodem como supernovas, deixando estrelas de nêutrons ou buracos "
     "negros. Muitos elementos que existem no nosso corpo foram formados dentro de estrelas antigas."),
    ("a Lua", "O que sabemos sobre a Lua?",
     "A Lua é o único satélite natural da Terra e fica, em média, a cerca de 384 mil quilômetros de distância. A "
     "explicação mais aceita para a origem dela é que, há uns 4,5 bilhões de anos, um corpo do tamanho de Marte "
     "bateu na Terra, e os pedaços lançados no espaço se juntaram e formaram a Lua.\n\n"
     "Ela não tem luz própria: reflete a luz do Sol, e por isso vemos as fases, conforme a parte iluminada virada "
     "para nós. A Lua sempre mostra a mesma face para a Terra, porque leva o mesmo tempo para girar em torno de si "
     "e em torno do planeta. A gravidade dela provoca as marés nos oceanos. Entre 1969 e 1972, doze astronautas "
     "das missões Apollo caminharam na superfície lunar."),
    ("os dinossauros", "Quem foram os dinossauros?",
     "Os dinossauros foram répteis que dominaram a Terra por mais de 160 milhões de anos, até cerca de 66 milhões de "
     "anos atrás. Havia espécies de todos os tamanhos: gigantes herbívoros de pescoço longo, como o braquiossauro, "
     "caçadores como o tiranossauro e pequenos dinossauros do tamanho de uma galinha. Sabemos sobre eles pelos "
     "fósseis, ossos e pegadas que ficaram nas rochas.\n\n"
     "A maioria dos dinossauros desapareceu depois que um asteroide enorme caiu onde hoje é o México. O impacto "
     "levantou poeira e fumaça, escureceu o céu e mudou o clima, e muitas plantas e animais morreram. Mas nem todos "
     "sumiram: as aves são descendentes de dinossauros. No Brasil, foram encontrados vários fósseis, em estados como "
     "Rio Grande do Sul, Minas Gerais e Maranhão."),
    ("a evolução das espécies", "O que é a evolução das espécies?",
     "A evolução é o processo pelo qual os seres vivos mudam ao longo de muitas gerações. Dentro de uma espécie, os "
     "indivíduos não são iguais: uns são mais rápidos, outros têm cores diferentes, e parte dessas diferenças passa "
     "dos pais para os filhos. Os que têm características mais vantajosas para o ambiente sobrevivem mais e deixam "
     "mais filhotes.\n\n"
     "Com o tempo, essas características se espalham, e a espécie vai mudando. Esse mecanismo, chamado seleção "
     "natural, foi explicado por Charles Darwin e Alfred Wallace no século XIX. Depois de milhões de anos, uma "
     "população pode dar origem a espécies novas. Fósseis, comparações entre os corpos dos animais e estudos do DNA "
     "mostram que todos os seres vivos têm parentesco entre si."),
    ("o DNA", "O que é o DNA?",
     "O DNA é uma molécula que fica dentro das células e guarda as instruções para formar e fazer funcionar um ser "
     "vivo. Ele tem o formato de uma escada torcida, a dupla hélice, e os degraus são formados por quatro tipos de "
     "peças, representadas pelas letras A, T, C e G. A ordem dessas letras funciona como um código.\n\n"
     "Pedaços de DNA chamados genes dizem à célula como fabricar proteínas, que constroem e controlam o corpo. Metade "
     "do nosso DNA vem da mãe e metade do pai, e é por isso que nos parecemos com eles. O estudo do DNA ajuda a "
     "entender doenças, desenvolver remédios, identificar pessoas e descobrir o parentesco entre espécies."),
    ("as células", "O que são as células?",
     "As células são as menores partes vivas de um ser vivo, como os tijolos de uma construção. Algumas criaturas, "
     "como as bactérias, são formadas por uma única célula. Outras, como as plantas e os animais, têm bilhões delas; "
     "o corpo humano tem dezenas de trilhões. A maioria das células é tão pequena que só pode ser vista ao "
     "microscópio.\n\n"
     "Cada célula tem uma membrana que a envolve e controla o que entra e o que sai. Nas plantas e nos animais, o "
     "núcleo guarda o DNA, e outras estruturas cuidam da energia e da produção de substâncias. As células se "
     "especializam: há células dos músculos, dos nervos, do sangue, da pele. Elas se multiplicam dividindo-se em "
     "duas, e é assim que crescemos e repomos as células que morrem."),
    ("as bactérias", "O que são as bactérias?",
     "As bactérias são seres vivos formados por uma única célula, tão pequenos que só aparecem ao microscópio. Elas "
     "estão em quase todo lugar: no solo, na água, no ar e dentro do nosso corpo. Muitas pessoas pensam nelas só "
     "como causadoras de doenças, mas a maioria das bactérias é inofensiva, e muitas são muito úteis.\n\n"
     "No intestino, bilhões de bactérias ajudam na digestão e na defesa do corpo. Na natureza, elas decompõem restos "
     "de plantas e animais e devolvem os nutrientes ao solo. As bactérias também são usadas para fazer iogurte e "
     "queijo. Algumas, porém, causam doenças, como a tuberculose, e por isso os antibióticos são tão importantes. "
     "Usar antibiótico sem necessidade faz surgirem bactérias resistentes, difíceis de combater."),
    ("os vírus", "O que são os vírus?",
     "Os vírus são partículas muito menores que as bactérias, formadas basicamente por material genético envolvido "
     "numa capa de proteína. Eles não conseguem se reproduzir sozinhos: precisam entrar numa célula viva e usar a "
     "maquinaria dela para fazer cópias de si mesmos. Por isso, muitos cientistas consideram que os vírus ficam na "
     "fronteira entre o vivo e o não vivo.\n\n"
     "Os vírus causam doenças como gripe, resfriado, sarampo e dengue. Como são diferentes das bactérias, os "
     "antibióticos não funcionam contra eles. A melhor proteção contra muitas viroses são as vacinas, que treinam o "
     "sistema de defesa. Hábitos simples, como lavar as mãos e cobrir a boca ao tossir, também ajudam a impedir que "
     "os vírus se espalhem."),
    ("a gravidade", "O que é a gravidade?",
     "A gravidade é a força de atração que existe entre tudo o que tem massa. Quanto maior a massa de um corpo, mais "
     "forte é a atração que ele exerce, e ela fica mais fraca com a distância. É a gravidade da Terra que faz os "
     "objetos caírem e nos mantém presos ao chão, e é a do Sol que segura os planetas em suas órbitas.\n\n"
     "Isaac Newton descreveu a gravidade no século XVII e mostrou que a mesma força que derruba uma maçã mantém a Lua "
     "girando em torno da Terra. Mais tarde, Albert Einstein explicou a gravidade como uma curvatura do espaço e do "
     "tempo causada pela massa. Na Lua, a gravidade é cerca de seis vezes mais fraca que na Terra, e por isso os "
     "astronautas pulavam tão alto."),
    ("a eletricidade", "O que é a eletricidade?",
     "A eletricidade é uma forma de energia ligada às cargas elétricas, presentes em todos os átomos. Quando "
     "partículas chamadas elétrons se movem de forma organizada por um material, como um fio de cobre, temos uma "
     "corrente elétrica. Os materiais que deixam a corrente passar com facilidade são chamados condutores, e os que "
     "bloqueiam, como a borracha e o plástico, são isolantes.\n\n"
     "Nas usinas, a eletricidade é gerada girando ímãs dentro de bobinas de fio, movidos pela força da água, do "
     "vento, do vapor ou de outras fontes. Ela chega às casas pelos fios e faz funcionar lâmpadas, geladeiras, "
     "computadores e celulares. Como a corrente pode passar pelo corpo e causar choques graves, é preciso cuidado "
     "com tomadas, fios desencapados e aparelhos molhados."),
    ("o magnetismo", "O que é o magnetismo?",
     "O magnetismo é a propriedade que certos materiais têm de atrair ou repelir outros, como os ímãs fazem com o "
     "ferro. Todo ímã tem dois polos, o norte e o sul. Polos diferentes se atraem e polos iguais se repelem. Em "
     "volta do ímã existe um campo magnético, uma região invisível onde essa força age.\n\n"
     "A própria Terra funciona como um ímã gigante, por causa do movimento do metal derretido no núcleo. É por isso "
     "que a agulha da bússola aponta para o norte. O campo magnético da Terra também protege o planeta de partículas "
     "que vêm do Sol; quando algumas delas chegam perto dos polos, formam as auroras. O magnetismo e a eletricidade "
     "estão ligados e são a base de motores, alto-falantes e geradores."),
    ("a luz", "O que é a luz?",
     "A luz é uma forma de energia que viaja pelo espaço como uma onda e, ao mesmo tempo, em pequenos pacotes "
     "chamados fótons. Ela é a coisa mais rápida que existe: percorre cerca de 300 mil quilômetros por segundo e "
     "leva uns oito minutos para chegar do Sol até a Terra. A luz pode atravessar o vácuo, por isso nos alcança "
     "vinda das estrelas.\n\n"
     "A luz branca é uma mistura de cores, como mostra o arco-íris. Os objetos têm cor porque absorvem algumas "
     "dessas cores e refletem outras. Além da luz visível, existem outras ondas do mesmo tipo que não enxergamos, "
     "como o infravermelho, o ultravioleta, as ondas de rádio e os raios X. Sem a luz do Sol, não haveria "
     "fotossíntese nem vida como conhecemos."),
    ("o som", "Como o som funciona?",
     "O som é uma vibração que se propaga pelo ar, pela água ou por materiais sólidos. Quando um objeto vibra, como "
     "a corda de um violão, ele empurra as partículas do ar à sua volta, que empurram as vizinhas, formando uma onda. "
     "Essa onda chega aos nossos ouvidos e faz o tímpano vibrar; o cérebro interpreta essas vibrações como som.\n\n"
     "Vibrações rápidas produzem sons agudos, e vibrações lentas, sons graves. A força da vibração define se o som é "
     "alto ou baixo. O som viaja a cerca de 340 metros por segundo no ar e ainda mais rápido na água e nos sólidos. "
     "No espaço, onde quase não há matéria, o som não se propaga. Barulho muito alto por muito tempo pode prejudicar "
     "a audição."),
    ("os oceanos", "Qual é a importância dos oceanos?",
     "Os oceanos cobrem cerca de 70% da superfície da Terra e guardam quase toda a água do planeta. São cinco: "
     "Pacífico, Atlântico, Índico, Glacial Ártico e Glacial Antártico. Eles abrigam uma enorme variedade de vida, "
     "das algas microscópicas às baleias, e muitas espécies do fundo do mar ainda nem foram descobertas.\n\n"
     "Os oceanos são essenciais para o clima. Eles absorvem calor e gás carbônico, e as correntes marinhas levam "
     "calor de uma região para outra. As algas do mar produzem boa parte do oxigênio que respiramos. Além disso, "
     "milhões de pessoas dependem da pesca e do transporte marítimo. A poluição por plástico, a pesca exagerada e o "
     "aquecimento da água estão entre as maiores ameaças a esse ambiente."),
    ("as florestas tropicais", "Por que as florestas tropicais são importantes?",
     "As florestas tropicais ficam nas regiões quentes e chuvosas perto da linha do Equador, como a Amazônia, as "
     "florestas da África Central e as do Sudeste Asiático. Elas ocupam uma parte pequena da superfície da Terra, "
     "mas abrigam mais da metade das espécies de plantas e animais conhecidas.\n\n"
     "Essas florestas guardam muito carbono nas árvores e no solo e ajudam a controlar o clima. Na Amazônia, a água "
     "que as árvores soltam no ar forma os chamados rios voadores, que levam chuva para outras regiões do Brasil. Das "
     "florestas também vêm frutas, fibras e substâncias usadas em remédios. O desmatamento para pasto, agricultura e "
     "garimpo ameaça esse patrimônio e os povos que vivem nele."),
    ("o aquecimento global", "O que é o aquecimento global?",
     "O aquecimento global é o aumento da temperatura média da Terra nas últimas décadas. A principal causa é a "
     "queima de carvão, petróleo e gás natural, além do desmatamento, que lançam no ar gases como o gás carbônico e "
     "o metano. Esses gases reforçam o efeito estufa: seguram parte do calor que a Terra mandaria de volta para o "
     "espaço.\n\n"
     "Com mais calor, as geleiras derretem, o nível do mar sobe e ficam mais comuns secas, ondas de calor, "
     "tempestades e enchentes. Isso afeta a agricultura, a saúde e a vida de muitos animais. Para frear o "
     "aquecimento, os países discutem acordos para reduzir as emissões, trocar combustíveis fósseis por energia "
     "limpa, como a solar e a eólica, e proteger as florestas."),
    ("o efeito estufa", "O que é o efeito estufa?",
     "O efeito estufa é um fenômeno natural que mantém a Terra aquecida. A luz do Sol atravessa a atmosfera e "
     "esquenta a superfície do planeta, que então solta calor. Alguns gases da atmosfera, como o vapor de água, o gás "
     "carbônico e o metano, seguram parte desse calor, como o vidro de uma estufa de plantas.\n\n"
     "Sem o efeito estufa, a temperatura média da Terra seria de uns 18 graus abaixo de zero, e quase não haveria "
     "vida. O problema é que, desde a Revolução Industrial, as atividades humanas aumentaram muito a quantidade "
     "desses gases, principalmente pela queima de combustíveis e pelo desmatamento. Com isso, o efeito ficou mais "
     "forte do que o natural e a Terra está esquentando."),
    ("as placas tectônicas", "O que são as placas tectônicas?",
     "A camada de fora da Terra, a crosta, junto com a parte de cima do manto, é quebrada em grandes pedaços "
     "chamados placas tectônicas. Elas flutuam sobre rochas muito quentes e se movem devagar, poucos centímetros por "
     "ano, mais ou menos a velocidade com que as unhas crescem.\n\n"
     "Nas bordas, as placas se afastam, se chocam ou deslizam uma ao lado da outra. Esses movimentos causam "
     "terremotos, formam vulcões e levantam cordilheiras, como os Andes e o Himalaia. Há cerca de 200 milhões de "
     "anos, os continentes estavam juntos num único bloco, a Pangeia, e o movimento das placas os separou. Por isso o "
     "contorno da América do Sul se encaixa com o da África."),
    ("as abelhas", "Qual é a importância das abelhas?",
     "As abelhas são insetos que vivem, em muitas espécies, em colônias organizadas, com uma rainha, operárias e "
     "zangões. As operárias saem para buscar néctar e pólen nas flores e voltam para a colmeia, onde transformam o "
     "néctar em mel. Existem milhares de espécies de abelhas, e muitas brasileiras, como a jataí, nem têm ferrão.\n\n"
     "A maior importância das abelhas é a polinização. Ao passar de flor em flor, elas levam o pólen que permite às "
     "plantas formar frutos e sementes. Grande parte das frutas, verduras e grãos que comemos depende desse "
     "trabalho. O uso exagerado de agrotóxicos, a destruição de habitats e as doenças estão diminuindo as populações "
     "de abelhas, o que preocupa cientistas e agricultores."),
    ("os golfinhos", "Como vivem os golfinhos?",
     "Os golfinhos são mamíferos marinhos muito inteligentes. Como todo mamífero, eles respiram ar, e por isso sobem "
     "à superfície e respiram por um orifício no alto da cabeça. As fêmeas amamentam os filhotes, que nascem já "
     "sabendo nadar. Os golfinhos vivem em grupos, chamados de bandos, e caçam peixes e lulas em equipe.\n\n"
     "Eles se comunicam com assobios e estalos e usam a ecolocalização: emitem sons e escutam o eco que volta dos "
     "objetos para perceber o que está em volta, até no escuro. Existem golfinhos de água doce, como o boto-cor-de-"
     "rosa da Amazônia. A poluição, a pesca com redes e o barulho dos barcos estão entre as ameaças a esses animais."),
    ("os tubarões", "Como são os tubarões?",
     "Os tubarões são peixes que vivem nos oceanos há mais de 400 milhões de anos, desde antes dos dinossauros. Em vez "
     "de ossos, o esqueleto deles é feito de cartilagem, o mesmo material da nossa orelha. Eles respiram com "
     "brânquias e têm várias fileiras de dentes, que caem e são substituídos ao longo da vida.\n\n"
     "Existem centenas de espécies, do pequeno tubarão-lanterna ao tubarão-baleia, o maior peixe do mundo, que se "
     "alimenta de plâncton. Os tubarões têm um olfato muito apurado e sentem até os pequenos sinais elétricos dos "
     "animais. Ataques a pessoas são raros. Na verdade, os tubarões correm mais perigo de nós: milhões são pescados "
     "todos os anos, e muitas espécies estão ameaçadas."),
    ("as formigas", "Como vivem as formigas?",
     "As formigas são insetos que vivem em colônias, às vezes com milhões de indivíduos. Cada colônia tem uma ou mais "
     "rainhas, que põem os ovos, e muitas operárias, que fazem todo o resto: buscam comida, cuidam das larvas, "
     "constroem e defendem o formigueiro. Existem mais de 12 mil espécies conhecidas.\n\n"
     "As formigas se comunicam principalmente por cheiros, os feromônios. Quando uma operária acha comida, ela deixa "
     "um rastro que as outras seguem, por isso andam em fila. Algumas espécies, como as saúvas, cortam folhas e as "
     "levam para o formigueiro, onde cultivam um fungo que serve de alimento. As formigas ajudam a arejar o solo e a "
     "espalhar sementes."),
    ("as borboletas", "Como as borboletas se desenvolvem?",
     "As borboletas passam por uma transformação completa chamada metamorfose, com quatro fases. Primeiro, a fêmea "
     "põe ovos numa planta. Do ovo sai a lagarta, que passa os dias comendo folhas e crescendo, trocando de pele "
     "várias vezes.\n\n"
     "Quando chega a hora, a lagarta forma uma crisálida, uma espécie de casulo, e dentro dela o corpo se reorganiza "
     "por inteiro. Depois de alguns dias ou semanas, sai a borboleta adulta, com asas coloridas cobertas de pequenas "
     "escamas. Adultas, elas se alimentam de néctar com uma língua comprida e enrolada e ajudam a polinizar as "
     "flores. Muitas cores servem para atrair parceiros ou avisar aos predadores que a borboleta tem gosto ruim."),
    ("a onça-pintada", "O que você sabe sobre a onça-pintada?",
     "A onça-pintada é o maior felino das Américas e o terceiro maior do mundo, depois do tigre e do leão. Ela vive "
     "em florestas e áreas alagadas, como a Amazônia e o Pantanal. A pelagem amarelada tem manchas em forma de "
     "rosetas, que ajudam a camuflar o animal entre a vegetação, e existem também onças quase pretas.\n\n"
     "A onça é uma caçadora solitária e tem a mordida mais forte entre os felinos, capaz de atravessar o casco de "
     "uma tartaruga. Ela caça capivaras, jacarés, veados e peixes e, ao contrário de muitos gatos, gosta de água e "
     "nada muito bem. O desmatamento, as queimadas e a caça fazem dela uma espécie ameaçada. Proteger a onça é "
     "proteger também todo o ambiente onde ela vive."),
    ("as árvores", "Como uma árvore cresce?",
     "Uma árvore começa como uma semente, que guarda uma plantinha em miniatura e uma reserva de alimento. Com água, "
     "calor e ar, a semente germina: primeiro sai a raiz, que busca água e prende a planta no solo, e depois o "
     "caule, que sobe em direção à luz. As primeiras folhas começam a fazer fotossíntese e produzir o alimento da "
     "planta.\n\n"
     "Ano após ano, a árvore cresce para cima, nas pontas dos galhos, e também engrossa, formando uma nova camada de "
     "madeira por baixo da casca. Em muitos lugares, essas camadas formam os anéis que permitem calcular a idade de "
     "uma árvore cortada. Algumas árvores vivem milhares de anos. Elas oferecem sombra, frutos, madeira, abrigo para "
     "os animais e ajudam a regular o clima."),
    ("as estações do ano", "Como acontecem as estações do ano?",
     "As estações do ano acontecem porque o eixo da Terra é inclinado, cerca de 23 graus, em relação ao caminho que "
     "ela faz em torno do Sol. Enquanto a Terra dá a volta, ora o hemisfério norte fica mais virado para o Sol, ora o "
     "hemisfério sul. O hemisfério mais virado recebe a luz de forma mais direta e por mais horas, e tem verão.\n\n"
     "Por isso, quando é verão no Brasil, é inverno na Europa, e o contrário. Entre o verão e o inverno, vêm o outono "
     "e a primavera. Perto da linha do Equador, as estações quase não se diferenciam pela temperatura, mas sim pelas "
     "chuvas, e muitas regiões do Brasil têm uma época seca e outra chuvosa. Perto dos polos, as diferenças são "
     "enormes, com meses de dia ou de noite."),
    ("a camada de ozônio", "O que é a camada de ozônio?",
     "A camada de ozônio é uma faixa da atmosfera, entre 15 e 35 quilômetros de altura, onde há mais concentração de "
     "um gás chamado ozônio. Ela funciona como um filtro: absorve a maior parte dos raios ultravioleta do Sol, que em "
     "excesso causam queimaduras, câncer de pele e problemas nos olhos, além de prejudicar plantas e animais.\n\n"
     "Nos anos 1980, cientistas descobriram um buraco nessa camada sobre a Antártida, causado por gases chamados "
     "CFCs, usados em geladeiras e sprays. Em 1987, os países assinaram o Protocolo de Montreal e proibiram esses "
     "gases. Desde então, a camada de ozônio está se recuperando aos poucos, e o acordo é considerado um exemplo de "
     "cooperação mundial que deu certo."),
    ("os rios", "Qual é a importância dos rios?",
     "Os rios são cursos de água doce que nascem em nascentes, lagos ou geleiras e correm até o mar, um lago ou outro "
     "rio. Ao longo do caminho, recebem a água das chuvas e de rios menores, chamados afluentes. O Brasil tem algumas "
     "das maiores bacias hidrográficas do mundo, como a do Amazonas, a do Paraná e a do São Francisco.\n\n"
     "Os rios fornecem água para beber, irrigar plantações e abastecer indústrias, além de servir para a pesca e o "
     "transporte. Muitas cidades nasceram às suas margens. As usinas hidrelétricas usam a força da água para gerar "
     "boa parte da energia elétrica do Brasil. O esgoto sem tratamento, o lixo e o desmatamento das margens poluem e "
     "assoreiam os rios, e por isso é preciso protegê-los."),
    ("os terremotos", "Como acontecem os terremotos?",
     "Os terremotos são tremores do chão causados pela liberação repentina de energia dentro da Terra. A crosta é "
     "dividida em placas tectônicas que se movem devagar. Em alguns pontos, elas ficam travadas umas nas outras, e a "
     "tensão vai se acumulando por anos. Quando a rocha não aguenta mais, ela se rompe e desliza de uma vez, e as "
     "vibrações se espalham em ondas.\n\n"
     "A força de um terremoto é medida por escalas como a de magnitude, e os mais fortes podem derrubar prédios e "
     "causar tsunamis quando acontecem no fundo do mar. Os países mais afetados ficam nas bordas das placas, como "
     "Japão, Chile e Indonésia. Não é possível prever o momento exato de um terremoto, mas construções resistentes e "
     "treinamento salvam muitas vidas."),
    ("os cometas", "O que são os cometas?",
     "Os cometas são corpos pequenos feitos de gelo, poeira e rochas que giram em torno do Sol, em geral em órbitas "
     "bem alongadas. Muitas vezes são chamados de bolas de neve sujas. Eles vêm das regiões mais distantes do Sistema "
     "Solar e passam a maior parte do tempo longe do Sol, escuros e congelados.\n\n"
     "Quando um cometa se aproxima do Sol, o calor faz o gelo virar gás, que arrasta poeira e forma uma nuvem "
     "brilhante em volta do núcleo, a coma, e uma ou mais caudas que podem ter milhões de quilômetros. As caudas "
     "sempre apontam para longe do Sol, empurradas pelo vento solar. O cometa Halley, um dos mais famosos, passa "
     "perto da Terra a cada 76 anos, mais ou menos."),
    ("o corpo humano e a água", "Por que a água é tão importante para o corpo?",
     "A água forma cerca de 60% do peso de um adulto e está em todas as células. Ela é o meio onde acontecem as "
     "reações químicas do corpo e faz parte do sangue, que transporta oxigênio e nutrientes. A água também ajuda na "
     "digestão, amolece as fezes, lubrifica as articulações e protege órgãos como o cérebro.\n\n"
     "Outra função importante é controlar a temperatura: quando o corpo esquenta, o suor evapora e leva o calor "
     "embora. Como perdemos água o tempo todo, pela urina, pelo suor e até pela respiração, precisamos repor "
     "diariamente, bebendo água e comendo alimentos como frutas e verduras. Sede, boca seca, urina escura e dor de "
     "cabeça podem ser sinais de que falta água."),
]
