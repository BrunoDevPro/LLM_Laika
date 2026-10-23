"""Temas para pedidos genéricos (parte 3: história, política, economia e sociedade).

Os temas políticos ficam neutros: o que a ideia defende, onde apareceu e as críticas principais.
"""

TEMAS_HISTORIA = [
    ("a chegada dos portugueses ao Brasil",
     "Os portugueses chegaram ao Brasil em 22 de abril de 1500, na esquadra de Pedro Álvares Cabral.",
     "Em 22 de abril de 1500, a esquadra de Pedro Álvares Cabral chegou ao litoral do atual sul da Bahia, perto de "
     "Porto Seguro. A terra já era habitada por milhões de indígenas, de muitos povos diferentes. A carta de Pero Vaz "
     "de Caminha descreveu a chegada ao rei de Portugal. Nas décadas seguintes, os portugueses começaram a explorar o "
     "pau-brasil e a colonizar o território."),
    ("os povos indígenas do Brasil",
     "Os povos indígenas são os primeiros habitantes do Brasil; hoje são mais de 300 povos, com mais de 270 línguas.",
     "Antes da chegada dos europeus, o território brasileiro era habitado por milhões de indígenas, de centenas de "
     "povos. Com a colonização, muitos morreram por guerras, escravidão e doenças trazidas de fora. Hoje, existem mais "
     "de trezentos povos indígenas no Brasil, como os Guarani, os Yanomami, os Kayapó e os Terena, que falam mais de "
     "duzentas e setenta línguas. Muitas palavras do português vêm do tupi, como abacaxi, pipoca e capivara."),
    ("a escravidão no Brasil",
     "A escravidão no Brasil durou mais de três séculos e só terminou com a Lei Áurea, em 1888.",
     "Durante o período colonial e o Império, milhões de africanos foram trazidos à força para o Brasil e obrigados a "
     "trabalhar nas plantações, nas minas e nas cidades, sem liberdade e sob violência. Indígenas também foram "
     "escravizados. Muitos resistiram, fugindo e formando quilombos. O Brasil foi o último país das Américas a abolir "
     "a escravidão, com a Lei Áurea, em 13 de maio de 1888. As consequências dessa história ainda aparecem na desigualdade de hoje."),
    ("a Lei Áurea",
     "A Lei Áurea, assinada pela princesa Isabel em 13 de maio de 1888, aboliu a escravidão no Brasil.",
     "A Lei Áurea foi assinada pela princesa Isabel em 13 de maio de 1888 e declarou extinta a escravidão no Brasil. "
     "Ela foi o resultado de anos de luta do movimento abolicionista e da resistência das pessoas escravizadas. Mas a "
     "lei não trouxe terra, escola nem trabalho para os libertos, que continuaram enfrentando pobreza e preconceito."),
    ("os quilombos",
     "Quilombos eram comunidades formadas por pessoas que fugiam da escravidão.",
     "Os quilombos eram comunidades criadas por pessoas que fugiam da escravidão, em lugares de difícil acesso. Neles, "
     "plantavam, criavam animais e se defendiam. O mais famoso foi o Quilombo dos Palmares, na serra da Barriga, em "
     "Alagoas, que resistiu por quase um século e teve Zumbi como um de seus líderes. Hoje existem comunidades "
     "quilombolas, descendentes desses grupos, em vários estados do Brasil."),
    ("Zumbi dos Palmares",
     "Zumbi dos Palmares foi um dos líderes do Quilombo dos Palmares e é símbolo da resistência negra no Brasil.",
     "Zumbi foi um dos principais líderes do Quilombo dos Palmares, em Alagoas, no século dezessete. Ele lutou contra "
     "as tropas que queriam destruir o quilombo e foi morto em 20 de novembro de 1695. Por isso, essa data é o Dia "
     "Nacional de Zumbi e da Consciência Negra, que se tornou feriado nacional. Zumbi é lembrado como símbolo da luta "
     "contra a escravidão e o racismo."),
    ("a Independência do Brasil",
     "O Brasil se tornou independente de Portugal em 7 de setembro de 1822, com Dom Pedro I.",
     "Em 7 de setembro de 1822, às margens do riacho Ipiranga, em São Paulo, o príncipe Dom Pedro declarou a separação "
     "entre Brasil e Portugal. O episódio ficou conhecido como Grito do Ipiranga. Dom Pedro se tornou o primeiro "
     "imperador do Brasil. A independência não foi pacífica em todo lugar: houve guerras em províncias como a Bahia, "
     "onde a vitória veio em 2 de julho de 1823."),
    ("o Império do Brasil",
     "O Império do Brasil foi o período de 1822 a 1889, governado por Dom Pedro I e Dom Pedro II.",
     "Depois da independência, o Brasil foi uma monarquia por quase setenta anos. Dom Pedro I governou até 1831, quando "
     "abdicou. Depois de um período de regências, Dom Pedro II assumiu ainda adolescente e reinou por cerca de "
     "cinquenta anos. Nesse período, o café se tornou a principal riqueza do país e a escravidão foi abolida. O "
     "Império terminou com a Proclamação da República, em 1889."),
    ("Dom Pedro II",
     "Dom Pedro II foi o segundo e último imperador do Brasil, de 1840 a 1889.",
     "Dom Pedro II assumiu o trono em 1840, com apenas catorze anos, e governou o Brasil por quase meio século. Ele "
     "gostava de ciência, de livros e de fotografia, falava várias línguas e se correspondia com cientistas de outros "
     "países. Em seu reinado, aconteceram a Guerra do Paraguai e a abolição da escravidão. Com a Proclamação da "
     "República, em 1889, ele foi exilado e morreu em Paris, em 1891."),
    ("a Proclamação da República",
     "A República foi proclamada no Brasil em 15 de novembro de 1889, pelo marechal Deodoro da Fonseca.",
     "Em 15 de novembro de 1889, militares liderados pelo marechal Deodoro da Fonseca derrubaram a monarquia e "
     "proclamaram a República no Rio de Janeiro. Dom Pedro II e sua família foram para a Europa. Deodoro se tornou o "
     "primeiro presidente do Brasil. A data é feriado nacional."),
    ("a Inconfidência Mineira",
     "A Inconfidência Mineira foi um movimento de 1789, em Minas Gerais, contra o domínio de Portugal.",
     "A Inconfidência Mineira foi uma conspiração organizada em 1789, em Vila Rica, a atual Ouro Preto, por pessoas "
     "insatisfeitas com os altos impostos cobrados por Portugal sobre o ouro. O movimento foi descoberto antes de "
     "começar. Vários participantes foram presos e exilados, e Tiradentes foi o único executado, em 21 de abril de "
     "1792."),
    ("Tiradentes",
     "Tiradentes foi um dos participantes da Inconfidência Mineira e é considerado herói nacional.",
     "Joaquim José da Silva Xavier ficou conhecido como Tiradentes porque, entre outras atividades, trabalhava como "
     "dentista. Ele participou da Inconfidência Mineira, que queria libertar Minas Gerais do domínio português. Foi "
     "preso, assumiu a responsabilidade pelo movimento e foi enforcado no Rio de Janeiro, em 21 de abril de 1792. "
     "Essa data virou feriado nacional."),
    ("a Era Vargas",
     "A Era Vargas foi o período de 1930 a 1945 em que Getúlio Vargas governou o Brasil.",
     "Getúlio Vargas chegou ao poder com a Revolução de 1930 e governou até 1945. Nesse período, foram criados o "
     "salário mínimo e a Consolidação das Leis do Trabalho, a CLT, e as mulheres conquistaram o direito ao voto, em "
     "1932. A partir de 1937, porém, Vargas instalou o Estado Novo, uma ditadura com censura e perseguição a "
     "opositores. Ele voltou à presidência pelo voto em 1951 e morreu em 1954."),
    ("a ditadura militar no Brasil",
     "A ditadura militar governou o Brasil de 1964 a 1985, com censura e perseguição a opositores.",
     "Em 1964, os militares tomaram o poder com um golpe e governaram o Brasil até 1985. Nesse período, houve censura à "
     "imprensa e às artes, prisões, tortura e mortes de opositores, principalmente depois do AI-5, de 1968. Houve "
     "também anos de grande crescimento econômico, seguidos de inflação alta e dívida. A campanha das Diretas Já, em "
     "1984, ajudou a pôr fim ao regime, e a nova Constituição veio em 1988."),
    ("a Constituição de 1988",
     "A Constituição de 1988 é a lei mais importante do Brasil e foi chamada de Constituição Cidadã.",
     "A Constituição Federal foi promulgada em 5 de outubro de 1988, depois do fim da ditadura militar. Ela garante "
     "direitos como o voto direto, a liberdade de expressão, a saúde e a educação, criou o SUS e definiu a organização "
     "dos três poderes. Por ampliar os direitos dos cidadãos, ficou conhecida como Constituição Cidadã. Todas as "
     "outras leis do país precisam respeitá-la."),
    ("o SUS",
     "O SUS, Sistema Único de Saúde, é o sistema público e gratuito de saúde do Brasil.",
     "O Sistema Único de Saúde foi criado pela Constituição de 1988 e garante atendimento gratuito a qualquer pessoa "
     "no Brasil. Ele vai dos postos de saúde aos hospitais, passando pela vacinação, pelo SAMU, por transplantes e "
     "pela vigilância sanitária. É um dos maiores sistemas públicos de saúde do mundo. Ainda enfrenta problemas, como "
     "filas e falta de recursos, mas atende milhões de brasileiros todos os dias."),
    ("Brasília",
     "Brasília é a capital do Brasil e foi inaugurada em 21 de abril de 1960.",
     "Brasília foi construída no Planalto Central para levar a capital para o interior do país. Foi inaugurada em 21 "
     "de abril de 1960, no governo de Juscelino Kubitschek. O plano da cidade, desenhado por Lúcio Costa, tem a forma "
     "de um avião, e muitos prédios, como o Congresso Nacional e a Catedral, foram projetados por Oscar Niemeyer. "
     "Brasília é Patrimônio Mundial da Unesco."),
    ("a imigração no Brasil",
     "Milhões de imigrantes, como italianos, portugueses, espanhóis, japoneses e alemães, vieram para o Brasil.",
     "Entre o fim do século dezenove e meados do século vinte, milhões de imigrantes chegaram ao Brasil, muitos para "
     "trabalhar nas lavouras de café. Vieram italianos, portugueses, espanhóis, alemães, japoneses, sírios e libaneses, "
     "entre outros. Os primeiros imigrantes japoneses chegaram em 1908, no navio Kasato Maru. Essas pessoas "
     "influenciaram a comida, a língua, a música e o jeito de viver de muitas regiões."),
    ("o ciclo do ouro",
     "O ciclo do ouro foi o período do século dezoito em que a mineração de ouro, em Minas Gerais, era a maior riqueza da colônia.",
     "No fim do século dezessete, foi descoberto ouro na região de Minas Gerais. Milhares de pessoas foram para lá, e "
     "surgiram cidades como Vila Rica, hoje Ouro Preto, Mariana e Diamantina. O trabalho nas minas era feito "
     "principalmente por pessoas escravizadas. Grande parte do ouro foi enviada a Portugal. Da época ficaram igrejas "
     "barrocas e as obras de artistas como Aleijadinho."),
    ("o ciclo do café",
     "O ciclo do café foi o período, principalmente no século dezenove, em que o café era o principal produto do Brasil.",
     "No século dezenove, o café se tornou o principal produto de exportação do Brasil. As plantações se espalharam "
     "pelo Vale do Paraíba e depois pelo oeste de São Paulo. O trabalho era feito por pessoas escravizadas e, depois "
     "da abolição, principalmente por imigrantes. O dinheiro do café ajudou a construir ferrovias e a fazer crescer a "
     "cidade de São Paulo."),
    ("a Pré-História",
     "Pré-História é o longo período da vida humana antes da invenção da escrita.",
     "A Pré-História vai do surgimento dos primeiros seres humanos até a invenção da escrita, há uns cinco mil anos. "
     "No Paleolítico, as pessoas viviam da caça, da pesca e da coleta, usavam ferramentas de pedra e dominaram o fogo. "
     "No Neolítico, começaram a plantar, criar animais e morar em aldeias. As pinturas nas cavernas mostram como "
     "viviam. No Brasil, a Serra da Capivara, no Piauí, tem muitas pinturas rupestres."),
    ("a invenção da escrita",
     "A escrita foi inventada há uns cinco mil anos, na Mesopotâmia, pelos sumérios.",
     "Os sumérios, que viviam na Mesopotâmia, onde hoje fica o Iraque, criaram uma das primeiras formas de escrita, há "
     "cerca de cinco mil anos. Eles faziam marcas em forma de cunha em placas de barro, e por isso essa escrita se "
     "chama cuneiforme. Os egípcios criaram os hieróglifos. A escrita permitiu registrar leis, contas, histórias e "
     "conhecimentos, e marca o fim da Pré-História."),
    ("o Egito Antigo",
     "O Egito Antigo foi uma civilização que se desenvolveu às margens do rio Nilo, famosa pelas pirâmides e pelos faraós.",
     "O Egito Antigo surgiu às margens do rio Nilo, cujas cheias deixavam a terra fértil para a agricultura. Era "
     "governado pelos faraós, considerados divinos. Os egípcios construíram pirâmides e templos, desenvolveram a "
     "escrita hieroglífica, o papiro e conhecimentos de matemática e medicina, e mumificavam os mortos porque "
     "acreditavam numa vida depois da morte."),
    ("as pirâmides do Egito",
     "As pirâmides do Egito são enormes construções de pedra feitas como túmulos de faraós.",
     "As pirâmides foram construídas há mais de quatro mil anos como túmulos para os faraós. As mais famosas ficam em "
     "Gizé, perto do Cairo. A maior, a de Quéops, tinha cerca de 146 metros de altura e foi a construção mais alta do "
     "mundo por milhares de anos. Ela é a única das sete maravilhas do mundo antigo que ainda existe. Hoje se sabe que "
     "foram construídas por trabalhadores organizados, não por escravizados como se pensava."),
    ("a Grécia Antiga",
     "A Grécia Antiga foi a civilização que deu origem à democracia, à filosofia e aos Jogos Olímpicos.",
     "A Grécia Antiga era formada por cidades independentes, como Atenas e Esparta. Em Atenas surgiu a democracia, em "
     "que os cidadãos votavam as decisões, embora mulheres e escravizados não participassem. Os gregos criaram a "
     "filosofia, com Sócrates, Platão e Aristóteles, o teatro e os Jogos Olímpicos, e deixaram mitos sobre deuses "
     "como Zeus e Atena. Muitas palavras do português vêm do grego."),
    ("o Império Romano",
     "O Império Romano foi um dos maiores impérios da Antiguidade, com centro na cidade de Roma.",
     "Roma começou como uma pequena cidade na Itália e chegou a dominar toda a região do mar Mediterrâneo. Os romanos "
     "construíram estradas, pontes, aquedutos e cidades, e criaram leis que influenciam o direito até hoje. O latim, "
     "a língua dos romanos, deu origem ao português, ao espanhol, ao francês e ao italiano. O Império Romano do "
     "Ocidente terminou em 476."),
    ("a Idade Média",
     "Idade Média é o período da história europeia entre os anos 476 e 1453, aproximadamente.",
     "A Idade Média começou com o fim do Império Romano do Ocidente, em 476, e terminou por volta de 1453. Na Europa, a "
     "sociedade era organizada no feudalismo: os senhores tinham as terras e os camponeses trabalhavam nelas. A Igreja "
     "Católica tinha grande poder. Foi a época dos castelos, dos cavaleiros e das primeiras universidades. Ao mesmo "
     "tempo, o mundo árabe vivia um grande desenvolvimento das ciências."),
    ("os vikings",
     "Os vikings eram povos navegadores da Escandinávia que viajaram e atacaram várias regiões entre os séculos oito e onze.",
     "Os vikings vieram da região onde hoje ficam Noruega, Suécia e Dinamarca. Eram ótimos navegadores e construíam "
     "barcos compridos e rápidos. Atacaram cidades e mosteiros, mas também foram comerciantes e colonizadores. Chegaram "
     "à Islândia, à Groenlândia e, por volta do ano mil, à América do Norte, séculos antes de Colombo. Ao contrário do "
     "que se vê em desenhos, não há provas de que usassem capacetes com chifres."),
    ("as Grandes Navegações",
     "As Grandes Navegações foram as viagens marítimas dos europeus nos séculos quinze e dezesseis, que chegaram a novas terras.",
     "Nos séculos quinze e dezesseis, Portugal e Espanha lideraram viagens pelo oceano em busca de novas rotas de "
     "comércio. Cristóvão Colombo chegou à América em 1492, Vasco da Gama chegou à Índia contornando a África em 1498 e "
     "Pedro Álvares Cabral chegou ao Brasil em 1500. A expedição de Fernão de Magalhães fez a primeira volta ao mundo. "
     "Essas viagens ligaram continentes, mas também trouxeram conquista, escravidão e doenças aos povos nativos."),
    ("o Renascimento",
     "O Renascimento foi um movimento cultural e artístico europeu dos séculos catorze a dezesseis, que começou na Itália.",
     "O Renascimento valorizou o ser humano, a razão e a cultura da Grécia e de Roma antigas. Começou nas cidades "
     "italianas, como Florença, e se espalhou pela Europa. Foi a época de artistas como Leonardo da Vinci, autor da "
     "Mona Lisa, Michelangelo, que pintou o teto da Capela Sistina, e Rafael. A invenção da imprensa por Gutenberg "
     "ajudou a espalhar livros e ideias."),
    ("a Revolução Francesa",
     "A Revolução Francesa, iniciada em 1789, derrubou a monarquia absoluta na França.",
     "A Revolução Francesa começou em 1789, numa França com fome, crise e privilégios para o clero e a nobreza. Em 14 "
     "de julho, o povo de Paris tomou a prisão da Bastilha. A revolução aprovou a Declaração dos Direitos do Homem e "
     "do Cidadão, acabou com a monarquia absoluta e espalhou o lema liberdade, igualdade e fraternidade. Também teve "
     "um período de muita violência, chamado Terror."),
    ("a Revolução Industrial",
     "A Revolução Industrial foi a passagem da produção manual para a produção com máquinas, a partir do século dezoito, na Inglaterra.",
     "A Revolução Industrial começou na Inglaterra, no século dezoito, com o uso de máquinas a vapor e o surgimento das "
     "fábricas. A produção de tecidos e outros produtos aumentou muito, surgiram as ferrovias e as cidades cresceram. "
     "No início, os operários, inclusive crianças, trabalhavam muitas horas por pouco dinheiro, o que levou à criação "
     "dos sindicatos e das leis trabalhistas."),
    ("a Primeira Guerra Mundial",
     "A Primeira Guerra Mundial aconteceu de 1914 a 1918 e envolveu as grandes potências da época.",
     "A Primeira Guerra Mundial começou em 1914, depois do assassinato do herdeiro do trono da Áustria-Hungria, num "
     "momento de disputa entre potências europeias. De um lado estavam países como França, Reino Unido e Rússia; do "
     "outro, Alemanha e Áustria-Hungria. A guerra foi marcada pelas trincheiras e por armas novas, como tanques e "
     "gases venenosos. Terminou em 1918, com milhões de mortos."),
    ("a Segunda Guerra Mundial",
     "A Segunda Guerra Mundial aconteceu de 1939 a 1945 e foi o conflito mais mortal da história.",
     "A Segunda Guerra Mundial começou em 1939, quando a Alemanha nazista invadiu a Polônia. De um lado estavam os "
     "Aliados, como Reino Unido, União Soviética e Estados Unidos; do outro, o Eixo, formado por Alemanha, Itália e "
     "Japão. Morreram dezenas de milhões de pessoas, e o regime nazista cometeu o Holocausto. O Brasil enviou soldados "
     "da Força Expedicionária Brasileira para lutar na Itália. A guerra acabou em 1945."),
    ("o Holocausto",
     "O Holocausto foi o genocídio de cerca de seis milhões de judeus pelo regime nazista durante a Segunda Guerra Mundial.",
     "O Holocausto foi a perseguição e o assassinato sistemático de cerca de seis milhões de judeus pela Alemanha "
     "nazista e seus colaboradores, principalmente durante a Segunda Guerra Mundial. Ciganos, pessoas com deficiência, homossexuais e opositores também "
     "foram perseguidos e mortos. Muitas vítimas foram levadas para campos de concentração e de extermínio, como "
     "Auschwitz. Lembrar o Holocausto é importante para que algo assim nunca mais aconteça."),
    ("a Guerra Fria",
     "A Guerra Fria foi a disputa entre Estados Unidos e União Soviética, de 1947 a 1991, sem guerra direta entre os dois.",
     "Depois da Segunda Guerra, Estados Unidos e União Soviética disputaram a influência sobre o mundo. Os Estados "
     "Unidos defendiam o capitalismo, e a União Soviética, o socialismo de modelo soviético. Os dois não se enfrentaram "
     "diretamente, mas disputaram uma corrida armamentista e a corrida espacial e apoiaram lados opostos em guerras em "
     "outros países. A Guerra Fria terminou com o fim da União Soviética, em 1991."),
    ("o Muro de Berlim",
     "O Muro de Berlim dividiu a cidade de Berlim de 1961 a 1989 e era um símbolo da Guerra Fria.",
     "O Muro de Berlim foi construído em 1961 pela Alemanha Oriental, socialista, para impedir que seus moradores "
     "fugissem para Berlim Ocidental. Ele separou famílias e amigos por quase trinta anos, e muitas pessoas morreram "
     "tentando atravessá-lo. Em 9 de novembro de 1989, a fronteira foi aberta e o povo começou a derrubar o muro. Um "
     "ano depois, a Alemanha foi reunificada."),
    ("a corrida espacial",
     "A corrida espacial foi a competição entre a União Soviética e os Estados Unidos pela exploração do espaço.",
     "Durante a Guerra Fria, soviéticos e norte-americanos competiram para mostrar sua tecnologia no espaço. Em 1957, a "
     "União Soviética lançou o Sputnik 1, o primeiro satélite artificial, e depois o Sputnik 2, com a cadela Laika. Em "
     "1961, Iuri Gagarin foi o primeiro ser humano no espaço. Em 1969, os Estados Unidos levaram os primeiros "
     "astronautas à Lua, com a Apollo 11."),
    ("a chegada do homem à Lua",
     "Os primeiros seres humanos pisaram na Lua em 20 de julho de 1969, na missão Apollo 11.",
     "Em 20 de julho de 1969, os astronautas norte-americanos Neil Armstrong e Buzz Aldrin pousaram na Lua com o módulo "
     "lunar da missão Apollo 11, enquanto Michael Collins ficava em órbita. Armstrong foi o primeiro a pisar no solo "
     "lunar. Milhões de pessoas assistiram pela televisão. Até 1972, doze astronautas caminharam na Lua."),
    ("a ONU",
     "A ONU, Organização das Nações Unidas, foi criada em 1945 para promover a paz e a cooperação entre os países.",
     "A Organização das Nações Unidas foi criada em 1945, logo depois da Segunda Guerra Mundial, para evitar novas "
     "guerras e estimular a cooperação entre os países. Sua sede fica em Nova York, e quase todos os países do mundo "
     "fazem parte dela. A ONU tem agências como a Unicef, para a infância, a OMS, para a saúde, e a Unesco, para a "
     "educação e a cultura."),
    ("a Declaração Universal dos Direitos Humanos",
     "A Declaração Universal dos Direitos Humanos foi aprovada pela ONU em 1948 e lista direitos de todas as pessoas.",
     "Aprovada pela ONU em 10 de dezembro de 1948, a Declaração Universal dos Direitos Humanos afirma que todas as "
     "pessoas nascem livres e iguais em dignidade e direitos. Ela lista direitos como a vida, a liberdade, a "
     "educação, o trabalho, a liberdade de expressão e o julgamento justo, e proíbe a escravidão e a tortura. É um dos "
     "documentos mais traduzidos do mundo."),
    ("a Revolução Russa",
     "A Revolução Russa de 1917 derrubou o czar e levou os bolcheviques, liderados por Lênin, ao poder.",
     "Em 1917, a Rússia vivia fome e derrotas na Primeira Guerra Mundial. Em fevereiro, o czar Nicolau II foi derrubado; "
     "em outubro, os bolcheviques, liderados por Lênin, tomaram o poder. Depois de uma guerra civil, foi criada em "
     "1922 a União Soviética, o primeiro Estado socialista, governado por um partido único."),
    ("a União Soviética",
     "A União Soviética foi um país socialista que existiu de 1922 a 1991, com capital em Moscou.",
     "A União das Repúblicas Socialistas Soviéticas reunia a Rússia e outras repúblicas, com capital em Moscou. O "
     "Estado controlava a economia e era governado por um só partido, o Comunista. O país se industrializou "
     "rapidamente e teve grandes conquistas espaciais, como o primeiro satélite e o primeiro astronauta, mas também "
     "teve repressão, falta de liberdade e períodos de fome. Ela se dissolveu em 1991."),
]

