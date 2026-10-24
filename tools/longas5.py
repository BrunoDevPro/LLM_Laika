"""Respostas longas (parte 5: passo a passo e conselhos práticos). Mesmo formato do longas1; assunto None
quando "Escreva um texto longo sobre..." não combina (o gerador usa outras formas de pedir)."""

LONGAS = [
    (None, "Como fazer arroz?",
     "Para fazer arroz soltinho, comece lavando uma xícara de arroz numa peneira até a água sair mais clara. Numa "
     "panela, aqueça um fio de óleo e refogue um pouco de cebola e alho picados até ficarem dourados. Junte o arroz "
     "escorrido e mexa por um ou dois minutos, para os grãos ficarem envolvidos no óleo.\n\n"
     "Acrescente duas xícaras de água quente e sal a gosto, mais ou menos uma colher de chá. Quando ferver, abaixe o "
     "fogo, tampe a panela deixando uma pequena abertura e cozinhe até a água secar, por uns 15 minutos. Desligue o "
     "fogo e deixe o arroz descansar tampado por cinco minutos antes de soltar os grãos com um garfo. A proporção de "
     "duas medidas de água para uma de arroz funciona para o arroz branco comum."),
    (None, "Como fazer um bolo simples?",
     "Para um bolo simples, separe três ovos, uma xícara de açúcar, meia xícara de óleo, uma xícara de leite, duas "
     "xícaras de farinha de trigo e uma colher de sopa de fermento em pó. Ligue o forno a 180 graus para aquecer e "
     "unte uma forma com manteiga e farinha.\n\n"
     "Bata os ovos com o açúcar até a mistura ficar clara e fofa. Junte o óleo e o leite e misture bem. Acrescente a "
     "farinha aos poucos, mexendo até a massa ficar lisa, e por último o fermento, misturando com delicadeza. Despeje "
     "na forma e asse por cerca de 35 a 40 minutos. Para saber se está pronto, espete um palito no meio: se sair "
     "limpo, o bolo está assado. Espere amornar antes de desenformar."),
    (None, "Como estudar para uma prova?",
     "O primeiro passo é começar com antecedência, e não na véspera. Veja quais conteúdos vão cair e divida o estudo "
     "em partes, distribuídas pelos dias que faltam. Estudar um pouco todos os dias funciona muito melhor do que "
     "passar horas seguidas na última noite, porque o cérebro precisa de tempo e de sono para guardar o que "
     "aprendeu.\n\n"
     "Na hora de estudar, escolha um lugar tranquilo e deixe o celular longe. Em vez de só reler, faça resumos com "
     "suas palavras, mapas mentais e, principalmente, exercícios: tentar lembrar a matéria sem olhar é uma das formas "
     "mais eficazes de aprender. Explique o conteúdo para alguém ou para você mesmo em voz alta. Faça pausas curtas, "
     "beba água e, antes da prova, durma bem."),
    (None, "Como plantar uma árvore?",
     "Escolha uma espécie adequada ao clima e ao espaço, de preferência nativa da sua região, e veja o tamanho que "
     "ela vai ter adulta, para não plantar embaixo de fios ou perto demais de casas. O melhor momento costuma ser o "
     "início da estação das chuvas. Cave uma cova de uns 40 a 60 centímetros de largura e de profundidade.\n\n"
     "Misture a terra retirada com adubo orgânico, como esterco curtido ou composto. Tire a muda do saquinho com "
     "cuidado, sem desmanchar o torrão de terra das raízes, coloque-a no centro da cova e complete com a terra "
     "adubada, apertando de leve. Regue bem logo depois de plantar e continue regando nos primeiros meses, se não "
     "chover. Um tutor, uma estaca amarrada sem apertar, ajuda a muda a crescer reta."),
    (None, "Como economizar água em casa?",
     "Muitas atitudes simples economizam água. No banheiro, tome banhos mais curtos e feche o chuveiro enquanto se "
     "ensaboa. Ao escovar os dentes ou fazer a barba, mantenha a torneira fechada; só isso pode poupar vários litros "
     "por dia. Verifique se há vazamentos em torneiras, canos e na descarga, porque um pequeno gotejamento desperdiça "
     "muita água ao longo do mês.\n\n"
     "Na cozinha, lave a louça com a torneira fechada, ensaboando tudo antes de enxaguar, e use a máquina de lavar só "
     "com a carga completa. Para limpar a calçada, use balde e vassoura em vez de mangueira. A água da máquina de "
     "lavar pode ser reaproveitada para limpar o quintal, e a água da chuva, guardada com segurança, pode regar as "
     "plantas."),
    (None, "Como fazer uma boa apresentação na escola?",
     "Comece entendendo bem o tema e pesquisando em fontes confiáveis, como livros, sites de instituições e "
     "enciclopédias. Depois, organize as ideias numa ordem lógica: uma introdução dizendo do que você vai falar, o "
     "desenvolvimento com as informações principais e uma conclusão que resuma o que foi apresentado.\n\n"
     "Se usar slides, coloque pouco texto, com tópicos curtos, imagens e letras grandes; os slides devem ajudar, e não "
     "ser lidos palavra por palavra. Ensaie várias vezes em voz alta, marcando o tempo, se possível na frente de "
     "alguém. Na hora, fale devagar, olhe para a turma e respire fundo se ficar nervoso. Prepare-se também para "
     "perguntas. Lembre que todo mundo fica um pouco ansioso, e a prática diminui esse medo."),
    (None, "Como fazer uma redação?",
     "Antes de escrever, leia o tema com atenção e pense no que você quer defender ou contar. Anote as ideias "
     "principais e os argumentos num rascunho e organize o texto em três partes. Na introdução, apresente o assunto e "
     "a sua opinião ou o ponto central. No desenvolvimento, em dois ou três parágrafos, explique os argumentos com "
     "exemplos, dados ou comparações.\n\n"
     "Na conclusão, retome a ideia principal e, quando o tipo de texto pedir, proponha uma solução para o problema "
     "discutido. Use frases claras, evite repetir palavras e ligue os parágrafos com conectivos, como além disso, "
     "porém e portanto. Depois de escrever, releia procurando erros de ortografia, de pontuação e trechos confusos. "
     "Ler bastante e praticar com frequência são as melhores formas de melhorar."),
    (None, "Como cuidar de um cachorro?",
     "Cuidar de um cachorro exige tempo e responsabilidade. Ele precisa de ração de boa qualidade, adequada à idade e "
     "ao tamanho, e de água limpa sempre disponível. Evite dar comida temperada, chocolate, uva, cebola e ossos "
     "cozidos, que fazem mal. Leve-o ao veterinário regularmente, mantenha as vacinas e o vermífugo em dia e proteja-"
     "o contra pulgas e carrapatos.\n\n"
     "Os cães precisam de exercício e de distração: passeie com ele todos os dias, sempre com coleira e guia, e "
     "ofereça brinquedos. Dê banho com produtos próprios para cães e escove os pelos. Ensine as regras da casa com "
     "paciência e recompensas, sem violência. A castração evita filhotes indesejados e alguns problemas de saúde. Em "
     "troca, o cachorro oferece companhia e muito carinho."),
    (None, "Como fazer uma horta em casa?",
     "Uma horta pode caber até numa varanda ou janela. Escolha um lugar que receba pelo menos quatro a seis horas de "
     "sol por dia. Use vasos, caixotes ou garrafas com furos no fundo para a água escorrer, coloque uma camada de "
     "pedrinhas ou argila expandida e complete com terra adubada.\n\n"
     "Para começar, prefira plantas fáceis, como cebolinha, salsinha, manjericão, alface, rúcula e tomate-cereja. "
     "Plante as sementes ou mudas seguindo a profundidade indicada no pacote e regue de preferência de manhã cedo ou "
     "no fim da tarde, sem encharcar. Tire as ervas daninhas, que roubam nutrientes, e adube de tempos em tempos com "
     "composto orgânico, que pode ser feito com cascas de frutas e verduras. Em poucas semanas, já dá para colher os "
     "primeiros temperos."),
    (None, "Como ter uma boa noite de sono?",
     "Para dormir bem, tente manter horários regulares, deitando e acordando mais ou menos no mesmo horário, inclusive "
     "nos fins de semana. O quarto deve ser escuro, silencioso e com temperatura agradável, e a cama deve ser usada "
     "principalmente para dormir. Evite cochilos longos no fim da tarde.\n\n"
     "Diminua o uso de celular, computador e televisão pelo menos uma hora antes de deitar, porque a luz das telas "
     "atrasa a produção de melatonina, o hormônio do sono. Evite café, chá preto, refrigerante e chocolate à noite, "
     "assim como refeições muito pesadas. Exercícios durante o dia ajudam, mas não muito perto da hora de dormir. Se "
     "a insônia for frequente e atrapalhar o dia, vale procurar um médico."),
    (None, "Como se preparar para uma entrevista de emprego?",
     "Antes da entrevista, pesquise sobre a empresa: o que ela faz, seus produtos e valores. Releia a descrição da "
     "vaga e pense em exemplos da sua experiência, da escola ou de outros trabalhos que mostrem as habilidades "
     "pedidas. Prepare respostas para perguntas comuns, como fale sobre você, quais são seus pontos fortes e por que "
     "quer trabalhar ali.\n\n"
     "No dia, chegue com alguns minutos de antecedência, vista-se de forma adequada ao ambiente e leve documentos e "
     "o currículo. Durante a conversa, cumprimente com educação, olhe para o entrevistador, ouça com atenção e "
     "responda com sinceridade, sem inventar. No fim, é uma boa ideia fazer uma ou duas perguntas sobre a vaga. "
     "Depois, agradeça pela oportunidade."),
    (None, "Como fazer um currículo?",
     "Um bom currículo é curto, claro e organizado, de preferência com uma ou duas páginas. No topo, coloque seu nome, "
     "telefone, e-mail e cidade. Logo abaixo, escreva um objetivo de uma ou duas linhas, dizendo a área ou a vaga que "
     "você procura.\n\n"
     "Depois, liste a formação, como escola, cursos técnicos e faculdade, com as datas, e as experiências "
     "profissionais, começando pela mais recente, com o nome da empresa, o cargo, o período e as principais tarefas. "
     "Se ainda não tem experiência, inclua trabalhos voluntários, projetos da escola e cursos livres. Acrescente "
     "habilidades, como idiomas e programas de computador. Revise com cuidado os erros de português e adapte o "
     "currículo para cada vaga."),
    (None, "Como lidar com o estresse?",
     "O estresse é a reação do corpo e da mente a situações de pressão, como provas, trabalho em excesso ou "
     "problemas em casa. Em pequenas doses, ele ajuda a reagir, mas, quando dura muito, causa cansaço, irritação, dor "
     "de cabeça e problemas de sono. Um primeiro passo é identificar o que está causando o estresse e ver o que pode "
     "ser mudado ou dividido em partes menores.\n\n"
     "Cuidar do corpo ajuda muito: dormir bem, comer de forma equilibrada e fazer atividade física, que libera "
     "substâncias que trazem bem-estar. Reserve momentos para descansar e fazer o que gosta, e experimente "
     "respirar devagar e fundo por alguns minutos. Conversar com amigos ou a família alivia. Se o estresse "
     "estiver muito forte, procurar um profissional de saúde é uma atitude importante."),
    (None, "Como fazer amigos numa escola nova?",
     "Chegar a uma escola nova pode dar medo, e isso é normal. Um bom começo é se mostrar aberto: sorrir, "
     "cumprimentar os colegas e se apresentar. Fazer perguntas simples, como de onde a pessoa é, do que ela gosta ou "
     "o que acha de uma matéria, ajuda a puxar conversa. Prestar atenção no que o outro diz também mostra interesse "
     "de verdade.\n\n"
     "Participar de atividades em grupo, como esportes, trabalhos de classe, clubes ou o recreio, facilita conhecer "
     "pessoas com os mesmos interesses. Oferecer ajuda e ser gentil faz diferença. Não precisa ter pressa: amizades "
     "levam tempo para se formar, e é melhor ter poucos amigos verdadeiros do que muitos colegas distantes. Seja você "
     "mesmo, e as pessoas certas vão se aproximar."),
    (None, "Como economizar dinheiro?",
     "Para economizar, o primeiro passo é saber para onde vai o dinheiro. Anote todos os gastos durante um mês e "
     "separe o que é essencial, como aluguel, contas, comida e transporte, do que é supérfluo. Muitas vezes, pequenas "
     "despesas do dia a dia, como lanches e assinaturas que você nem usa, somam bastante no fim do mês.\n\n"
     "Defina um objetivo e guarde uma parte do que ganha assim que receber, antes de gastar com o resto. Compare "
     "preços, faça lista antes de ir ao mercado e evite comprar por impulso. Fuja de juros altos, como os do cartão "
     "de crédito rotativo e do cheque especial. Com o tempo, a reserva de dinheiro dá segurança para imprevistos e "
     "permite realizar planos maiores."),
    (None, "Como aprender uma língua estrangeira?",
     "Aprender uma língua exige contato frequente com ela. Estudar um pouco todos os dias, nem que sejam 15 minutos, "
     "funciona melhor do que estudar horas uma vez por semana. Comece pelas palavras e expressões mais usadas no dia "
     "a dia e pela pronúncia, e use aplicativos, livros e cursos para ter uma base organizada.\n\n"
     "Exponha-se à língua de forma divertida: ouça músicas, assista a filmes e séries com legendas na própria língua, "
     "leia textos simples e notícias. Falar é essencial, mesmo errando: converse com outras pessoas que estudam, com "
     "falantes nativos ou até sozinho, em voz alta. Anote as palavras novas e revise. Não tenha medo de errar, porque "
     "os erros fazem parte do aprendizado."),
    (None, "Como evitar a dengue?",
     "A melhor forma de evitar a dengue é impedir que o mosquito Aedes aegypti se reproduza. Ele põe os ovos em água "
     "parada e limpa, então é preciso eliminar os criadouros. Uma vez por semana, verifique a casa e o quintal: "
     "esvazie e lave os pratinhos dos vasos de plantas ou coloque areia neles, guarde garrafas de boca para baixo e "
     "não deixe pneus expostos à chuva.\n\n"
     "Mantenha as caixas-d'água, tonéis e cisternas bem tampados, limpe as calhas e jogue o lixo em sacos fechados. "
     "Ralos pouco usados devem ser tampados. Para se proteger das picadas, use repelente e telas nas janelas, "
     "principalmente nos períodos de mais casos. Em caso de febre alta, dores no corpo e atrás dos olhos, procure "
     "atendimento e não tome remédio por conta própria."),
    (None, "Como fazer uma pesquisa escolar?",
     "Comece entendendo exatamente o que o professor pediu e delimitando o tema. Depois, procure informações em "
     "fontes confiáveis: livros da biblioteca, enciclopédias, sites de universidades, museus e órgãos oficiais. Na "
     "internet, desconfie de páginas sem autor ou sem fonte e compare a mesma informação em lugares diferentes.\n\n"
     "Leia o material, anote as ideias principais e escreva o trabalho com suas próprias palavras, em vez de copiar e "
     "colar; copiar textos de outros sem citar é plágio. Organize o trabalho com introdução, desenvolvimento e "
     "conclusão e inclua imagens ou gráficos se ajudarem. No final, liste as fontes que você usou, as referências. "
     "Revise o texto antes de entregar."),
    (None, "Como agir em caso de incêndio?",
     "Em caso de incêndio, o mais importante é sair do local com segurança e chamar os bombeiros pelo número 193. "
     "Mantenha a calma e avise as outras pessoas. Se houver fumaça, abaixe-se e ande o mais perto possível do chão, "
     "porque a fumaça e o calor sobem; cubra o nariz e a boca com um pano, de preferência molhado.\n\n"
     "Antes de abrir uma porta, toque nela com as costas da mão: se estiver quente, o fogo pode estar do outro lado, "
     "e é melhor procurar outra saída. Em prédios, use as escadas, nunca o elevador. Se a roupa pegar fogo, não corra: "
     "pare, deite no chão e role para abafar as chamas. Nunca volte para buscar objetos. Ter um plano de fuga em casa "
     "e um extintor ajuda a agir rápido."),
    (None, "Como organizar o tempo?",
     "Organizar o tempo começa por saber o que precisa ser feito. Faça uma lista das tarefas da semana e separe as "
     "mais importantes e urgentes das que podem esperar. Uma agenda, de papel ou no celular, ajuda a distribuir as "
     "atividades pelos dias, sem esquecer momentos de descanso e de lazer.\n\n"
     "Divida tarefas grandes em partes menores, que parecem menos assustadoras e são mais fáceis de começar. Ao "
     "trabalhar ou estudar, tente se concentrar numa coisa por vez e afaste as distrações, como as notificações do "
     "celular. Uma técnica comum é trabalhar 25 minutos e descansar cinco. Aprender a dizer não para alguns "
     "compromissos também faz parte. No fim do dia, revise o que foi feito e ajuste o plano para o dia seguinte."),
    (None, "Como fazer uma vitamina de frutas?",
     "Para uma vitamina de banana, que é das mais simples, você vai precisar de uma banana madura, um copo de leite, "
     "que pode ser de vaca ou vegetal, e, se quiser, uma colher de aveia e um pouco de mel. Descasque a banana, corte "
     "em pedaços e coloque no liquidificador com o leite e os outros ingredientes.\n\n"
     "Bata por cerca de um minuto, até ficar cremoso. Se preferir mais gelada, acrescente algumas pedras de gelo ou "
     "use a banana congelada. Dá para variar com morango, mamão, manga ou abacate, e até misturar frutas. Como a "
     "banana madura já é doce, muitas vezes nem é preciso colocar açúcar. Sirva logo depois de bater, para não "
     "escurecer e manter o sabor e os nutrientes."),
    (None, "Como ajudar o meio ambiente no dia a dia?",
     "Pequenas atitudes, somadas, fazem diferença para o meio ambiente. Economize água, com banhos mais curtos e "
     "torneiras fechadas, e energia, apagando as luzes e desligando os aparelhos que não estão em uso. Separe o lixo "
     "reciclável e descarte corretamente pilhas, baterias, eletrônicos e óleo de cozinha, que não devem ir para o lixo "
     "comum nem para o ralo.\n\n"
     "Reduza o uso de plástico descartável, levando sacolas retornáveis e garrafas reutilizáveis. Quando possível, "
     "prefira andar a pé, de bicicleta ou de transporte público. Compre só o necessário e dê preferência a produtos "
     "duráveis e locais. Plantar árvores, cuidar das plantas e não jogar lixo na rua também ajudam. E conversar sobre "
     "o assunto incentiva outras pessoas a fazerem o mesmo."),
    (None, "Como manter a calma numa discussão?",
     "Numa discussão, o primeiro passo é perceber quando a raiva está subindo: o coração acelera, a voz fica mais alta "
     "e dá vontade de interromper. Nesse momento, respire fundo algumas vezes e fale mais devagar. Se for preciso, "
     "peça uma pausa e diga que prefere continuar a conversa mais tarde, quando os dois estiverem mais calmos.\n\n"
     "Tente ouvir de verdade o que a outra pessoa está dizendo, sem preparar a resposta enquanto ela fala. Fale sobre "
     "o que você sente, usando frases como eu fiquei chateado quando, em vez de acusar. Evite xingamentos e "
     "assuntos antigos. Lembre que o objetivo é resolver o problema, e não vencer a discussão. Às vezes, aceitar que "
     "os dois pensam diferente já é uma boa solução."),
]
