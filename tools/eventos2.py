"""Detalhes dos acontecimentos de eventos.py: quem fez, por que aconteceu e quem estava no poder.

Cada item: nome (o mesmo de eventos.EVENTOS): (quem fez, por que aconteceu, pergunta sobre o líder, resposta).
A pergunta sobre o líder junta duas informações ("Quem era o imperador bizantino quando Constantinopla caiu?");
None quando não faz sentido. O gerador monta "Quem fez X?", "Por que aconteceu X?", perguntas que juntam duas
coisas ("O que foi X e por que aconteceu?") e as conversas "O que foi X e por que aconteceu?" -> "Mas quando?",
"O que aconteceu em X, e quando?" -> "Mas quem fez isso?" (ver gerar_pergeresp.detalhes_sections).
"""

DETALHES = {
    "a chegada dos portugueses ao Brasil": (
        "A frota era comandada por Pedro Álvares Cabral, enviado pelo rei de Portugal.",
        "Portugal procurava uma rota marítima para comerciar especiarias com a Índia, e a frota se afastou da costa da África para aproveitar os ventos do Atlântico.",
        "Quem era o rei de Portugal quando os portugueses chegaram ao Brasil?",
        "O rei de Portugal era Dom Manuel I, conhecido como o Venturoso."),
    "a fundação de Salvador": (
        "Salvador foi fundada por Tomé de Sousa, o primeiro governador-geral do Brasil.",
        "O rei de Portugal quis organizar melhor a colônia, porque o sistema de capitanias hereditárias não estava dando certo, e criou um governo central com sede em Salvador.",
        "Quem era o rei de Portugal quando Salvador foi fundada?",
        "O rei de Portugal era Dom João III."),
    "a fundação de São Paulo": (
        "São Paulo foi fundada por padres jesuítas, entre eles Manuel da Nóbrega e José de Anchieta.",
        "Os jesuítas queriam um colégio no planalto para catequizar os povos indígenas da região.",
        "Quem era o rei de Portugal quando São Paulo foi fundada?",
        "O rei de Portugal era Dom João III."),
    "a fundação do Rio de Janeiro": (
        "O Rio de Janeiro foi fundado por Estácio de Sá.",
        "Os portugueses queriam expulsar os franceses, que tinham se instalado na Baía de Guanabara, e garantir o controle da região.",
        "Quem era o rei de Portugal quando o Rio de Janeiro foi fundado?",
        "O rei de Portugal era Dom Sebastião, que era ainda muito jovem."),
    "a fundação de Recife": (
        "A ocupação da região foi organizada por Duarte Coelho, o donatário da capitania de Pernambuco.",
        "O porto era importante para exportar o açúcar produzido nos engenhos da capitania.",
        None, None),
    "a fundação de Belo Horizonte": (
        "A cidade foi planejada pelo engenheiro Aarão Reis.",
        "Minas Gerais queria uma capital nova e moderna para substituir Ouro Preto, uma cidade cercada de morros, com pouco espaço para crescer.",
        None, None),
    "a execução de Tiradentes": (
        "Tiradentes foi condenado pela Justiça da Coroa portuguesa e enforcado no Rio de Janeiro.",
        "Ele foi considerado o principal culpado da Inconfidência Mineira, uma conspiração contra o domínio português e os impostos sobre o ouro.",
        "Quem governava Portugal quando Tiradentes foi executado?",
        "Portugal era governado pela rainha Dona Maria I."),
    "a chegada da família real portuguesa ao Rio de Janeiro": (
        "A viagem foi comandada pelo príncipe regente Dom João, que governava em nome da mãe, a rainha Dona Maria I.",
        "As tropas de Napoleão estavam invadindo Portugal, e a família real fugiu para o Brasil com a proteção da Marinha britânica.",
        "Quem governava Portugal quando a família real veio para o Brasil?",
        "O governo estava nas mãos do príncipe regente Dom João, que depois se tornou o rei Dom João VI."),
    "a abertura dos portos do Brasil": (
        "Os portos foram abertos pelo príncipe regente Dom João.",
        "Portugal estava ocupado pelas tropas de Napoleão, e o Brasil precisava comerciar diretamente com outros países, principalmente com a Inglaterra, aliada dos portugueses.",
        None, None),
    "o Dia do Fico": (
        "Quem anunciou que ficaria no Brasil foi o príncipe regente Dom Pedro.",
        "As Cortes de Portugal exigiam a volta de Dom Pedro e queriam diminuir a autonomia do Brasil, e muitos brasileiros pediram que ele ficasse.",
        "Quem era o rei de Portugal no Dia do Fico?",
        "O rei de Portugal era Dom João VI, pai de Dom Pedro."),
    "a Independência do Brasil": (
        "A independência foi declarada por Dom Pedro, que depois foi coroado imperador como Dom Pedro I.",
        "As Cortes de Portugal queriam que o Brasil voltasse a ser uma colônia, com menos autonomia, e exigiam a volta de Dom Pedro a Lisboa.",
        "Quem era o rei de Portugal quando o Brasil ficou independente?",
        "O rei de Portugal era Dom João VI, pai de Dom Pedro I."),
    "a primeira Constituição do Brasil": (
        "A Constituição foi dada ao país por Dom Pedro I, depois que ele dissolveu a Assembleia Constituinte.",
        "O Brasil tinha acabado de ficar independente e precisava de leis próprias para organizar o novo país.",
        None, None),
    "a Batalha do Riachuelo": (
        "A esquadra brasileira foi comandada pelo almirante Francisco Manuel Barroso da Silva.",
        "Durante a Guerra do Paraguai, a Tríplice Aliança precisava controlar os rios da região para impedir o avanço paraguaio.",
        "Quem governava o Paraguai durante a Batalha do Riachuelo?",
        "O Paraguai era governado por Francisco Solano López."),
    "a Lei do Ventre Livre": (
        "A lei foi assinada pela princesa Isabel, que governava como regente, e foi proposta pelo gabinete do Visconde do Rio Branco.",
        "Havia cada vez mais pressão, dentro e fora do Brasil, para acabar com a escravidão, e o governo escolheu fazer isso aos poucos.",
        "Quem era o imperador do Brasil quando a Lei do Ventre Livre foi assinada?",
        "O imperador era Dom Pedro II, que estava viajando pela Europa; por isso a princesa Isabel governava como regente."),
    "a abolição da escravidão no Brasil": (
        "A Lei Áurea foi assinada pela princesa Isabel, que governava como regente.",
        "O movimento abolicionista cresceu muito, muitas pessoas escravizadas fugiam das fazendas, e o Brasil era o último país das Américas que ainda mantinha a escravidão.",
        "Quem era o imperador do Brasil quando a escravidão foi abolida?",
        "O imperador era Dom Pedro II, que estava na Europa tratando da saúde; por isso a princesa Isabel assinou a lei como regente."),
    "a Proclamação da República": (
        "A República foi proclamada pelo marechal Deodoro da Fonseca, com o apoio de militares e de políticos republicanos.",
        "Parte do Exército estava insatisfeita com o governo, os fazendeiros que perderam os escravizados deixaram de apoiar o Império, e o movimento republicano tinha crescido.",
        "Quem era o imperador quando a República foi proclamada?",
        "O imperador era Dom Pedro II, que foi exilado com a família na Europa."),
    "o voo do 14-Bis": (
        "Quem voou com o 14-Bis foi o próprio inventor, Alberto Santos Dumont.",
        "Santos Dumont queria provar que um aparelho mais pesado que o ar podia decolar sozinho e voar, e disputava prêmios oferecidos para os primeiros voos.",
        None, None),
    "a chegada dos primeiros imigrantes japoneses ao Brasil": (
        "A viagem foi organizada por uma companhia de imigração japonesa, num acordo com o governo de São Paulo.",
        "As fazendas de café precisavam de trabalhadores, e muitos japoneses enfrentavam dificuldades no campo e buscavam uma vida nova.",
        None, None),
    "a Revolta da Chibata": (
        "A revolta foi liderada pelo marinheiro João Cândido, conhecido como o Almirante Negro.",
        "Os marinheiros, em sua maioria negros e pobres, ainda eram castigados com chicotadas, além de receberem salários baixos e comida ruim.",
        "Quem era o presidente do Brasil durante a Revolta da Chibata?",
        "O presidente era Hermes da Fonseca, que tinha tomado posse poucos dias antes."),
    "a Semana de Arte Moderna": (
        "A Semana foi organizada por artistas e escritores como Mário de Andrade, Oswald de Andrade, Anita Malfatti e Di Cavalcanti.",
        "Os artistas queriam romper com a arte tradicional e criar uma arte moderna e brasileira, no ano em que a independência fazia cem anos.",
        "Quem era o presidente do Brasil durante a Semana de Arte Moderna?",
        "O presidente era Epitácio Pessoa."),
    "a Revolução de 1930": (
        "O movimento foi liderado por Getúlio Vargas, com o apoio de políticos do Rio Grande do Sul, de Minas Gerais e da Paraíba e de parte do Exército.",
        "A eleição de 1930 foi contestada, o acordo entre São Paulo e Minas Gerais tinha se rompido, e o assassinato de João Pessoa aumentou a revolta.",
        "Quem era o presidente derrubado pela Revolução de 1930?",
        "O presidente derrubado foi Washington Luís."),
    "a inauguração do Cristo Redentor": (
        "A estátua foi projetada pelo engenheiro Heitor da Silva Costa, com a escultura do francês Paul Landowski.",
        "A ideia era fazer um monumento religioso que também fosse um símbolo da cidade do Rio de Janeiro.",
        "Quem governava o Brasil quando o Cristo Redentor foi inaugurado?",
        "O país era governado por Getúlio Vargas, que chefiava o governo provisório."),
    "a primeira transmissão de televisão no Brasil": (
        "A transmissão foi feita pela TV Tupi, do empresário Assis Chateaubriand.",
        "Chateaubriand era dono de jornais e rádios e quis trazer para o Brasil a novidade que já existia nos Estados Unidos e na Europa.",
        "Quem era o presidente do Brasil na primeira transmissão de televisão?",
        "O presidente era Eurico Gaspar Dutra."),
    "a final da Copa do Mundo de 1950": (
        "O Uruguai virou o jogo com gols de Schiaffino e Ghiggia.",
        "O Brasil saiu na frente, mas o Uruguai empatou e marcou o segundo gol perto do fim, calando o Maracanã lotado.",
        "Quem era o técnico do Brasil na Copa de 1950?",
        "O técnico do Brasil era Flávio Costa."),
    "a criação da Petrobras": (
        "A lei que criou a Petrobras foi sancionada pelo presidente Getúlio Vargas.",
        "A campanha O petróleo é nosso defendia que a exploração do petróleo ficasse nas mãos do Brasil, e não de empresas estrangeiras.",
        None, None),
    "o primeiro título do Brasil na Copa do Mundo": (
        "A seleção era treinada por Vicente Feola e tinha jogadores como Pelé, Garrincha, Didi e Nilton Santos.",
        "O time combinava jogadores experientes e jovens talentos, e Pelé e Garrincha foram decisivos nos jogos finais.",
        "Quem era o presidente do Brasil quando o país ganhou a primeira Copa?",
        "O presidente era Juscelino Kubitschek."),
    "a inauguração de Brasília": (
        "Brasília foi construída no governo de Juscelino Kubitschek, com o plano de Lúcio Costa e os prédios de Oscar Niemeyer.",
        "A ideia era levar o desenvolvimento para o interior do país e tirar a capital do litoral; a mudança já estava prevista desde a primeira Constituição da República.",
        "Quem era o presidente quando Brasília foi inaugurada?",
        "O presidente era Juscelino Kubitschek, que inaugurou a cidade."),
    "o golpe militar de 1964": (
        "O golpe foi feito por militares das Forças Armadas, com o apoio de parte dos políticos e da sociedade civil.",
        "Havia uma grave crise política e econômica, e os setores que derrubaram o governo se opunham às reformas propostas pelo presidente, num momento de forte tensão da Guerra Fria.",
        "Quem era o presidente do Brasil antes do golpe de 1964?",
        "O presidente era João Goulart, conhecido como Jango."),
    "o tricampeonato do Brasil na Copa do Mundo": (
        "A seleção era treinada por Zagallo e tinha jogadores como Pelé, Tostão, Gérson, Jairzinho, Rivelino e Carlos Alberto.",
        "O Brasil reuniu muitos craques num time ofensivo e venceu todos os jogos da Copa do México.",
        "Quem era o técnico do Brasil na Copa de 1970?",
        "O técnico era Zagallo."),
    "o fim da ditadura militar": (
        "José Sarney assumiu a presidência, porque Tancredo Neves, eleito pelo Colégio Eleitoral, adoeceu antes da posse.",
        "O regime perdeu apoio com a crise econômica e com movimentos como as Diretas Já, e a abertura política levou à volta de um civil à presidência.",
        "Quem foi eleito presidente no fim da ditadura militar?",
        "Tancredo Neves foi eleito pelo Colégio Eleitoral, mas adoeceu e morreu antes de assumir; quem governou foi o vice, José Sarney."),
    "a Constituição de 1988": (
        "A Constituição foi escrita pela Assembleia Nacional Constituinte, presidida pelo deputado Ulysses Guimarães.",
        "Com o fim do regime militar, o Brasil precisava de uma nova Constituição democrática, que garantisse direitos e eleições diretas.",
        "Quem era o presidente do Brasil quando a Constituição de 1988 foi promulgada?",
        "O presidente era José Sarney."),
    "o lançamento do real": (
        "O Plano Real foi preparado pela equipe econômica do Ministério da Fazenda, num trabalho iniciado por Fernando Henrique Cardoso.",
        "O Brasil sofria com uma inflação altíssima, e os preços subiam quase todos os dias.",
        "Quem era o presidente do Brasil quando o real foi lançado?",
        "O presidente era Itamar Franco."),
    "o pentacampeonato do Brasil na Copa do Mundo": (
        "A seleção era treinada por Luiz Felipe Scolari e tinha jogadores como Ronaldo, Rivaldo, Ronaldinho Gaúcho, Roberto Carlos e Cafu, o capitão.",
        "Ronaldo, que tinha se recuperado de uma lesão grave, foi o artilheiro da Copa e marcou os dois gols da final.",
        "Quem era o técnico do Brasil na Copa de 2002?",
        "O técnico era Luiz Felipe Scolari, o Felipão."),
    "a ida do primeiro astronauta brasileiro ao espaço": (
        "O astronauta foi Marcos Pontes, tenente-coronel da Força Aérea Brasileira.",
        "A viagem foi possível por um acordo do Brasil com a agência espacial da Rússia e homenageou os cem anos do voo do 14-Bis.",
        "Quem era o presidente do Brasil quando o primeiro astronauta brasileiro foi ao espaço?",
        "O presidente era Luiz Inácio Lula da Silva."),
    "a coroação de Carlos Magno": (
        "Carlos Magno foi coroado pelo papa Leão III, na Basílica de São Pedro, em Roma.",
        "O papa buscava a proteção do poderoso rei dos francos, e a coroação recriava um império no Ocidente, ligado à Igreja.",
        None, None),
    "a assinatura da Magna Carta": (
        "Os barões da Inglaterra obrigaram o rei João, conhecido como João Sem Terra, a aceitar o documento.",
        "O rei cobrava impostos muito altos, tinha perdido terras na França e agia sem respeitar os direitos dos nobres.",
        "Quem era o rei da Inglaterra quando a Magna Carta foi assinada?",
        "O rei era João, conhecido como João Sem Terra."),
    "a queda de Constantinopla": (
        "A cidade foi conquistada pelo exército do Império Otomano, comandado pelo sultão Maomé II.",
        "Os otomanos queriam a cidade, muito rica e numa posição estratégica entre a Europa e a Ásia, e o Império Bizantino já estava enfraquecido.",
        "Quem era o imperador bizantino quando Constantinopla caiu?",
        "O imperador era Constantino XI Paleólogo, que morreu defendendo a cidade."),
    "a chegada de Cristóvão Colombo à América": (
        "A viagem foi comandada por Cristóvão Colombo e patrocinada pelos reis da Espanha.",
        "Colombo queria chegar às Índias navegando para o oeste, para comerciar especiarias sem passar pelos caminhos controlados por outros povos.",
        "Quem patrocinou a viagem de Colombo?",
        "A viagem foi patrocinada pelos Reis Católicos da Espanha, Isabel de Castela e Fernando de Aragão."),
    "o Tratado de Tordesilhas": (
        "O tratado foi assinado pelos reinos de Portugal e da Espanha.",
        "Depois da viagem de Colombo, os dois reinos disputavam as terras recém-descobertas e quiseram dividir o mundo entre eles para evitar uma guerra.",
        "Quem era o rei de Portugal quando o Tratado de Tordesilhas foi assinado?",
        "O rei de Portugal era Dom João II."),
    "a chegada de Vasco da Gama à Índia": (
        "A frota foi comandada por Vasco da Gama, enviado pelo rei de Portugal.",
        "Portugal queria chegar à Índia por mar para comprar especiarias diretamente, sem depender dos comerciantes que controlavam as rotas por terra.",
        "Quem era o rei de Portugal quando Vasco da Gama chegou à Índia?",
        "O rei de Portugal era Dom Manuel I."),
    "a publicação das 95 teses de Lutero": (
        "As teses foram escritas pelo monge e professor alemão Martinho Lutero.",
        "Lutero discordava da venda de indulgências, o perdão dos pecados em troca de dinheiro, e de outras práticas da Igreja da época.",
        "Quem era o papa quando Lutero publicou as 95 teses?",
        "O papa era Leão X."),
    "o fim da primeira volta ao mundo": (
        "A viagem começou sob o comando de Fernão de Magalhães e terminou sob o comando de Juan Sebastián Elcano.",
        "A expedição procurava um caminho pelo oeste até as Ilhas das Especiarias, na Ásia.",
        "Quem era o rei da Espanha quando a primeira volta ao mundo terminou?",
        "O rei era Carlos I da Espanha, que também era o imperador Carlos V."),
    "o Grande Incêndio de Londres": (
        "O fogo começou numa padaria da rua Pudding Lane.",
        "As casas eram de madeira e muito próximas umas das outras, o verão tinha sido seco e um vento forte espalhou as chamas.",
        "Quem era o rei da Inglaterra durante o Grande Incêndio de Londres?",
        "O rei era Carlos II."),
    "o terremoto de Lisboa": (
        "Foi um desastre natural; a reconstrução da cidade foi comandada pelo Marquês de Pombal.",
        "O terremoto foi causado pelo movimento das placas tectônicas no fundo do Oceano Atlântico, e depois vieram um tsunami e incêndios.",
        "Quem era o rei de Portugal durante o terremoto de Lisboa?",
        "O rei era Dom José I, e o seu ministro mais poderoso era o Marquês de Pombal."),
    "a Independência dos Estados Unidos": (
        "A declaração foi aprovada pelos representantes das treze colônias, e o principal autor do texto foi Thomas Jefferson.",
        "Os colonos não aceitavam pagar impostos criados pelo Parlamento britânico sem ter representantes nele, e os conflitos com a Grã-Bretanha viraram guerra.",
        "Quem era o rei da Grã-Bretanha quando os Estados Unidos declararam a independência?",
        "O rei era Jorge III."),
    "a Tomada da Bastilha": (
        "A Bastilha foi tomada pelo povo de Paris.",
        "A França vivia uma crise econômica, com fome e impostos altos, e o povo se revoltou contra o poder absoluto do rei e temia uma reação das tropas.",
        "Quem era o rei da França na Tomada da Bastilha?",
        "O rei era Luís XVI."),
    "a primeira vacina": (
        "A vacina foi criada pelo médico inglês Edward Jenner.",
        "A varíola matava muita gente, e Jenner percebeu que as pessoas que pegavam a varíola das vacas ficavam protegidas da varíola humana.",
        None, None),
    "o Grito de Dolores": (
        "O chamado foi feito pelo padre Miguel Hidalgo.",
        "Havia muita desigualdade no México colonial, e a invasão da Espanha por Napoleão enfraqueceu o domínio espanhol na América.",
        None, None),
    "a primeira mensagem do telégrafo de Morse": (
        "A mensagem foi enviada pelo inventor Samuel Morse.",
        "Morse queria mostrar que era possível mandar mensagens por fios elétricos, a longas distâncias, em poucos minutos.",
        None, None),
    "a publicação de A Origem das Espécies": (
        "O livro foi escrito pelo naturalista inglês Charles Darwin.",
        "Darwin estudava o assunto desde a viagem do navio Beagle e decidiu publicar quando Alfred Russel Wallace chegou a ideias parecidas.",
        None, None),
    "a Proclamação de Emancipação": (
        "A proclamação foi assinada pelo presidente Abraham Lincoln.",
        "Durante a Guerra Civil, Lincoln quis enfraquecer os estados do sul, que dependiam do trabalho escravo, e dar um sentido de liberdade à guerra.",
        None, None),
    "o assassinato de Abraham Lincoln": (
        "Lincoln foi baleado pelo ator John Wilkes Booth, que apoiava os estados do sul.",
        "Booth queria vingar a derrota do sul na Guerra Civil.",
        None, None),
    "a inauguração da Torre Eiffel": (
        "A torre foi construída pela empresa do engenheiro Gustave Eiffel.",
        "Ela foi feita para a Exposição Universal de Paris, que comemorava os cem anos da Revolução Francesa.",
        None, None),
    "a primeira sessão de cinema": (
        "A sessão foi organizada pelos irmãos Auguste e Louis Lumière.",
        "Os irmãos tinham criado o cinematógrafo e quiseram mostrar a invenção ao público, cobrando ingresso.",
        None, None),
    "a abertura dos primeiros Jogos Olímpicos modernos": (
        "Os Jogos foram recriados por iniciativa do francês Pierre de Coubertin.",
        "Coubertin queria reviver os jogos da Grécia Antiga e acreditava que o esporte podia aproximar os povos.",
        None, None),
    "o primeiro voo dos irmãos Wright": (
        "Os voos foram feitos pelos irmãos Orville e Wilbur Wright; Orville pilotou o primeiro.",
        "Os irmãos queriam construir um avião que pudesse ser controlado no ar, e testavam planadores havia anos.",
        None, None),
    "a chegada ao Polo Sul": (
        "A expedição foi liderada pelo norueguês Roald Amundsen.",
        "Havia uma disputa para ver quem chegaria primeiro ao Polo Sul, e Amundsen competia com a expedição britânica de Robert Scott.",
        None, None),
    "o naufrágio do Titanic": (
        "O navio era comandado pelo capitão Edward Smith.",
        "O navio bateu num iceberg em alta velocidade, à noite, e não havia botes salva-vidas suficientes para todos.",
        "Quem era o capitão do Titanic?",
        "O capitão era Edward Smith, que morreu no naufrágio."),
    "o início da Primeira Guerra Mundial": (
        "A guerra começou quando a Áustria-Hungria declarou guerra à Sérvia, e as alianças levaram as grandes potências da Europa ao conflito.",
        "O arquiduque Francisco Ferdinando, herdeiro do trono austro-húngaro, foi assassinado em Sarajevo, num clima de disputas entre as potências europeias.",
        "Quem era o imperador da Áustria-Hungria quando começou a Primeira Guerra Mundial?",
        "O imperador era Francisco José I."),
    "a abertura do Canal do Panamá": (
        "O canal foi construído pelos Estados Unidos, depois que uma tentativa francesa fracassou.",
        "O canal evitava que os navios precisassem contornar toda a América do Sul para ir do Atlântico ao Pacífico.",
        "Quem era o presidente dos Estados Unidos quando o Canal do Panamá foi aberto?",
        "O presidente era Woodrow Wilson."),
    "a Revolução Russa": (
        "O poder foi tomado pelos bolcheviques, liderados por Lênin e Trótski.",
        "A Rússia vivia uma grande crise, com fome, derrotas na Primeira Guerra Mundial e um governo provisório fraco.",
        "Quem governava a Rússia quando os bolcheviques tomaram o poder?",
        "O governo provisório era chefiado por Alexandre Kerensky; o czar Nicolau II já tinha deixado o trono meses antes."),
    "o fim da Primeira Guerra Mundial": (
        "O armistício foi assinado pela Alemanha e pelos países aliados, num vagão de trem em Compiègne, na França.",
        "A Alemanha estava sendo derrotada, sem recursos e com revoltas internas.",
        "Quem era o imperador da Alemanha no fim da Primeira Guerra Mundial?",
        "O imperador era Guilherme II, que deixou o trono dois dias antes do armistício."),
    "a primeira Copa do Mundo": (
        "A Copa foi organizada pela FIFA, presidida por Jules Rimet, e realizada no Uruguai.",
        "O Uruguai foi escolhido porque comemorava cem anos de independência e era o campeão olímpico de futebol.",
        None, None),
    "o início da Segunda Guerra Mundial": (
        "A guerra começou com a invasão da Polônia pela Alemanha nazista, comandada por Adolf Hitler.",
        "Hitler queria expandir o território alemão e desfazer o Tratado de Versalhes, e o Reino Unido e a França tinham prometido defender a Polônia.",
        "Quem governava a Alemanha quando começou a Segunda Guerra Mundial?",
        "A Alemanha era governada por Adolf Hitler."),
    "o ataque a Pearl Harbor": (
        "O ataque foi feito por aviões da Marinha do Japão.",
        "O Japão queria impedir que a frota americana atrapalhasse a sua expansão no Pacífico, depois que os Estados Unidos cortaram a venda de petróleo.",
        "Quem era o presidente dos Estados Unidos no ataque a Pearl Harbor?",
        "O presidente era Franklin D. Roosevelt."),
    "o Dia D": (
        "O desembarque foi feito por tropas aliadas, principalmente dos Estados Unidos, do Reino Unido e do Canadá, sob o comando do general Dwight Eisenhower.",
        "Os aliados queriam abrir uma frente no oeste da Europa para libertar a França e derrotar a Alemanha nazista.",
        "Quem comandou os aliados no Dia D?",
        "O comandante supremo era o general americano Dwight Eisenhower."),
    "o fim da Segunda Guerra Mundial na Europa": (
        "A rendição foi assinada por comandantes militares da Alemanha.",
        "Berlim tinha sido tomada pelos soviéticos, Hitler tinha morrido, e a Alemanha não tinha mais como continuar a guerra.",
        None, None),
    "o bombardeio de Hiroshima": (
        "A bomba foi lançada pelos Estados Unidos, de um avião chamado Enola Gay.",
        "Os Estados Unidos queriam forçar o Japão a se render logo, encerrando a guerra no Pacífico.",
        "Quem era o presidente dos Estados Unidos no bombardeio de Hiroshima?",
        "O presidente era Harry Truman."),
    "a fundação da ONU": (
        "A ONU foi criada por 51 países, entre eles o Brasil.",
        "Depois da Segunda Guerra Mundial, os países queriam uma organização para manter a paz e evitar uma nova guerra mundial.",
        None, None),
    "a independência da Índia": (
        "A luta pela independência teve líderes como Mahatma Gandhi e Jawaharlal Nehru.",
        "Depois de décadas de protestos, em grande parte sem violência, o Reino Unido, enfraquecido pela Segunda Guerra Mundial, aceitou deixar a Índia.",
        "Quem foi o primeiro primeiro-ministro da Índia independente?",
        "O primeiro primeiro-ministro foi Jawaharlal Nehru."),
    "a Declaração Universal dos Direitos Humanos": (
        "A declaração foi aprovada pela Assembleia Geral da ONU; a comissão que a preparou foi presidida por Eleanor Roosevelt.",
        "Depois dos horrores da Segunda Guerra Mundial, os países quiseram definir os direitos que todas as pessoas devem ter.",
        None, None),
    "o protesto de Rosa Parks": (
        "O protesto foi de Rosa Parks, uma costureira e ativista de Montgomery.",
        "As leis de segregação obrigavam as pessoas negras a ceder o lugar no ônibus aos brancos.",
        "Quem liderou o boicote aos ônibus depois do protesto de Rosa Parks?",
        "O boicote teve como líder o jovem pastor Martin Luther King."),
    "o lançamento do Sputnik 1": (
        "O satélite foi lançado pela União Soviética; o engenheiro-chefe do programa era Serguei Korolev.",
        "Na Guerra Fria, a União Soviética e os Estados Unidos disputavam quem chegaria primeiro ao espaço.",
        "Quem governava a União Soviética no lançamento do Sputnik 1?",
        "A União Soviética era governada por Nikita Khrushchev."),
    "a viagem da cadela Laika ao espaço": (
        "A missão foi da União Soviética, no programa comandado pelo engenheiro Serguei Korolev.",
        "Os cientistas queriam saber se um ser vivo aguentaria o lançamento e a falta de gravidade, e o governo queria comemorar os quarenta anos da Revolução Russa.",
        "Quem governava a União Soviética quando a cadela Laika foi ao espaço?",
        "A União Soviética era governada por Nikita Khrushchev."),
    "o primeiro voo de um ser humano ao espaço": (
        "O voo foi feito pelo cosmonauta soviético Yuri Gagarin.",
        "Na corrida espacial, a União Soviética queria ser a primeira a mandar um ser humano ao espaço.",
        "Quem governava a União Soviética quando Gagarin foi ao espaço?",
        "A União Soviética era governada por Nikita Khrushchev."),
    "o discurso Eu tenho um sonho": (
        "O discurso foi feito pelo pastor Martin Luther King, na Marcha sobre Washington.",
        "O movimento pelos direitos civis lutava contra a segregação racial e pela igualdade de direitos para a população negra.",
        "Quem era o presidente dos Estados Unidos no discurso Eu tenho um sonho?",
        "O presidente era John F. Kennedy."),
    "o primeiro transplante de coração": (
        "A cirurgia foi feita pelo médico sul-africano Christiaan Barnard; o paciente se chamava Louis Washkansky.",
        "O paciente tinha uma doença grave no coração, e a equipe de Barnard vinha se preparando para a operação havia anos.",
        None, None),
    "a chegada do homem à Lua": (
        "A missão Apollo 11, da NASA, levou Neil Armstrong, Buzz Aldrin e Michael Collins.",
        "Na corrida espacial com a União Soviética, os Estados Unidos queriam cumprir a promessa do presidente Kennedy de levar um homem à Lua antes do fim da década.",
        "Quem era o presidente dos Estados Unidos quando o homem chegou à Lua?",
        "O presidente era Richard Nixon."),
    "a Revolução dos Cravos": (
        "A revolução foi feita por capitães do Movimento das Forças Armadas, com o apoio da população.",
        "Portugal vivia uma ditadura havia mais de quarenta anos e enfrentava guerras longas nas colônias da África.",
        "Quem governava Portugal antes da Revolução dos Cravos?",
        "O chefe do governo era Marcello Caetano, que tinha sucedido Salazar."),
    "o acidente de Chernobyl": (
        "O acidente aconteceu durante um teste feito pelos operadores da usina.",
        "O teste foi mal conduzido, e o reator tinha falhas de projeto, o que causou a explosão.",
        "Quem governava a União Soviética no acidente de Chernobyl?",
        "A União Soviética era governada por Mikhail Gorbachev."),
    "a queda do Muro de Berlim": (
        "A abertura foi anunciada pelo governo da Alemanha Oriental, e a população foi para o muro e começou a derrubá-lo.",
        "Havia grandes protestos na Alemanha Oriental, e as reformas na União Soviética tinham enfraquecido os governos comunistas da Europa.",
        "Quem governava a União Soviética quando o Muro de Berlim caiu?",
        "A União Soviética era governada por Mikhail Gorbachev."),
    "a libertação de Nelson Mandela": (
        "Mandela foi libertado pelo governo do presidente sul-africano Frederik de Klerk.",
        "A pressão internacional contra o apartheid era cada vez maior, e o governo decidiu negociar o fim do regime.",
        "Quem era o presidente da África do Sul quando Mandela foi libertado?",
        "O presidente era Frederik de Klerk."),
    "o lançamento do telescópio Hubble": (
        "O telescópio foi construído pela NASA, com a participação da Agência Espacial Europeia.",
        "Fora da atmosfera, um telescópio enxerga o espaço com muito mais nitidez.",
        None, None),
    "o primeiro site da internet": (
        "O site foi criado por Tim Berners-Lee, no CERN.",
        "Berners-Lee queria facilitar a troca de documentos entre os cientistas, ligando os textos por links.",
        None, None),
    "o fim da União Soviética": (
        "Os líderes das repúblicas decidiram dissolver a União Soviética, e Mikhail Gorbachev renunciou.",
        "O país vivia uma crise econômica, várias repúblicas queriam a independência, e uma tentativa de golpe em agosto de 1991 enfraqueceu o governo central.",
        "Quem era o presidente da Rússia quando a União Soviética acabou?",
        "O presidente da Rússia era Boris Iéltsin."),
    "o ataque às Torres Gêmeas": (
        "O ataque foi feito pelo grupo terrorista Al-Qaeda, liderado por Osama bin Laden.",
        "O grupo se opunha à presença e à política dos Estados Unidos no Oriente Médio.",
        "Quem era o presidente dos Estados Unidos no ataque às Torres Gêmeas?",
        "O presidente era George W. Bush."),
    "o começo da circulação do euro": (
        "O euro é emitido pelo Banco Central Europeu, para os países da zona do euro.",
        "Os países da União Europeia queriam facilitar o comércio e as viagens com uma moeda única.",
        None, None),
    "a chegada do robô Curiosity a Marte": (
        "O robô foi enviado pela NASA.",
        "Os cientistas queriam descobrir se Marte já teve condições para a vida, estudando as rochas e o solo.",
        None, None),
    "a declaração da pandemia de covid-19": (
        "A pandemia foi declarada pela Organização Mundial da Saúde, dirigida por Tedros Adhanom.",
        "A doença tinha se espalhado rapidamente por muitos países de vários continentes.",
        None, None),
    "o lançamento do telescópio James Webb": (
        "O telescópio foi feito pela NASA, com a Agência Espacial Europeia e a Agência Espacial Canadense, e lançado por um foguete Ariane 5.",
        "Os cientistas queriam observar galáxias muito antigas e distantes, usando a luz infravermelha.",
        None, None),
    "a destruição de Pompeia": (
        "Foi uma erupção do vulcão Vesúvio.",
        "O Vesúvio estava adormecido havia muito tempo, e as cidades tinham crescido ao pé do vulcão.",
        "Quem era o imperador romano quando Pompeia foi destruída?",
        "O imperador era Tito, que tinha assumido o trono naquele mesmo ano."),
    "a Inconfidência Mineira": (
        "A conspiração reuniu figuras como Tiradentes, Cláudio Manuel da Costa e Tomás Antônio Gonzaga; foi denunciada por Joaquim Silvério dos Reis.",
        "Os mineiros estavam revoltados com os impostos sobre o ouro e com a ameaça da derrama, a cobrança dos impostos atrasados.",
        "Quem governava Portugal durante a Inconfidência Mineira?",
        "Portugal era governado pela rainha Dona Maria I."),
    "o início da Guerra do Paraguai": (
        "A guerra começou com ataques do Paraguai, governado por Francisco Solano López, ao Brasil e à Argentina.",
        "Havia disputas por territórios e pelo uso dos rios da região, e o Paraguai reagiu à intervenção brasileira no Uruguai.",
        "Quem governava o Brasil durante a Guerra do Paraguai?",
        "O Brasil era governado pelo imperador Dom Pedro II."),
    "a Revolta da Vacina": (
        "A revolta foi da população do Rio de Janeiro contra a vacinação obrigatória organizada por Oswaldo Cruz.",
        "Muitas pessoas não sabiam como a vacina funcionava e tinham medo dela, e já estavam revoltadas com as reformas que demoliram cortiços.",
        "Quem era o presidente do Brasil durante a Revolta da Vacina?",
        "O presidente era Rodrigues Alves."),
    "a descoberta da penicilina": (
        "A penicilina foi descoberta pelo médico escocês Alexander Fleming.",
        "Fleming percebeu que um fungo que tinha crescido por acaso numa placa do laboratório matava as bactérias em volta.",
        None, None),
    "as Diretas Já": (
        "O movimento reuniu políticos, artistas e milhões de pessoas; a emenda das eleições diretas foi proposta pelo deputado Dante de Oliveira.",
        "Os brasileiros queriam voltar a eleger o presidente pelo voto direto, depois de duas décadas de regime militar.",
        "Quem era o presidente do Brasil durante as Diretas Já?",
        "O presidente era o general João Figueiredo, o último presidente do regime militar."),
}
