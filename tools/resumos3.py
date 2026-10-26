"""Resumos escritos à mão (parte 3): resumos dos textos longos de tools/longas5..7.py (passo a passo,
comparações, histórias, animais, lugares e cultura).

Mesmo formato de resumos1.py: pergunta -> (uma frase, duas frases, três tópicos).
"""

RESUMOS = {
    "Como fazer arroz?": (
        "Para o arroz ficar soltinho, lave os grãos, refogue com cebola e alho, cozinhe em duas medidas de água e "
        "deixe descansar antes de servir.",
        "Depois de lavar e refogar o arroz, junte água quente e sal. Cozinhe em fogo baixo até secar e espere cinco "
        "minutos com a panela tampada.",
        ["Lave e refogue o arroz.",
         "Use duas medidas de água para uma de arroz.",
         "Deixe descansar antes de soltar os grãos."]),
    "Como fazer um bolo simples?": (
        "O bolo simples é feito batendo ovos e açúcar, juntando os outros ingredientes e assando a massa por cerca "
        "de 40 minutos.",
        "A massa leva ovos, açúcar, óleo, leite, farinha e fermento, que entra por último. O bolo assa a 180 graus "
        "e está pronto quando o palito sai limpo.",
        ["Bata os ovos com o açúcar.",
         "Coloque o fermento por último.",
         "Teste com um palito antes de tirar do forno."]),
    "Como estudar para uma prova?": (
        "Para ir bem numa prova, comece cedo, estude um pouco todos os dias, pratique com exercícios e durma bem "
        "na véspera.",
        "Dividir a matéria ao longo dos dias funciona melhor do que estudar tudo na última noite. Fazer exercícios "
        "e tentar lembrar sem olhar ajuda a fixar o conteúdo.",
        ["Não deixe para a véspera.",
         "Faça exercícios e resumos próprios.",
         "Durma bem antes da prova."]),
    "Como plantar uma árvore?": (
        "Para plantar uma árvore, escolha uma espécie adequada, prepare uma cova com adubo, plante a muda sem "
        "desmanchar o torrão e regue bem.",
        "É melhor plantar no começo das chuvas, longe de fios e de casas. Depois do plantio, a muda precisa de rega "
        "e de uma estaca para crescer reta.",
        ["Escolha uma espécie nativa.",
         "Plante sem desmanchar o torrão.",
         "Regue nos primeiros meses."]),
    "Como economizar água em casa?": (
        "Dá para economizar muita água com banhos curtos, torneiras fechadas, consertando vazamentos e "
        "reaproveitando água.",
        "No banheiro e na cozinha, o segredo é não deixar a torneira aberta à toa. Usar balde em vez de mangueira e "
        "reaproveitar a água da máquina também ajudam.",
        ["Tome banhos mais curtos.",
         "Conserte os vazamentos.",
         "Reaproveite a água quando puder."]),
    "Como fazer uma boa apresentação na escola?": (
        "Uma boa apresentação exige pesquisar bem, organizar as ideias, usar slides simples e ensaiar antes.",
        "O trabalho precisa ter introdução, desenvolvimento e conclusão, e os slides devem ter pouco texto. Na hora, "
        "fale devagar, olhe para a turma e lembre que a prática diminui o nervosismo.",
        ["Pesquise em fontes confiáveis.",
         "Use slides com pouco texto.",
         "Ensaie em voz alta."]),
    "Como fazer uma redação?": (
        "Uma boa redação nasce de um rascunho organizado em introdução, desenvolvimento e conclusão, com uma "
        "revisão no fim.",
        "Pense na ideia principal, sustente-a com argumentos e exemplos e ligue os parágrafos com conectivos. "
        "Depois, releia procurando erros, e pratique sempre.",
        ["Faça um rascunho antes.",
         "Divida o texto em três partes.",
         "Revise antes de entregar."]),
    "Como cuidar de um cachorro?": (
        "Cuidar de um cachorro exige boa alimentação, veterinário, passeios diários e muito carinho.",
        "O cão precisa de ração adequada, água limpa e vacinas em dia, e não deve comer chocolate nem uva. "
        "Passeios, brinquedos e um treino paciente deixam o animal saudável e feliz.",
        ["Dê ração e água limpa.",
         "Mantenha as vacinas em dia.",
         "Passeie com ele todos os dias."]),
    "Como fazer uma horta em casa?": (
        "Uma horta pode caber numa varanda: basta um lugar com sol, vasos com boa drenagem, terra adubada e plantas "
        "fáceis.",
        "Comece com temperos e verduras simples, como cebolinha e alface, e regue sem encharcar. Com adubo caseiro e "
        "algumas semanas, já dá para colher.",
        ["Escolha um lugar com sol.",
         "Use vasos com furos no fundo.",
         "Comece com plantas fáceis."]),
    "Como ter uma boa noite de sono?": (
        "Para dormir bem, mantenha horários regulares, deixe o quarto escuro e evite telas e café à noite.",
        "A luz das telas atrasa o hormônio do sono, e refeições pesadas atrapalham. Se a insônia for frequente, é "
        "bom procurar um médico.",
        ["Durma e acorde nos mesmos horários.",
         "Evite telas antes de deitar.",
         "Corte o café à noite."]),
    "Como se preparar para uma entrevista de emprego?": (
        "Para uma entrevista, pesquise a empresa, prepare respostas, chegue cedo e seja educado e sincero.",
        "Pense em exemplos que mostrem as habilidades pedidas e leve o currículo. Durante a conversa, ouça com "
        "atenção e, no fim, faça uma pergunta e agradeça.",
        ["Conheça a empresa antes.",
         "Chegue com antecedência.",
         "Responda com sinceridade."]),
    "Como fazer um currículo?": (
        "Um bom currículo é curto e organizado, com contato, objetivo, formação, experiências e habilidades.",
        "Liste as experiências da mais recente para a mais antiga e, sem experiência, inclua projetos e cursos. "
        "Revise os erros e adapte o currículo a cada vaga.",
        ["Use no máximo duas páginas.",
         "Comece pela experiência mais recente.",
         "Adapte para cada vaga."]),
    "Como lidar com o estresse?": (
        "Para lidar com o estresse, descubra a causa, cuide do corpo, descanse e converse com alguém.",
        "O estresse longo causa cansaço e problemas de sono. Dormir bem, fazer exercícios e respirar devagar "
        "ajudam, e um profissional pode ser procurado quando ele estiver forte.",
        ["Identifique o que causa o estresse.",
         "Durma e se exercite.",
         "Peça ajuda se precisar."]),
    "Como fazer amigos numa escola nova?": (
        "Para fazer amigos numa escola nova, seja aberto, puxe conversa, participe de atividades em grupo e tenha "
        "paciência.",
        "Cumprimentar, fazer perguntas e ouvir mostram interesse. As amizades levam tempo, e sendo você mesmo as "
        "pessoas certas se aproximam.",
        ["Sorria e se apresente.",
         "Participe de atividades em grupo.",
         "Amizades levam tempo."]),
    "Como economizar dinheiro?": (
        "Para economizar, anote os gastos, guarde dinheiro assim que receber, evite compras por impulso e fuja de "
        "juros altos.",
        "Pequenos gastos do dia a dia somam muito no fim do mês. Com uma meta e uma reserva, fica mais fácil "
        "enfrentar imprevistos e realizar planos.",
        ["Saiba para onde vai o dinheiro.",
         "Guarde antes de gastar.",
         "Evite o cartão rotativo."]),
    "Como aprender uma língua estrangeira?": (
        "Aprender uma língua exige contato todos os dias, com estudo, músicas, filmes e muita prática de "
        "conversa, sem medo de errar.",
        "Pouco tempo diário funciona melhor que horas uma vez por semana. Ouvir, ler e falar mesmo errando faz o "
        "aprendizado avançar.",
        ["Estude um pouco todos os dias.",
         "Use músicas e filmes.",
         "Fale mesmo errando."]),
    "Como evitar a dengue?": (
        "Para evitar a dengue, acabe com a água parada onde o mosquito põe ovos e proteja-se das picadas.",
        "Uma vez por semana, esvazie pratinhos, tampe caixas-d'água e não deixe pneus na chuva. Repelente e telas "
        "ajudam, e quem tiver febre alta deve procurar atendimento.",
        ["Elimine a água parada.",
         "Tampe caixas-d'água e ralos.",
         "Use repelente."]),
    "Como fazer uma pesquisa escolar?": (
        "Uma boa pesquisa escolar usa fontes confiáveis, é escrita com as próprias palavras e lista as referências.",
        "Primeiro entenda o tema, depois compare informações de livros e sites sérios. Copiar sem citar é plágio, "
        "então escreva o seu texto e revise antes de entregar.",
        ["Use fontes confiáveis.",
         "Escreva com suas palavras.",
         "Liste as referências."]),
    "Como agir em caso de incêndio?": (
        "Num incêndio, saia com segurança, chame os bombeiros pelo 193 e fique perto do chão se houver fumaça.",
        "Teste as portas antes de abrir e use a escada, nunca o elevador. Se a roupa pegar fogo, pare, deite e role, "
        "e jamais volte para buscar objetos.",
        ["Ligue para o 193.",
         "Abaixe-se por causa da fumaça.",
         "Não use o elevador."]),
    "Como organizar o tempo?": (
        "Para organizar o tempo, liste as tarefas, priorize as importantes, use uma agenda e evite distrações.",
        "Dividir tarefas grandes em partes facilita começar, e pausas regulares ajudam a concentração. Revisar o "
        "dia permite ajustar o plano.",
        ["Faça uma lista de tarefas.",
         "Faça uma coisa de cada vez.",
         "Reserve tempo para descansar."]),
    "Como fazer uma vitamina de frutas?": (
        "Para fazer uma vitamina, bata banana e leite no liquidificador, com aveia ou mel se quiser, e sirva logo.",
        "Em um minuto a mistura fica cremosa, e o gelo deixa a bebida mais gelada. Dá para trocar a banana por "
        "outras frutas, e quase nunca é preciso açúcar.",
        ["Use banana madura e leite.",
         "Bata por um minuto.",
         "Sirva logo para não escurecer."]),
    "Como ajudar o meio ambiente no dia a dia?": (
        "Pequenas atitudes, como economizar água e energia, reciclar e usar menos plástico, ajudam o meio ambiente.",
        "Pilhas e óleo devem ter descarte correto, e andar a pé ou de ônibus polui menos. Comprar só o necessário e "
        "conversar sobre o tema também fazem diferença.",
        ["Economize água e energia.",
         "Separe o lixo reciclável.",
         "Use menos plástico descartável."]),
    "Como manter a calma numa discussão?": (
        "Para manter a calma numa discussão, respire fundo, ouça o outro, fale do que sente e busque resolver, não "
        "vencer.",
        "Perceber a raiva subindo ajuda a pedir uma pausa. Evitar acusações e assuntos antigos deixa a conversa "
        "mais tranquila.",
        ["Respire fundo e fale devagar.",
         "Ouça sem interromper.",
         "O objetivo é resolver o problema."]),
    "Qual é a diferença entre vírus e bactéria?": (
        "As bactérias são células vivas que se reproduzem sozinhas, e os vírus só se multiplicam dentro de outras "
        "células, por isso o tratamento é diferente.",
        "Muitas bactérias são úteis e algumas causam doenças, tratadas com antibióticos. Os vírus são menores e "
        "mais simples, não respondem a antibióticos e são prevenidos com vacinas.",
        ["Bactérias são seres de uma célula.",
         "Vírus dependem de outras células.",
         "Antibióticos só funcionam contra bactérias."]),
    "Qual é a diferença entre clima e tempo?": (
        "O tempo é a condição da atmosfera agora, e o clima é o padrão dessa condição ao longo de muitos anos.",
        "O tempo muda de um dia para o outro e aparece na previsão. O clima é medido por médias de décadas, e por "
        "isso um dia frio não muda o clima de uma cidade.",
        ["Tempo é o que acontece agora.",
         "Clima é a média de muitos anos.",
         "Mudança climática se mede em décadas."]),
    "Qual é a diferença entre mamíferos e répteis?": (
        "Os mamíferos têm pelos, sangue quente e amamentam, e os répteis têm escamas, dependem do calor do ambiente "
        "e em geral põem ovos.",
        "Cachorros, baleias e pessoas são mamíferos, e cobras, lagartos e jacarés são répteis. Os répteis tomam sol "
        "para se aquecer, e as aves descendem deles.",
        ["Mamíferos amamentam os filhotes.",
         "Répteis têm escamas.",
         "Répteis dependem do calor do ambiente."]),
    "Qual é a diferença entre cidade e campo?": (
        "A cidade concentra pessoas, comércio e serviços, e o campo tem menos moradores e vive da agricultura e da "
        "pecuária.",
        "A vida na cidade é mais agitada, com mais opções e mais trânsito. O campo é mais tranquilo e produz boa "
        "parte da comida, e os dois dependem um do outro.",
        ["A cidade tem mais serviços.",
         "O campo produz os alimentos.",
         "Um depende do outro."]),
    "Qual é a diferença entre planeta e estrela?": (
        "As estrelas produzem a própria luz pela fusão nuclear, e os planetas só refletem a luz de uma estrela.",
        "Uma estrela como o Sol é uma enorme bola de gás, e os planetas giram em volta dela. No céu, as estrelas "
        "costumam piscar, e os planetas brilham de forma mais firme.",
        ["Estrelas têm luz própria.",
         "Planetas giram em torno de estrelas.",
         "Estrelas piscam no céu, planetas não."]),
    "Qual é a diferença entre um vírus de computador e um vírus biológico?": (
        "O vírus biológico é uma partícula natural que infecta células, e o de computador é um programa feito de "
        "propósito para causar estragos.",
        "Os dois se espalham, mas um causa doenças e o outro apaga arquivos ou rouba senhas. Para se proteger do "
        "vírus de computador, use antivírus e evite links suspeitos.",
        ["Um é natural e o outro é um programa.",
         "O de computador rouba dados e apaga arquivos.",
         "Um não passa para o outro."]),
    "Conte uma história sobre uma cadela que foi ao espaço.": (
        "A história conta como Laika, uma cadela das ruas de Moscou, foi levada ao espaço e, mesmo sem voltar, "
        "ajudou os astronautas que vieram depois.",
        "Cientistas escolheram a cadelinha calma e corajosa e a lançaram numa cápsula. Laika não voltou, mas a "
        "viagem ensinou como sobreviver no espaço.",
        ["Laika vivia nas ruas de Moscou.",
         "Foi lançada ao espaço numa cápsula.",
         "Sua viagem ajudou os futuros astronautas."]),
    "Conte uma história sobre um menino que queria voar.": (
        "Pedro sonhava em voar, caiu ao pular com asas de papelão, estudou aviões e acabou virando engenheiro.",
        "Em vez de desistir depois da queda, ele leu sobre os pioneiros da aviação e testou aviõezinhos de madeira. "
        "Anos depois, projetava aviões de verdade.",
        ["Pedro queria muito voar.",
         "A queda o levou aos livros.",
         "Ele se tornou engenheiro."]),
    "Escreva uma história sobre uma tartaruga que precisava atravessar um rio.": (
        "A tartaruga Lúcia atravessou um rio que todos achavam impossível para ela, mostrando que paciência vale "
        "mais que velocidade.",
        "Ela observou o rio por dias e descobriu a hora mais calma e as pedras para descansar. Assim chegou ao "
        "outro lado e surpreendeu os outros animais.",
        ["Lúcia precisava das frutas do outro lado.",
         "Ela estudou o rio antes de tentar.",
         "Paciência a levou longe."]),
    "Conte uma história sobre uma menina que plantou um jardim.": (
        "Ana começou a limpar sozinha um terreno abandonado, e os vizinhos se juntaram até ele virar uma horta "
        "comunitária.",
        "Aos poucos, cada pessoa trouxe uma ajuda, como uma pá, mudas ou adubo. A horta uniu os moradores, que "
        "passaram a se encontrar ali todo fim de tarde.",
        ["Ana começou com um saco de lixo.",
         "Os vizinhos foram ajudando.",
         "O terreno virou um ponto de encontro."]),
    "Escreva uma história sobre um robô que aprendeu a ser amigo.": (
        "O robô Bento, que sabia muitos fatos mas não entendia sentimentos, aprendeu com Clara que às vezes ajudar "
        "é só ouvir.",
        "Quando Clara chegou triste, Bento ofereceu soluções, mas ela queria companhia. Ao ficar em silêncio e "
        "prestar atenção, ele ganhou uma amiga.",
        ["Bento não entendia as emoções.",
         "Clara só queria ser ouvida.",
         "Estar presente também é ajudar."]),
    "Conte uma história sobre um pescador numa tempestade.": (
        "O pescador Raimundo foi pego por uma tempestade, manteve a calma, esperou passar e voltou para casa guiado "
        "pelas estrelas.",
        "Mesmo vendo nuvens escuras, ele saiu para pescar e ficou sem ver a praia. Lembrando os conselhos do pai, "
        "teve paciência e, à noite, foi recebido pela família.",
        ["Raimundo pescava havia quarenta anos.",
         "Ele esperou a tempestade passar.",
         "Voltou guiado pelas estrelas."]),
    "Conte a história do nome deste projeto.": (
        "O projeto se chama Laika em homenagem à cadela que foi o primeiro animal em órbita, um símbolo de "
        "coragem e de pioneirismo.",
        "Laika viajou no Sputnik 2 em 1957 e não voltou, mas abriu caminho para os astronautas. O modelo também se "
        "vê como uma pequena pioneira, treinada do zero em português.",
        ["O nome homenageia a cadela Laika.",
         "Ela foi a primeira a orbitar a Terra.",
         "O nome lembra coragem e curiosidade."]),
    "Como são os gatos?": (
        "Os gatos são caçadores ágeis, domesticados há milhares de anos, que dormem muito e se comunicam com "
        "miados e com o corpo.",
        "Eles enxergam bem com pouca luz, têm garras retráteis e são muito limpos. Para viver bem, precisam de "
        "ração, água, caixa de areia e vacinas.",
        ["Gatos protegiam os celeiros dos ratos.",
         "Dormem de 12 a 16 horas por dia.",
         "São limpos e independentes."]),
    "O que você sabe sobre os cavalos?": (
        "Os cavalos, domesticados há cerca de cinco mil anos, transformaram o transporte e o trabalho humano.",
        "Eles têm visão quase panorâmica e conseguem dormir em pé. Hoje são usados no campo, em esportes e em "
        "terapias como a equoterapia.",
        ["Mudaram a história do transporte.",
         "Dormem em pé.",
         "Vivem em grupo e comem capim."]),
    "Como vivem os elefantes?": (
        "Os elefantes são os maiores animais terrestres, vivem em famílias lideradas por uma matriarca e estão "
        "ameaçados pela caça.",
        "A tromba serve para respirar, beber, comer e cumprimentar. Eles são muito inteligentes e têm ótima "
        "memória, mas sofrem com a caça pelo marfim.",
        ["Há elefantes africanos e asiáticos.",
         "A matriarca guia o grupo.",
         "A caça pelo marfim os ameaça."]),
    "Como vivem os pinguins?": (
        "Os pinguins são aves que não voam, mas nadam muito bem, e vivem quase todos no hemisfério sul.",
        "Penas impermeáveis e gordura os protegem do frio, e eles comem peixes e krill. Muitos vivem em colônias, e "
        "alguns aparecem no Brasil no inverno.",
        ["As asas viraram nadadeiras.",
         "Vivem principalmente na Antártida.",
         "O casal se reveza para chocar o ovo."]),
    "Como são as baleias?": (
        "As baleias são mamíferos marinhos enormes, que respiram ar e fazem longas migrações, e hoje são protegidas.",
        "A baleia-azul é o maior animal que já existiu. A jubarte viaja da Antártida até Abrolhos para se "
        "reproduzir, e a caça quase acabou com várias espécies.",
        ["Baleias respiram com pulmões.",
         "A baleia-azul é o maior animal do mundo.",
         "Muitas migram por milhares de quilômetros."]),
    "O que você sabe sobre os girassóis?": (
        "O girassol é uma planta de flor grande e amarela, formada por centenas de florzinhas, que dá sementes e "
        "óleo.",
        "Quando jovem, ele acompanha o Sol durante o dia e, adulto, fica virado para o leste. Suas sementes "
        "alimentam pessoas e animais, e ele atrai abelhas.",
        ["A flor é um conjunto de pequenas flores.",
         "O girassol jovem segue o Sol.",
         "As sementes viram óleo."]),
    "O que são as Cataratas do Iguaçu?": (
        "As Cataratas do Iguaçu são um dos maiores conjuntos de quedas-d'água do mundo, na fronteira entre o Brasil "
        "e a Argentina.",
        "São cerca de 275 quedas, e a maior é a Garganta do Diabo. Ficam em parques nacionais de Mata Atlântica e "
        "são patrimônio natural da humanidade.",
        ["Têm cerca de 275 quedas.",
         "A Garganta do Diabo é a mais forte.",
         "Ficam perto da usina de Itaipu."]),
    "O que são os Lençóis Maranhenses?": (
        "Os Lençóis Maranhenses são um parque de dunas brancas no Maranhão que, com as chuvas, se enche de lagoas "
        "azuis e verdes.",
        "O vento forma as dunas com a areia da praia. Na época das chuvas surgem milhares de lagoas, visitadas "
        "principalmente entre junho e setembro.",
        ["As dunas parecem um lençol.",
         "A chuva forma lagoas entre elas.",
         "O parque atrai turistas do mundo todo."]),
    "O que você sabe sobre a cidade do Rio de Janeiro?": (
        "O Rio de Janeiro, antiga capital do Brasil, é famoso pelas paisagens entre o mar e as montanhas, pelo "
        "carnaval e pela música.",
        "A cidade tem o Cristo Redentor, o Pão de Açúcar, praias conhecidas e uma enorme floresta urbana. Como "
        "outras metrópoles, enfrenta desigualdade e violência.",
        ["Foi capital até 1960.",
         "Tem o Cristo Redentor e o Pão de Açúcar.",
         "É conhecida pelo samba e pelo carnaval."]),
    "O que você sabe sobre Salvador?": (
        "Salvador foi a primeira capital do Brasil e é um dos maiores centros da cultura afro-brasileira.",
        "A cidade tem a Cidade Alta e a Cidade Baixa, ligadas pelo Elevador Lacerda, e o Pelourinho histórico. O "
        "carnaval com trios elétricos é um dos maiores do mundo.",
        ["Foi capital de 1549 a 1763.",
         "O Pelourinho é patrimônio mundial.",
         "A cultura afro-brasileira é muito forte lá."]),
    "O que são os eclipses?": (
        "Um eclipse acontece quando um astro entra na sombra de outro: no solar, a Lua esconde o Sol, e no lunar, "
        "a Terra faz sombra na Lua.",
        "O eclipse solar só pode ser visto com filtros especiais. No eclipse lunar total, a Lua fica avermelhada e "
        "pode ser observada a olho nu.",
        ["No eclipse solar, a Lua tapa o Sol.",
         "No lunar, a Terra faz sombra na Lua.",
         "Só o lunar pode ser visto sem proteção."]),
    "Como se formam os relâmpagos?": (
        "Os relâmpagos são descargas elétricas enormes que surgem quando as cargas se separam dentro das nuvens de "
        "tempestade.",
        "Gelo e gotas se chocam e separam cargas, até que a diferença provoca a descarga. O ar aquecido se expande "
        "e faz o trovão, e o lugar seguro é dentro de casa ou de um carro.",
        ["As cargas se separam nas nuvens.",
         "O raio é a descarga que chega ao chão.",
         "O trovão vem do ar que se expande."]),
    "Como funciona a energia nuclear?": (
        "A energia nuclear vem da divisão de átomos de urânio, cujo calor gera vapor e eletricidade, quase sem "
        "gás carbônico.",
        "A fissão libera calor numa reação em cadeia controlada. A desvantagem é o lixo radioativo e o risco de "
        "acidentes, e o Brasil tem duas usinas em Angra dos Reis.",
        ["A fissão divide os núcleos de urânio.",
         "Quase não emite gás carbônico.",
         "Gera lixo radioativo."]),
    "O que são os átomos?": (
        "Os átomos são as partículas minúsculas que formam toda a matéria, com prótons e nêutrons no núcleo e "
        "elétrons em volta.",
        "O número de prótons define o elemento químico, e há pouco mais de cem na tabela periódica. Os átomos se "
        "unem em moléculas, como a da água.",
        ["Tudo é feito de átomos.",
         "Os prótons definem o elemento.",
         "Átomos formam moléculas."]),
    "Como funciona o GPS?": (
        "O GPS descobre a posição de um aparelho calculando a distância até vários satélites pelo tempo que os "
        "sinais levam para chegar.",
        "Cada satélite envia a hora exata e a sua posição, e o receptor precisa de pelo menos quatro sinais. O "
        "sistema é usado em mapas, entregas, aviões e na agricultura.",
        ["Satélites enviam sinais com a hora.",
         "São necessários quatro satélites.",
         "Os relógios precisam ser muito precisos."]),
    "Como funcionam os carros elétricos?": (
        "Os carros elétricos andam com motores movidos a bateria, não soltam fumaça, mas ainda têm baterias caras "
        "e recarga demorada.",
        "As baterias são carregadas na tomada ou em estações. Com eletricidade limpa, eles ajudam o clima, embora a "
        "extração de minerais como o lítio cause impactos.",
        ["O motor usa energia da bateria.",
         "Não há fumaça no escapamento.",
         "Baterias caras são um desafio."]),
    "O que é a festa junina?": (
        "A festa junina é uma celebração de junho, vinda de Portugal, com fogueira, quadrilha, forró e comidas de "
        "milho.",
        "Ela homenageia santos como São João e é muito forte no Nordeste. Tem bandeirinhas, brincadeiras e comidas "
        "como pamonha, canjica e pé de moleque.",
        ["Homenageia santos de junho.",
         "É muito forte no Nordeste.",
         "As comidas são feitas de milho."]),
    "O que é a capoeira?": (
        "A capoeira é uma mistura de luta, dança e música criada por africanos escravizados no Brasil como forma "
        "de resistência.",
        "Na roda, dois jogadores fazem movimentos ao som do berimbau, enquanto os outros cantam. Antes perseguida, "
        "hoje ela é patrimônio da humanidade.",
        ["Nasceu como resistência.",
         "É jogada ao som do berimbau.",
         "Tem os estilos angola e regional."]),
    "O que é a literatura de cordel?": (
        "O cordel é uma poesia popular do Nordeste, em versos rimados, vendida em folhetos ilustrados com "
        "xilogravura.",
        "O nome vem dos cordões em que os folhetos eram pendurados nas feiras. As histórias falam de amor, "
        "cangaceiros e fatos do dia a dia, muitas vezes com humor.",
        ["Os folhetos ficavam pendurados em cordões.",
         "Os versos são rimados.",
         "É patrimônio cultural do Brasil."]),
    "Qual é a história do samba?": (
        "O samba nasceu de ritmos africanos, ganhou forma no Rio de Janeiro no começo do século XX e virou símbolo "
        "do Brasil.",
        "Ele se formou em encontros de músicos em casas como a de Tia Ciata, e Pelo Telefone foi o primeiro samba "
        "gravado. Com o rádio e o carnaval, espalhou-se em várias formas.",
        ["Tem raízes africanas.",
         "Pelo Telefone, de 1916, foi o primeiro gravado.",
         "Tem formas como o samba-enredo e o pagode."]),
    "O que é a empatia?": (
        "Empatia é se colocar no lugar do outro para entender o que ele sente, mesmo sem concordar com tudo.",
        "Ela se desenvolve ouvindo sem julgar e conhecendo outras realidades. É essencial para as amizades, o "
        "trabalho em equipe e uma sociedade com menos preconceito.",
        ["Empatia é entender o que o outro sente.",
         "Ouvir com atenção a desenvolve.",
         "Ela reduz conflitos."]),
    "O que é o trabalho voluntário?": (
        "O trabalho voluntário é ajudar sem receber salário, e faz bem tanto a quem recebe quanto a quem participa.",
        "Ele acontece em hospitais, abrigos, ONGs e campanhas. Quem participa conhece outras realidades, faz "
        "amizades e desenvolve habilidades.",
        ["É feito por vontade própria.",
         "Ajuda pessoas, animais e o ambiente.",
         "Exige compromisso."]),
    "O que são os marsupiais?": (
        "Os marsupiais são mamíferos cujos filhotes nascem pequenos e crescem numa bolsa da mãe, como o canguru e "
        "o gambá.",
        "Muitos vivem na Austrália, mas o gambá é comum no Brasil, inclusive nas cidades. Ele é útil porque come "
        "insetos e escorpiões.",
        ["Os filhotes crescem no marsúpio.",
         "Canguru e coala são marsupiais.",
         "O gambá brasileiro também é."]),
    "O que são os corais?": (
        "Os corais são animais marinhos que formam recifes cheios de vida e estão ameaçados pelo aquecimento da água.",
        "Eles vivem com algas que lhes dão alimento e cor e, ao longo de milhares de anos, formam os recifes. Com a "
        "água quente, expulsam as algas e ficam brancos, o que pode matá-los.",
        ["Corais são animais, não pedras.",
         "Formam recifes com muitos peixes.",
         "O branqueamento os ameaça."]),
}
