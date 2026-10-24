"""Perguntas de "por quê" (parte 3: casa, comida, esportes, geografia, curiosidades e língua)."""

PORQUES = [
    ("Por que a geladeira conserva os alimentos?",
     "A geladeira conserva os alimentos porque o frio deixa os micróbios, como bactérias e fungos, muito mais lentos. "
     "Eles continuam lá, mas se multiplicam devagar, e por isso a comida demora mais para estragar. O frio também "
     "desacelera as reações químicas que deixam os alimentos murchos ou rançosos."),
    ("Por que o sal conserva a carne?",
     "O sal conserva a carne porque puxa a água das células dos alimentos e dos micróbios. Sem água disponível, as "
     "bactérias e os fungos não conseguem se multiplicar. É por isso que a carne-seca e o bacalhau duram tanto tempo "
     "fora da geladeira."),
    ("Por que a comida estraga?",
     "A comida estraga principalmente por causa de micróbios, como bactérias e fungos, que se alimentam dela e se "
     "multiplicam, mudando o cheiro, o gosto e a textura. Calor, umidade e contato com o ar aceleram esse processo. "
     "Por isso guardamos os alimentos na geladeira, em potes fechados e longe do sol."),
    ("Por que a cebola refogada fica doce?",
     "Quando a cebola é refogada devagar, o calor quebra parte das substâncias que dão o sabor forte e ardido, e os "
     "açúcares naturais dela começam a caramelizar. Por isso ela fica dourada, macia e com um gosto mais doce."),
    ("Por que o feijão precisa ficar de molho?",
     "Deixar o feijão de molho por algumas horas amolece os grãos e faz com que eles cozinhem mais rápido e por "
     "igual. A água do molho também leva embora parte das substâncias que causam gases. Por isso muita gente joga "
     "fora essa água antes de cozinhar."),
    ("Por que a pimenta arde?",
     "A pimenta arde por causa da capsaicina, uma substância que ativa na boca os mesmos sensores que percebem o "
     "calor. O cérebro recebe o sinal como se a boca estivesse queimando, embora não haja queimadura de verdade. "
     "Leite e alimentos com gordura aliviam mais que água."),
    ("Por que o café deixa a gente acordado?",
     "O café tem cafeína, que bloqueia no cérebro a ação da adenosina, uma substância que se acumula durante o dia e "
     "dá sono. Com a adenosina bloqueada, a pessoa se sente mais alerta. O efeito dura algumas horas, por isso café "
     "à noite pode atrapalhar o sono."),
    ("Por que o pão fica duro?",
     "O pão fica duro porque, com o tempo, o amido da massa se reorganiza e perde água, num processo chamado "
     "retrogradação. Por isso o miolo fica seco e firme. Esquentar o pão no forno ou na frigideira devolve um pouco "
     "da maciez por um tempo."),
    ("Por que as frutas têm sementes?",
     "As frutas têm sementes porque são a forma que a planta encontrou para se reproduzir e se espalhar. A polpa "
     "gostosa atrai os animais, que comem a fruta e levam as sementes para longe, onde podem nascer novas plantas."),
    ("Por que a bola quica?",
     "A bola quica porque, ao bater no chão, ela se deforma e o ar e a borracha de dentro se comprimem. Logo depois, "
     "eles voltam ao formato original e empurram a bola para cima. Parte da energia se perde em calor e som, por isso "
     "cada quique fica mais baixo."),
    ("Por que a bicicleta não cai quando está andando?",
     "A bicicleta em movimento se equilibra principalmente porque o ciclista faz pequenas correções com o guidão e "
     "com o corpo o tempo todo, quase sem perceber. O formato do garfo da roda dianteira também ajuda a roda a "
     "virar para o lado certo quando a bicicleta começa a inclinar. Parada, fica muito mais difícil."),
    ("Por que os atletas se aquecem antes do exercício?",
     "O aquecimento aumenta aos poucos a temperatura dos músculos e a circulação de sangue, deixando músculos e "
     "articulações mais flexíveis. Isso diminui o risco de lesões e melhora o desempenho. Também prepara o coração e "
     "a respiração para o esforço maior."),
    ("Por que sentimos cãibra?",
     "A cãibra é uma contração forte e involuntária de um músculo. Ela costuma aparecer com cansaço muscular, esforço "
     "intenso, falta de água ou de alguns minerais, como o potássio e o magnésio, ou por ficar muito tempo na mesma "
     "posição. Alongar o músculo devagar costuma aliviar."),
    ("Por que o futebol é tão popular no Brasil?",
     "O futebol ficou popular no Brasil porque é fácil de jogar: basta uma bola e um espaço, em qualquer rua, campo "
     "de várzea ou praia. Desde o começo do século XX, ele se espalhou pelos bairros e pelas fábricas, e as vitórias "
     "da seleção em Copas do Mundo criaram ídolos e uma enorme paixão nacional."),
    ("Por que o Brasil é tão grande?",
     "O território brasileiro foi se formando durante a colonização. Bandeirantes, missionários, criadores de gado e "
     "exploradores avançaram para o interior, muito além da linha do Tratado de Tordesilhas, e depois tratados com a "
     "Espanha e outros países reconheceram essas áreas. Hoje o Brasil é o quinto maior país do mundo."),
    ("Por que o Nordeste tem secas?",
     "O sertão nordestino tem um clima semiárido, com chuvas poucas e irregulares, concentradas em poucos meses. Isso "
     "acontece por causa da circulação do ar na região, que dificulta a formação de nuvens de chuva, e de fenômenos "
     "como o El Niño, que podem deixar alguns anos ainda mais secos. A evaporação alta piora a falta de água."),
    ("Por que faz frio no Sul do Brasil?",
     "O Sul do Brasil fica mais longe da linha do Equador, então recebe a luz do Sol mais inclinada, principalmente "
     "no inverno. Além disso, a região é atingida por massas de ar polar que vêm do sul do continente. Por isso tem "
     "invernos frios e, em alguns lugares altos, até neve."),
    ("Por que o Rio de Janeiro já foi capital do Brasil?",
     "O Rio de Janeiro virou capital em 1763 porque o porto da cidade era importante para levar o ouro de Minas "
     "Gerais para Portugal. Em 1808, a família real portuguesa se instalou lá, e a cidade continuou como capital do "
     "Império e da República até 1960, quando Brasília foi inaugurada."),
    ("Por que a Amazônia é chamada de pulmão do mundo?",
     "A Amazônia ganhou esse apelido por causa da quantidade enorme de árvores que fazem fotossíntese. Mas os "
     "cientistas explicam que ela consome quase todo o oxigênio que produz, e que a maior parte do oxigênio do "
     "planeta vem das algas dos oceanos. A grande importância da floresta está em guardar carbono, abrigar a "
     "biodiversidade e regular as chuvas."),
    ("Por que o mar é azul?",
     "O mar parece azul porque a água absorve mais as cores de onda longa, como o vermelho, e deixa a luz azul "
     "penetrar e voltar. O reflexo do céu também contribui. Em alguns lugares, algas, areia ou sedimentos deixam a "
     "água esverdeada ou marrom."),
    ("Por que a areia da praia esquenta tanto?",
     "A areia esquenta muito porque absorve bem a luz do Sol e conduz mal o calor para baixo, então a camada de cima "
     "concentra a temperatura. A água do mar, ao contrário, precisa de muito mais energia para esquentar. Por isso, "
     "num dia de sol, a areia queima os pés e a água continua fresca."),
    ("Por que alguns lugares têm terremotos e outros não?",
     "Os terremotos acontecem principalmente nas bordas das placas tectônicas, onde elas se chocam, se afastam ou "
     "deslizam uma ao lado da outra. Países como Japão e Chile ficam nessas bordas. O Brasil fica no meio de uma "
     "placa, por isso os tremores aqui são raros e fracos."),
    ("Por que a Torre de Pisa é inclinada?",
     "A Torre de Pisa, na Itália, começou a inclinar ainda durante a construção, no século XII, porque o solo embaixo "
     "dela é mole, de argila e areia, e a fundação era rasa. Um lado afundou mais que o outro. Obras feitas nas "
     "últimas décadas estabilizaram a torre para ela não cair."),
    ("Por que usamos o calendário com 12 meses?",
     "O calendário que usamos vem dos romanos e foi ajustado ao longo dos séculos, até o calendário gregoriano, de "
     "1582. Os 12 meses têm relação com os ciclos da Lua, que se repetem cerca de 12 vezes por ano. Os dias foram "
     "distribuídos para o ano acompanhar a volta da Terra em torno do Sol."),
    ("Por que o relógio tem 12 horas?",
     "A divisão do dia em 24 horas vem dos antigos egípcios, que dividiam o dia e a noite em 12 partes cada. O número "
     "12 era prático porque pode ser dividido por 2, 3, 4 e 6. Por isso o mostrador do relógio tem 12 horas, e o "
     "ponteiro dá duas voltas por dia."),
    ("Por que as cidades têm trânsito?",
     "O trânsito aparece quando há mais veículos do que as ruas conseguem receber ao mesmo tempo, principalmente nos "
     "horários em que muita gente vai e volta do trabalho e da escola. Cidades que dependem muito do carro, com "
     "pouco transporte público, sofrem mais. Ônibus, metrôs, ciclovias e calçadas boas ajudam a diminuir."),
    ("Por que existe poluição do ar nas cidades?",
     "A poluição do ar nas cidades vem principalmente da fumaça dos carros, caminhões e ônibus, das indústrias e de "
     "queimadas. Esses gases e partículas ficam no ar, principalmente em dias sem vento e sem chuva, e fazem mal à "
     "respiração. Transporte público, carros menos poluentes e áreas verdes ajudam a melhorar o ar."),
    ("Por que as pessoas vão para as cidades?",
     "Muitas pessoas se mudam do campo para as cidades em busca de empregos, escolas, hospitais e mais serviços. Com "
     "as máquinas, o trabalho no campo passou a precisar de menos gente. Esse movimento, chamado êxodo rural, fez as "
     "cidades brasileiras crescerem muito a partir dos anos 1950."),
    ("Por que é importante votar?",
     "Votar é importante porque é a forma de os cidadãos escolherem quem vai governar e fazer as leis numa "
     "democracia. As decisões desses representantes afetam a escola, a saúde, o transporte e muitas outras coisas do "
     "dia a dia. Se informar sobre os candidatos ajuda a escolher melhor."),
    ("Por que precisamos de documentos?",
     "Os documentos, como a certidão de nascimento, o RG e o CPF, comprovam quem a pessoa é e garantem o acesso a "
     "direitos e serviços, como matricular-se na escola, ser atendido no posto de saúde, trabalhar com carteira "
     "assinada, abrir uma conta no banco e votar."),
    ("Por que existem regras na escola?",
     "As regras da escola existem para que todos possam aprender e conviver bem. Elas organizam horários, protegem a "
     "segurança, garantem que cada um tenha sua vez de falar e que todos sejam tratados com respeito. Sem regras, "
     "seria difícil estudar e a convivência seria cheia de conflitos."),
    ("Por que devemos atravessar na faixa de pedestres?",
     "A faixa de pedestres é o lugar onde os motoristas esperam encontrar pessoas atravessando e onde a lei dá "
     "preferência ao pedestre. Atravessar fora dela, no meio dos carros, aumenta muito o risco de atropelamento. "
     "Mesmo na faixa, é bom olhar para os dois lados antes de atravessar."),
    ("Por que as crianças devem andar na cadeirinha do carro?",
     "A cadeirinha protege a criança porque o cinto de segurança comum foi feito para o corpo de um adulto. Numa "
     "freada ou batida, a criança pode escorregar por baixo do cinto ou se machucar com ele. A cadeirinha adequada à "
     "idade e ao peso segura o corpo do jeito certo e reduz muito os ferimentos."),
    ("Por que o celular atrapalha o sono?",
     "O celular atrapalha o sono porque a luz da tela, principalmente a azul, faz o cérebro produzir menos "
     "melatonina, o hormônio que dá sono. Além disso, mensagens, vídeos e jogos deixam a mente agitada. O ideal é "
     "deixar o celular de lado pelo menos uma hora antes de dormir."),
    ("Por que é importante fazer backup?",
     "Fazer backup, uma cópia de segurança dos arquivos, é importante porque celulares e computadores podem quebrar, "
     "ser roubados, pegar vírus ou simplesmente apagar dados por erro. Com a cópia guardada em outro lugar, como um "
     "disco externo ou a nuvem, fotos e documentos não se perdem."),
    ("Por que as senhas não devem ser iguais em todos os sites?",
     "Se você usa a mesma senha em vários sites e um deles sofrer um vazamento, quem conseguir essa senha poderá "
     "tentar entrar em todas as suas outras contas. Usando senhas diferentes, o estrago fica limitado a um lugar só. "
     "Um gerenciador de senhas ajuda a guardar todas."),
    ("Por que os computadores usam números binários?",
     "Os computadores usam o sistema binário, com zeros e uns, porque seus circuitos funcionam com milhões de "
     "pequenos interruptores que só têm dois estados: ligado ou desligado. É mais fácil e confiável distinguir dois "
     "estados do que dez. Combinando muitos zeros e uns, dá para representar números, letras, imagens e sons."),
    ("Por que o avião deixa um rastro branco no céu?",
     "O rastro branco que os aviões deixam lá no alto é feito de pequenos cristais de gelo. Os motores soltam gases "
     "quentes com vapor de água, que, em contato com o ar muito frio da altitude, condensa e congela rapidamente, "
     "como a fumaça que sai da boca num dia frio."),
    ("Por que os ouvidos tampam no avião?",
     "Os ouvidos tampam no avião porque a pressão do ar muda rápido na subida e na descida, e a pressão dentro do "
     "ouvido demora a se igualar. O tímpano fica esticado e a sensação é de ouvido tapado. Engolir, bocejar ou mascar "
     "chiclete ajuda a abrir a tuba auditiva e equilibrar a pressão."),
    ("Por que a gente se sente tonto ao girar?",
     "Dentro do ouvido existem canais com líquido que ajudam no equilíbrio. Quando giramos, o líquido gira junto; "
     "quando paramos, ele continua se movendo por alguns segundos, e o cérebro recebe a informação de que ainda "
     "estamos girando, enquanto os olhos dizem que paramos. Essa confusão causa a tontura."),
    ("Por que algumas pessoas são canhotas?",
     "Ser canhoto ou destro tem relação com a forma como o cérebro se organiza, e isso é influenciado pela genética e "
     "por fatores durante o desenvolvimento antes do nascimento. Cerca de uma em cada dez pessoas é canhota. Ser "
     "canhoto é uma característica natural, e não algo a ser corrigido."),
    ("Por que cada pessoa tem uma voz diferente?",
     "Cada voz é diferente porque depende do tamanho e da forma das cordas vocais, da garganta, da boca e do nariz, "
     "que funcionam como uma caixa de ressonância. O jeito de falar, o sotaque e a respiração também mudam o som. Por "
     "isso reconhecemos as pessoas pela voz."),
    ("Por que a voz dos meninos muda na adolescência?",
     "Na adolescência, os hormônios fazem a laringe crescer e as cordas vocais ficarem mais longas e grossas, "
     "principalmente nos meninos. Cordas vocais maiores vibram mais devagar e produzem um som mais grave. Durante a "
     "mudança, a voz pode falhar e ficar alternando entre fina e grossa."),
    ("Por que temos sotaques diferentes?",
     "Os sotaques surgem porque grupos de pessoas que vivem juntos por muito tempo desenvolvem jeitos próprios de "
     "pronunciar as palavras, influenciados pela história da região, pelos povos que viveram ali e pelo contato com "
     "outras línguas. No Brasil, por isso, há sotaques muito variados, e nenhum é mais certo que o outro."),
    ("Por que as palavras mudam com o tempo?",
     "As palavras mudam porque a língua é viva e é usada por pessoas. Com o tempo, a pronúncia se transforma, surgem "
     "palavras novas para coisas novas, como internet, e outras caem em desuso. Vossa mercê, por exemplo, virou você. "
     "Todas as línguas mudam assim."),
    ("Por que existem tantas palavras de origem tupi no português?",
     "Quando os portugueses chegaram ao Brasil, o tupi era falado por muitos povos do litoral e virou uma língua de "
     "comunicação entre indígenas e colonizadores, chamada língua geral. Por isso muitos nomes de plantas, animais e "
     "lugares vieram do tupi, como abacaxi, jabuti, capim, Ipanema e Piracicaba."),
    ("Por que algumas palavras se escrevem com x e outras com ch?",
     "Hoje o x e o ch muitas vezes têm o mesmo som, mas no passado eram pronunciados de jeitos diferentes. A escrita "
     "manteve a forma de origem das palavras: muitas com ch vêm do latim ou do francês, e muitas com x vêm de línguas "
     "indígenas, africanas ou do árabe. Por isso é preciso memorizar e consultar o dicionário."),
    ("Por que o h não tem som no começo das palavras?",
     "O h no começo de palavras como hoje e homem é uma herança do latim, em que essas palavras já eram escritas com "
     "h. A pronúncia mudou e o som desapareceu, mas a escrita manteve a letra por tradição e para mostrar a origem da "
     "palavra."),
    ("Por que os gatos caem em pé?",
     "Os gatos costumam cair em pé por causa de um reflexo de endireitamento. Durante a queda, eles usam o ouvido "
     "interno para perceber onde é o chão e giram primeiro a cabeça e a parte da frente do corpo, depois a de trás, "
     "graças à coluna muito flexível. Mesmo assim, quedas de lugares altos podem machucá-los."),
    ("Por que os cachorros têm o focinho molhado?",
     "O focinho do cachorro fica úmido porque ele produz um muco fino e também lambe o nariz com frequência. A "
     "umidade ajuda a capturar as partículas de cheiro no ar, melhorando o olfato, que é muito poderoso. Ela também "
     "ajuda um pouco a refrescar o corpo."),
    ("Por que os pássaros cantam?",
     "Os pássaros cantam principalmente para se comunicar: para atrair parceiros, avisar que um território tem dono "
     "e alertar o grupo sobre perigos. Muitos cantam mais de manhã cedo. Em várias espécies, os filhotes aprendem o "
     "canto ouvindo os adultos."),
    ("Por que o galo canta de manhã?",
     "O galo canta de manhã porque tem um relógio biológico interno que acompanha o ciclo de luz do dia. Perto do "
     "amanhecer, ele anuncia o território e sua presença para o grupo. Ele também pode cantar em outros horários, "
     "estimulado por luzes, barulhos ou outros galos."),
    ("Por que as corujas giram tanto a cabeça?",
     "As corujas giram muito a cabeça porque seus olhos, grandes e em forma de tubo, quase não se mexem dentro do "
     "crânio. Para olhar para os lados, elas giram a cabeça, que pode virar cerca de 270 graus graças a um pescoço "
     "com muitas vértebras e vasos sanguíneos adaptados."),
    ("Por que os flamingos são cor-de-rosa?",
     "Os flamingos são cor-de-rosa por causa da alimentação. Eles comem pequenos crustáceos e algas ricos em "
     "pigmentos chamados carotenoides, que vão para as penas. Filhotes nascem acinzentados, e flamingos que comem "
     "pouco desses alimentos ficam mais pálidos."),
    ("Por que os polvos mudam de cor?",
     "Os polvos mudam de cor porque têm na pele milhares de células com pigmentos, controladas pelo sistema nervoso. "
     "Eles abrem e fecham essas células em frações de segundo para se camuflar, assustar predadores ou se comunicar. "
     "Alguns também mudam a textura da pele para imitar pedras e algas."),
    ("Por que o leite é branco?",
     "O leite é branco porque tem pequenas gotas de gordura e proteínas, como a caseína, espalhadas na água. Essas "
     "partículas espalham todas as cores da luz igualmente, e a mistura de todas as cores parece branca."),
    ("Por que a neve é branca?",
     "A neve é feita de muitos cristais de gelo com faces e cantos que refletem e espalham a luz em todas as "
     "direções. Como espalham todas as cores da luz por igual, o conjunto parece branco, embora cada cristal de gelo "
     "seja transparente."),
    ("Por que as nuvens de chuva são escuras?",
     "As nuvens de chuva são escuras porque são muito grossas e cheias de gotas grandes. A luz do Sol não consegue "
     "atravessá-las e é espalhada e absorvida antes de chegar à parte de baixo da nuvem, que fica acinzentada. As "
     "nuvens finas deixam a luz passar e parecem brancas."),
    ("Por que o fogo é quente?",
     "O fogo é quente porque a queima é uma reação química que libera energia. O combustível, como a madeira ou o "
     "gás, reage com o oxigênio do ar e solta calor e luz. Parte desse calor mantém a reação acontecendo, enquanto "
     "houver combustível e oxigênio."),
    ("Por que o algodão-doce derrete na boca?",
     "O algodão-doce é feito de açúcar derretido que a máquina gira e transforma em fios finíssimos, que endurecem no "
     "ar. Como os fios são muito finos e têm pouca massa, a saliva os dissolve quase na hora, e por isso ele derrete "
     "na boca."),
    ("Por que as moedas antigas eram de ouro e prata?",
     "As moedas antigas eram de ouro e prata porque esses metais são raros, bonitos, não enferrujam e podem ser "
     "divididos em pedaços pequenos sem perder valor. Assim, as pessoas confiavam que a moeda tinha valor por si "
     "mesma. Hoje, o valor do dinheiro vem da confiança na moeda do país."),
]