TEMAS_SOCIEDADE = [
    ("o capitalismo",
     "O capitalismo é um sistema econômico baseado na propriedade privada, no mercado e na busca do lucro.",
     "No capitalismo, empresas e meios de produção, como fábricas e terras, pertencem principalmente a pessoas e "
     "empresas privadas, que produzem para vender e ter lucro. Os preços se formam no mercado, pela oferta e pela "
     "procura, e os trabalhadores recebem salários. Seus defensores destacam a liberdade econômica, a concorrência e "
     "a inovação; seus críticos apontam a desigualdade e as crises. Hoje, a maioria dos países tem economias de "
     "mercado com alguma participação do Estado."),
    ("o comunismo",
     "O comunismo é uma ideologia que propõe uma sociedade sem classes sociais e sem propriedade privada dos meios de produção.",
     "O comunismo foi formulado principalmente por Karl Marx e Friedrich Engels, que publicaram o Manifesto Comunista "
     "em 1848. A ideia é uma sociedade sem classes, em que os meios de produção sejam de todos. No século vinte, "
     "países como a União Soviética, a China e Cuba foram governados por partidos comunistas, com o Estado "
     "controlando a economia. Esses regimes tiveram avanços em educação e indústria, mas também partido único, "
     "censura e repressão, por isso o tema divide muitas opiniões."),
    ("o socialismo",
     "Socialismo é o conjunto de ideias que defende a propriedade coletiva ou social dos meios de produção e a redução das desigualdades.",
     "O socialismo surgiu no século dezenove como resposta às duras condições dos trabalhadores na Revolução "
     "Industrial. Ele defende que a riqueza e os meios de produção sejam controlados de forma coletiva, pelo Estado "
     "ou pelos trabalhadores, para diminuir as desigualdades. Há muitas correntes: para Marx, era uma fase de "
     "transição para o comunismo; já os partidos socialistas democráticos defendem mudanças pelo voto. Os críticos "
     "dizem que o controle estatal reduz a eficiência e a liberdade."),
    ("a social-democracia",
     "Social-democracia é a corrente que combina economia de mercado, democracia e um Estado que garante serviços e proteção social.",
     "A social-democracia aceita a economia de mercado e a democracia, mas defende que o Estado reduza as "
     "desigualdades com impostos, saúde e educação públicas, aposentadorias e proteção aos trabalhadores. Países "
     "nórdicos, como Suécia, Noruega e Dinamarca, são exemplos conhecidos desse modelo, chamado de Estado de "
     "bem-estar social. Os críticos apontam os impostos altos e o peso do Estado."),
    ("o liberalismo",
     "Liberalismo é a corrente que defende a liberdade individual, o poder limitado do Estado e a economia de mercado.",
     "O liberalismo surgiu nos séculos dezessete e dezoito, com pensadores como John Locke e Adam Smith. No plano "
     "político, defende direitos individuais, separação dos poderes e governos limitados por leis. No plano "
     "econômico, defende o livre mercado, a propriedade privada e pouca interferência do Estado. Os críticos dizem "
     "que, sem regras e proteção social, o mercado pode aumentar as desigualdades."),
    ("o anarquismo",
     "Anarquismo é a corrente política que defende uma sociedade sem Estado e sem hierarquias impostas.",
     "O anarquismo defende que as pessoas podem se organizar de forma livre e cooperativa, sem governo, sem polícia e "
     "sem patrões. Pensadores como Proudhon e Bakunin desenvolveram essas ideias no século dezenove. No Brasil, "
     "anarquistas participaram das primeiras greves operárias, no início do século vinte. Os críticos consideram a "
     "proposta difícil de pôr em prática. Anarquia, no sentido de bagunça, é um uso popular diferente do sentido político."),
    ("o fascismo",
     "Fascismo é um regime autoritário e nacionalista, criado por Benito Mussolini na Itália, em 1922.",
     "O fascismo surgiu na Itália, com Benito Mussolini, que governou de 1922 a 1943. Era um regime de partido único, "
     "com culto ao líder, nacionalismo extremo, censura, violência contra opositores e controle da sociedade pelo "
     "Estado. Ele inspirou outros movimentos autoritários na Europa, como o nazismo. Hoje, a palavra também é usada "
     "para criticar ideias autoritárias."),
    ("o nazismo",
     "O nazismo foi o regime de Adolf Hitler na Alemanha, de 1933 a 1945, baseado no racismo e no autoritarismo.",
     "O nazismo governou a Alemanha de 1933 a 1945, sob Adolf Hitler. Era um regime de partido único, com censura, "
     "propaganda e perseguição a opositores, baseado na falsa ideia de superioridade racial. O nazismo levou a "
     "Alemanha à Segunda Guerra Mundial e cometeu o Holocausto. Em muitos países, inclusive no Brasil, fazer "
     "propaganda nazista é crime."),
    ("a ditadura",
     "Ditadura é um governo em que o poder fica concentrado num líder ou grupo, sem eleições livres e com limites à liberdade.",
     "Numa ditadura, o governo não é escolhido em eleições livres, ou elas existem só de fachada. O poder fica nas "
     "mãos de uma pessoa, de um partido ou dos militares, e costuma haver censura, perseguição a opositores e "
     "restrições à imprensa e aos direitos. O Brasil viveu ditaduras no Estado Novo, de 1937 a 1945, e no regime "
     "militar, de 1964 a 1985."),
    ("a monarquia",
     "Monarquia é a forma de governo em que o chefe de Estado é um rei ou uma rainha, normalmente por herança.",
     "Na monarquia, o chefe de Estado é um monarca, como um rei, uma rainha ou um imperador, que em geral ocupa o "
     "cargo por toda a vida e o passa aos herdeiros. Nas monarquias absolutas, o monarca tem quase todo o poder. Nas "
     "monarquias constitucionais, como Reino Unido, Espanha e Japão, quem governa é um primeiro-ministro, e o monarca "
     "tem papel mais simbólico. O Brasil foi uma monarquia de 1822 a 1889."),
    ("a república",
     "República é a forma de governo em que o chefe de Estado é escolhido por um tempo determinado, e não por herança.",
     "Na república, quem ocupa o cargo de chefe de Estado é escolhido, geralmente por eleições, para um mandato com "
     "prazo para acabar. A palavra vem do latim e significa coisa pública. O Brasil é uma república desde 1889 e "
     "adota o presidencialismo, em que o presidente é ao mesmo tempo chefe de Estado e de governo."),
    ("as eleições",
     "Eleições são o processo em que os cidadãos escolhem, pelo voto, os seus representantes.",
     "Nas eleições, os cidadãos votam para escolher presidente, governadores, prefeitos, senadores, deputados e "
     "vereadores. No Brasil, o voto é secreto e feito em urnas eletrônicas. Ele é obrigatório para quem tem de 18 a "
     "70 anos e opcional para jovens de 16 e 17 anos e para quem tem mais de 70. Eleições livres e periódicas são uma "
     "das bases da democracia."),
    ("o voto",
     "O voto é a forma pela qual o cidadão escolhe seus representantes e participa das decisões.",
     "O voto é um direito e uma responsabilidade do cidadão. No Brasil, ele é secreto, para que cada pessoa escolha "
     "sem pressão. Por muito tempo, só homens com renda podiam votar; as mulheres conquistaram esse direito em 1932, e "
     "as pessoas analfabetas, em 1985. Antes de votar, é bom conhecer as propostas e o histórico dos candidatos."),
    ("os três poderes",
     "Os três poderes são o Executivo, o Legislativo e o Judiciário, que dividem as funções do Estado.",
     "A ideia de dividir o poder em três partes foi defendida pelo pensador francês Montesquieu, para evitar abusos. "
     "O Executivo governa e administra, com o presidente, os governadores e os prefeitos. O Legislativo faz as leis e "
     "fiscaliza o governo, com deputados, senadores e vereadores. O Judiciário julga e garante que as leis sejam "
     "cumpridas. Os poderes devem ser independentes e harmônicos entre si."),
    ("o Congresso Nacional",
     "O Congresso Nacional é o Poder Legislativo do Brasil, formado pela Câmara dos Deputados e pelo Senado Federal.",
     "O Congresso Nacional fica em Brasília, num prédio projetado por Oscar Niemeyer. Ele é formado pela Câmara dos "
     "Deputados, com 513 deputados que representam a população, e pelo Senado Federal, com 81 senadores, três por "
     "estado e pelo Distrito Federal. O Congresso faz as leis, aprova o orçamento e fiscaliza o governo."),
    ("os impostos",
     "Impostos são valores que pessoas e empresas pagam ao governo para financiar os serviços públicos.",
     "Os impostos são cobrados sobre a renda, o consumo e o patrimônio. No Brasil, alguns exemplos são o Imposto de "
     "Renda, o IPTU, sobre imóveis, o IPVA, sobre veículos, e os impostos embutidos nos preços dos produtos. Com esse "
     "dinheiro, o governo paga escolas, hospitais, estradas, segurança e aposentadorias. Muita gente discute se os "
     "impostos são justos e se o dinheiro é bem usado."),
    ("a inflação",
     "Inflação é o aumento geral e contínuo dos preços, que faz o dinheiro comprar menos.",
     "Quando há inflação, os preços sobem e o mesmo dinheiro compra menos coisas. Ela pode acontecer quando a procura "
     "cresce mais que a produção, quando os custos sobem ou quando se emite dinheiro demais. O Brasil teve "
     "hiperinflação nos anos 1980 e no início dos anos 1990, com preços subindo todos os dias, até o Plano Real, de "
     "1994. Para controlar a inflação, o Banco Central costuma mexer na taxa de juros."),
    ("o Plano Real",
     "O Plano Real foi o plano econômico de 1994 que criou o real e acabou com a hiperinflação no Brasil.",
     "Antes de 1994, o Brasil tinha inflação altíssima: os preços mudavam quase todo dia e a moeda trocou de nome "
     "várias vezes. O Plano Real criou uma unidade de transição, a URV, e depois a nova moeda, o real, lançado em 1º "
     "de julho de 1994. A inflação caiu muito, o que ajudou principalmente os mais pobres, que não tinham como "
     "proteger o seu dinheiro."),
    ("o dinheiro",
     "Dinheiro é o meio usado para comprar e vender coisas e para medir o valor delas.",
     "Antes do dinheiro, as pessoas trocavam mercadorias, o que se chama escambo. Depois vieram as moedas de metal, as "
     "notas de papel e, hoje, o dinheiro digital, como o cartão e o Pix. O dinheiro serve para trocar, medir o valor "
     "das coisas e guardar riqueza. A moeda do Brasil é o real, desde 1994."),
    ("os bancos",
     "Bancos são empresas que guardam dinheiro, fazem pagamentos e emprestam dinheiro cobrando juros.",
     "Os bancos guardam o dinheiro das pessoas e das empresas, fazem pagamentos e transferências e emprestam dinheiro, "
     "cobrando juros. Eles também pagam rendimentos a quem deixa dinheiro aplicado. O Banco Central é o banco do "
     "governo, que cuida da moeda e fiscaliza os outros bancos. Antes de pegar um empréstimo, é importante comparar os "
     "juros e ver se a parcela cabe no orçamento."),
    ("os juros",
     "Juros são o preço pago por usar dinheiro emprestado, ou o rendimento de quem empresta.",
     "Quando alguém pega dinheiro emprestado, devolve mais do que recebeu: essa diferença são os juros. Quando alguém "
     "guarda dinheiro numa aplicação, recebe juros como rendimento. Nos juros compostos, os juros de cada mês se "
     "somam ao valor e também rendem juros, e por isso uma dívida no cartão de crédito pode crescer muito rápido."),
    ("a poupança",
     "Poupar é guardar parte do dinheiro que se ganha para usar no futuro.",
     "Poupar é separar uma parte do que se ganha em vez de gastar tudo. Ter uma reserva ajuda em emergências, como uma "
     "doença ou a perda do emprego, e permite realizar planos, como uma viagem ou um curso. Uma dica é guardar logo "
     "que recebe, mesmo que seja pouco. A caderneta de poupança é uma aplicação simples, mas existem outras que "
     "podem render mais."),
    ("o desemprego",
     "Desemprego é a situação de quem quer e pode trabalhar, mas não encontra emprego.",
     "O desemprego acontece quando há mais pessoas procurando trabalho do que vagas disponíveis. Ele aumenta em crises "
     "econômicas e traz dificuldades para as famílias, como a falta de renda e a ansiedade. Estudar, fazer cursos e "
     "procurar oportunidades em agências de emprego ajudam quem está procurando. O seguro-desemprego ajuda por um "
     "tempo quem foi demitido sem justa causa."),
    ("a desigualdade social",
     "Desigualdade social é a diferença de renda, oportunidades e acesso a direitos entre as pessoas de uma sociedade.",
     "A desigualdade social aparece quando algumas pessoas têm muito e outras têm muito pouco: renda, moradia, "
     "educação, saúde e oportunidades. O Brasil está entre os países mais desiguais do mundo. Entre as causas "
     "apontadas estão a história de escravidão, a concentração de terras e diferenças na qualidade da educação. "
     "Como diminuí-la é um dos grandes debates da política."),
    ("a globalização",
     "Globalização é a maior integração entre os países no comércio, na tecnologia, na cultura e nas comunicações.",
     "Com a globalização, produtos, informações, pessoas e dinheiro circulam com mais facilidade pelo mundo. Um celular "
     "pode ser projetado num país e montado em outro com peças de vários lugares. A internet aproxima culturas. Os "
     "defensores dizem que ela aumenta o comércio e o acesso a produtos; os críticos dizem que pode prejudicar "
     "indústrias locais e concentrar riqueza."),
    ("os direitos humanos",
     "Direitos humanos são os direitos básicos de todas as pessoas, como a vida, a liberdade e a igualdade.",
     "Os direitos humanos valem para todas as pessoas, sem distinção de cor, origem, religião, gênero ou opinião. "
     "Entre eles estão o direito à vida, à liberdade, à educação, à saúde, ao trabalho e a um julgamento justo, e a "
     "proibição da tortura e da escravidão. Eles foram reunidos na Declaração Universal dos Direitos Humanos, de 1948, "
     "e estão na Constituição brasileira."),
    ("a cidadania",
     "Cidadania é o conjunto de direitos e deveres de uma pessoa como membro de uma sociedade.",
     "Ser cidadão é ter direitos, como votar, estudar, ter saúde e se expressar, e também deveres, como respeitar as "
     "leis e as outras pessoas, pagar impostos e cuidar do que é público. Exercer a cidadania é participar da vida da "
     "comunidade: votar com consciência, cobrar os governantes, ajudar o bairro e respeitar a diversidade."),
    ("o racismo",
     "Racismo é o preconceito e a discriminação contra pessoas por causa da sua cor ou origem étnica.",
     "O racismo trata pessoas como inferiores por causa da cor da pele ou da origem. Ele aparece em ofensas, mas "
     "também em desvantagens no emprego, na escola e no tratamento pela polícia, o que se chama racismo estrutural. "
     "No Brasil, o racismo é crime inafiançável e imprescritível, segundo a Constituição. Combater o racismo é "
     "dever de todos."),
    ("o preconceito",
     "Preconceito é uma opinião negativa formada sobre alguém ou um grupo sem conhecê-lo, só por ser de determinado jeito.",
     "O preconceito é julgar antes de conhecer, por causa da cor, da origem, da religião, do sotaque, do corpo, da "
     "deficiência, da orientação sexual ou da condição social de alguém. Quando vira ação, como excluir ou ofender, "
     "chama-se discriminação. Conviver com pessoas diferentes, ouvir as suas histórias e se informar ajudam a "
     "combater o preconceito."),
    ("o bullying",
     "Bullying são agressões repetidas e intencionais, físicas ou verbais, contra alguém que tem dificuldade de se defender.",
     "O bullying acontece quando uma pessoa ou um grupo humilha, ameaça, exclui ou agride outra pessoa várias vezes, "
     "de propósito. Pode acontecer na escola, no trabalho ou pela internet, quando se chama cyberbullying. Quem sofre "
     "bullying pode ficar triste, ansioso e com medo. É importante contar a um adulto de confiança, um professor ou a "
     "família. Quem presencia também pode ajudar, não participando e pedindo ajuda."),
    ("a sustentabilidade",
     "Sustentabilidade é usar os recursos do planeta de forma a atender às necessidades de hoje sem prejudicar as futuras gerações.",
     "Ser sustentável é cuidar do meio ambiente, da sociedade e da economia ao mesmo tempo. Isso inclui economizar "
     "água e energia, reduzir o lixo, reciclar, preferir transportes menos poluentes, proteger as florestas e "
     "produzir de forma responsável. Empresas, governos e cada pessoa podem contribuir com escolhas do dia a dia."),
    ("a economia",
     "Economia é a ciência que estuda como as pessoas e os países produzem, distribuem e consomem bens e serviços.",
     "A economia estuda como a sociedade decide o que produzir, como produzir e para quem, já que os recursos são "
     "limitados. Ela trata de assuntos como preços, salários, empregos, impostos, juros, inflação e comércio entre "
     "países. A palavra economia também é usada no sentido de gastar menos, como economizar água ou dinheiro."),
    ("o PIB",
     "PIB, Produto Interno Bruto, é a soma do valor de todos os bens e serviços produzidos num país num período.",
     "O Produto Interno Bruto mede o tamanho da economia de um país. Ele soma tudo o que foi produzido num período, "
     "como alimentos, carros, roupas, serviços de saúde e de transporte. Quando o PIB cresce, em geral há mais "
     "empregos e renda. Mas o PIB não mostra tudo: não mede, por exemplo, como a riqueza é dividida nem a qualidade de vida."),
    ("a política",
     "Política é a atividade de organizar a vida em sociedade e tomar decisões coletivas.",
     "A política trata das decisões que afetam todos: as leis, os impostos, a saúde, a educação e a segurança. Ela "
     "acontece nos governos e nos parlamentos, mas também nas associações de bairro, nos sindicatos e nas escolas. "
     "Numa democracia, as pessoas participam votando, debatendo e cobrando os representantes. Discordar faz parte da "
     "política, e o respeito às opiniões diferentes é essencial."),
    ("os partidos políticos",
     "Partidos políticos são organizações de pessoas com ideias parecidas que disputam eleições para governar.",
     "Os partidos reúnem pessoas que compartilham ideias e propostas para o país. No Brasil, para ser candidato, é "
     "preciso ser filiado a um partido. Costuma-se falar em partidos de esquerda, que dão mais ênfase à igualdade e ao "
     "papel do Estado, de direita, que dão mais ênfase à liberdade econômica e à ordem, e de centro, entre os dois."),
    ("a esquerda e a direita na política",
     "Esquerda e direita são formas de classificar ideias políticas: a esquerda enfatiza a igualdade, e a direita, a liberdade econômica e a tradição.",
     "Os termos esquerda e direita nasceram na Revolução Francesa, por causa do lugar onde os grupos se sentavam na "
     "assembleia. Em geral, a esquerda defende mais ação do Estado para reduzir desigualdades, e a direita defende "
     "mais liberdade de mercado, menos impostos e valores tradicionais. Há muitas posições no meio, o centro, e cada "
     "pessoa pode concordar com ideias de lados diferentes."),
    ("o feminismo",
     "Feminismo é o movimento que defende a igualdade de direitos e oportunidades entre mulheres e homens.",
     "O feminismo lutou por conquistas como o direito das mulheres ao voto, ao estudo e ao trabalho, a igualdade de "
     "salários e o combate à violência contra a mulher. No Brasil, as mulheres conquistaram o voto em 1932, e a Lei "
     "Maria da Penha, de 2006, combate a violência doméstica. Há várias correntes feministas, com ideias diferentes "
     "sobre como alcançar a igualdade."),
    ("a religião",
     "Religião é um conjunto de crenças, práticas e valores ligados ao sagrado e ao sentido da vida.",
     "As religiões tentam responder a perguntas como de onde viemos e qual é o sentido da vida, e reúnem pessoas em "
     "rituais, festas e comunidades. Entre as maiores do mundo estão o cristianismo, o islamismo, o hinduísmo e o "
     "budismo. No Brasil, há católicos, evangélicos, espíritas, seguidores de religiões de matriz africana, como o "
     "candomblé e a umbanda, e muitas outras crenças, além de pessoas sem religião. O Brasil é um Estado laico, com liberdade de crença."),
    ("a filosofia",
     "Filosofia é a busca de conhecimento por meio da razão sobre questões como a verdade, a ética, a existência e o saber.",
     "A palavra filosofia vem do grego e quer dizer amor à sabedoria. Os filósofos fazem perguntas profundas: o que é "
     "a verdade, o que é justo, o que podemos conhecer, como devemos viver. A filosofia ocidental começou na Grécia "
     "Antiga, com pensadores como Sócrates, Platão e Aristóteles, mas houve filosofia também na China, na Índia e em "
     "outras culturas."),
    ("a ética",
     "Ética é a reflexão sobre o que é certo e errado e sobre como devemos agir.",
     "A ética procura entender quais são as boas ações e por quê. Ela aparece no dia a dia: falar a verdade, cumprir "
     "promessas, respeitar os outros, não prejudicar ninguém. Também existem códigos de ética profissional, como os "
     "de médicos e jornalistas. Muitas vezes, pessoas diferentes chegam a conclusões diferentes, e por isso a ética "
     "envolve diálogo."),
    ("a democracia",
     "Democracia é a forma de governo em que o poder vem do povo, que escolhe seus representantes pelo voto.",
     "A palavra democracia vem do grego e quer dizer governo do povo. Na democracia, os cidadãos escolhem seus "
     "governantes em eleições livres, podem criticar o governo e têm direitos garantidos por lei, como a liberdade de "
     "expressão e de imprensa. Os poderes são separados e ninguém está acima da lei. A democracia exige "
     "participação, respeito às regras e convivência com quem pensa diferente."),
    ("o trabalho infantil",
     "Trabalho infantil é o trabalho feito por crianças e adolescentes abaixo da idade permitida por lei.",
     "No Brasil, o trabalho é proibido para menores de 16 anos, exceto como aprendiz a partir dos 14, e trabalhos "
     "perigosos ou noturnos são proibidos até os 18. O trabalho infantil prejudica a saúde, os estudos e a infância. "
     "Lugar de criança é na escola e brincando. Casos de trabalho infantil podem ser denunciados pelo Disque 100."),
    ("o Estatuto da Criança e do Adolescente",
     "O Estatuto da Criança e do Adolescente, o ECA, é a lei de 1990 que garante os direitos de crianças e adolescentes no Brasil.",
     "O ECA foi criado em 1990 e diz que crianças e adolescentes têm direito à vida, à saúde, à educação, ao lazer, ao "
     "respeito e à convivência familiar, com prioridade absoluta. Ele também protege contra a violência, a exploração "
     "e o trabalho infantil e criou os conselhos tutelares, que cuidam desses direitos nas cidades."),
]
