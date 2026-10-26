"""Resumos escritos à mão (parte 4): textos novos, de tipos que os textos longos não têm (notícias de bairro,
cartas, avisos, relatos, opiniões, crônicas), cada um com três resumos.

Cada item: (texto, resumo em uma frase, resumo curto em duas frases, três tópicos). As pessoas e os lugares
pequenos são inventados; os fatos gerais são verdadeiros. Os textos têm de 80 a 150 palavras, para o resumo
ter o que cortar.
"""

TEXTOS = [
    ("A biblioteca do bairro Santa Luzia reabriu na segunda-feira depois de seis meses fechada para reforma. O "
     "prédio, construído na década de 1970, tinha goteiras e problemas na fiação elétrica. Agora, ganhou telhado "
     "novo, rampas de acesso para cadeiras de rodas e uma sala infantil com tapetes e almofadas.\n\n"
     "O acervo também cresceu: foram doados cerca de dois mil livros por moradores e por uma editora da região. A "
     "bibliotecária Marta Silveira conta que a procura no primeiro dia surpreendeu. \"Tinha fila na porta antes de "
     "abrirmos\", disse. A biblioteca funciona de segunda a sábado, das 8h às 18h, e o cadastro para empréstimo é "
     "gratuito, bastando apresentar um documento e um comprovante de endereço.",
     "A biblioteca do bairro Santa Luzia reabriu reformada, mais acessível e com mais livros, e atraiu muita gente "
     "logo no primeiro dia.",
     "Depois de seis meses de obras, o prédio ganhou telhado novo, rampas e uma sala infantil. Os moradores e uma "
     "editora doaram cerca de dois mil livros, e o cadastro para empréstimo é gratuito.",
     ["A biblioteca reabriu após seis meses de reforma.",
      "Ganhou acessibilidade, sala infantil e dois mil livros.",
      "O empréstimo é gratuito."]),
    ("Querida vó,\n\nEstou com saudade das suas tardes de bolo de fubá. Aqui na cidade grande tudo é corrido: acordo "
     "às seis, pego dois ônibus até a faculdade e só volto à noite. Mas estou gostando muito do curso de "
     "enfermagem. Nesta semana, fizemos a primeira aula prática no laboratório e aprendi a medir a pressão.\n\n"
     "Dividi o apartamento com duas colegas, a Júlia e a Renata, e nos revezamos para cozinhar. Ainda não acertei "
     "o ponto do seu arroz, mas estou tentando. Nas férias de julho vou passar uns dias aí. Guarde um pedaço de "
     "bolo para mim e dê um abraço no vô.\n\nCom carinho,\nBeatriz",
     "Na carta, Beatriz conta à avó que está gostando da faculdade de enfermagem na cidade grande e promete "
     "visitá-la nas férias.",
     "Beatriz sente saudade da avó e descreve a rotina corrida, a primeira aula prática e o apartamento dividido "
     "com duas colegas. Ela diz que vai visitar os avós em julho.",
     ["Beatriz estuda enfermagem na cidade grande.",
      "Divide o apartamento com duas colegas.",
      "Vai visitar a avó nas férias de julho."]),
    ("Atenção, moradores do Condomínio Primavera: na próxima quinta-feira, dia 14, o fornecimento de água será "
     "interrompido das 9h às 15h para a limpeza das duas caixas-d'água do prédio. A limpeza é obrigatória e deve "
     "ser feita a cada seis meses, para garantir a qualidade da água.\n\n"
     "Pedimos que todos guardem água em baldes ou garrafas para as necessidades do dia e evitem usar a máquina de "
     "lavar na manhã seguinte, porque a água pode sair turva nas primeiras horas. Em caso de dúvida, procure a "
     "portaria. Agradecemos a compreensão.\n\nA administração",
     "O condomínio avisa que a água será cortada na quinta-feira, das 9h às 15h, para a limpeza obrigatória das "
     "caixas-d'água.",
     "Os moradores devem guardar água para o dia e evitar a máquina de lavar na manhã seguinte, quando a água "
     "pode sair turva. A limpeza é feita a cada seis meses.",
     ["A água será cortada na quinta, das 9h às 15h.",
      "O motivo é a limpeza das caixas-d'água.",
      "É bom guardar água antes."]),
    ("No sábado passado, fui com meus pais e meu irmão até a Chapada dos Veadeiros, em Goiás. Saímos de Brasília "
     "ainda de madrugada e chegamos a Alto Paraíso a tempo do café da manhã. Depois, seguimos para uma trilha de "
     "uns cinco quilômetros até uma cachoeira.\n\n"
     "O caminho tinha subidas cansativas e muitas pedras, e meu irmão reclamou o tempo todo. Mas, quando chegamos, "
     "a vista compensou tudo: a água caía de um paredão enorme num poço verde e gelado. Ficamos lá quase duas "
     "horas, nadando e fazendo piquenique. Na volta, vimos um lobo-guará atravessando a estrada. Foi o melhor "
     "passeio do ano.",
     "O narrador conta um passeio em família à Chapada dos Veadeiros, com uma trilha cansativa até uma cachoeira "
     "linda e um lobo-guará na volta.",
     "A família saiu de madrugada de Brasília e caminhou cerca de cinco quilômetros até a cachoeira. Apesar das "
     "reclamações do irmão, todos aproveitaram o poço gelado e o piquenique.",
     ["A família foi à Chapada dos Veadeiros.",
      "A trilha foi difícil, mas a cachoeira compensou.",
      "Na volta, viram um lobo-guará."]),
    ("Muita gente acha que ler é perda de tempo, já que hoje existem vídeos sobre quase tudo. Eu discordo. Um vídeo "
     "pode até explicar um assunto depressa, mas a leitura exige atenção e faz o leitor imaginar, comparar e "
     "tirar as próprias conclusões.\n\n"
     "Além disso, quem lê com frequência escreve melhor, porque aprende palavras novas e vê como os bons textos são "
     "organizados. Ler também ajuda a entender pessoas diferentes: num romance, passamos horas dentro da cabeça de "
     "outra pessoa. Não é preciso começar com livros difíceis. Quadrinhos, contos curtos e reportagens já são um "
     "bom caminho. O importante é criar o hábito.",
     "O autor defende que a leitura continua importante, porque exige atenção, melhora a escrita e ajuda a "
     "entender outras pessoas.",
     "Para ele, os vídeos explicam rápido, mas a leitura faz pensar e imaginar. Quem quer começar pode escolher "
     "quadrinhos e contos, desde que crie o hábito.",
     ["Ler exige atenção e estimula a imaginação.",
      "Quem lê escreve melhor.",
      "Dá para começar com textos simples."]),
    ("A feira de ciências da Escola Estadual Monteiro Lobato reuniu mais de quarenta trabalhos nesta sexta-feira. "
     "Os alunos do 6º ao 9º ano apresentaram experiências sobre energia, plantas, reciclagem e o corpo humano. O "
     "trabalho mais visitado foi um forno solar feito com caixa de papelão, papel-alumínio e vidro, que conseguiu "
     "derreter queijo em vinte minutos.\n\n"
     "O primeiro lugar, porém, ficou com um grupo do 8º ano que mediu a quantidade de lixo produzida na cantina e "
     "propôs uma composteira para os restos de comida. A direção prometeu colocar a ideia em prática no próximo "
     "semestre. Os três primeiros colocados vão representar a escola na feira regional, em novembro.",
     "Na feira de ciências da escola, um projeto de composteira para os restos da cantina venceu, e os três "
     "primeiros vão para a feira regional.",
     "Os alunos apresentaram mais de quarenta trabalhos, e o forno solar de papelão foi o mais visitado. A direção "
     "prometeu adotar a composteira do grupo vencedor.",
     ["A feira teve mais de quarenta trabalhos.",
      "A composteira para a cantina ganhou.",
      "Os melhores vão à feira regional em novembro."]),
    ("Olá, pessoal! Como combinado na última reunião, o mutirão de limpeza da praça do bairro vai acontecer neste "
     "domingo, a partir das 8h. Vamos recolher o lixo, pintar os bancos e plantar mudas de ipê doadas pela "
     "prefeitura.\n\n"
     "Quem puder, traga luvas, sacos de lixo e uma garrafa de água. As tintas e os pincéis já foram comprados com "
     "o dinheiro da rifa. Crianças são bem-vindas, desde que acompanhadas. Às 11h, vamos fazer um lanche "
     "coletivo, então cada um pode levar alguma coisa para dividir. Se chover, o mutirão fica para o domingo "
     "seguinte. Contamos com vocês!",
     "A mensagem convida os moradores para um mutirão de limpeza da praça no domingo, com pintura dos bancos, "
     "plantio de ipês e lanche coletivo.",
     "Os participantes devem levar luvas, sacos e água, já que as tintas foram compradas com o dinheiro da rifa. "
     "Se chover, o mutirão passa para a semana seguinte.",
     ["O mutirão é no domingo, às 8h.",
      "Vão limpar, pintar bancos e plantar ipês.",
      "Cada um pode levar algo para o lanche."]),
    ("Quando eu era criança, a rua onde eu morava era o nosso parque. Não havia muitos carros, e as crianças "
     "passavam a tarde jogando bola, pulando corda e brincando de esconde-esconde até as mães chamarem para o "
     "jantar. O asfalto quente queimava os pés, e um poste servia de trave.\n\n"
     "Hoje, passo pela mesma rua e vejo carros estacionados dos dois lados e quase nenhuma criança. Elas estão "
     "dentro de casa, muitas vezes com um celular nas mãos. Não acho que antigamente era tudo melhor, mas sinto "
     "falta daquele tempo em que a vizinhança inteira se conhecia pelo nome e a rua era de todos.",
     "O autor lembra com saudade a infância em que as crianças brincavam na rua e lamenta que hoje elas fiquem "
     "dentro de casa.",
     "Antes, a rua servia de parque, com bola, corda e esconde-esconde. Hoje está cheia de carros, e ele sente "
     "falta da vizinhança que se conhecia.",
     ["A rua era o lugar de brincar.",
      "Hoje há carros e poucas crianças fora de casa.",
      "Ele sente falta da convivência entre vizinhos."]),
    ("Prezados pais e responsáveis,\n\nInformamos que, a partir do dia 3 de março, o horário de entrada do turno da "
     "manhã passará a ser às 7h30, e não mais às 7h. A mudança atende a um pedido de muitas famílias, que "
     "relataram dificuldade com o transporte no início da manhã, e também à recomendação de especialistas, que "
     "apontam que adolescentes rendem mais quando dormem um pouco mais.\n\n"
     "Com isso, a saída será às 12h20. O portão continuará abrindo quinze minutos antes da entrada. Pedimos atenção "
     "ao novo horário para evitar atrasos. Dúvidas podem ser enviadas à secretaria.\n\nAtenciosamente,\nA direção",
     "A escola avisa que, a partir de 3 de março, as aulas da manhã começarão às 7h30 e terminarão às 12h20.",
     "A mudança atende às famílias que tinham problemas com o transporte e à ideia de que adolescentes rendem "
     "mais dormindo mais. O portão continua abrindo quinze minutos antes.",
     ["A entrada passa das 7h para as 7h30.",
      "A saída será às 12h20.",
      "O motivo é o transporte e o sono dos alunos."]),
    ("O pequeno município de Serra Azul viveu um domingo agitado com a primeira corrida de rua da sua história. "
     "Cerca de 600 pessoas participaram da prova, que teve percursos de cinco e dez quilômetros pelas ruas do "
     "centro e pela estrada de terra que leva à represa.\n\n"
     "O vencedor dos dez quilômetros foi um agricultor de 34 anos que treina correndo entre as plantações de café. "
     "Entre as mulheres, venceu uma professora de educação física da cidade vizinha. O dinheiro das inscrições foi "
     "doado ao hospital municipal, que vai comprar duas cadeiras de rodas e um aparelho de pressão. A prefeitura "
     "já fala em repetir a corrida no ano que vem.",
     "A primeira corrida de rua de Serra Azul reuniu cerca de 600 pessoas e arrecadou dinheiro para o hospital "
     "municipal.",
     "A prova teve percursos de cinco e dez quilômetros, e um agricultor venceu a mais longa. As inscrições vão "
     "comprar equipamentos para o hospital, e a corrida deve se repetir.",
     ["Foi a primeira corrida da cidade.",
      "Participaram cerca de 600 pessoas.",
      "As inscrições foram doadas ao hospital."]),
    ("— Mãe, posso ter um cachorro?\n— Quem vai passear com ele todo dia?\n— Eu! Prometo.\n— E quem vai limpar "
     "quando ele fizer xixi na sala?\n— Eu também.\n— E nas férias, quando a gente viajar?\n— A vó pode cuidar. Ela "
     "adora bicho.\n\n"
     "A mãe ficou em silêncio por um tempo, olhando para o filho. Depois disse que ia pensar, mas que ele "
     "precisaria mostrar responsabilidade antes. Combinaram que, durante um mês, o menino arrumaria a cama e "
     "regaria as plantas sem que ninguém mandasse. Se conseguisse, no fim do mês iriam juntos a uma feira de "
     "adoção.",
     "Um menino pede um cachorro, e a mãe combina que ele só poderá adotar um se mostrar responsabilidade durante "
     "um mês.",
     "O filho promete passear e limpar, e a mãe pergunta sobre cada cuidado. Se ele arrumar a cama e regar as "
     "plantas sozinho por um mês, os dois vão a uma feira de adoção.",
     ["O menino quer um cachorro.",
      "A mãe pede uma prova de responsabilidade.",
      "Se ele cumprir o combinado, vão adotar um."]),
    ("O preço do tomate subiu quase 40% nas feiras da cidade neste mês. Segundo os comerciantes, as chuvas fortes "
     "de janeiro estragaram parte das plantações nas regiões produtoras, e a oferta diminuiu. Uma caixa que custava "
     "80 reais no atacado agora sai por mais de 110.\n\n"
     "Os feirantes contam que muitos clientes estão comprando menos ou trocando o tomate por outros legumes. "
     "Especialistas dizem que a alta deve ser passageira: com o fim das chuvas e a chegada de novas colheitas, os "
     "preços tendem a cair em dois ou três meses. Até lá, a dica é aproveitar os legumes da estação, que estão "
     "mais baratos.",
     "O tomate ficou quase 40% mais caro porque as chuvas estragaram plantações, mas o preço deve cair em alguns "
     "meses.",
     "Com menos tomate disponível, a caixa no atacado passou de 80 para mais de 110 reais. Os clientes compram "
     "menos, e a sugestão é preferir legumes da estação até a nova colheita.",
     ["O tomate subiu quase 40%.",
      "A causa foram as chuvas de janeiro.",
      "A alta deve ser passageira."]),
    ("Seu Joaquim tem 82 anos e, todas as manhãs, abre a pequena oficina de consertos que mantém há mais de "
     "cinquenta anos no centro da cidade. Ali ele conserta rádios, liquidificadores, ventiladores e até "
     "máquinas de costura antigas que ninguém mais sabe arrumar.\n\n"
     "Ele aprendeu o ofício com o pai, que também era consertador. Diz que hoje o movimento é menor, porque as "
     "pessoas preferem comprar um aparelho novo a consertar o velho. Mesmo assim, não pensa em parar. \"Jogar fora "
     "uma coisa que ainda tem jeito me dói\", explica. Nos últimos anos, alguns jovens começaram a visitar a oficina "
     "para aprender, e ele ensina de graça.",
     "Seu Joaquim, de 82 anos, mantém há mais de cinquenta anos uma oficina de consertos e agora ensina o ofício "
     "a jovens de graça.",
     "Ele aprendeu com o pai a consertar aparelhos de todo tipo. Mesmo com menos clientes, continua trabalhando, "
     "porque acha errado jogar fora o que ainda tem conserto.",
     ["Seu Joaquim conserta aparelhos há mais de cinquenta anos.",
      "Hoje as pessoas preferem comprar coisas novas.",
      "Ele ensina jovens sem cobrar."]),
    ("Uso de protetor solar não é só coisa de praia. Os raios ultravioleta do Sol chegam à pele mesmo em dias "
     "nublados e também quando estamos andando na rua, esperando o ônibus ou dirigindo. Com o tempo, essa "
     "exposição causa manchas, envelhecimento precoce e aumenta o risco de câncer de pele, o tipo de câncer mais "
     "comum no Brasil.\n\n"
     "Os dermatologistas recomendam usar protetor com fator de proteção 30 ou mais todos os dias, aplicando cerca "
     "de vinte minutos antes de sair e reaplicando a cada duas horas quando houver suor ou contato com água. "
     "Chapéu, óculos escuros e evitar o sol forte entre as 10h e as 16h completam a proteção.",
     "O texto explica que o protetor solar deve ser usado todos os dias, e não só na praia, para proteger a pele "
     "dos raios ultravioleta.",
     "O sol causa manchas e câncer de pele mesmo em dias nublados. Os médicos indicam fator 30 ou mais, "
     "reaplicação e cuidados como chapéu e evitar o sol do meio do dia.",
     ["Os raios UV agem até em dias nublados.",
      "Use fator 30 ou mais todos os dias.",
      "Evite o sol entre as 10h e as 16h."]),
    ("A pequena padaria da dona Cida, no bairro da Vila Nova, ficou famosa nas redes sociais depois que uma cliente "
     "publicou um vídeo do pão de queijo saindo do forno. Em uma semana, o vídeo foi visto mais de um milhão de "
     "vezes, e a fila começou a dobrar a esquina.\n\n"
     "Dona Cida, que faz a receita da mãe há trinta anos, precisou chamar a filha e dois sobrinhos para ajudar. "
     "Antes, assava cerca de 300 pães de queijo por dia; agora são mais de mil. Ela conta que está feliz, mas "
     "cansada, e que não pretende mudar a receita nem abrir filiais. \"O segredo é o queijo da minha terra e o "
     "tempo certo no forno\", diz.",
     "A padaria da dona Cida ficou famosa depois que um vídeo do seu pão de queijo viralizou, e a produção mais "
     "que triplicou.",
     "O vídeo passou de um milhão de visualizações, e a fila começou a dobrar a esquina. A família foi chamada "
     "para ajudar, mas dona Cida não quer mudar a receita nem abrir filiais.",
     ["Um vídeo tornou a padaria famosa.",
      "A produção subiu de 300 para mais de mil pães por dia.",
      "A receita da família continua a mesma."]),
    ("Na última reunião do conselho da escola, os alunos apresentaram uma proposta para proibir o uso de "
     "celulares durante o intervalo. Segundo eles, muitos colegas passavam os vinte minutos olhando para a tela, "
     "sem conversar nem brincar. A ideia era guardar os aparelhos numa caixa na entrada da sala.\n\n"
     "Alguns pais acharam a medida exagerada, porque gostam de poder falar com os filhos em caso de emergência. "
     "Depois de muita discussão, chegou-se a um acordo: os celulares ficam guardados durante as aulas e o "
     "intervalo, mas a secretaria terá um telefone disponível para os casos urgentes. A regra vai ser testada por "
     "três meses.",
     "Depois de uma proposta dos alunos e de alguma resistência dos pais, a escola decidiu testar por três meses "
     "a proibição dos celulares nas aulas e no intervalo.",
     "Os alunos queriam que os colegas conversassem e brincassem mais no intervalo. Para atender aos pais, a "
     "secretaria terá um telefone para emergências.",
     ["A proposta partiu dos próprios alunos.",
      "Os pais se preocupavam com emergências.",
      "A regra será testada por três meses."]),
    ("Era uma vez um gato chamado Bigode que morava numa livraria. Durante o dia, dormia na vitrine, em cima dos "
     "livros de culinária, e os clientes faziam carinho nele antes de entrar. À noite, quando a livraria fechava, "
     "ele caçava os ratos que tentavam roer as páginas.\n\n"
     "Um dia, o dono decidiu vender a livraria, e o novo proprietário disse que não queria gatos ali. Os clientes "
     "ficaram tão tristes que fizeram um abaixo-assinado com mais de trezentos nomes. O novo dono, surpreso, "
     "resolveu experimentar ficar com Bigode por um mês. No fim do mês, já tinha comprado uma almofada nova para a "
     "vitrine.",
     "O gato Bigode, que vivia numa livraria, quase foi mandado embora pelo novo dono, mas os clientes o "
     "defenderam e ele ficou.",
     "Bigode dormia na vitrine de dia e caçava ratos à noite. Depois de um abaixo-assinado dos clientes, o novo "
     "proprietário o testou por um mês e acabou se encantando.",
     ["Bigode morava numa livraria.",
      "O novo dono não queria gatos.",
      "Os clientes o defenderam, e ele ficou."]),
    ("Começa nesta segunda-feira a campanha de vacinação contra a gripe nos postos de saúde do município. Nesta "
     "primeira fase, podem se vacinar idosos acima de 60 anos, crianças de seis meses a menores de seis anos, "
     "gestantes, puérperas e profissionais de saúde. Os outros grupos serão chamados nas próximas semanas.\n\n"
     "É preciso levar um documento com foto e, se tiver, a caderneta de vacinação. A Secretaria de Saúde lembra que "
     "a vacina é atualizada todos os anos, porque o vírus da gripe muda, e por isso quem tomou no ano passado "
     "também deve tomar de novo. Os postos funcionam das 8h às 17h, e no sábado haverá um dia de vacinação especial.",
     "A campanha de vacinação contra a gripe começa na segunda-feira para idosos, crianças pequenas, gestantes e "
     "profissionais de saúde.",
     "É preciso levar documento e caderneta, e quem se vacinou no ano anterior deve tomar outra dose, porque o "
     "vírus muda. Os outros grupos serão chamados depois.",
     ["A vacinação começa na segunda-feira.",
      "A primeira fase é para os grupos prioritários.",
      "A vacina deve ser tomada todo ano."]),
    ("Fazer compras com lista parece bobagem, mas faz diferença no bolso. Quem vai ao mercado sem saber o que "
     "precisa acaba voltando com coisas desnecessárias e esquecendo o que realmente faltava. As lojas são "
     "organizadas para chamar a atenção, com doces perto do caixa e promoções no fim dos corredores.\n\n"
     "Antes de sair, vale olhar a geladeira e o armário, anotar o que acabou e pensar nas refeições da semana. No "
     "mercado, compare o preço por quilo ou por litro, e não só o preço da embalagem. Evite ir com fome, porque "
     "a fome aumenta as compras por impulso. Com o tempo, a lista vira hábito e a economia aparece no fim do mês.",
     "Fazer uma lista antes de ir ao mercado evita compras desnecessárias e ajuda a economizar.",
     "Sem lista, a pessoa cai nas armadilhas da loja e esquece o que precisava. Vale conferir a despensa, comparar "
     "o preço por quilo e não fazer compras com fome.",
     ["A lista evita compras por impulso.",
      "Compare o preço por quilo.",
      "Não vá ao mercado com fome."]),
    ("Marina sempre teve medo de falar em público. Na escola, tremia ao ler em voz alta, e na faculdade chegou a "
     "faltar no dia de uma apresentação. Quando foi promovida no trabalho e soube que teria de apresentar os "
     "resultados da equipe todo mês, pensou em recusar o cargo.\n\n"
     "Em vez disso, inscreveu-se num curso de oratória. Aprendeu a respirar antes de começar, a ensaiar em voz "
     "alta e a olhar para algumas pessoas da plateia em vez de fixar o chão. A primeira apresentação foi difícil, "
     "mas a segunda foi melhor. Seis meses depois, ela ainda fica nervosa, mas já consegue falar com segurança e "
     "até fazer piadas.",
     "Marina tinha pavor de falar em público, mas fez um curso de oratória e, com prática, passou a apresentar com "
     "segurança.",
     "A promoção a obrigou a apresentar resultados todo mês, e ela quase recusou. Com técnicas de respiração e "
     "ensaio, foi melhorando a cada apresentação.",
     ["Marina tinha medo de falar em público.",
      "Fez um curso de oratória.",
      "Com a prática, ganhou segurança."]),
    ("A prefeitura anunciou que a linha 304 de ônibus, que liga o bairro Jardim das Flores ao centro, vai ganhar "
     "mais quatro veículos a partir do mês que vem. Com isso, o intervalo entre os ônibus no horário de pico deve "
     "cair de 30 para 15 minutos.\n\n"
     "A medida atende a uma reclamação antiga dos moradores, que enfrentavam ônibus lotados e longas esperas, "
     "principalmente de manhã cedo. A associação do bairro chegou a fazer um protesto em frente à prefeitura no "
     "ano passado. Além dos novos ônibus, o ponto final no bairro vai ganhar cobertura e bancos. O preço da "
     "passagem continua o mesmo.",
     "A linha de ônibus do Jardim das Flores ganhará quatro veículos, e a espera no horário de pico deve cair "
     "pela metade.",
     "Os moradores reclamavam havia tempo de ônibus lotados e chegaram a protestar na prefeitura. O ponto final "
     "também será melhorado, sem aumento na passagem.",
     ["A linha 304 terá mais quatro ônibus.",
      "O intervalo cai de 30 para 15 minutos.",
      "Era um pedido antigo dos moradores."]),
    ("Quem tem plantas em casa sabe que regar demais é tão ruim quanto esquecer de regar. Quando a terra fica "
     "encharcada o tempo todo, as raízes não conseguem respirar e começam a apodrecer. As folhas ficam amarelas e "
     "moles, e muita gente, achando que a planta está com sede, rega ainda mais.\n\n"
     "Para saber a hora certa, enfie o dedo uns dois centímetros na terra: se estiver úmida, espere. Vasos precisam "
     "de furos no fundo para a água sair, e o pratinho embaixo deve ser esvaziado depois da rega. Cada planta tem a "
     "sua necessidade: suculentas e cactos querem pouca água, enquanto samambaias gostam de terra sempre um pouco "
     "úmida.",
     "O texto alerta que regar demais apodrece as raízes e ensina a testar a umidade da terra com o dedo antes de "
     "regar.",
     "Folhas amarelas e moles podem ser sinal de excesso de água, e não de sede. Vasos com furos, pratinho vazio e "
     "atenção a cada tipo de planta evitam o problema.",
     ["Água demais apodrece as raízes.",
      "Teste a terra com o dedo.",
      "Cada planta precisa de uma quantidade diferente."]),
    ("Na pequena cidade de Pedra Branca, a festa da padroeira é o evento mais esperado do ano. Durante nove dias, a "
     "praça da igreja recebe barracas de comida, brinquedos para as crianças e shows de músicos da região. No "
     "último dia, a procissão percorre as ruas enfeitadas com bandeirinhas e tapetes de serragem colorida.\n\n"
     "Este ano, a festa teve uma novidade: uma feira com produtos dos agricultores familiares, como queijo, doce de "
     "leite, mel e farinha de mandioca. Segundo a organização, a feira vendeu tudo antes do fim do segundo dia. Os "
     "comerciantes da cidade também comemoram, porque o movimento nos restaurantes e pousadas quase dobra no "
     "período.",
     "A festa da padroeira de Pedra Branca, com nove dias de barracas, shows e procissão, ganhou neste ano uma "
     "feira de agricultores que esgotou rapidamente.",
     "A festa enche a praça e termina com uma procissão por ruas enfeitadas. Os produtos da agricultura familiar "
     "acabaram em dois dias, e o comércio da cidade também lucra.",
     ["A festa dura nove dias.",
      "A novidade foi a feira de agricultores.",
      "O comércio local quase dobra o movimento."]),
    ("O professor Henrique pediu que cada aluno entrevistasse uma pessoa mais velha da família sobre como era a "
     "vida quando ela tinha a idade deles. Lucas escolheu o avô, que cresceu num sítio no interior de Minas Gerais.\n\n"
     "O avô contou que acordava às cinco da manhã para tirar leite das vacas antes de ir à escola, que ficava a "
     "uma hora de caminhada. Não havia luz elétrica, e à noite a família conversava à luz do lampião. Brinquedo "
     "era feito em casa, com sabugo de milho e pedaços de madeira. Lucas disse que ficou impressionado e que, depois "
     "da entrevista, passou a reclamar menos de acordar cedo.",
     "Numa entrevista para a escola, Lucas descobriu como o avô cresceu num sítio sem luz elétrica, com muito "
     "trabalho e brinquedos feitos em casa.",
     "O avô tirava leite de madrugada e andava uma hora até a escola. A conversa impressionou Lucas, que passou a "
     "reclamar menos de acordar cedo.",
     ["Lucas entrevistou o avô.",
      "O avô cresceu num sítio sem luz elétrica.",
      "Lucas passou a valorizar a própria rotina."]),
    ("Muitas pessoas têm dúvida sobre a diferença entre reduzir, reutilizar e reciclar. Reduzir é a primeira e a "
     "mais importante atitude: consumir menos e evitar desperdícios, como recusar sacolas e embalagens "
     "desnecessárias. Reutilizar é dar um novo uso a algo que seria jogado fora, como transformar um pote de vidro "
     "em porta-lápis.\n\n"
     "Reciclar é transformar o material usado em matéria-prima para novos produtos, o que acontece nas indústrias "
     "depois da coleta seletiva. Embora seja muito útil, a reciclagem gasta energia e transporte. Por isso, os "
     "especialistas dizem que a ordem importa: primeiro reduzir, depois reutilizar e, só então, reciclar.",
     "O texto explica a diferença entre reduzir, reutilizar e reciclar e mostra que reduzir o consumo é a atitude "
     "mais importante.",
     "Reduzir é consumir menos, reutilizar é dar novo uso aos objetos, e reciclar é transformar o material na "
     "indústria. Como a reciclagem gasta energia, ela deve vir por último.",
     ["Reduzir é consumir menos.",
      "Reutilizar é dar outro uso aos objetos.",
      "Reciclar vem por último."]),
    ("Na manhã de ontem, um cavalo solto causou confusão na avenida principal de São Roque do Sul. O animal, que "
     "tinha fugido de um sítio próximo, andou por quase meia hora entre os carros, parando o trânsito e assustando "
     "os pedestres.\n\n"
     "Um motorista de caminhão conseguiu acalmar o cavalo com um punhado de capim e o levou até uma praça, onde "
     "ficou amarrado até a chegada do dono. Ninguém se feriu. O proprietário pediu desculpas e disse que a cerca do "
     "pasto tinha sido derrubada pela chuva. A prefeitura lembrou que animais soltos em vias públicas podem causar "
     "acidentes graves e que os donos podem ser multados.",
     "Um cavalo fugido de um sítio parou o trânsito da avenida principal até ser acalmado por um caminhoneiro, e "
     "ninguém se feriu.",
     "O animal andou por meia hora entre os carros depois que a chuva derrubou a cerca do pasto. A prefeitura "
     "lembrou que donos de animais soltos podem ser multados.",
     ["Um cavalo fugido parou o trânsito.",
      "Um caminhoneiro o acalmou com capim.",
      "O dono pode ser multado."]),
    ("Desde que comecei a caminhar meia hora por dia, minha vida mudou mais do que eu esperava. No começo, era só "
     "uma recomendação do médico por causa da pressão. Eu saía de má vontade, contando os minutos para voltar para "
     "casa.\n\n"
     "Depois de umas três semanas, percebi que estava dormindo melhor e que as dores nas costas tinham diminuído. "
     "Comecei a reparar nas árvores da rua, a cumprimentar os vizinhos e até descobri uma padaria nova no caminho. "
     "Hoje, se fico um dia sem caminhar, sinto falta. A pressão está controlada, e o médico ficou satisfeito. Não "
     "precisei de academia nem de equipamentos caros, só de um par de tênis confortável.",
     "O autor conta que começou a caminhar por recomendação médica e, com o tempo, passou a dormir melhor, sentir "
     "menos dor e gostar do hábito.",
     "No início, ele caminhava sem vontade, mas depois de algumas semanas percebeu os benefícios. A pressão ficou "
     "controlada, sem precisar de academia.",
     ["A caminhada começou por ordem médica.",
      "Ele passou a dormir melhor e sentir menos dor.",
      "Bastou um tênis confortável."]),
    ("O incêndio que atingiu a Serra do Cipó no fim de semana foi controlado na noite de domingo, depois de três "
     "dias de trabalho de bombeiros, brigadistas e voluntários. As chamas destruíram cerca de 800 hectares de "
     "vegetação, principalmente de campos e cerrado.\n\n"
     "Segundo os brigadistas, o tempo seco e o vento forte dificultaram o combate. Ainda não se sabe o que causou o "
     "fogo, mas a polícia investiga se ele começou com uma queimada para limpar um terreno. Os especialistas "
     "lembram que a vegetação do cerrado costuma se recuperar com as chuvas, mas que os animais que não conseguem "
     "fugir, como tamanduás e filhotes de aves, são as maiores vítimas.",
     "Um incêndio na Serra do Cipó destruiu cerca de 800 hectares antes de ser controlado, e a polícia investiga a "
     "causa.",
     "Bombeiros e voluntários levaram três dias para apagar o fogo, dificultado pela seca e pelo vento. A "
     "vegetação deve se recuperar, mas muitos animais morreram.",
     ["O fogo destruiu cerca de 800 hectares.",
      "O combate durou três dias.",
      "A suspeita é de uma queimada para limpar terreno."]),
    ("Oi, Paulo! Tudo bem? Estou escrevendo porque não vou conseguir ir ao seu aniversário no sábado. Minha mãe vai "
     "fazer uma cirurgia simples na sexta, e eu vou ficar com ela no fim de semana para ajudar em casa. Os médicos "
     "disseram que está tudo bem, mas ela vai precisar de repouso.\n\n"
     "Fiquei chateado de perder a festa, porque sei que você preparou tudo com carinho. Já comprei o seu presente e "
     "vou entregar na semana que vem. Que tal a gente sair para comer uma pizza na quarta? Aí você me conta como "
     "foi a festa. Feliz aniversário adiantado, e aproveita bastante!",
     "Na mensagem, o amigo avisa Paulo que não poderá ir ao aniversário porque vai cuidar da mãe depois de uma "
     "cirurgia, e propõe uma pizza na semana seguinte.",
     "A mãe dele fará uma cirurgia simples e precisará de repouso no fim de semana. Ele já comprou o presente e "
     "deseja feliz aniversário a Paulo.",
     ["Ele não poderá ir à festa de sábado.",
      "Vai cuidar da mãe após uma cirurgia.",
      "Propõe sair para comer pizza na quarta."]),
    ("O Brasil tem mais de 200 milhões de habitantes, mas eles não estão distribuídos de forma igual pelo "
     "território. A maior parte da população vive perto do litoral, nas regiões Sudeste e Nordeste, enquanto a "
     "região Norte, que é a maior do país, tem poucos moradores para o seu tamanho.\n\n"
     "Isso tem raízes na história: a colonização portuguesa começou pelo litoral, onde ficavam os portos, e as "
     "primeiras cidades e plantações surgiram ali. O interior foi ocupado mais tarde, com a mineração, a criação "
     "de gado e, no século XX, a construção de Brasília e de estradas. Ainda hoje, a densidade de moradores no "
     "litoral é muito maior do que no interior.",
     "A população brasileira se concentra no litoral, especialmente no Sudeste e no Nordeste, porque a colonização "
     "começou pela costa.",
     "A região Norte é a maior, mas tem poucos moradores. O interior foi ocupado mais tarde, com a mineração, o "
     "gado, Brasília e as estradas.",
     ["A maioria vive perto do litoral.",
      "O Norte é grande e pouco povoado.",
      "A colonização começou pela costa."]),
    ("Ontem à noite, faltou luz no prédio inteiro por quase quatro horas. No começo, todo mundo reclamou: a "
     "geladeira desligada, o celular com pouca bateria, a internet fora do ar. Meu filho achou que ia morrer de "
     "tédio.\n\n"
     "Acendemos umas velas e, sem nada para fazer, pegamos um jogo de tabuleiro esquecido no armário. Jogamos três "
     "partidas, rimos muito e depois ficamos contando histórias de quando eu era criança. Quando a luz voltou, "
     "ninguém correu para a televisão. Foi estranho perceber que uma falta de energia trouxe uma das noites mais "
     "divertidas que tivemos em muito tempo.",
     "Uma falta de luz de quatro horas, que começou com reclamações, acabou virando uma noite divertida de jogos "
     "e histórias em família.",
     "Sem internet e televisão, a família pegou um jogo de tabuleiro esquecido e conversou à luz de velas. Quando "
     "a energia voltou, ninguém quis ligar a televisão.",
     ["Faltou luz por quatro horas.",
      "A família jogou e contou histórias.",
      "A noite foi melhor do que o esperado."]),
    ("A Associação dos Pescadores de Vila do Mar comemora o retorno das tainhas ao litoral da região. Nos últimos "
     "cinco anos, a quantidade de peixes vinha caindo, e muitas famílias que vivem da pesca passaram por "
     "dificuldades. Neste inverno, porém, os cardumes voltaram em grande número.\n\n"
     "Os pescadores atribuem a melhora ao respeito ao período de defeso, quando a pesca é proibida para que os "
     "peixes se reproduzam, e à fiscalização contra barcos industriais que pescavam perto da costa. Os "
     "pesquisadores da universidade local concordam, mas lembram que é cedo para comemorar: é preciso acompanhar "
     "os próximos anos para saber se a recuperação vai continuar.",
     "As tainhas voltaram em grande número ao litoral de Vila do Mar, graças ao defeso e à fiscalização, mas os "
     "pesquisadores pedem cautela.",
     "Depois de cinco anos de queda, os cardumes reapareceram neste inverno e animaram as famílias de pescadores. "
     "A universidade quer acompanhar os próximos anos para confirmar a recuperação.",
     ["As tainhas voltaram neste inverno.",
      "O defeso e a fiscalização ajudaram.",
      "Ainda é cedo para comemorar."]),
    ("Antes de comprar um celular, vale pensar em como você vai usá-lo. Quem só quer conversar, ver redes sociais "
     "e tirar fotos de vez em quando não precisa do modelo mais caro. Já quem joga, edita vídeos ou fotografa muito "
     "deve olhar com atenção o processador, a memória e a câmera.\n\n"
     "Alguns pontos importam para todo mundo: a bateria, que deve durar o dia inteiro; o espaço de armazenamento, "
     "porque fotos e aplicativos ocupam cada vez mais; e o tempo de atualizações do sistema, que garante segurança. "
     "Ler avaliações de outros compradores e comparar preços em várias lojas também ajuda a não pagar caro por "
     "recursos que nunca vão ser usados.",
     "Antes de comprar um celular, pense no seu uso e confira a bateria, o armazenamento e as atualizações, para "
     "não pagar por recursos desnecessários.",
     "Para usos simples, um modelo intermediário basta, e quem joga ou edita vídeo precisa de mais desempenho. "
     "Ler avaliações e comparar preços evita gastar demais.",
     ["Escolha conforme o seu uso.",
      "Bateria e armazenamento importam para todos.",
      "Compare preços e avaliações."]),
    ("O Museu Histórico da cidade inaugurou uma exposição sobre a imigração japonesa na região. Os primeiros "
     "imigrantes chegaram por volta de 1930 para trabalhar nas fazendas de café e, anos depois, muitos compraram "
     "terras e passaram a plantar verduras, frutas e chá.\n\n"
     "A mostra reúne fotografias, documentos, ferramentas agrícolas e objetos domésticos doados pelas famílias "
     "descendentes, como quimonos, louças e uma máquina de costura de 1940. Há também depoimentos em vídeo de "
     "moradores que contam as histórias dos avós. A entrada é gratuita, e a exposição fica aberta até o fim do ano, "
     "de terça a domingo.",
     "O museu da cidade abriu uma exposição gratuita sobre a imigração japonesa, com objetos e histórias das "
     "famílias descendentes.",
     "Os imigrantes chegaram por volta de 1930 para trabalhar no café e depois viraram agricultores. A mostra tem "
     "fotos, ferramentas, roupas e depoimentos em vídeo.",
     ["A exposição trata da imigração japonesa.",
      "Os objetos foram doados pelas famílias.",
      "A entrada é gratuita até o fim do ano."]),
    ("Quando meu pai se aposentou, todos achamos que ele ia descansar. Durante trinta e cinco anos, ele trabalhou "
     "como motorista de ônibus e sempre dizia que sonhava em não ter horário para nada. Mas, depois de dois meses "
     "em casa, ele estava inquieto, mudando os móveis de lugar e consertando o que não estava quebrado.\n\n"
     "Foi então que um vizinho o convidou para ajudar numa horta comunitária. Hoje, meu pai passa as manhãs "
     "cuidando de alfaces e couves, conversa com todo mundo e voltou a acordar cedo, agora por vontade própria. Ele "
     "diz que descobriu que não queria parar de trabalhar; queria trabalhar com algo que escolhesse.",
     "Depois de se aposentar e ficar inquieto em casa, o pai do narrador encontrou numa horta comunitária uma "
     "atividade que o deixa feliz.",
     "Ele trabalhou trinta e cinco anos como motorista e sonhava em descansar, mas sentiu falta de ter o que "
     "fazer. Na horta, percebeu que queria trabalhar com algo escolhido por ele.",
     ["O pai se aposentou depois de 35 anos.",
      "Ficou inquieto sem atividade.",
      "Encontrou alegria numa horta comunitária."]),
    ("Uma pesquisa feita com cinco mil estudantes do ensino médio mostrou que os alunos que dormem menos de seis "
     "horas por noite têm notas mais baixas e mais dificuldade de concentração. O estudo também apontou que o uso "
     "do celular na cama, depois da meia-noite, é um dos principais motivos para o sono curto.\n\n"
     "Os pesquisadores recomendam que os adolescentes durmam de oito a dez horas por noite e que os aparelhos "
     "fiquem fora do quarto na hora de dormir. Eles também sugerem que as famílias combinem horários e que as "
     "escolas falem sobre o assunto. Segundo os autores, pequenas mudanças de hábito já podem melhorar o "
     "rendimento em poucas semanas.",
     "Uma pesquisa mostrou que estudantes que dormem menos de seis horas têm notas piores, e o celular na cama é "
     "uma das principais causas.",
     "Os pesquisadores recomendam de oito a dez horas de sono para adolescentes e celulares fora do quarto. "
     "Combinar horários pode melhorar o rendimento em poucas semanas.",
     ["Dormir pouco piora as notas.",
      "O celular na cama atrapalha o sono.",
      "Adolescentes precisam de oito a dez horas."]),
    ("Na entrada do parque estadual, uma placa lembra as regras para os visitantes. É proibido alimentar os "
     "animais, porque a comida humana faz mal a eles e os acostuma a se aproximar das pessoas. Também não é "
     "permitido levar animais de estimação, fazer fogueiras ou sair das trilhas sinalizadas.\n\n"
     "Todo o lixo produzido deve ser levado de volta, já que não há lixeiras dentro da mata. O parque abre às 8h e "
     "a entrada é permitida até as 14h, para que todos voltem antes de escurecer. Crianças devem estar sempre "
     "acompanhadas, e quem for fazer as trilhas mais longas precisa se registrar na portaria.",
     "A placa do parque lista as regras de visita, como não alimentar os animais, não sair das trilhas e levar o "
     "lixo de volta.",
     "Também é proibido levar animais de estimação e fazer fogueiras. O parque abre às 8h, a entrada vai até as "
     "14h, e as trilhas longas exigem registro.",
     ["Não alimente os animais.",
      "Leve o lixo de volta.",
      "A entrada é permitida até as 14h."]),
]
