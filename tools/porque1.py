"""Perguntas de "por quê" (parte 1: natureza, céu, corpo e saúde). Respostas de 2 a 4 frases, com a causa."""

PORQUES = [
    # céu, clima e Terra
    ("Por que o céu é azul?",
     "O céu é azul porque a luz do Sol, ao atravessar o ar, se espalha nas moléculas da atmosfera. A luz azul tem "
     "onda mais curta e se espalha muito mais do que a vermelha. Por isso, olhando para qualquer parte do céu, "
     "chega aos nossos olhos principalmente luz azul."),
    ("Por que o pôr do sol é alaranjado?",
     "No fim da tarde, a luz do Sol atravessa uma camada de ar muito mais grossa até chegar até nós. No caminho, "
     "quase toda a luz azul se espalha e se perde, e sobram as cores de onda mais longa, como o laranja e o "
     "vermelho. Poeira e umidade no ar deixam essas cores ainda mais fortes."),
    ("Por que chove?",
     "Chove porque o vapor de água sobe com o ar quente, esfria lá no alto e se condensa em gotinhas que formam as "
     "nuvens. Quando essas gotinhas se juntam e ficam pesadas demais para continuar flutuando, elas caem como chuva. "
     "Esse vaivém da água entre o chão e o céu faz parte do ciclo da água."),
    ("Por que existe o arco-íris?",
     "O arco-íris aparece quando a luz do Sol entra nas gotas de chuva, se curva e se reflete dentro delas. Cada cor "
     "da luz se curva um pouco diferente, então a luz branca se separa em vermelho, laranja, amarelo, verde, azul, "
     "anil e violeta. Por isso ele só aparece com sol atrás de você e chuva na sua frente."),
    ("Por que o trovão vem depois do relâmpago?",
     "O relâmpago e o trovão acontecem ao mesmo tempo, mas a luz viaja muito mais rápido do que o som. A luz chega "
     "quase na hora, enquanto o som anda cerca de 340 metros por segundo. Contando os segundos entre os dois, dá "
     "para ter uma ideia de quão longe a tempestade está."),
    ("Por que existem as estações do ano?",
     "As estações existem porque o eixo da Terra é inclinado em relação ao caminho que ela faz em volta do Sol. Em "
     "uma parte do ano, um hemisfério recebe os raios do Sol mais diretamente e por mais horas, e fica mais quente; "
     "na outra parte, recebe a luz mais inclinada e fica mais frio. Não é porque a Terra fica mais perto ou mais "
     "longe do Sol."),
    ("Por que existe o dia e a noite?",
     "O dia e a noite existem porque a Terra gira em torno de si mesma, uma volta a cada 24 horas. O lado virado "
     "para o Sol fica iluminado e tem dia, enquanto o lado oposto fica no escuro e tem noite. Esse giro se chama "
     "movimento de rotação."),
    ("Por que a Lua muda de forma?",
     "A Lua não muda de forma de verdade: ela é sempre redonda. O que muda é a parte iluminada pelo Sol que "
     "conseguimos ver daqui da Terra, conforme a Lua dá a volta em torno do nosso planeta. Por isso vemos as fases: "
     "nova, crescente, cheia e minguante, num ciclo de cerca de 29 dias e meio."),
    ("Por que a água do mar é salgada?",
     "A água do mar é salgada porque, durante milhões de anos, a chuva e os rios foram dissolvendo minerais das "
     "rochas e levando esses sais para o oceano. Quando a água do mar evapora, o sal fica para trás, então ele foi "
     "se acumulando. O sal mais comum no mar é o mesmo sal de cozinha, o cloreto de sódio."),
    ("Por que o gelo boia na água?",
     "O gelo boia porque é menos denso do que a água líquida. Quando a água congela, as moléculas se organizam numa "
     "estrutura com mais espaço vazio entre elas, ocupando mais volume com a mesma massa. Isso é importante para a "
     "vida: os lagos congelam por cima, e a água de baixo continua líquida para os peixes."),
    ("Por que as folhas das árvores ficam amarelas no outono?",
     "No outono, com menos luz e mais frio, muitas árvores param de produzir clorofila, o pigmento verde que faz a "
     "fotossíntese. Sem o verde por cima, aparecem outros pigmentos que já estavam na folha, amarelos e alaranjados. "
     "Depois, a árvore solta as folhas para economizar água e energia durante o inverno."),
    ("Por que os vulcões entram em erupção?",
     "Os vulcões entram em erupção porque, embaixo da crosta, existe rocha derretida, chamada magma, cheia de gases. "
     "O magma é mais leve que as rochas em volta e sobe; quando a pressão dos gases fica grande demais, ele "
     "atravessa a crosta e sai como lava, cinzas e gases. Muitos vulcões ficam nas bordas das placas tectônicas."),
    ("Por que acontecem terremotos?",
     "Os terremotos acontecem porque a crosta da Terra é dividida em grandes placas que se movem bem devagar. Em "
     "alguns lugares, essas placas ficam presas umas nas outras e acumulam tensão. Quando a rocha não aguenta mais e "
     "se rompe de repente, a energia liberada faz o chão tremer."),
    ("Por que o vento sopra?",
     "O vento sopra porque o Sol aquece a superfície da Terra de forma desigual. O ar quente fica mais leve e sobe, "
     "e o ar mais frio das regiões vizinhas corre para ocupar o lugar dele. Esse movimento do ar, de onde a pressão "
     "é maior para onde é menor, é o vento."),
    ("Por que neva?",
     "Neva quando a temperatura nas nuvens é tão baixa que o vapor de água vira pequenos cristais de gelo, em vez de "
     "gotas. Os cristais se juntam em flocos e caem. Para a neve chegar ao chão sem derreter, o ar perto do solo "
     "também precisa estar frio, perto de zero grau ou abaixo."),
    ("Por que faz mais frio no alto das montanhas?",
     "Faz mais frio nas montanhas porque o ar lá em cima é mais rarefeito, com menos pressão. Ar com menos pressão "
     "se expande e esfria, e também guarda menos calor. Em média, a temperatura cai cerca de 6 graus a cada mil "
     "metros de altitude."),
    ("Por que o mar tem ondas?",
     "A maior parte das ondas do mar é formada pelo vento, que empurra a superfície da água e transfere energia "
     "para ela. Quanto mais forte e mais longo o vento, maiores as ondas. Terremotos no fundo do mar também podem "
     "formar ondas gigantes, chamadas tsunamis."),
    ("Por que existe a maré?",
     "A maré existe principalmente por causa da gravidade da Lua, que puxa a água dos oceanos e forma uma espécie "
     "de elevação do lado virado para ela e também do lado oposto. Como a Terra gira, cada lugar passa por essas "
     "elevações, e a maré sobe e desce cerca de duas vezes por dia. O Sol também ajuda, mas com menos força."),
    ("Por que as estrelas piscam?",
     "As estrelas parecem piscar porque a luz delas atravessa a atmosfera da Terra, que está sempre em movimento, "
     "com camadas de ar de temperaturas diferentes. Essas camadas desviam a luz um pouquinho de um jeito que muda o "
     "tempo todo. Vistas do espaço, sem atmosfera, as estrelas não piscam."),
    ("Por que o Sol brilha?",
     "O Sol brilha porque, no centro dele, a pressão e a temperatura são tão altas que átomos de hidrogênio se "
     "juntam e formam hélio. Essa reação, chamada fusão nuclear, libera uma quantidade enorme de energia, que sai "
     "do Sol em forma de luz e calor."),
    ("Por que os planetas giram em volta do Sol?",
     "Os planetas giram em volta do Sol porque a gravidade do Sol os puxa o tempo todo, e eles também têm uma "
     "velocidade para os lados. A combinação dos dois faz com que eles fiquem caindo em direção ao Sol sem nunca "
     "chegar, numa órbita. Sem a gravidade, eles seguiriam em linha reta pelo espaço."),
    ("Por que não sentimos a Terra girar?",
     "Não sentimos a Terra girar porque ela gira de maneira constante, sem trancos, e nós, o ar e tudo à nossa volta "
     "giramos junto com ela. Só percebemos movimento quando a velocidade muda, como num carro que freia. Por isso a "
     "sensação é de estar parado."),
    ("Por que Marte é vermelho?",
     "Marte é avermelhado porque o solo e a poeira da superfície têm muito óxido de ferro, que é basicamente "
     "ferrugem. Os ventos espalham essa poeira pela atmosfera fina do planeta, e tudo fica com um tom vermelho ou "
     "alaranjado."),
    ("Por que a Lua não cai na Terra?",
     "A Lua não cai na Terra porque ela se move muito rápido para os lados, a cerca de um quilômetro por segundo. A "
     "gravidade da Terra puxa a Lua, mas, como ela também avança, a queda vira uma curva em volta do planeta, que é "
     "a órbita. É o mesmo motivo de os satélites ficarem no espaço."),
    # corpo humano e saúde
    ("Por que a gente boceja?",
     "Os cientistas ainda estudam o motivo exato do bocejo. Uma das explicações mais aceitas é que ele ajuda a "
     "esfriar o cérebro e a deixar a pessoa mais alerta quando ela está com sono ou entediada. Bocejar também é "
     "contagioso: ver alguém bocejando muitas vezes faz a gente bocejar junto."),
    ("Por que a gente sente sono?",
     "Sentimos sono porque, durante o dia, uma substância chamada adenosina vai se acumulando no cérebro e aumenta "
     "a vontade de dormir. Além disso, o corpo tem um relógio interno que, quando escurece, libera melatonina, o "
     "hormônio que prepara o corpo para o descanso. Dormindo, o corpo e o cérebro se recuperam."),
    ("Por que precisamos dormir?",
     "Precisamos dormir porque é durante o sono que o cérebro organiza as memórias e o que aprendemos, e o corpo "
     "repara músculos e tecidos. O sono também ajuda o sistema de defesa e o controle do humor e do apetite. "
     "Dormir pouco por muito tempo deixa a pessoa cansada, desatenta e mais sujeita a doenças."),
    ("Por que a gente sua?",
     "Suamos para controlar a temperatura do corpo. Quando o corpo esquenta, por causa do calor ou de exercício, as "
     "glândulas da pele soltam suor; quando ele evapora, leva calor junto e a pele esfria. Por isso é importante "
     "beber água quando se sua muito."),
    ("Por que o coração bate?",
     "O coração bate para bombear o sangue por todo o corpo. Cada batida é uma contração do músculo do coração, "
     "comandada por pequenos sinais elétricos que nascem nele mesmo. O sangue leva oxigênio e nutrientes para as "
     "células e traz de volta o gás carbônico."),
    ("Por que o coração bate mais rápido quando corremos?",
     "Quando corremos, os músculos trabalham mais e precisam de mais oxigênio e energia. Para levar mais sangue até "
     "eles, o coração acelera e bate com mais força. Ao mesmo tempo, a respiração também fica mais rápida."),
    ("Por que temos febre?",
     "A febre é uma defesa do corpo. Quando o organismo detecta uma infecção, o cérebro aumenta a temperatura do "
     "corpo, o que atrapalha a multiplicação de muitos vírus e bactérias e ajuda o sistema de defesa a trabalhar. "
     "Febre alta ou que dura muito precisa de avaliação médica."),
    ("Por que espirramos?",
     "Espirramos para expulsar do nariz coisas que irritam, como poeira, pólen ou o excesso de muco de um "
     "resfriado. O espirro é um reflexo: o corpo puxa o ar e solta tudo de uma vez, com muita força. Por isso é "
     "bom cobrir o nariz e a boca com o braço ao espirrar."),
    ("Por que soluçamos?",
     "O soluço acontece quando o diafragma, o músculo que fica embaixo dos pulmões, se contrai de repente, sem a "
     "gente querer. O ar entra rápido e as cordas vocais se fecham, fazendo o som do soluço. Comer muito rápido, "
     "tomar refrigerante ou ficar nervoso pode provocar soluço, que quase sempre passa sozinho."),
    ("Por que a pele fica enrugada depois de muito tempo na água?",
     "Depois de muito tempo na água, os dedos ficam enrugados porque o sistema nervoso faz os vasos sanguíneos da "
     "ponta dos dedos se contraírem. A pele se dobra e forma pequenas rugas. Uma explicação estudada é que isso "
     "ajuda a segurar objetos molhados com mais firmeza, como os sulcos de um pneu."),
    ("Por que temos impressões digitais?",
     "As impressões digitais são os desenhos de linhas na ponta dos dedos. Elas ajudam a segurar objetos e a "
     "perceber texturas pelo tato. O desenho se forma ainda na barriga da mãe e é diferente em cada pessoa, até em "
     "gêmeos idênticos, por isso é usado para identificar as pessoas."),
    ("Por que o sangue é vermelho?",
     "O sangue é vermelho por causa da hemoglobina, uma proteína que fica dentro dos glóbulos vermelhos e carrega o "
     "oxigênio. A hemoglobina tem ferro, e é a ligação do ferro com o oxigênio que dá a cor vermelha. O sangue nas "
     "veias também é vermelho, só que um pouco mais escuro."),
    ("Por que as veias parecem azuis?",
     "As veias parecem azuis por um efeito da luz, não porque o sangue seja azul. A pele deixa passar e reflete as "
     "cores de um jeito diferente: a luz vermelha entra mais fundo e é absorvida, enquanto a azul volta mais para os "
     "nossos olhos. O sangue dentro delas é vermelho-escuro."),
    ("Por que temos que escovar os dentes?",
     "Precisamos escovar os dentes porque restos de comida, principalmente de açúcar, alimentam bactérias da boca. "
     "Essas bactérias formam a placa e produzem ácidos que corroem o esmalte e causam cáries, além de inflamar a "
     "gengiva. Escovar e usar fio dental tira a placa antes que ela faça estragos."),
    ("Por que o açúcar faz mal para os dentes?",
     "O açúcar faz mal para os dentes porque as bactérias da boca se alimentam dele e, ao digerir o açúcar, "
     "produzem ácidos. Esses ácidos dissolvem aos poucos o esmalte, a camada protetora do dente, e abrem caminho "
     "para as cáries. Quanto mais vezes por dia se come doce, mais tempo os dentes ficam sob ataque."),
    ("Por que precisamos beber água?",
     "Precisamos beber água porque cerca de 60% do corpo é feito de água, e ela participa de quase tudo: transporta "
     "nutrientes, ajuda na digestão, controla a temperatura pelo suor e leva embora o que o corpo não usa, pela "
     "urina. Como perdemos água o tempo todo, precisamos repor todos os dias."),
    ("Por que temos que tomar vacina?",
     "As vacinas ensinam o sistema de defesa a reconhecer um vírus ou uma bactéria sem que a pessoa precise ficar "
     "doente. Assim, se o corpo encontrar o micróbio de verdade, ele já sabe se defender rápido. Quando muita gente "
     "se vacina, a doença tem dificuldade de se espalhar e também protege quem não pode tomar a vacina."),
    ("Por que devemos lavar as mãos?",
     "Devemos lavar as mãos porque elas tocam em muitas coisas e acabam carregando vírus e bactérias que podem "
     "causar doenças. Ao levar a mão à boca, ao nariz ou à comida, esses micróbios entram no corpo. Lavar com água e "
     "sabão por uns 20 segundos remove a maior parte deles."),
    ("Por que o sabão limpa?",
     "O sabão limpa porque suas moléculas têm duas pontas diferentes: uma gosta de água e a outra gosta de gordura. "
     "A ponta que gosta de gordura gruda na sujeira oleosa, e a outra fica voltada para a água. Assim, a sujeira se "
     "solta e vai embora com o enxágue."),
    ("Por que não devemos olhar diretamente para o Sol?",
     "Não devemos olhar para o Sol porque a luz dele é tão forte que pode queimar a retina, a parte do fundo do olho "
     "que recebe as imagens. Essa lesão pode ser permanente e não dói na hora, então a pessoa nem percebe o dano. "
     "Mesmo durante um eclipse, só se deve olhar com filtros próprios."),
    ("Por que o protetor solar é importante?",
     "O protetor solar é importante porque bloqueia parte dos raios ultravioleta do Sol, que queimam a pele e, com o "
     "tempo, causam manchas, envelhecimento e podem levar ao câncer de pele. Ele deve ser usado mesmo em dias "
     "nublados e reaplicado depois de algumas horas ou de entrar na água."),
    ("Por que sentimos dor?",
     "Sentimos dor porque ela é um alarme do corpo. Quando algo machuca ou ameaça os tecidos, nervos especiais "
     "mandam sinais para o cérebro, que transforma esses sinais em dor. Isso faz a gente se afastar do perigo, como "
     "tirar a mão de algo quente, e cuidar da parte machucada."),
    ("Por que a barriga ronca?",
     "A barriga ronca porque o estômago e o intestino se contraem o tempo todo para empurrar a comida, o líquido e o "
     "ar. Quando estão vazios, esses movimentos fazem mais barulho, já que não há comida para abafar o som. Por isso "
     "o ronco aparece mais quando estamos com fome."),
    ("Por que sentimos fome?",
     "Sentimos fome porque o corpo precisa de energia e nutrientes. Quando o estômago fica vazio e o açúcar no "
     "sangue diminui, alguns hormônios, como a grelina, avisam o cérebro, que cria a vontade de comer. Depois da "
     "refeição, outros hormônios trazem a sensação de saciedade."),
    ("Por que os olhos lacrimejam quando cortamos cebola?",
     "Quando a cebola é cortada, suas células se rompem e liberam substâncias que se transformam num gás irritante. "
     "Esse gás chega aos olhos, e eles produzem lágrimas para se proteger e lavar a irritação. Usar uma faca bem "
     "afiada ou gelar a cebola antes ajuda a diminuir o choro."),
    ("Por que choramos?",
     "Choramos por motivos diferentes. Lágrimas sempre umedecem e protegem os olhos, e também aparecem quando algo "
     "irrita, como poeira ou cebola. Também choramos por emoção, de tristeza ou de alegria; esse choro ajuda a "
     "aliviar a tensão e mostra aos outros que precisamos de apoio."),
    ("Por que ficamos vermelhos de vergonha?",
     "Ficamos vermelhos de vergonha porque, numa situação constrangedora, o corpo libera adrenalina, que dilata os "
     "vasos sanguíneos do rosto. Com mais sangue passando perto da pele, as bochechas ficam vermelhas e quentes. É "
     "uma reação automática, que não dá para controlar."),
    ("Por que a gente fica arrepiado?",
     "Ficamos arrepiados porque pequenos músculos na base de cada pelo se contraem e levantam os pelos, com frio ou "
     "com emoção. Nos animais com muito pelo, isso guarda uma camada de ar quente ou faz o bicho parecer maior. Em "
     "nós, sobrou só o arrepio."),
    ("Por que crianças crescem?",
     "As crianças crescem porque o corpo produz o hormônio do crescimento, principalmente durante o sono. Ele faz os "
     "ossos se alongarem nas regiões perto das pontas, chamadas placas de crescimento, que ficam ativas até o fim da "
     "adolescência. Comer bem, dormir e fazer atividade física ajudam."),
    ("Por que os cabelos ficam brancos?",
     "Os cabelos ficam brancos porque, com o tempo, as células da raiz do cabelo produzem menos melanina, o pigmento "
     "que dá cor aos fios. Sem pigmento, o fio nasce branco ou grisalho. A idade em que isso começa depende muito da "
     "genética da família."),
    ("Por que temos dois olhos?",
     "Ter dois olhos ajuda a perceber a profundidade e a distância das coisas. Cada olho vê a cena de um ângulo um "
     "pouco diferente, e o cérebro junta as duas imagens numa só, em três dimensões. Também aumenta o campo de visão "
     "e funciona como reserva se um olho se machucar."),
    ("Por que o exercício físico faz bem?",
     "O exercício físico faz bem porque fortalece o coração, os pulmões, os músculos e os ossos. Ele também ajuda a "
     "controlar o peso e a pressão, melhora o sono e libera substâncias no cérebro que diminuem o estresse e dão "
     "sensação de bem-estar. O ideal é se movimentar um pouco todos os dias."),
    ("Por que comer frutas e verduras é importante?",
     "Frutas e verduras são importantes porque têm vitaminas, minerais e fibras que o corpo precisa para funcionar "
     "bem. As vitaminas ajudam o sistema de defesa, e as fibras ajudam o intestino. Comer cores variadas no prato "
     "garante uma mistura maior de nutrientes."),
    ("Por que o fumo faz mal?",
     "O cigarro faz mal porque a fumaça tem milhares de substâncias tóxicas, muitas delas causadoras de câncer. Ela "
     "danifica os pulmões, endurece os vasos sanguíneos e aumenta o risco de infarto e derrame. A nicotina vicia, o "
     "que torna difícil parar, mas largar o cigarro traz benefícios em qualquer idade."),
    ("Por que não devemos tomar remédio sem orientação?",
     "Não devemos tomar remédio sem orientação porque cada medicamento tem uma dose certa, efeitos colaterais e pode "
     "reagir mal com outros remédios. Um remédio errado pode esconder os sintomas de uma doença séria ou até "
     "intoxicar. Antibióticos usados à toa também deixam as bactérias resistentes."),
    ("Por que o antibiótico não funciona contra gripe?",
     "O antibiótico não funciona contra gripe porque ele age contra bactérias, e a gripe é causada por um vírus. Os "
     "vírus são muito diferentes das bactérias e não são afetados por esses remédios. Tomar antibiótico sem precisar "
     "ainda ajuda a criar bactérias resistentes."),
    # animais e plantas
    ("Por que as plantas são verdes?",
     "As plantas são verdes por causa da clorofila, o pigmento que elas usam para fazer fotossíntese. A clorofila "
     "absorve bem a luz vermelha e a azul e reflete a luz verde. É essa luz verde refletida que chega aos nossos "
     "olhos."),
    ("Por que as plantas precisam de luz?",
     "As plantas precisam de luz porque produzem o próprio alimento pela fotossíntese. Usando a energia da luz, elas "
     "transformam água e gás carbônico em açúcar e liberam oxigênio. Sem luz, a planta fica sem energia, enfraquece "
     "e acaba morrendo."),
    ("Por que as árvores são importantes?",
     "As árvores são importantes porque produzem oxigênio, absorvem gás carbônico, dão sombra e refrescam o ar. Elas "
     "também seguram o solo com as raízes, evitando erosão, protegem rios e nascentes e são casa e alimento para "
     "muitos animais."),
    ("Por que as abelhas são importantes?",
     "As abelhas são importantes porque, ao voar de flor em flor atrás de néctar, levam o pólen de uma para outra e "
     "fazem a polinização. Sem isso, muitas plantas não formam frutos nem sementes. Boa parte das frutas, verduras e "
     "grãos que comemos depende delas."),
    ("Por que o camaleão muda de cor?",
     "O camaleão muda de cor principalmente para se comunicar e controlar a temperatura, e não só para se camuflar. "
     "Na pele, ele tem células com pequenos cristais que mudam de arrumação, alterando a cor refletida. Ele fica "
     "mais escuro para absorver calor e mais colorido para chamar atenção de outros camaleões."),
    ("Por que os gatos ronronam?",
     "Os gatos ronronam vibrando músculos da garganta quando respiram. Eles fazem isso quando estão tranquilos e "
     "satisfeitos, mas também quando estão doentes ou com medo, como forma de se acalmar. Alguns estudos sugerem que "
     "a vibração ajuda até a recuperar ossos e músculos."),
    ("Por que os cães abanam o rabo?",
     "Os cães abanam o rabo para se comunicar. Um rabo balançando solto e para os lados costuma mostrar alegria, mas "
     "o jeito do movimento também conta: rabo alto e duro pode indicar alerta, e rabo baixo entre as pernas mostra "
     "medo. É preciso olhar o corpo todo do cachorro para entender."),
    ("Por que os peixes não se afogam?",
     "Os peixes não se afogam porque respiram com brânquias, que retiram o oxigênio dissolvido na água. A água entra "
     "pela boca, passa pelas brânquias, que pegam o oxigênio, e sai pelas laterais. Por isso, fora da água, a "
     "maioria dos peixes não consegue respirar."),
    ("Por que as baleias soltam um jato de água?",
     "As baleias são mamíferos e respiram ar, por um orifício no alto da cabeça. Quando sobem para respirar, soltam "
     "com força o ar quente dos pulmões, que se mistura com a água do mar e com vapor e forma o jato. Depois, puxam "
     "ar fresco e mergulham de novo."),
    ("Por que os pássaros migram?",
     "Muitos pássaros migram para fugir do inverno e da falta de comida. Eles viajam para regiões mais quentes, onde "
     "há alimento, e voltam na primavera para se reproduzir. Para se orientar, usam o Sol, as estrelas, o campo "
     "magnético da Terra e pontos da paisagem."),
    ("Por que os ursos hibernam?",
     "Alguns ursos passam o inverno numa espécie de sono profundo porque nessa época quase não há comida. Antes do "
     "frio, eles comem muito e acumulam gordura. Na toca, o corpo deles desacelera, o coração bate mais devagar e a "
     "gordura guardada mantém o animal vivo até a primavera."),
    ("Por que as cobras trocam de pele?",
     "As cobras trocam de pele porque a camada de fora da pele não cresce junto com o corpo e vai se desgastando. De "
     "tempos em tempos, uma pele nova se forma por baixo, e a cobra se esfrega em pedras e galhos até soltar a pele "
     "velha inteira, como uma meia virada do avesso."),
    ("Por que as girafas têm o pescoço comprido?",
     "As girafas têm o pescoço comprido por causa da evolução. As que tinham pescoço mais longo conseguiam comer "
     "folhas mais altas das árvores e, nas brigas entre os machos, que usam o pescoço, levavam vantagem. Assim, elas "
     "deixaram mais filhotes, e a característica foi passando de geração em geração."),
    ("Por que as zebras têm listras?",
     "Os cientistas estudaram várias explicações para as listras das zebras, e uma das mais aceitas é que elas "
     "atrapalham moscas e mutucas, que têm dificuldade de pousar em superfícies listradas. As listras também podem "
     "confundir predadores quando o grupo corre junto e ajudar a controlar a temperatura."),
    ("Por que o morcego dorme de cabeça para baixo?",
     "O morcego dorme de cabeça para baixo porque assim fica mais fácil levantar voo: basta soltar as patas e abrir "
     "as asas no meio da queda. Pendurado no teto de cavernas, ele também fica longe de muitos predadores. As patas "
     "dele têm um mecanismo que as mantém fechadas sem esforço."),
    ("Por que as formigas andam em fila?",
     "As formigas andam em fila porque seguem um rastro químico, chamado feromônio, deixado pelas que passaram antes. "
     "Quando uma formiga acha comida, ela volta para o formigueiro marcando o caminho, e as outras seguem o cheiro. "
     "Quanto mais formigas usam a trilha, mais forte fica o rastro."),
    ("Por que os vagalumes brilham?",
     "Os vagalumes brilham por causa de uma reação química no abdômen deles, chamada bioluminescência. Uma substância "
     "chamada luciferina reage com o oxigênio e produz luz quase sem calor. Eles usam o brilho para atrair parceiros "
     "e, em algumas espécies, para avisar que têm gosto ruim."),
    ("Por que as flores têm cheiro?",
     "As flores têm cheiro para atrair animais polinizadores, como abelhas, borboletas, mariposas e morcegos. Esses "
     "animais visitam a flor em busca de néctar e acabam levando o pólen para outras flores. Algumas flores têm "
     "cheiro de carne podre para atrair moscas."),
    ("Por que os cactos têm espinhos?",
     "Os espinhos dos cactos são folhas transformadas. Eles protegem a planta de animais que querem comer sua polpa "
     "cheia de água e ajudam a perder menos água, já que uma folha larga deixaria evaporar muito. Os espinhos também "
     "fazem um pouco de sombra sobre o caule."),
    ("Por que as frutas amadurecem?",
     "As frutas amadurecem porque a planta quer que elas sejam comidas e espalhem as sementes. Com o tempo, a fruta "
     "produz um gás chamado etileno, que transforma o amido em açúcar, amolece a polpa e muda a cor e o cheiro. Por "
     "isso, guardar uma banana madura perto de outras frutas faz todas amadurecerem mais rápido."),
    ("Por que a maçã escurece depois de cortada?",
     "A maçã escurece porque, ao cortar, as células se rompem e certas substâncias da fruta entram em contato com o "
     "oxigênio do ar. Uma enzima acelera essa reação e forma pigmentos marrons. Pingar suco de limão ajuda a "
     "retardar o escurecimento."),
    ("Por que alguns animais estão em extinção?",
     "Muitos animais estão em extinção por causa das ações humanas: destruição das florestas e de outros ambientes, "
     "caça e pesca ilegais, poluição e mudanças no clima. Também pesa a chegada de espécies de outros lugares, que "
     "competem por comida ou trazem doenças. Proteger os habitats é a forma mais eficaz de salvar as espécies."),
]
