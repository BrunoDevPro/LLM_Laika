"""Resumos escritos à mão (parte 5): textos novos de explicação, curiosidade e instrução.

Mesmo formato de resumos4.py: (texto, uma frase, duas frases, três tópicos).
"""

TEXTOS = [
    ("O sal de cozinha que usamos todos os dias é, na maior parte, cloreto de sódio. No Brasil, boa parte dele vem "
     "das salinas do Rio Grande do Norte, onde a água do mar é levada para tanques rasos. Com o sol forte e o vento, "
     "a água evapora devagar, e o sal fica no fundo, formando uma camada branca que depois é recolhida.\n\n"
     "O sal é importante para o corpo, porque ajuda a controlar a água e o funcionamento dos nervos e dos músculos. "
     "O problema é o excesso: os brasileiros comem, em média, bem mais do que o recomendado, e o sal demais "
     "aumenta a pressão arterial. Grande parte dele não vem do saleiro, mas de alimentos industrializados, como "
     "embutidos, salgadinhos e temperos prontos.",
     "O sal de cozinha vem principalmente da evaporação da água do mar nas salinas e é necessário ao corpo, mas o "
     "excesso aumenta a pressão.",
     "No Rio Grande do Norte, o sol e o vento evaporam a água dos tanques e deixam o sal. Os brasileiros comem sal "
     "demais, a maior parte escondida em alimentos industrializados.",
     ["O sal vem das salinas.",
      "Ele ajuda os nervos e os músculos.",
      "O excesso está nos industrializados."]),
    ("O arco-íris aparece quando a luz do Sol atravessa gotas de chuva suspensas no ar. Ao entrar na gota, a luz "
     "muda de direção e se separa nas cores que a formam, porque cada cor se desvia um pouco diferente. Depois, ela "
     "reflete no fundo da gota e sai de novo, espalhada em faixas.\n\n"
     "Por isso, para ver um arco-íris, é preciso estar de costas para o Sol e de frente para a chuva. As cores "
     "aparecem sempre na mesma ordem: vermelho por fora, depois laranja, amarelo, verde, azul, anil e violeta. Às "
     "vezes surge um segundo arco, mais fraco e com as cores invertidas, formado pela luz que reflete duas vezes "
     "dentro das gotas.",
     "O arco-íris surge quando a luz do Sol entra nas gotas de chuva, se separa nas suas cores e sai espalhada.",
     "Para vê-lo, é preciso ficar de costas para o Sol e de frente para a chuva. As cores seguem sempre a mesma "
     "ordem, e um segundo arco pode aparecer com as cores invertidas.",
     ["A luz se separa dentro das gotas.",
      "É preciso estar de costas para o Sol.",
      "O vermelho fica sempre por fora."]),
    ("O café chegou ao Brasil em 1727, trazido da Guiana Francesa por Francisco de Melo Palheta, segundo a "
     "história mais contada. As primeiras plantações ficaram no Pará, mas foi no Sudeste, principalmente no vale do "
     "Paraíba e depois no oeste de São Paulo, que o café encontrou clima e solo ideais.\n\n"
     "No século XIX, o café virou o principal produto de exportação do país e enriqueceu os fazendeiros, que "
     "ganharam grande poder político. O trabalho nas fazendas foi feito por pessoas escravizadas e, depois da "
     "abolição, por imigrantes, sobretudo italianos. As ferrovias paulistas foram construídas em boa parte para "
     "levar o café até o porto de Santos. Hoje, o Brasil é o maior produtor de café do mundo.",
     "O café chegou ao Brasil no século XVIII, prosperou no Sudeste e se tornou o principal produto do país no "
     "século XIX.",
     "A riqueza do café deu poder aos fazendeiros e levou à construção de ferrovias até Santos. O trabalho foi "
     "feito por escravizados e, depois, por imigrantes, e o Brasil é hoje o maior produtor mundial.",
     ["O café chegou em 1727.",
      "Enriqueceu o Sudeste no século XIX.",
      "O Brasil é o maior produtor do mundo."]),
    ("As abelhas sem ferrão são nativas do Brasil e existem centenas de espécies, como a jataí, a mandaçaia e a "
     "uruçu. Ao contrário da abelha-europeia, mais comum nas criações, elas não picam, o que permite criá-las até em "
     "quintais e escolas, em caixas de madeira próprias.\n\n"
     "O mel dessas abelhas é mais líquido e ácido e é produzido em menor quantidade, por isso costuma ser mais "
     "caro. Mas o mais importante é a polinização: muitas plantas nativas dependem delas para formar frutos. Os "
     "povos indígenas criam abelhas sem ferrão há séculos. Hoje, a criação dessas abelhas, chamada "
     "meliponicultura, ajuda a preservar as espécies e gera renda para pequenos produtores.",
     "As abelhas sem ferrão, nativas do Brasil, não picam, produzem um mel especial e são importantes para "
     "polinizar as plantas nativas.",
     "Por não picarem, podem ser criadas em quintais e escolas, numa atividade chamada meliponicultura. Os "
     "indígenas já as criavam há séculos, e hoje elas também geram renda.",
     ["Existem centenas de espécies nativas.",
      "O mel é mais líquido e mais raro.",
      "Elas polinizam muitas plantas."]),
    ("A pressão de um pneu murcho parece um detalhe, mas faz diferença. Com pouca pressão, o pneu se deforma, gasta "
     "mais rápido nas laterais e esquenta, o que pode causar um estouro. O carro também fica mais pesado de "
     "conduzir e consome mais combustível.\n\n"
     "O ideal é calibrar os pneus a cada quinze dias, sempre com eles frios, ou seja, antes de rodar muito. A "
     "pressão certa vem no manual do carro e, em muitos modelos, num adesivo na porta do motorista ou na tampa do "
     "tanque. Não se esqueça do estepe, que costuma ficar esquecido e murcho justamente quando é mais necessário. "
     "Pneus com sulcos muito rasos devem ser trocados.",
     "Manter os pneus calibrados evita desgaste, acidentes e gasto extra de combustível, e a calibragem deve ser "
     "feita a cada quinze dias.",
     "O pneu murcho se deforma, esquenta e pode estourar. A pressão certa aparece no manual ou num adesivo do carro, "
     "e o estepe também deve ser conferido.",
     ["Pneu murcho gasta mais e pode estourar.",
      "Calibre a cada quinze dias, com os pneus frios.",
      "Não esqueça o estepe."]),
    ("O Rio São Francisco nasce na Serra da Canastra, em Minas Gerais, e percorre cerca de 2.800 quilômetros até "
     "desaguar no Oceano Atlântico, entre Alagoas e Sergipe. Ele atravessa cinco estados e é chamado de rio da "
     "integração nacional, porque ligou o Sudeste ao Nordeste quando quase não havia estradas.\n\n"
     "Grande parte do seu caminho fica no semiárido, e suas águas são usadas para beber, irrigar plantações de "
     "frutas e gerar energia em usinas como Sobradinho e Xingó. O rio enfrenta problemas como o desmatamento das "
     "margens, o assoreamento e a diminuição da água em períodos de seca. Projetos de revitalização tentam "
     "recuperar as nascentes e as matas ciliares.",
     "O Rio São Francisco nasce em Minas Gerais, corta cinco estados até o Atlântico e é essencial para a água e a "
     "energia do semiárido.",
     "Chamado de rio da integração nacional, ele liga o Sudeste ao Nordeste e abastece cidades, irrigações e "
     "usinas. O desmatamento e o assoreamento o ameaçam.",
     ["Nasce na Serra da Canastra.",
      "Atravessa cinco estados.",
      "Sofre com assoreamento e desmatamento."]),
    ("Para limpar a tela do celular sem estragá-la, desligue o aparelho e use um pano de microfibra seco, o mesmo "
     "tipo usado para limpar óculos. Passe o pano com movimentos suaves, sem fazer muita força. Se houver manchas de "
     "gordura, umedeça levemente o pano com um pouco de água; nunca jogue líquido diretamente na tela.\n\n"
     "Evite produtos como álcool comum em grande quantidade, limpa-vidros, vinagre e papel-toalha, que podem "
     "riscar a tela ou remover a camada que diminui as marcas de dedo. Para as entradas do carregador e dos fones, "
     "use um pincel macio ou um palito de madeira com cuidado. Uma capinha e uma película ajudam a proteger o "
     "aparelho no dia a dia.",
     "Para limpar a tela do celular, desligue o aparelho e use um pano de microfibra seco ou levemente úmido, "
     "evitando produtos fortes.",
     "Álcool em excesso, limpa-vidros e papel-toalha podem riscar a tela ou tirar a sua proteção. As entradas "
     "podem ser limpas com pincel macio, e capinha e película ajudam a proteger.",
     ["Desligue o celular antes de limpar.",
      "Use pano de microfibra.",
      "Evite produtos fortes."]),
    ("Os ipês são árvores brasileiras famosas pelas flores que cobrem a copa inteira no fim do inverno, quando "
     "muitas outras plantas estão sem folhas. Há ipês amarelos, roxos, rosa e brancos, e cada cor floresce numa "
     "época um pouco diferente. O ipê-amarelo é considerado a árvore símbolo do Brasil.\n\n"
     "A floração dura poucos dias, mas transforma ruas e estradas, e por isso muitas cidades plantam ipês nas "
     "calçadas e praças. A madeira do ipê é muito dura e resistente e foi bastante usada em construções e móveis, o "
     "que levou à exploração ilegal em florestas. Além da beleza, as flores atraem abelhas e beija-flores.",
     "Os ipês são árvores brasileiras que se cobrem de flores amarelas, roxas, rosa ou brancas no fim do inverno.",
     "A floração dura poucos dias e enfeita muitas cidades, e o ipê-amarelo é símbolo do Brasil. A madeira "
     "resistente levou à exploração ilegal.",
     ["Os ipês florescem no fim do inverno.",
      "O amarelo é a árvore símbolo do Brasil.",
      "A madeira dura é muito explorada."]),
    ("O fuso horário existe porque a Terra gira, e o Sol não nasce ao mesmo tempo em todos os lugares. Para "
     "organizar os horários, o planeta foi dividido em faixas, e cada faixa tem uma hora diferente. Quando é meio-dia "
     "em Brasília, por exemplo, ainda é madrugada no Japão.\n\n"
     "O Brasil, por ser muito largo de leste a oeste, tem quatro fusos horários. A maior parte do país segue o "
     "horário de Brasília, mas estados como Mato Grosso, Rondônia e Amazonas ficam uma hora atrás, e o Acre fica "
     "duas horas atrás. Já o arquipélago de Fernando de Noronha fica uma hora à frente. Por isso, programas de "
     "televisão ao vivo passam em horários diferentes em cada região.",
     "Os fusos horários existem porque a Terra gira, e o Brasil, por ser muito largo, tem quatro deles.",
     "O planeta é dividido em faixas com horas diferentes. No Brasil, a maioria segue o horário de Brasília, mas "
     "estados do oeste ficam atrás e Fernando de Noronha fica à frente.",
     ["O Sol nasce em horas diferentes no planeta.",
      "O Brasil tem quatro fusos.",
      "O Acre fica duas horas atrás de Brasília."]),
    ("As formigas-cortadeiras, como as saúvas, são conhecidas por carregar pedaços de folhas maiores do que elas. "
     "Mas elas não comem as folhas. Dentro do formigueiro, as operárias mastigam o material e o usam para cultivar "
     "um fungo, que é o verdadeiro alimento da colônia. É uma espécie de agricultura que as formigas praticam há "
     "milhões de anos.\n\n"
     "Um formigueiro de saúva pode ter milhões de formigas e câmaras a vários metros de profundidade. Cada formiga "
     "tem uma função, de acordo com o tamanho: as maiores defendem o ninho, as médias cortam e carregam as folhas e "
     "as menores cuidam do fungo. Por cortarem muitas plantas, elas podem causar prejuízo em plantações e jardins.",
     "As saúvas cortam folhas não para comer, mas para cultivar um fungo dentro do formigueiro, que é o alimento "
     "da colônia.",
     "Os formigueiros podem ter milhões de formigas, cada uma com uma função conforme o tamanho. Como cortam muitas "
     "plantas, elas causam prejuízo nas lavouras.",
     ["As folhas servem para cultivar um fungo.",
      "Cada formiga tem uma função.",
      "Podem prejudicar plantações."]),
    ("Para fazer pipoca na panela, coloque três colheres de sopa de óleo e meia xícara de milho de pipoca numa "
     "panela grande, de fundo grosso. Tampe e leve ao fogo médio. Quando os primeiros grãos começarem a estourar, "
     "sacuda a panela de vez em quando, sem abrir a tampa, para os grãos não queimarem no fundo.\n\n"
     "Quando o intervalo entre os estouros passar de dois ou três segundos, desligue o fogo e espere um pouco antes "
     "de abrir, porque alguns grãos ainda podem pular. Coloque sal a gosto ou, para pipoca doce, misture açúcar ao "
     "óleo antes do milho. O milho estoura porque a água dentro do grão vira vapor e rompe a casca.",
     "Para fazer pipoca, aqueça óleo e milho numa panela tampada, sacuda quando começar a estourar e desligue "
     "quando os estouros ficarem espaçados.",
     "Sacudir a panela evita que os grãos queimem, e é bom esperar antes de abrir a tampa. O milho estoura porque "
     "a água do grão vira vapor e rompe a casca.",
     ["Use panela grande e tampada.",
      "Sacuda sem abrir a tampa.",
      "O vapor dentro do grão o faz estourar."]),
    ("O Carnaval de Olinda, em Pernambuco, é conhecido pelos bonecos gigantes que desfilam pelas ladeiras do centro "
     "histórico. Eles podem ter mais de três metros de altura e são carregados por uma pessoa que fica dentro da "
     "estrutura, enxergando por uma pequena abertura. O mais famoso é o Homem da Meia-Noite, que sai às ruas desde "
     "1932.\n\n"
     "Os bonecos representam personagens da cultura popular, artistas, políticos e figuras da cidade. A festa é "
     "animada pelo frevo, um ritmo acelerado tocado por orquestras de metais, e pelo maracatu. Ao contrário de "
     "outros carnavais, o de Olinda é gratuito e acontece nas ruas, sem cordas nem camarotes, com os foliões "
     "seguindo os blocos.",
     "O carnaval de Olinda é famoso pelos bonecos gigantes que desfilam nas ladeiras, ao som do frevo e do maracatu.",
     "Os bonecos chegam a três metros e são carregados por uma pessoa dentro deles, e o Homem da Meia-Noite sai "
     "desde 1932. A festa é gratuita e acontece nas ruas.",
     ["Os bonecos gigantes são a marca da festa.",
      "O frevo anima as ladeiras.",
      "O carnaval é gratuito e de rua."]),
    ("O mosquito que mais incomoda à noite, o pernilongo, é atraído pelo gás carbônico que soltamos na respiração e "
     "pelo calor e pelo cheiro do corpo. Só as fêmeas picam, porque precisam do sangue para produzir os ovos. Os "
     "machos se alimentam de néctar e seiva das plantas.\n\n"
     "Para afastá-los, telas nas janelas, mosquiteiros e repelentes funcionam bem. Ventiladores também ajudam, "
     "porque os mosquitos voam mal com vento. Como os ovos são postos em água parada, evitar recipientes com água "
     "acumulada diminui a população. Nem todo mosquito transmite doenças, mas espécies como o Aedes aegypti "
     "transmitem a dengue, e por isso a prevenção é importante.",
     "Os pernilongos são atraídos pela respiração e pelo calor do corpo, e só as fêmeas picam, para produzir os "
     "ovos.",
     "Telas, mosquiteiros, repelentes e ventiladores ajudam a afastá-los. Acabar com a água parada reduz os "
     "mosquitos, alguns dos quais transmitem doenças como a dengue.",
     ["O gás carbônico atrai os mosquitos.",
      "Só as fêmeas picam.",
      "Ventilador e tela ajudam a afastá-los."]),
    ("A Torre Eiffel foi construída para a Exposição Universal de 1889, em Paris, que comemorava o centenário da "
     "Revolução Francesa. O projeto foi da empresa do engenheiro Gustave Eiffel, e a torre, feita de ferro, tinha "
     "cerca de 300 metros, o que a tornou a construção mais alta do mundo por mais de quarenta anos.\n\n"
     "No começo, muitos artistas e moradores de Paris acharam a torre feia e protestaram contra ela. A ideia era "
     "desmontá-la depois de vinte anos, mas ela se mostrou útil como antena de rádio e acabou ficando. Hoje é o "
     "símbolo da França e um dos monumentos mais visitados do mundo, recebendo milhões de pessoas por ano.",
     "A Torre Eiffel foi feita para a Exposição de 1889, quase foi desmontada e acabou virando o símbolo da França.",
     "A torre de ferro foi a construção mais alta do mundo por décadas e, no começo, foi muito criticada. Sua "
     "utilidade como antena de rádio a salvou, e hoje ela recebe milhões de visitantes.",
     ["Foi construída para a exposição de 1889.",
      "Muitos a acharam feia no começo.",
      "Virou o símbolo da França."]),
    ("O sistema braille permite que pessoas cegas leiam pelo tato. Ele foi criado pelo francês Louis Braille, que "
     "perdeu a visão ainda criança, depois de um acidente. Aos quinze anos, em 1824, ele adaptou um código militar "
     "de pontos em relevo e criou um sistema mais simples.\n\n"
     "Cada letra é formada por uma combinação de até seis pontos, organizados em duas colunas de três. Com eles, é "
     "possível escrever letras, números, sinais de pontuação e até notas musicais. O braille é usado em livros, "
     "embalagens de remédios, elevadores e placas. Hoje, além da escrita em papel, existem aparelhos que mostram o "
     "texto do computador em braille.",
     "O braille, criado por Louis Braille em 1824, permite que pessoas cegas leiam com o tato, por meio de pontos "
     "em relevo.",
     "Cada letra é feita com até seis pontos, e o sistema também escreve números e música. Ele aparece em livros, "
     "remédios e elevadores e até em aparelhos ligados ao computador.",
     ["Louis Braille criou o sistema aos quinze anos.",
      "Cada letra usa até seis pontos.",
      "O braille está em livros, remédios e elevadores."]),
    ("Quando uma pessoa engasga e não consegue falar nem tossir, é preciso agir rápido com a manobra de Heimlich. "
     "Fique atrás dela, envolva a cintura com os braços e feche uma das mãos, colocando-a um pouco acima do umbigo. "
     "Com a outra mão por cima, faça compressões rápidas para dentro e para cima.\n\n"
     "Repita até o objeto sair ou a pessoa voltar a respirar. Se ela desmaiar, deite-a no chão, chame o SAMU pelo "
     "192 e, se souber, inicie a massagem no peito. Em bebês, a técnica é diferente: eles são colocados de bruços "
     "sobre o antebraço e recebem tapinhas nas costas. Se a pessoa ainda consegue tossir, incentive a tosse, que é "
     "a melhor forma de expulsar o objeto.",
     "Se alguém engasgar e não conseguir tossir, faça a manobra de Heimlich, com compressões para cima logo acima do "
     "umbigo.",
     "Repita até o objeto sair e, se a pessoa desmaiar, chame o SAMU pelo 192. Bebês recebem tapinhas nas costas, e "
     "quem ainda tosse deve ser incentivado a tossir.",
     ["Abrace a pessoa por trás.",
      "Comprima acima do umbigo, para dentro e para cima.",
      "Em bebês, a técnica é outra."]),
    ("O Rio Amazonas é o rio com o maior volume de água do mundo. Ele nasce na Cordilheira dos Andes, no Peru, e "
     "atravessa o norte do Brasil até o Oceano Atlântico. Em alguns trechos, ele é tão largo que não é possível ver a "
     "outra margem, e a água doce que despeja no mar é tanta que muda a cor do oceano por muitos quilômetros.\n\n"
     "Perto de Manaus, acontece o encontro das águas: o Rio Negro, de água escura, e o Rio Solimões, de água "
     "barrenta, correm lado a lado por vários quilômetros sem se misturar, por causa das diferenças de temperatura, "
     "velocidade e densidade. Para muitos moradores da região, o rio é a principal estrada, percorrida por barcos.",
     "O Amazonas é o rio com mais água do mundo, nasce nos Andes e é a principal via de transporte para muitos "
     "moradores da região.",
     "Ele é tão largo que, em alguns pontos, não se vê a outra margem. Perto de Manaus, os rios Negro e Solimões "
     "correm lado a lado sem se misturar.",
     ["Tem o maior volume de água do mundo.",
      "Nasce nos Andes, no Peru.",
      "O encontro das águas fica perto de Manaus."]),
    ("O chocolate é feito das sementes do cacau, uma árvore nativa da América. Os povos maias e astecas já usavam "
     "o cacau para fazer uma bebida amarga, misturada com pimenta, e as sementes chegavam a servir como moeda. Os "
     "espanhóis levaram o cacau para a Europa, onde ele passou a ser adoçado com açúcar.\n\n"
     "Para virar chocolate, as sementes são fermentadas, secas ao sol, torradas e moídas, formando uma pasta. Dela "
     "se separam a manteiga de cacau e o pó. O chocolate em barra mistura essas partes com açúcar e, às vezes, leite. "
     "No Brasil, o sul da Bahia foi um grande produtor de cacau até os anos 1990, quando uma praga chamada "
     "vassoura-de-bruxa destruiu muitas plantações.",
     "O chocolate vem das sementes do cacau, que os povos da América já usavam e que os europeus passaram a adoçar.",
     "As sementes são fermentadas, secas, torradas e moídas antes de virar chocolate. No Brasil, o sul da Bahia foi "
     "grande produtor até a vassoura-de-bruxa atingir as plantações.",
     ["O cacau é nativo da América.",
      "Os maias e astecas o bebiam amargo.",
      "Uma praga destruiu plantações na Bahia."]),
    ("Na hora de escolher uma senha, muita gente usa a data de aniversário, o nome do cachorro ou sequências como "
     "123456. Essas são as primeiras que os criminosos tentam. Uma senha segura deve ser longa, com pelo menos doze "
     "caracteres, misturando letras, números e símbolos, ou ser formada por várias palavras sem relação entre si.\n\n"
     "Também é importante não repetir a mesma senha em vários sites: se um deles for invadido, todas as contas ficam "
     "em risco. Um gerenciador de senhas ajuda a guardar senhas diferentes sem precisar decorar todas. Sempre que "
     "possível, ative a verificação em duas etapas, que pede um código extra no celular. E nunca envie senhas por "
     "mensagem.",
     "Uma senha segura é longa, difícil de adivinhar e diferente em cada site, e a verificação em duas etapas aumenta "
     "a proteção.",
     "Datas e sequências simples são as primeiras tentadas pelos criminosos. Um gerenciador ajuda a guardar senhas "
     "diferentes, e elas nunca devem ser enviadas por mensagem.",
     ["Use senhas longas.",
      "Não repita a mesma senha.",
      "Ative a verificação em duas etapas."]),
    ("O sabiá-laranjeira é a ave símbolo do Brasil desde 2002. Ele tem as costas acinzentadas e a barriga cor de "
     "ferrugem, e vive em quase todo o país, inclusive nas cidades, onde é comum em parques e quintais. O sabiá se "
     "alimenta de frutas, minhocas e insetos.\n\n"
     "O canto do sabiá é muito melodioso e costuma ser ouvido de madrugada, principalmente na primavera, época de "
     "reprodução. Por isso, ele aparece em muitas poesias e músicas brasileiras. O poema mais famoso é a Canção do "
     "Exílio, de Gonçalves Dias, que começa com os versos: minha terra tem palmeiras, onde canta o sabiá.",
     "O sabiá-laranjeira, ave símbolo do Brasil, vive em quase todo o país e é famoso pelo canto, presente em "
     "muitas poesias.",
     "Ele tem a barriga cor de ferrugem e come frutas, minhocas e insetos. Canta de madrugada na primavera e aparece "
     "na Canção do Exílio, de Gonçalves Dias.",
     ["É a ave símbolo do Brasil.",
      "Canta muito na primavera.",
      "Aparece no poema de Gonçalves Dias."]),
    ("A febre é uma reação de defesa do corpo, e não uma doença. Quando o organismo enfrenta uma infecção, o cérebro "
     "aumenta a temperatura para dificultar a vida dos micróbios e acelerar as defesas. Considera-se febre quando a "
     "temperatura passa de cerca de 37,8 graus.\n\n"
     "Na maioria das vezes, a febre passa em poucos dias. Beber bastante líquido, descansar e usar roupas leves "
     "ajudam. Remédios para baixar a febre podem ser usados conforme a orientação de um médico ou farmacêutico. É "
     "preciso procurar atendimento se a febre for muito alta, durar mais de três dias, vier com falta de ar, "
     "manchas no corpo ou sonolência excessiva, ou se for num bebê pequeno.",
     "A febre é uma defesa do corpo contra infecções e costuma passar em poucos dias, mas alguns sinais exigem "
     "atendimento.",
     "O cérebro aumenta a temperatura para ajudar a combater os micróbios. Líquidos e descanso ajudam, e febre muito "
     "alta, longa ou num bebê pede um médico.",
     ["A febre é uma reação de defesa.",
      "Beber líquido e descansar ajudam.",
      "Febre longa ou muito alta exige atendimento."]),
    ("Os dias têm 24 horas porque esse é o tempo que a Terra leva para dar uma volta completa em torno de si mesma, "
     "o movimento de rotação. Enquanto gira, metade do planeta fica virada para o Sol, e é dia, e a outra metade "
     "fica no escuro, e é noite.\n\n"
     "Já o ano tem cerca de 365 dias porque esse é o tempo da volta da Terra em torno do Sol, a translação. Na "
     "verdade, essa volta leva 365 dias e cerca de seis horas. Para não deixar o calendário atrasar, a cada quatro "
     "anos acrescenta-se um dia, o 29 de fevereiro, e esse ano é chamado de bissexto.",
     "O dia dura 24 horas por causa da rotação da Terra, e o ano tem cerca de 365 dias por causa da volta em torno "
     "do Sol.",
     "A rotação faz uma metade do planeta ter dia e a outra, noite. Como a translação leva seis horas a mais, a cada "
     "quatro anos há um ano bissexto, com 29 de fevereiro.",
     ["A rotação faz o dia e a noite.",
      "A translação define o ano.",
      "O ano bissexto corrige as seis horas a mais."]),
    ("Para fazer um bom café coado, aqueça a água até quase ferver, mas desligue o fogo antes da fervura forte, "
     "porque a água fervendo demais deixa o café amargo. Coloque o filtro no suporte e use cerca de duas colheres "
     "de sopa de pó para cada xícara de água.\n\n"
     "Comece despejando um pouco de água para molhar o pó e espere alguns segundos: ele vai inchar e soltar o "
     "aroma. Depois, despeje o resto da água devagar, em movimentos circulares, sem encher o filtro de uma vez. "
     "Sirva logo, porque o café requentado perde o sabor. Guardar o pó num pote bem fechado, longe da luz e do calor, "
     "também ajuda a manter o aroma.",
     "Para um bom café coado, use água quase fervendo, umedeça o pó primeiro e despeje o resto devagar, servindo "
     "logo em seguida.",
     "Água fervendo demais amarga o café, e a medida é de cerca de duas colheres de pó por xícara. Guardar o pó bem "
     "fechado conserva o aroma.",
     ["Não deixe a água ferver demais.",
      "Molhe o pó antes de coar.",
      "Sirva o café logo."]),
    ("Os primeiros jogos de futebol feminino no Brasil aconteceram nas primeiras décadas do século XX, mas, em 1941, "
     "um decreto do governo proibiu as mulheres de praticar esportes considerados violentos, como o futebol. A "
     "proibição durou até 1979, e o esporte só foi regulamentado para mulheres em 1983.\n\n"
     "Mesmo com décadas de atraso e pouco apoio, o futebol feminino brasileiro revelou grandes jogadoras. Marta foi "
     "eleita seis vezes a melhor jogadora do mundo pela FIFA e é a maior artilheira da história das Copas do Mundo, "
     "entre homens e mulheres. Formiga participou de sete Copas, um recorde. Nos últimos anos, os clubes e as "
     "transmissões passaram a dar mais espaço às mulheres.",
     "O futebol feminino foi proibido no Brasil de 1941 a 1979, mas, mesmo com pouco apoio, revelou craques como "
     "Marta e Formiga.",
     "Depois da proibição, o esporte só foi regulamentado em 1983. Marta foi seis vezes a melhor do mundo, e hoje as "
     "mulheres ganham mais espaço nos clubes e na televisão.",
     ["Um decreto proibiu as mulheres de jogar.",
      "A proibição acabou em 1979.",
      "Marta foi seis vezes a melhor do mundo."]),
    ("O lixo eletrônico inclui celulares, computadores, pilhas, baterias, carregadores e outros aparelhos que não "
     "funcionam mais. Ele não deve ir para o lixo comum, porque tem metais pesados, como chumbo e mercúrio, que "
     "contaminam o solo e a água quando os aparelhos são jogados em lixões.\n\n"
     "Ao mesmo tempo, esse lixo tem materiais valiosos, como cobre, ouro e prata, que podem ser recuperados e "
     "reutilizados. Muitas lojas, fabricantes e prefeituras têm pontos de coleta para eletrônicos. Antes de "
     "descartar um celular ou computador, é importante apagar os dados pessoais. E, se o aparelho ainda funciona, "
     "doar pode ser a melhor opção.",
     "O lixo eletrônico tem metais tóxicos e materiais valiosos, por isso deve ir para pontos de coleta, e não para "
     "o lixo comum.",
     "Chumbo e mercúrio contaminam o solo, mas cobre e ouro podem ser recuperados. Antes de descartar, apague os "
     "dados, e doe o aparelho se ele ainda funcionar.",
     ["Eletrônicos não vão para o lixo comum.",
      "Eles têm metais tóxicos e valiosos.",
      "Apague os dados antes de descartar."]),
    ("O Pão de Açúcar é um morro de granito com cerca de 396 metros de altura na entrada da Baía de Guanabara, no "
     "Rio de Janeiro. O nome provavelmente vem da semelhança com os blocos de açúcar usados na época colonial, que "
     "tinham forma de cone.\n\n"
     "Em 1912, foi inaugurado o bondinho que leva os visitantes até o topo, em duas etapas: primeiro até o Morro da "
     "Urca e depois até o Pão de Açúcar. Foi um dos primeiros teleféricos do mundo. Lá de cima, dá para ver as "
     "praias, o Cristo Redentor e a ponte Rio-Niterói. O morro também é muito procurado por praticantes de "
     "escalada, com centenas de vias.",
     "O Pão de Açúcar é um morro de granito no Rio de Janeiro, famoso pelo bondinho inaugurado em 1912 e pela vista "
     "da cidade.",
     "O nome deve vir dos blocos de açúcar em forma de cone da época colonial. O bondinho sobe em duas etapas, e o "
     "morro também atrai escaladores.",
     ["Tem cerca de 396 metros de altura.",
      "O bondinho existe desde 1912.",
      "É muito usado para escalada."]),
    ("O cérebro humano consegue se adaptar e criar novas ligações durante toda a vida, uma capacidade chamada "
     "plasticidade. Antigamente, pensava-se que, depois da infância, o cérebro quase não mudava. Hoje se sabe que "
     "aprender algo novo, como tocar um instrumento ou falar outra língua, muda a estrutura do cérebro em qualquer "
     "idade.\n\n"
     "A plasticidade também ajuda na recuperação de lesões: depois de um derrame, por exemplo, outras áreas do "
     "cérebro podem assumir funções perdidas, com fisioterapia e treino. Para estimular o cérebro, os especialistas "
     "recomendam aprender coisas novas, ler, conviver com outras pessoas, dormir bem e fazer exercícios físicos.",
     "O cérebro continua criando novas ligações a vida toda, o que permite aprender em qualquer idade e se "
     "recuperar de lesões.",
     "Aprender um instrumento ou uma língua muda o cérebro mesmo na idade adulta. Ler, conviver, dormir e se "
     "exercitar estimulam essa capacidade.",
     ["O cérebro se adapta a vida inteira.",
      "Aprender coisas novas o transforma.",
      "Ajuda na recuperação de lesões."]),
    ("Guardar comida na geladeira do jeito certo evita desperdício e doenças. As carnes cruas devem ficar na parte "
     "de baixo, bem embaladas, para que o líquido não pingue sobre outros alimentos. Frutas e verduras ficam na "
     "gaveta, e os alimentos prontos, em potes fechados nas prateleiras de cima.\n\n"
     "A porta é a parte que mais esquenta, porque é aberta o tempo todo, e por isso não é o melhor lugar para o "
     "leite e os ovos, apesar de muita gente guardá-los ali. Sobras de comida devem esfriar um pouco e ir para a "
     "geladeira em até duas horas e ser consumidas em poucos dias. Não encha demais a geladeira: o ar frio precisa "
     "circular.",
     "Organizar bem a geladeira, com carnes embaixo, verduras na gaveta e prontos em potes, evita desperdício e "
     "contaminação.",
     "A porta esquenta muito e não é o melhor lugar para leite e ovos. Sobras devem ir para a geladeira em até duas "
     "horas, e o ar frio precisa de espaço para circular.",
     ["Carnes cruas ficam embaixo.",
      "A porta é a parte menos fria.",
      "Não lote a geladeira."]),
    ("A Antártida é o continente mais frio, seco e com mais vento do planeta. Quase todo o seu território é coberto "
     "por uma camada de gelo que, em alguns lugares, tem mais de quatro quilômetros de espessura. Ali está a maior "
     "parte da água doce da Terra, congelada.\n\n"
     "Ninguém mora na Antártida de forma permanente. Ela é protegida por um tratado internacional, que proíbe a "
     "exploração de minérios e o uso militar e reserva o continente para a pesquisa científica. Vários países mantêm "
     "estações de pesquisa lá, inclusive o Brasil, com a Estação Antártica Comandante Ferraz. Os cientistas estudam "
     "o clima, o gelo e os animais, como pinguins, focas e baleias.",
     "A Antártida é o continente mais frio do planeta, guarda a maior parte da água doce e é reservada à pesquisa "
     "científica.",
     "O gelo chega a ter mais de quatro quilômetros de espessura, e ninguém vive lá permanentemente. Um tratado "
     "proíbe a exploração, e o Brasil mantém a Estação Comandante Ferraz.",
     ["É o continente mais frio e seco.",
      "Guarda muita água doce congelada.",
      "É usada só para pesquisa."]),
    ("O tempo de decomposição dos materiais na natureza varia muito. Uma casca de banana leva poucas semanas para se "
     "decompor, e o papel, alguns meses. Já uma lata de alumínio pode levar mais de cem anos, e uma garrafa de "
     "plástico, centenas de anos. O vidro é ainda mais resistente e pode durar milhares de anos.\n\n"
     "Por isso, o lixo jogado em lugares errados se acumula por muito tempo e causa problemas, como entupir bueiros, "
     "poluir rios e matar animais que confundem plástico com comida. Esses números mostram por que separar o lixo, "
     "reciclar e, principalmente, usar menos descartáveis é tão importante para o meio ambiente.",
     "Os materiais levam tempos muito diferentes para se decompor, de semanas para a casca de banana a milhares de "
     "anos para o vidro.",
     "Latas e plásticos podem durar séculos e, jogados em lugares errados, entopem bueiros e matam animais. Por "
     "isso, reciclar e usar menos descartáveis é importante.",
     ["Restos de comida se decompõem rápido.",
      "Plástico e vidro duram séculos.",
      "Usar menos descartáveis ajuda."]),
    ("Na hora de atravessar a rua, a regra mais importante é usar a faixa de pedestres e esperar o sinal verde, "
     "quando houver semáforo. Antes de atravessar, olhe para os dois lados, mesmo em ruas de mão única, porque "
     "motos e bicicletas às vezes andam na contramão.\n\n"
     "Evite atravessar entre carros estacionados, porque os motoristas não conseguem ver você, e não use o celular "
     "durante a travessia. À noite, roupas claras ajudam a ser visto. Com crianças, segure sempre a mão delas e "
     "ensine as regras desde cedo. Mesmo na faixa, confirme que o motorista viu você e parou antes de seguir.",
     "Para atravessar a rua com segurança, use a faixa, espere o sinal, olhe para os dois lados e confirme que o "
     "motorista parou.",
     "Evite passar entre carros estacionados e usar o celular na travessia. Crianças devem ir de mão dada e aprender "
     "as regras cedo.",
     ["Use a faixa de pedestres.",
      "Olhe para os dois lados.",
      "Não use o celular ao atravessar."]),
    ("A mandioca, também chamada de aipim ou macaxeira conforme a região, é uma raiz nativa da América do Sul, "
     "cultivada pelos povos indígenas há milhares de anos. Ela cresce bem em solos pobres e resiste à seca, o que a "
     "tornou um alimento importante em todo o Brasil.\n\n"
     "Da mandioca se fazem a farinha, a tapioca, o polvilho usado no pão de queijo e muitos pratos, como o "
     "escondidinho e o bolo de aipim. Existe a mandioca mansa, que pode ser cozida e comida, e a mandioca brava, que "
     "tem uma substância tóxica e só pode ser consumida depois de processada, como na fabricação da farinha. Os "
     "indígenas desenvolveram técnicas para isso muito antes da chegada dos europeus.",
     "A mandioca é uma raiz nativa, cultivada pelos indígenas, que resiste à seca e dá origem à farinha, à tapioca e "
     "ao polvilho.",
     "Ela tem nomes diferentes em cada região, como aipim e macaxeira. A mandioca brava é tóxica e precisa ser "
     "processada, técnica criada pelos indígenas.",
     ["A mandioca é nativa da América do Sul.",
      "Dela vêm farinha, tapioca e polvilho.",
      "A mandioca brava precisa ser processada."]),
    ("Os satélites artificiais são aparelhos lançados ao espaço por foguetes para girar em volta da Terra. O "
     "primeiro foi o Sputnik 1, lançado pela União Soviética em 1957. Hoje, há milhares de satélites em órbita, com "
     "funções muito diferentes.\n\n"
     "Alguns transmitem sinais de televisão, telefone e internet. Outros, como os do GPS, ajudam a descobrir a "
     "localização. Há satélites que fotografam a Terra para a previsão do tempo, o monitoramento de queimadas e do "
     "desmatamento e a agricultura. Também existem telescópios espaciais, que observam estrelas e galáxias sem a "
     "interferência da atmosfera. Os satélites velhos e os pedaços de foguetes formam o lixo espacial, um problema "
     "crescente.",
     "Os satélites artificiais, que começaram com o Sputnik em 1957, hoje são milhares e servem para comunicação, "
     "localização, observação da Terra e astronomia.",
     "Eles transmitem televisão e internet, guiam o GPS e ajudam a acompanhar o tempo e o desmatamento. Os satélites "
     "velhos formam o lixo espacial.",
     ["O primeiro foi o Sputnik 1.",
      "Têm muitas funções diferentes.",
      "O lixo espacial é um problema."]),
    ("Muita gente confunde jacaré e crocodilo, mas são animais diferentes. O jeito mais fácil de diferenciar é olhar "
     "a boca fechada: no crocodilo, um dente grande da mandíbula de baixo fica aparecendo dos lados; no jacaré, os "
     "dentes de baixo ficam escondidos. O focinho do jacaré também costuma ser mais largo e arredondado.\n\n"
     "No Brasil, não existem crocodilos na natureza, só jacarés, como o jacaré-do-pantanal e o jacaré-açu, da "
     "Amazônia, que pode passar de cinco metros. Os jacarés vivem em rios, lagoas e áreas alagadas e se alimentam "
     "de peixes, aves e pequenos mamíferos. Eles são importantes para controlar as populações de outros animais.",
     "Jacarés e crocodilos são animais diferentes, e no Brasil só existem jacarés na natureza.",
     "No crocodilo, um dente de baixo aparece com a boca fechada, e o jacaré tem o focinho mais largo. O jacaré-açu, "
     "da Amazônia, pode passar de cinco metros.",
     ["Os dentes mostram a diferença.",
      "O focinho do jacaré é mais largo.",
      "O Brasil só tem jacarés."]),
]
