"""Perguntas de "por quê" (parte 2: física do dia a dia, tecnologia, cotidiano, sociedade, história e língua)."""

PORQUES = [
    # física e química do dia a dia
    ("Por que as coisas caem?",
     "As coisas caem por causa da gravidade, a força com que a Terra atrai tudo o que tem massa. Ela puxa os objetos "
     "em direção ao centro do planeta. Sem a resistência do ar, uma pena e uma pedra cairiam juntas, com a mesma "
     "velocidade."),
    ("Por que o avião voa?",
     "O avião voa porque as asas têm um formato e uma inclinação que desviam o ar para baixo enquanto ele avança. Ao "
     "empurrar o ar para baixo, a asa recebe uma força para cima, chamada sustentação. Os motores dão a velocidade "
     "necessária para que essa força fique maior do que o peso do avião."),
    ("Por que o navio não afunda?",
     "O navio não afunda, mesmo sendo de aço, porque o casco é oco e empurra para os lados uma quantidade enorme de "
     "água. A água empurra o navio para cima com uma força igual ao peso da água deslocada; enquanto essa força for "
     "maior que o peso do navio, ele flutua. Esse é o princípio de Arquimedes."),
    ("Por que o metal parece mais frio que a madeira?",
     "O metal e a madeira podem estar na mesma temperatura, mas o metal conduz calor muito melhor. Quando você toca "
     "no metal, ele tira o calor da sua mão rapidamente, e a pele sente isso como frio. A madeira conduz pouco calor, "
     "então a mão perde calor mais devagar."),
    ("Por que a água ferve?",
     "A água ferve quando recebe calor suficiente para que suas moléculas se agitem a ponto de formar bolhas de vapor "
     "no meio do líquido. Ao nível do mar, isso acontece a 100 graus Celsius. Em lugares altos, com menos pressão do "
     "ar, a água ferve a uma temperatura mais baixa."),
    ("Por que a panela de pressão cozinha mais rápido?",
     "A panela de pressão cozinha mais rápido porque, fechada, ela segura o vapor e a pressão lá dentro aumenta. Com "
     "mais pressão, a água só ferve a uma temperatura mais alta, perto de 120 graus. Com a água mais quente, os "
     "alimentos cozinham em menos tempo."),
    ("Por que o ferro enferruja?",
     "O ferro enferruja porque reage com o oxigênio do ar na presença de água ou umidade, formando óxido de ferro, a "
     "ferrugem. A ferrugem é quebradiça e se solta, expondo mais ferro, e o processo continua. Pintar, galvanizar ou "
     "manter o ferro seco ajuda a evitar."),
    ("Por que o fogo precisa de ar?",
     "O fogo precisa de ar porque a queima é uma reação química entre o combustível e o oxigênio. Sem oxigênio, a "
     "reação para. É por isso que abafar uma chama com uma tampa ou com um cobertor apaga o fogo."),
    ("Por que não se deve jogar água em óleo pegando fogo?",
     "Não se deve jogar água em óleo quente pegando fogo porque a água afunda no óleo, vira vapor de uma vez e "
     "explode, espalhando gotas de óleo em chamas para todo lado. O certo é desligar o fogo e abafar a panela com uma "
     "tampa ou um pano úmido, sem jogar água."),
    ("Por que o ímã atrai o ferro?",
     "O ímã atrai o ferro porque cria em volta de si um campo magnético. No ferro, pequenas regiões magnéticas se "
     "alinham com esse campo, e o pedaço de ferro vira um ímã temporário, que é atraído. Materiais como plástico, "
     "madeira e alumínio não reagem assim."),
    ("Por que a bússola aponta para o norte?",
     "A bússola aponta para o norte porque a agulha dela é um pequeno ímã, e a Terra funciona como um ímã gigante. A "
     "agulha se alinha com o campo magnético do planeta, apontando para perto do polo norte geográfico. Por isso ela "
     "é usada há séculos para orientação."),
    ("Por que ouvimos eco?",
     "Ouvimos eco quando o som bate numa superfície grande e dura, como uma parede de pedra ou uma montanha, e volta "
     "para nós. Se a superfície estiver longe o bastante, o som refletido chega depois do original, e escutamos a "
     "repetição."),
    ("Por que o som não se propaga no espaço?",
     "O som não se propaga no espaço porque ele é uma vibração que precisa de um meio, como ar, água ou um sólido, "
     "para passar de uma partícula para outra. No espaço quase não há matéria, então não há o que vibrar. Por isso "
     "as explosões no espaço seriam silenciosas."),
    ("Por que vemos as cores?",
     "Vemos as cores porque os objetos absorvem algumas cores da luz e refletem outras. Uma maçã vermelha, por "
     "exemplo, reflete principalmente a luz vermelha. No fundo do olho, células chamadas cones percebem essa luz e "
     "mandam sinais ao cérebro, que interpreta como cor."),
    ("Por que roupas escuras esquentam mais no sol?",
     "Roupas escuras esquentam mais porque absorvem quase toda a luz que recebem e transformam essa energia em calor. "
     "As roupas claras refletem boa parte da luz e por isso esquentam menos. Por esse motivo, em dias de muito sol, "
     "roupas claras são mais frescas."),
    ("Por que o espelho inverte a imagem?",
     "O espelho não inverte exatamente esquerda e direita: ele inverte a frente e o trás. Cada ponto é refletido bem "
     "à sua frente, então a imagem fica como se você estivesse olhando para si mesmo do outro lado. Por isso, quando "
     "você levanta a mão direita, a imagem parece levantar a esquerda."),
    ("Por que a colher parece quebrada dentro do copo de água?",
     "A colher parece quebrada porque a luz muda de direção ao passar da água para o ar, um fenômeno chamado "
     "refração. A luz que vem da parte mergulhada chega aos olhos num ângulo diferente, e o cérebro vê a colher fora "
     "do lugar real."),
    ("Por que o balão de gás sobe?",
     "O balão de gás sobe porque está cheio de hélio, um gás muito mais leve do que o ar. O ar em volta empurra o "
     "balão para cima com uma força maior que o peso dele, do mesmo jeito que a água empurra uma boia. O balão de "
     "ar quente sobe pelo mesmo motivo: o ar quente é mais leve."),
    ("Por que o pão cresce?",
     "O pão cresce por causa do fermento, que tem leveduras, fungos microscópicos. Elas se alimentam dos açúcares da "
     "massa e soltam gás carbônico. O glúten da farinha forma uma rede elástica que segura esse gás em pequenas "
     "bolhas, e a massa incha."),
    ("Por que a pipoca estoura?",
     "A pipoca estoura porque cada grão de milho tem um pouquinho de água dentro de uma casca dura. Ao esquentar, a "
     "água vira vapor e a pressão aumenta até a casca romper de repente. O amido de dentro se expande e forma a "
     "espuma branca que comemos."),
    ("Por que o refrigerante tem bolhas?",
     "O refrigerante tem bolhas porque gás carbônico é dissolvido nele sob pressão na fábrica. Quando a garrafa é "
     "aberta, a pressão cai e o gás começa a sair da bebida em forma de bolhas. Por isso o refrigerante aberto vai "
     "perdendo o gás."),
    ("Por que o leite derrama quando ferve?",
     "O leite derrama ao ferver porque tem proteínas e gordura que formam uma película na superfície. Essa película "
     "prende o vapor que sobe, criando uma espuma que cresce rapidamente e transborda. Na água, o vapor escapa "
     "livremente e isso não acontece."),
    ("Por que o sal derrete o gelo?",
     "O sal derrete o gelo porque, ao se misturar com a pequena camada de água que existe na superfície do gelo, "
     "forma uma salmoura que só congela a temperaturas bem abaixo de zero. Assim, o gelo em contato com o sal "
     "derrete mesmo num dia frio. Por isso se joga sal nas ruas com neve em alguns países."),
    # tecnologia
    ("Por que o celular esquenta?",
     "O celular esquenta porque o processador e a bateria trabalham e parte da energia vira calor. Jogos, vídeos, "
     "carregamento rápido e sinal fraco exigem mais do aparelho e esquentam mais. Se ficar muito quente, é bom deixar "
     "descansar e tirar da capinha."),
    ("Por que a bateria do celular acaba?",
     "A bateria do celular acaba porque guarda uma quantidade limitada de energia, e tudo no aparelho gasta um pouco: "
     "a tela, o processador, o GPS e a conexão com a internet. A tela acesa e o sinal fraco são grandes vilões. Com "
     "os anos de uso, a bateria também perde capacidade."),
    ("Por que o computador fica lento?",
     "O computador pode ficar lento por vários motivos: muitos programas abertos ao mesmo tempo, pouca memória, disco "
     "quase cheio, programas que iniciam sozinhos ou até vírus. Fechar o que não está usando, liberar espaço e manter "
     "o sistema atualizado costuma ajudar."),
    ("Por que precisamos de senhas fortes?",
     "Precisamos de senhas fortes porque senhas curtas ou óbvias, como datas e sequências, são descobertas facilmente "
     "por programas que testam milhões de combinações. Uma senha longa, com palavras variadas, é muito mais difícil "
     "de adivinhar. Também é importante não repetir a mesma senha em todos os sites."),
    ("Por que a internet às vezes fica lenta?",
     "A internet fica lenta quando muita gente usa a mesma rede ao mesmo tempo, quando o sinal do Wi-Fi está fraco "
     "por causa de paredes e distância, ou quando há problemas no provedor. Vídeos e downloads pesados também ocupam "
     "a conexão."),
    ("Por que a energia elétrica é perigosa?",
     "A eletricidade é perigosa porque a corrente pode passar pelo corpo, que conduz eletricidade por ter água e sais. "
     "Ela pode causar queimaduras e até parar o coração. Por isso não se deve mexer em tomadas com as mãos molhadas "
     "nem chegar perto de fios caídos."),
    ("Por que a lâmpada de LED gasta menos energia?",
     "A lâmpada de LED gasta menos porque transforma quase toda a energia em luz. As lâmpadas antigas, de "
     "filamento, esquentavam muito e desperdiçavam a maior parte da energia como calor. Os LEDs também duram muito "
     "mais tempo."),
    ("Por que os satélites não caem?",
     "Os satélites não caem porque estão viajando muito rápido para os lados, a vários quilômetros por segundo. A "
     "gravidade puxa o satélite para baixo, mas a Terra é curva, então ele cai acompanhando a curvatura sem nunca "
     "chegar ao chão. Sem essa velocidade, ele cairia."),
    # cotidiano e sociedade
    ("Por que devemos reciclar?",
     "Devemos reciclar porque assim muitos materiais, como papel, plástico, vidro e metal, voltam a ser usados em vez "
     "de virar lixo. Isso economiza matéria-prima, água e energia, diminui a poluição e a quantidade de lixo nos "
     "aterros. Separar o lixo em casa é o primeiro passo."),
    ("Por que devemos economizar água?",
     "Devemos economizar água porque, apesar de a Terra ter muita água, só uma pequena parte é doce e fácil de usar. "
     "Tratar e levar água até as casas custa energia e dinheiro, e em épocas de seca pode faltar. Fechar a torneira "
     "ao escovar os dentes e tomar banhos mais curtos já ajudam."),
    ("Por que devemos usar cinto de segurança?",
     "O cinto de segurança segura o corpo no banco numa freada ou batida. Sem ele, o corpo continua indo para a "
     "frente com a velocidade do carro e pode bater no painel, no vidro ou ser jogado para fora. Ele reduz muito o "
     "risco de morte e de ferimentos graves, também no banco de trás."),
    ("Por que existe o semáforo?",
     "O semáforo existe para organizar a passagem de carros e pedestres nos cruzamentos. Ao alternar quem pode passar, "
     "ele evita batidas e atropelamentos. O verde libera, o amarelo avisa que vai fechar e o vermelho manda parar."),
    ("Por que pagamos impostos?",
     "Os impostos são o dinheiro que o governo arrecada para pagar serviços e obras públicas, como escolas, postos de "
     "saúde, ruas, segurança e o salário dos servidores. Cada país decide quais impostos cobra e como usa o dinheiro, "
     "e acompanhar esse uso faz parte da cidadania."),
    ("Por que existem leis?",
     "As leis existem para organizar a vida em sociedade, dizendo o que é permitido e o que é proibido, e garantir "
     "direitos e deveres para todos. Sem regras comuns, os conflitos seriam resolvidos pela força. No Brasil, a lei "
     "mais importante é a Constituição."),
    ("Por que precisamos ir à escola?",
     "A escola ensina a ler, escrever, fazer contas e entender o mundo, da ciência à história. Ela também ensina a "
     "conviver com pessoas diferentes, trabalhar em grupo e pensar com autonomia. O estudo abre portas para o "
     "trabalho e para a vida em sociedade."),
    ("Por que é importante ler?",
     "Ler é importante porque amplia o vocabulário, melhora a escrita e ajuda a entender ideias mais complexas. A "
     "leitura também faz a gente conhecer outros lugares, épocas e pontos de vista, e exercita a imaginação e a "
     "concentração."),
    ("Por que o dinheiro tem valor?",
     "O dinheiro tem valor porque as pessoas confiam que poderão trocá-lo por produtos e serviços. Hoje, as notas e "
     "moedas não valem pelo material de que são feitas, mas porque o governo garante a moeda e todos a aceitam. Se "
     "essa confiança diminui, o dinheiro perde valor."),
    ("Por que os preços sobem?",
     "Os preços sobem por vários motivos, como aumento do custo de produção, de energia e transporte, procura maior "
     "do que a oferta ou mais dinheiro circulando do que produtos. Quando os preços sobem de forma geral e "
     "constante, chamamos isso de inflação."),
    ("Por que existem fusos horários?",
     "Existem fusos horários porque a Terra gira, e o Sol ilumina cada lugar numa hora diferente. Para que o meio-dia "
     "fique perto da hora em que o Sol está mais alto, o mundo foi dividido em faixas com horários diferentes. O "
     "Brasil, por ser grande, tem mais de um fuso."),
    ("Por que o ano bissexto existe?",
     "O ano bissexto existe porque a Terra leva cerca de 365 dias e 6 horas para dar uma volta em torno do Sol. Essas "
     "6 horas a mais formam um dia inteiro a cada quatro anos, que é acrescentado em fevereiro, no dia 29. Assim, o "
     "calendário não se desencontra das estações."),
    ("Por que a semana tem sete dias?",
     "A semana de sete dias vem de povos antigos do Oriente Médio, como os babilônios, que observavam sete astros "
     "visíveis a olho nu no céu e as fases da Lua, de cerca de sete dias cada. O costume foi adotado por outras "
     "culturas e se espalhou pelo mundo."),
    ("Por que comemoramos aniversários?",
     "Comemoramos aniversários para marcar mais um ano de vida e celebrar a pessoa com quem gostamos. O costume é "
     "antigo e mudou ao longo da história; o bolo com velas e os parabéns se popularizaram nos últimos séculos. É um "
     "momento de reunir amigos e família."),
    ("Por que as pessoas falam línguas diferentes?",
     "As pessoas falam línguas diferentes porque, ao longo de milhares de anos, grupos humanos se espalharam pelo "
     "mundo e ficaram separados. Cada grupo foi mudando sua forma de falar, até surgirem línguas diferentes. O "
     "português, por exemplo, veio do latim falado na Península Ibérica."),
    ("Por que no Brasil se fala português?",
     "No Brasil se fala português porque o território foi colonizado por Portugal a partir de 1500. Com o tempo, a "
     "língua dos colonizadores se tornou a principal do país, misturada com palavras de línguas indígenas e "
     "africanas. Ainda hoje, muitas línguas indígenas são faladas no Brasil."),
    ("Por que o português do Brasil é diferente do de Portugal?",
     "O português do Brasil e o de Portugal são a mesma língua, mas mudaram de jeitos diferentes depois de séculos "
     "de separação. O contato com línguas indígenas e africanas e com imigrantes também influenciou o Brasil. As "
     "diferenças aparecem na pronúncia, em algumas palavras e na gramática, mas os falantes se entendem."),
    ("Por que algumas palavras têm acento?",
     "Os acentos mostram qual sílaba é pronunciada com mais força e se a vogal é aberta ou fechada, como em café e "
     "você. Eles também diferenciam palavras que se escrevem quase igual, como avó e avô. As regras de acentuação "
     "ajudam a ler a palavra do jeito certo."),
    # história
    ("Por que os portugueses vieram para o Brasil?",
     "Os portugueses chegaram ao Brasil em 1500, durante as Grandes Navegações, buscando novas rotas de comércio, "
     "riquezas e terras. Depois, colonizaram o território para explorar o pau-brasil, o açúcar e, mais tarde, o "
     "ouro. A colonização teve um custo enorme para os povos indígenas e para os africanos escravizados."),
    ("Por que o Brasil ficou independente?",
     "O Brasil ficou independente em 1822 depois de vários conflitos com Portugal, que queria voltar a controlar o "
     "país com mais força. Dom Pedro, que governava o Brasil, rompeu com as cortes portuguesas e declarou a "
     "independência no dia 7 de setembro."),
    ("Por que as pirâmides do Egito foram construídas?",
     "As grandes pirâmides do Egito foram construídas como túmulos para os faraós. Os egípcios acreditavam na vida "
     "depois da morte, e o túmulo devia proteger o corpo e guardar objetos para a outra vida. A Grande Pirâmide de "
     "Gizé foi feita há cerca de 4.500 anos."),
    ("Por que os dinossauros foram extintos?",
     "A maioria dos dinossauros foi extinta há cerca de 66 milhões de anos, e a explicação mais aceita é a queda de "
     "um grande asteroide no México. O impacto levantou poeira e fumaça que escureceram o céu, esfriaram o clima e "
     "derrubaram as cadeias de alimento. As aves descendem de dinossauros que sobreviveram."),
    ("Por que a escrita foi inventada?",
     "A escrita foi inventada há mais de 5 mil anos, na Mesopotâmia, principalmente para registrar contas, impostos e "
     "trocas de mercadorias. Com o tempo, passou a ser usada para leis, histórias e cartas. Ela permitiu guardar o "
     "conhecimento e passá-lo para as próximas gerações."),
    ("Por que a Revolução Industrial foi importante?",
     "A Revolução Industrial, que começou na Inglaterra no século XVIII, trocou boa parte do trabalho manual por "
     "máquinas, primeiro movidas a vapor. A produção aumentou muito, as cidades cresceram e surgiram as fábricas e "
     "os operários. Ela também trouxe problemas, como poluição e jornadas de trabalho muito longas."),
    # sentimentos e convivência
    ("Por que sentimos medo?",
     "Sentimos medo porque ele é um alarme que nos protege do perigo. Diante de uma ameaça, o corpo libera "
     "adrenalina, o coração acelera e os músculos se preparam para fugir ou reagir. Ter medo é normal; quando ele é "
     "muito forte e atrapalha a vida, vale procurar ajuda."),
    ("Por que é bom ter amigos?",
     "Amigos fazem bem porque dão apoio nos momentos difíceis, dividem as alegrias e ajudam a gente a se sentir "
     "parte de um grupo. Conversar e rir com amigos diminui o estresse. Uma boa amizade se constrói com confiança, "
     "respeito e tempo juntos."),
    ("Por que devemos respeitar as diferenças?",
     "Devemos respeitar as diferenças porque cada pessoa tem sua história, aparência, cultura e jeito de pensar, e "
     "todas merecem ser tratadas com dignidade. O respeito torna a convivência mais justa e pacífica e permite "
     "aprender com quem é diferente da gente."),
    ("Por que pedir desculpas é importante?",
     "Pedir desculpas é importante porque mostra que reconhecemos o erro e que nos importamos com quem foi magoado. "
     "Isso ajuda a reparar a relação e reconstruir a confiança. Um bom pedido de desculpas é sincero e vem junto com "
     "a vontade de não repetir o erro."),
    ("Por que ficamos com raiva?",
     "A raiva aparece quando nos sentimos injustiçados, ameaçados ou frustrados. Ela prepara o corpo para reagir, "
     "acelerando o coração e a respiração. Sentir raiva é normal; o importante é respirar, se acalmar e expressar o "
     "que sente sem machucar ninguém."),
    ("Por que é difícil acordar cedo?",
     "Acordar cedo pode ser difícil quando a pessoa dorme tarde ou pouco, porque o corpo ainda não terminou o "
     "descanso. Telas à noite também atrapalham, já que a luz delas atrasa o sono. Adolescentes, em especial, têm um "
     "relógio biológico que tende a dormir e acordar mais tarde."),
    ("Por que a música mexe com as emoções?",
     "A música mexe com as emoções porque ativa várias partes do cérebro ao mesmo tempo, incluindo as ligadas à "
     "memória e ao prazer. Ritmos e melodias podem acalmar, animar ou deixar a gente saudoso, e muitas vezes trazem "
     "lembranças de momentos da vida."),
    ("Por que rimos?",
     "Rimos principalmente para nos comunicar e nos aproximar das pessoas. O riso aparece com piadas e situações "
     "engraçadas, mas também como sinal de simpatia numa conversa. Ele alivia a tensão e libera substâncias que dão "
     "sensação de bem-estar."),
    ("Por que sonhamos?",
     "Os cientistas ainda discutem por que sonhamos. Algumas explicações dizem que os sonhos ajudam o cérebro a "
     "organizar memórias e emoções do dia, e outras, que eles são um efeito da atividade do cérebro durante o sono. "
     "Os sonhos mais vívidos acontecem numa fase do sono chamada REM."),
    ("Por que esquecemos as coisas?",
     "Esquecemos porque o cérebro não guarda tudo: ele seleciona o que parece importante e deixa o resto se apagar, "
     "para não ficar sobrecarregado. Também esquecemos quando estamos distraídos, cansados ou estressados. Revisar, "
     "dormir bem e ligar o novo ao que já sabemos ajudam a lembrar."),
    ("Por que a gente aprende melhor praticando?",
     "Aprendemos melhor praticando porque, a cada repetição, as ligações entre os neurônios envolvidos ficam mais "
     "fortes. Fazer, errar e corrigir faz o cérebro prestar atenção nos detalhes. Por isso estudar um pouco todos os "
     "dias funciona melhor do que estudar tudo de uma vez."),
]
