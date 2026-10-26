"""Resumos escritos à mão (parte 7): textos novos variados (e-mails, resenhas, notícias, opiniões, receitas,
instruções e explicações curtas).

Mesmo formato de resumos4.py: (texto, uma frase, duas frases, três tópicos).
"""

TEXTOS = [
    ("Bom dia, equipe.\n\nInformo que a reunião de planejamento marcada para quarta-feira foi transferida para "
     "sexta, às 10h, na sala 3. A mudança foi necessária porque a diretora estará viajando no meio da semana e quer "
     "participar da discussão sobre o orçamento do próximo semestre.\n\n"
     "Peço que cada setor traga uma lista das principais despesas previstas e, se possível, sugestões de onde "
     "economizar. A reunião deve durar cerca de duas horas. Quem não puder comparecer deve avisar até quinta-feira e "
     "mandar as informações por e-mail. Obrigado pela compreensão.\n\nAtenciosamente,\nRoberto",
     "Roberto avisa que a reunião de planejamento passou para sexta, às 10h, e pede que cada setor traga as despesas "
     "previstas.",
     "A mudança aconteceu porque a diretora estará viajando e quer discutir o orçamento. Quem não puder ir deve "
     "avisar até quinta e mandar as informações por e-mail.",
     ["A reunião passou para sexta, às 10h.",
      "O tema é o orçamento do semestre.",
      "Cada setor deve levar suas despesas."]),
    ("Assisti ao novo filme do diretor no fim de semana e saí do cinema dividido. A fotografia é linda: as cenas do "
     "sertão, com o céu alaranjado no fim da tarde, parecem pinturas. A atriz principal também está ótima, "
     "principalmente nas cenas em que quase não fala e diz tudo com o olhar.\n\n"
     "O problema é o roteiro. A história demora muito para começar, e a segunda metade se perde em personagens que "
     "aparecem e somem sem explicação. São quase três horas de filme, e pelo menos quarenta minutos poderiam ter "
     "sido cortados. Vale a pena pela beleza e pela atuação, mas é preciso paciência.",
     "Para o autor da resenha, o filme tem fotografia e atuação excelentes, mas um roteiro lento e longo demais.",
     "As cenas do sertão são lindas, e a atriz principal se destaca. A história demora a começar e se perde na "
     "segunda metade, com quase três horas de duração.",
     ["A fotografia é bonita.",
      "A atriz principal está ótima.",
      "O roteiro é lento e longo demais."]),
    ("Para fazer um brigadeiro, coloque numa panela uma lata de leite condensado, uma colher de sopa de manteiga e "
     "três colheres de sopa de chocolate em pó. Leve ao fogo baixo e mexa sem parar, com uma colher de pau, para não "
     "grudar no fundo.\n\n"
     "Depois de uns dez minutos, a massa começa a engrossar. Ela está no ponto quando, ao inclinar a panela, desgruda "
     "do fundo inteira. Despeje num prato untado com manteiga e espere esfriar. Para enrolar, passe um pouco de "
     "manteiga nas mãos, faça bolinhas e passe no chocolate granulado. Se preferir comer de colher, é só tirar do "
     "fogo um pouco antes do ponto.",
     "O brigadeiro é feito cozinhando leite condensado, manteiga e chocolate em pó, mexendo sempre, até a massa "
     "desgrudar da panela.",
     "Depois de esfriar, a massa é enrolada com as mãos untadas e passada no granulado. Para comer de colher, basta "
     "tirar do fogo antes do ponto.",
     ["Use leite condensado, manteiga e chocolate.",
      "Mexa sempre em fogo baixo.",
      "O ponto é quando desgruda da panela."]),
    ("O governo do estado anunciou a construção de um novo hospital regional em São Bento do Sul, que vai atender "
     "moradores de doze municípios. A obra deve começar em março e levar dois anos. O hospital terá 150 leitos, "
     "pronto-socorro, centro cirúrgico e uma ala para tratamento de câncer.\n\n"
     "Hoje, os pacientes da região precisam viajar mais de 200 quilômetros até a capital para fazer cirurgias e "
     "tratamentos mais complexos. Os prefeitos comemoraram a notícia, mas lembraram que o maior desafio será contratar "
     "médicos e enfermeiros. O governo afirmou que vai abrir concurso público antes da inauguração.",
     "O estado vai construir um hospital regional com 150 leitos em São Bento do Sul, para atender doze municípios "
     "que hoje dependem da capital.",
     "A obra começa em março e deve durar dois anos, com pronto-socorro, cirurgias e tratamento de câncer. O desafio "
     "será contratar profissionais, e o governo promete concurso.",
     ["O hospital terá 150 leitos.",
      "Vai atender doze municípios.",
      "A falta de médicos é o maior desafio."]),
    ("Muita gente acredita que é preciso beber oito copos de água por dia, mas essa regra não vale para todo mundo. "
     "A quantidade de água de que cada pessoa precisa depende do peso, do clima, da atividade física e até da "
     "alimentação. Frutas, verduras, sopas e sucos também fornecem água.\n\n"
     "Em geral, a sede é um bom guia para pessoas saudáveis. A cor da urina também ajuda: clara indica que a "
     "hidratação está boa, e escura, que é preciso beber mais. Idosos, porém, sentem menos sede e devem beber água "
     "mesmo sem vontade. Em dias quentes e durante exercícios, a necessidade aumenta bastante.",
     "A necessidade de água varia de pessoa para pessoa, e a sede e a cor da urina são bons guias para saber se é "
     "preciso beber mais.",
     "A regra dos oito copos não vale para todos, porque o peso, o clima e a comida mudam a necessidade. Idosos devem "
     "beber mesmo sem sede, e o calor aumenta a necessidade.",
     ["A quantidade ideal varia.",
      "A sede e a urina ajudam a saber.",
      "Idosos devem beber mesmo sem sede."]),
    ("Na última semana, o time do Esporte Clube Vila Rica conquistou o seu primeiro título estadual, depois de "
     "sessenta anos de história. A final foi decidida nos pênaltis, depois de um empate de 1 a 1 no tempo normal. O "
     "goleiro Juninho, de 19 anos, defendeu duas cobranças e virou herói da cidade.\n\n"
     "O clube passou por dificuldades nos últimos anos, com salários atrasados e um estádio precisando de reforma. "
     "Para montar o time, a diretoria apostou em jogadores das categorias de base da própria cidade. Milhares de "
     "torcedores foram às ruas para comemorar, e a prefeitura decretou ponto facultativo no dia seguinte.",
     "O Vila Rica conquistou o seu primeiro título estadual em sessenta anos, nos pênaltis, com um goleiro de 19 anos "
     "como herói.",
     "Depois de anos de crise, o clube montou o time com jogadores da base da cidade. Os torcedores comemoraram nas "
     "ruas, e a prefeitura deu ponto facultativo.",
     ["Foi o primeiro título em sessenta anos.",
      "O goleiro defendeu dois pênaltis.",
      "O time foi feito com jogadores da base."]),
    ("O home office, ou trabalho em casa, cresceu muito nos últimos anos. Para muitas pessoas, ele trouxe vantagens: "
     "menos tempo no trânsito, mais flexibilidade de horário e a possibilidade de ficar perto da família. Algumas "
     "empresas também economizaram com aluguel de escritórios.\n\n"
     "Mas o trabalho em casa tem desafios. Sem horários claros, muita gente acaba trabalhando mais do que antes e "
     "tendo dificuldade de desligar. A falta de contato com os colegas pode causar isolamento, e nem todos têm um "
     "espaço tranquilo em casa. Por isso, muitas empresas adotaram o modelo híbrido, com alguns dias em casa e "
     "outros no escritório.",
     "O trabalho em casa trouxe menos trânsito e mais flexibilidade, mas também excesso de trabalho e isolamento, e "
     "por isso o modelo híbrido se espalhou.",
     "As empresas economizaram com escritórios, e os funcionários ganharam tempo. Sem horários definidos, porém, "
     "muitos trabalham demais e sentem falta dos colegas.",
     ["O home office reduz o tempo no trânsito.",
      "Pode causar isolamento e excesso de trabalho.",
      "O modelo híbrido mistura os dois."]),
    ("Prezado cliente,\n\nRecebemos a sua reclamação sobre o atraso na entrega do pedido número 4521 e pedimos "
     "desculpas pelo transtorno. Verificamos que o produto ficou retido no centro de distribuição por causa de um "
     "erro no endereço cadastrado, que estava sem o número do apartamento.\n\n"
     "O endereço já foi corrigido, e a nova previsão de entrega é de até três dias úteis. Como compensação, "
     "enviamos para o seu e-mail um cupom de 15% de desconto na próxima compra. Se o pedido não chegar no novo prazo, "
     "entre em contato pelo nosso atendimento, que providenciaremos o reembolso.\n\nEquipe de atendimento",
     "A loja pede desculpas pelo atraso do pedido, causado por um erro no endereço, e promete entregá-lo em até três "
     "dias úteis com um cupom de desconto.",
     "O produto ficou parado porque faltava o número do apartamento. O endereço foi corrigido, e, se o prazo não for "
     "cumprido, o cliente terá reembolso.",
     ["O atraso foi causado por erro no endereço.",
      "A nova entrega é em até três dias úteis.",
      "O cliente ganhou um cupom de 15%."]),
    ("O Dia da Árvore é comemorado no Brasil em 21 de setembro, perto do início da primavera. A data foi escolhida "
     "para lembrar a importância das árvores e incentivar o plantio, já que muitas regiões do país começam a ter "
     "chuvas nessa época, o que favorece o crescimento das mudas.\n\n"
     "As árvores produzem oxigênio, guardam carbono, dão sombra, diminuem a temperatura das cidades e ajudam a "
     "proteger o solo e as nascentes. Nas escolas, é comum a data ser marcada com o plantio de mudas e atividades "
     "sobre o meio ambiente. Os especialistas lembram que, mais do que plantar, é preciso cuidar das mudas nos "
     "primeiros anos.",
     "O Dia da Árvore, em 21 de setembro, lembra a importância das árvores e incentiva o plantio no começo das "
     "chuvas.",
     "As árvores dão oxigênio e sombra, refrescam as cidades e protegem a água. As escolas costumam plantar mudas, "
     "mas é preciso cuidar delas depois.",
     ["A data é 21 de setembro.",
      "As árvores refrescam as cidades.",
      "Plantar exige cuidar das mudas."]),
    ("A cidade de Ouro Preto, em Minas Gerais, foi o centro da mineração de ouro no século XVIII e chegou a ser uma "
     "das cidades mais ricas das Américas. Com o ouro, foram construídas igrejas decoradas com talhas douradas e "
     "esculturas de artistas como Aleijadinho, um dos maiores nomes do barroco brasileiro.\n\n"
     "Foi lá também que aconteceu a Inconfidência Mineira, em 1789, um movimento contra os altos impostos cobrados "
     "por Portugal, que terminou com a execução de Tiradentes. Hoje, o centro histórico, com ruas de pedra e casarões "
     "coloniais, é patrimônio mundial da UNESCO e atrai turistas e estudantes da universidade federal.",
     "Ouro Preto foi o centro da mineração de ouro no século XVIII, tem igrejas barrocas com obras de Aleijadinho e "
     "foi palco da Inconfidência Mineira.",
     "A riqueza do ouro construiu igrejas decoradas, e em 1789 a cidade viu o movimento contra os impostos de "
     "Portugal. O centro histórico é patrimônio mundial.",
     ["Foi a capital do ouro no século XVIII.",
      "Tem obras de Aleijadinho.",
      "Lá aconteceu a Inconfidência Mineira."]),
    ("Se o seu celular cair na água, a primeira coisa a fazer é tirá-lo dali o mais rápido possível e desligá-lo, "
     "mesmo que ainda esteja funcionando. Não tente carregar o aparelho nem apertar os botões, porque a corrente "
     "elétrica com a água dentro pode causar curto-circuito.\n\n"
     "Retire a capinha e, se for possível, o chip e o cartão de memória. Seque a parte de fora com um pano e deixe o "
     "aparelho num lugar arejado por pelo menos um dia. A famosa dica de colocar o celular no arroz não tem muito "
     "efeito e pode deixar grãos e pó nas entradas. Não use secador de cabelo quente. Se não voltar a funcionar, "
     "leve a uma assistência técnica.",
     "Se o celular cair na água, desligue-o logo, não o carregue e deixe-o secar num lugar arejado, sem arroz e sem "
     "secador.",
     "Tire a capinha e o chip e seque a parte de fora com um pano. Se o aparelho não funcionar depois de um dia, "
     "procure uma assistência técnica.",
     ["Desligue o celular imediatamente.",
      "Não carregue nem use secador.",
      "O arroz não ajuda muito."]),
    ("A dona de casa Joana Ribeiro, de 52 anos, terminou o ensino médio neste ano, numa turma de educação de jovens "
     "e adultos. Ela tinha parado de estudar aos treze anos para trabalhar e ajudar a criar os irmãos mais novos. "
     "Durante décadas, guardou o sonho de voltar para a escola.\n\n"
     "As aulas eram à noite, depois de um dia inteiro de trabalho, e muitas vezes ela pensou em desistir. Os filhos "
     "a ajudavam com matemática, e ela os ajudava com as redações. Na formatura, Joana foi escolhida para discursar "
     "pela turma. Agora, quer fazer um curso técnico de enfermagem e diz que nunca é tarde para aprender.",
     "Aos 52 anos, Joana terminou o ensino médio estudando à noite e agora quer fazer um curso técnico de "
     "enfermagem.",
     "Ela tinha deixado a escola aos treze anos para trabalhar e ajudar a família. Com o apoio dos filhos, venceu o "
     "cansaço e discursou na formatura.",
     ["Joana parou de estudar aos treze anos.",
      "Voltou à escola na educação de adultos.",
      "Quer fazer um curso de enfermagem."]),
    ("Uma das formas mais simples de reduzir o desperdício de comida em casa é planejar as refeições da semana. "
     "Sabendo o que vai cozinhar, você compra só o necessário e evita que verduras e frutas estraguem na geladeira. "
     "Outra dica é colocar na frente os alimentos que vencem primeiro.\n\n"
     "As sobras também podem virar novas receitas: o arroz de ontem vira bolinho, o pão amanhecido vira farinha de "
     "rosca ou torrada, e as frutas maduras demais vão para vitaminas e bolos. Talos e cascas de muitos legumes podem "
     "ser usados em sopas e refogados. No Brasil, uma grande quantidade de comida vai para o lixo todos os anos, "
     "enquanto muitas pessoas passam fome.",
     "Planejar as refeições, organizar a geladeira e reaproveitar as sobras ajudam a reduzir o desperdício de comida.",
     "Comprar só o necessário e deixar à frente o que vence primeiro evita perdas. Arroz, pão e frutas maduras podem "
     "virar novas receitas.",
     ["Planeje as refeições da semana.",
      "Use primeiro o que vence antes.",
      "Sobras podem virar novas receitas."]),
    ("O pequeno museu de ciências da universidade abriu uma sala nova dedicada aos meteoritos. A peça principal é um "
     "pedaço de rocha de quase vinte quilos que caiu num sítio do interior do estado em 1998. Na época, o dono do "
     "terreno guardou a pedra no galinheiro, sem saber o que era.\n\n"
     "Só anos depois, um professor da universidade ouviu falar da pedra estranha e confirmou que se tratava de um "
     "meteorito metálico, formado principalmente de ferro e níquel. A família doou a peça ao museu. A exposição "
     "também explica como os meteoritos ajudam a entender a formação do Sistema Solar e tem uma área onde os "
     "visitantes podem tocar em fragmentos.",
     "O museu de ciências abriu uma sala sobre meteoritos, cuja peça principal passou anos guardada num galinheiro "
     "antes de ser identificada.",
     "A rocha de quase vinte quilos caiu em 1998, e um professor descobriu que era um meteorito de ferro e níquel. A "
     "família a doou, e a exposição permite tocar em fragmentos.",
     ["A sala nova trata de meteoritos.",
      "A peça principal ficou anos num galinheiro.",
      "Os visitantes podem tocar em fragmentos."]),
    ("Na adolescência, é comum sentir que ninguém entende o que você está passando. O corpo muda, as emoções ficam "
     "mais intensas e as relações com a família e os amigos também se transformam. Brigas com os pais, dúvidas sobre "
     "o futuro e a vontade de ser aceito pelo grupo fazem parte dessa fase.\n\n"
     "Conversar ajuda muito, seja com os pais, com um professor de confiança ou com amigos. Escrever o que se sente, "
     "praticar esportes e ter momentos longe das redes sociais também fazem bem. Se a tristeza durar muito tempo ou "
     "atrapalhar os estudos e o sono, é importante pedir ajuda a um profissional. O CVV atende de graça pelo 188.",
     "A adolescência traz mudanças no corpo, nas emoções e nas relações, e conversar e pedir ajuda tornam essa fase "
     "mais leve.",
     "É normal sentir-se incompreendido, brigar com os pais e ter dúvidas sobre o futuro. Esportes, escrita e menos "
     "redes sociais ajudam, e o CVV atende pelo 188.",
     ["A adolescência é uma fase de mudanças.",
      "Conversar com alguém de confiança ajuda.",
      "Tristeza longa pede ajuda profissional."]),
    ("A ponte que liga os bairros Centro e Ribeira será fechada para obras a partir do dia 10. Os engenheiros da "
     "prefeitura encontraram rachaduras nos pilares durante uma vistoria e recomendaram a reforma imediata. A "
     "interdição deve durar cerca de quatro meses.\n\n"
     "Durante esse período, os carros terão de usar o desvio pela avenida Beira-Rio, o que deve aumentar o tempo de "
     "viagem em até vinte minutos nos horários de pico. Para os pedestres e ciclistas, será montada uma passarela "
     "provisória ao lado da ponte. As linhas de ônibus também mudam de trajeto, e os novos itinerários estarão nos "
     "pontos a partir da próxima semana.",
     "A ponte entre o Centro e a Ribeira será fechada por cerca de quatro meses para consertar rachaduras nos pilares.",
     "Os carros vão usar a avenida Beira-Rio, com até vinte minutos a mais no pico. Pedestres e ciclistas terão uma "
     "passarela provisória, e os ônibus mudam de trajeto.",
     ["A ponte fecha a partir do dia 10.",
      "Os pilares têm rachaduras.",
      "Haverá desvio e passarela provisória."]),
    ("O xadrez é um jogo de estratégia para duas pessoas, jogado num tabuleiro de 64 casas. Cada jogador começa com "
     "dezesseis peças: um rei, uma dama, duas torres, dois bispos, dois cavalos e oito peões. Cada peça se move de um "
     "jeito diferente, e o objetivo é dar xeque-mate, ou seja, encurralar o rei do adversário sem que ele tenha para "
     "onde fugir.\n\n"
     "O jogo surgiu provavelmente na Índia, há mais de mil e quinhentos anos, e chegou à Europa pela Pérsia e pelos "
     "árabes. O xadrez ajuda a desenvolver a concentração, o raciocínio e a paciência, e por isso é ensinado em "
     "muitas escolas. Hoje, também é muito jogado pela internet.",
     "O xadrez é um jogo de estratégia em que cada jogador tenta encurralar o rei do adversário, surgido "
     "provavelmente na Índia.",
     "Cada um começa com dezesseis peças, que se movem de formas diferentes, num tabuleiro de 64 casas. O jogo "
     "estimula a concentração e é ensinado em muitas escolas.",
     ["O objetivo é o xeque-mate.",
      "Cada jogador tem dezesseis peças.",
      "O jogo nasceu provavelmente na Índia."]),
    ("Caro vizinho do 302,\n\nEscrevo de forma amigável para falar sobre o barulho no seu apartamento à noite. Nas "
     "últimas semanas, tenho ouvido música alta e móveis sendo arrastados depois da meia-noite, o que tem "
     "atrapalhado o meu sono. Trabalho cedo e tenho uma filha pequena, que também acorda com o barulho.\n\n"
     "Entendo que cada um tem a sua rotina e não quero criar problemas. Só peço que, se possível, a música fique mais "
     "baixa depois das 22h, como manda o regulamento do condomínio. Se quiser, podemos conversar pessoalmente. Fico à "
     "disposição.\n\nObrigado,\nMárcio, do 202",
     "Márcio pede, de forma amigável, que o vizinho de cima diminua o barulho depois das 22h, porque a música e os "
     "móveis arrastados atrapalham o seu sono.",
     "Ele trabalha cedo e tem uma filha pequena que acorda com o barulho. Lembra o regulamento do condomínio e se "
     "oferece para conversar pessoalmente.",
     ["O barulho acontece depois da meia-noite.",
      "Márcio e a filha não conseguem dormir.",
      "Ele pede silêncio depois das 22h."]),
    ("As pessoas que trabalham em turnos da noite, como enfermeiros, vigilantes e motoristas, enfrentam um desafio "
     "extra para cuidar da saúde. O corpo humano tem um relógio interno que segue o dia e a noite, e dormir durante "
     "o dia é mais difícil, porque há luz e barulho.\n\n"
     "Os especialistas recomendam deixar o quarto bem escuro, usar tampões de ouvido e manter os mesmos horários "
     "mesmo nas folgas, quando possível. Evitar café nas últimas horas do turno e fazer refeições leves também "
     "ajudam. Quem trabalha à noite por muitos anos deve fazer exames com frequência, porque a falta de sono aumenta "
     "o risco de várias doenças.",
     "Quem trabalha à noite tem mais dificuldade para dormir, e quarto escuro, horários regulares e refeições leves "
     "ajudam a proteger a saúde.",
     "O relógio interno do corpo segue o dia e a noite, e dormir de dia é mais difícil. Exames frequentes são "
     "importantes, porque a falta de sono aumenta o risco de doenças.",
     ["O corpo tem um relógio interno.",
      "Escuro e silêncio ajudam a dormir de dia.",
      "Exames regulares são importantes."]),
    ("A primeira edição do festival de música da cidade, no último fim de semana, reuniu cerca de quinze mil pessoas "
     "no parque municipal. Foram dois dias de shows, com mais de vinte bandas, a maioria da própria região, e uma "
     "praça de alimentação com comida típica.\n\n"
     "A organização considerou o evento um sucesso, mas recebeu reclamações sobre as filas nos banheiros e a falta de "
     "ônibus no fim da noite. Moradores das ruas vizinhas também reclamaram do barulho. A prefeitura disse que vai "
     "corrigir os problemas e que o festival deve se repetir no próximo ano, com mais banheiros e um esquema especial "
     "de transporte.",
     "O primeiro festival de música da cidade reuniu quinze mil pessoas e foi considerado um sucesso, apesar de "
     "reclamações sobre filas, transporte e barulho.",
     "Foram dois dias com mais de vinte bandas, a maioria da região. A prefeitura promete mais banheiros e ônibus na "
     "próxima edição.",
     ["O festival teve quinze mil pessoas.",
      "Houve reclamações de filas e barulho.",
      "Deve se repetir no ano que vem."]),
    ("A Lua não tem luz própria e, ao contrário do que muitos pensam, não existe um lado escuro permanente. O que "
     "existe é uma face que nunca vemos da Terra, porque a Lua leva o mesmo tempo para girar em torno de si mesma e "
     "em torno do nosso planeta. Esse lado escondido recebe luz do Sol como o outro.\n\n"
     "A face oculta só foi fotografada em 1959, por uma sonda soviética. Ela tem mais crateras e menos manchas "
     "escuras, os chamados mares lunares, do que a face visível. Em 2019, uma sonda chinesa fez o primeiro pouso "
     "suave nesse lado da Lua, um feito difícil porque a comunicação com a Terra precisa passar por um satélite "
     "intermediário.",
     "A Lua tem uma face que nunca vemos, mas que recebe luz do Sol, e por isso não existe um lado escuro "
     "permanente.",
     "Como ela gira em torno de si no mesmo tempo em que gira em torno da Terra, mostra sempre o mesmo lado. A face "
     "oculta foi fotografada em 1959 e recebeu um pouso chinês em 2019.",
     ["A Lua não tem um lado sempre escuro.",
      "Vemos sempre a mesma face.",
      "A face oculta tem mais crateras."]),
    ("Para economizar energia elétrica em casa, comece pelos aparelhos que mais gastam: o chuveiro elétrico, a "
     "geladeira e o ar-condicionado. Banhos mais curtos e o chuveiro na posição verão, quando o tempo estiver quente, "
     "já reduzem bastante a conta.\n\n"
     "Não deixe a porta da geladeira aberta por muito tempo e não coloque comida quente dentro dela. Troque lâmpadas "
     "antigas por lâmpadas de LED, que gastam bem menos e duram mais. Aparelhos em modo de espera, com a luzinha "
     "acesa, também consomem energia, então vale tirá-los da tomada. Na hora de comprar um eletrodoméstico, prefira "
     "os que têm selo de eficiência energética.",
     "Para gastar menos energia, use menos o chuveiro elétrico, cuide da geladeira, troque as lâmpadas por LED e tire "
     "da tomada os aparelhos em espera.",
     "O chuveiro, a geladeira e o ar-condicionado são os que mais gastam. Na compra de eletrodomésticos, o selo de "
     "eficiência ajuda a escolher.",
     ["Banhos curtos economizam muito.",
      "Use lâmpadas de LED.",
      "Desligue os aparelhos em modo de espera."]),
    ("O pintor holandês Vincent van Gogh vendeu poucos quadros em vida e passou boa parte dos seus anos com "
     "dificuldades financeiras e problemas de saúde mental. Ele começou a pintar tarde, por volta dos 27 anos, e em "
     "pouco mais de dez anos produziu cerca de 900 pinturas.\n\n"
     "Suas obras, com cores fortes e pinceladas marcadas, como A Noite Estrelada e Os Girassóis, só ficaram famosas "
     "depois da sua morte, em 1890. Boa parte do que se sabe sobre ele vem das cartas que escreveu ao irmão Theo, "
     "que o apoiou durante toda a vida. Hoje, Van Gogh é um dos pintores mais conhecidos do mundo, e seus quadros "
     "valem fortunas.",
     "Van Gogh pintou cerca de 900 quadros em pouco mais de dez anos, mas só ficou famoso depois de morrer.",
     "Ele viveu com dificuldades financeiras e problemas de saúde e teve o apoio do irmão Theo, a quem escreveu muitas "
     "cartas. Obras como A Noite Estrelada hoje valem fortunas.",
     ["Começou a pintar por volta dos 27 anos.",
      "Vendeu poucos quadros em vida.",
      "Ficou famoso depois da morte, em 1890."]),
    ("Começou nesta semana a colheita da uva no Vale dos Vinhedos, na serra gaúcha. Os produtores estão animados, "
     "porque o tempo seco das últimas semanas deixou as frutas mais doces e saudáveis. A expectativa é de uma safra "
     "maior do que a do ano passado, quando o excesso de chuva prejudicou parte das plantações.\n\n"
     "A colheita é feita em boa parte à mão, por famílias que mantêm a tradição trazida pelos imigrantes italianos no "
     "fim do século XIX. Nessa época do ano, a região recebe muitos turistas, que podem participar da colheita, "
     "conhecer as vinícolas e as festas da uva. Os hotéis da região estão com quase todos os quartos ocupados.",
     "A colheita da uva começou na serra gaúcha com expectativa de uma safra melhor, graças ao tempo seco, e atrai "
     "muitos turistas.",
     "No ano passado, a chuva prejudicou as plantações, mas agora as frutas estão mais doces. A colheita manual segue a "
     "tradição dos imigrantes italianos.",
     ["O tempo seco melhorou as uvas.",
      "A colheita segue a tradição italiana.",
      "Os turistas lotam a região."]),
    ("Antes de adotar um animal de estimação, é importante pensar se você tem tempo, espaço e dinheiro para cuidar "
     "dele por muitos anos. Cães e gatos podem viver mais de quinze anos e precisam de comida, vacinas, consultas no "
     "veterinário e atenção todos os dias.\n\n"
     "Também vale pensar no tamanho e na energia do animal: um cão grande e agitado pode não se adaptar a um "
     "apartamento pequeno. Nas feiras de adoção e nos abrigos, há muitos animais esperando um lar, já vacinados e "
     "castrados. Adotar é uma forma de ajudar, mas é um compromisso: abandonar um animal é crime e causa muito "
     "sofrimento.",
     "Adotar um animal exige tempo, espaço e dinheiro por muitos anos, e é um compromisso que não pode terminar em "
     "abandono.",
     "Cães e gatos vivem mais de quinze anos e precisam de cuidados diários. É bom escolher um animal que combine com a "
     "casa, e os abrigos têm muitos à espera.",
     ["Pense no tempo e no dinheiro necessários.",
      "Escolha um animal adequado à casa.",
      "Abandonar animais é crime."]),
    ("O Brasil tem uma das maiores reservas de água doce do mundo, mas a água não está distribuída de forma igual. A "
     "região Norte, com a bacia do Amazonas, concentra a maior parte dela, embora tenha poucos habitantes. Já o "
     "Sudeste, onde vive muita gente, tem menos água disponível por pessoa.\n\n"
     "Por isso, em períodos de seca, grandes cidades como São Paulo já enfrentaram crises de abastecimento. Além do "
     "clima, o desperdício, os vazamentos nas redes e a poluição dos rios agravam o problema. Proteger as nascentes, "
     "tratar o esgoto e usar a água com consciência são medidas importantes para garantir o abastecimento no futuro.",
     "O Brasil tem muita água doce, mas ela se concentra no Norte, enquanto o Sudeste populoso enfrenta crises em "
     "períodos de seca.",
     "Desperdício, vazamentos e poluição agravam a falta de água nas grandes cidades. Proteger nascentes e tratar o "
     "esgoto ajudam a garantir o abastecimento.",
     ["O Norte concentra a maior parte da água.",
      "O Sudeste já teve crises de abastecimento.",
      "Tratar o esgoto e evitar desperdício ajudam."]),
    ("O Cristo Redentor, no alto do morro do Corcovado, no Rio de Janeiro, foi inaugurado em 1931. A estátua tem "
     "cerca de 30 metros de altura, sem contar o pedestal, e os braços abertos medem 28 metros de uma ponta à outra. "
     "Ela foi feita de concreto armado e revestida com milhares de pequenos triângulos de pedra-sabão.\n\n"
     "O projeto envolveu o engenheiro brasileiro Heitor da Silva Costa e o escultor francês Paul Landowski. Por "
     "estar no ponto mais alto da região, a estátua é atingida por raios várias vezes por ano e já precisou de "
     "reparos nos dedos e na cabeça. Em 2007, o Cristo foi eleito uma das sete novas maravilhas do mundo.",
     "O Cristo Redentor, inaugurado em 1931 no Corcovado, é uma estátua de cerca de 30 metros eleita uma das sete "
     "novas maravilhas do mundo.",
     "Feita de concreto e revestida de pedra-sabão, foi projetada por um engenheiro brasileiro e um escultor francês. "
     "Por ficar no alto, é atingida por raios com frequência.",
     ["Foi inaugurado em 1931.",
      "É revestido de pedra-sabão.",
      "Virou uma das sete novas maravilhas em 2007."]),
    ("Na escola, o grêmio estudantil organizou uma campanha para arrecadar agasalhos antes do inverno. Durante duas "
     "semanas, foram colocadas caixas em todas as salas, e cada turma competia para ver quem juntava mais peças. A "
     "turma vencedora ganharia um passeio ao museu da cidade.\n\n"
     "No fim, foram recolhidas mais de mil e duzentas peças, entre casacos, cobertores, gorros e meias. Os próprios "
     "alunos separaram as roupas por tamanho e entregaram tudo a uma instituição que atende famílias em situação de "
     "rua. A turma do 7º ano B venceu a competição, mas pediu que o passeio fosse feito com todas as turmas que "
     "participaram.",
     "A campanha de agasalhos do grêmio estudantil arrecadou mais de mil e duzentas peças, entregues a uma "
     "instituição que ajuda famílias em situação de rua.",
     "As turmas competiram por um passeio ao museu, e os alunos separaram as roupas por tamanho. A turma vencedora "
     "pediu que todas as turmas fossem ao passeio.",
     ["A campanha durou duas semanas.",
      "Foram arrecadadas mais de 1.200 peças.",
      "A turma vencedora dividiu o prêmio."]),
    ("Os vulcões do Brasil estão extintos há milhões de anos, e por isso o país não tem erupções. Mas há sinais "
     "dessa atividade antiga em vários lugares. O arquipélago de Fernando de Noronha, por exemplo, é o topo de um "
     "antigo vulcão que se formou no fundo do mar, e a ilha da Trindade também tem origem vulcânica.\n\n"
     "No continente, a região de Poços de Caldas, em Minas Gerais, fica dentro de uma antiga caldeira vulcânica, uma "
     "grande depressão circular formada depois de erupções. As fontes de águas termais da cidade estão ligadas a "
     "essa história geológica. O Brasil também tem poucos terremotos fortes, porque fica no meio de uma placa "
     "tectônica, longe das bordas.",
     "O Brasil não tem vulcões ativos, mas lugares como Fernando de Noronha e Poços de Caldas guardam marcas de "
     "vulcões muito antigos.",
     "Noronha é o topo de um vulcão submarino, e Poços de Caldas fica numa antiga caldeira vulcânica. O país tem "
     "poucos terremotos porque está no meio de uma placa tectônica.",
     ["Os vulcões do Brasil estão extintos.",
      "Noronha tem origem vulcânica.",
      "O país fica no meio de uma placa."]),
    ("Para fazer uma boa salada, comece lavando bem as folhas em água corrente e, depois, deixe-as de molho por "
     "alguns minutos numa mistura de água com algumas gotas de hipoclorito próprio para alimentos, seguindo a "
     "indicação da embalagem. Enxágue e seque bem, porque folhas molhadas não seguram o tempero.\n\n"
     "Misture cores e texturas: folhas verdes, tomate, cenoura ralada, pepino e algo crocante, como castanhas ou "
     "sementes. Para o molho, uma combinação simples é azeite, limão, sal e um pouco de mostarda ou mel. Tempere só na "
     "hora de servir, para as folhas não murcharem. Grãos, como grão-de-bico, e um ovo cozido deixam a salada mais "
     "completa.",
     "Para uma boa salada, higienize e seque as folhas, misture cores e texturas e tempere só na hora de servir.",
     "As folhas devem ficar de molho com hipoclorito próprio para alimentos e secar bem. Um molho de azeite, limão e "
     "sal e grãos ou ovo deixam o prato mais completo.",
     ["Lave e seque bem as folhas.",
      "Misture cores e texturas.",
      "Tempere só na hora de servir."]),
    ("A febre amarela é uma doença causada por um vírus transmitido pela picada de mosquitos. Nas matas, os "
     "transmissores são mosquitos silvestres, e os macacos também são infectados. Ao contrário do que muita gente "
     "pensa, os macacos não transmitem a doença para as pessoas; eles são vítimas e ajudam a avisar que o vírus está "
     "circulando na região.\n\n"
     "Os sintomas incluem febre, dor de cabeça, calafrios e, nos casos graves, pele e olhos amarelados e "
     "sangramentos. A forma mais eficaz de prevenção é a vacina, oferecida de graça pelo SUS. Quem vai viajar para "
     "áreas de mata deve se vacinar pelo menos dez dias antes. Matar macacos é crime e só dificulta o controle da "
     "doença.",
     "A febre amarela é transmitida por mosquitos, e não por macacos, que também são vítimas, e a melhor prevenção é a "
     "vacina gratuita.",
     "A doença causa febre e, nos casos graves, pele amarelada e sangramentos. Quem vai a áreas de mata deve se "
     "vacinar dez dias antes, e matar macacos atrapalha o controle.",
     ["A doença é transmitida por mosquitos.",
      "Os macacos não transmitem o vírus.",
      "A vacina é gratuita no SUS."]),
    ("Na cidade de Campos Altos, uma professora aposentada transformou a garagem de casa numa biblioteca "
     "comunitária. Tudo começou quando ela decidiu doar os livros que tinha guardado ao longo da vida. Em vez de "
     "levá-los para uma instituição, colocou estantes na garagem e abriu o portão para os vizinhos.\n\n"
     "Hoje, a biblioteca tem mais de quatro mil livros, quase todos doados pela comunidade, e funciona três tardes "
     "por semana. As crianças do bairro vão fazer as tarefas da escola, e às sextas-feiras há uma roda de leitura. "
     "Não há cadastro nem multa por atraso: a professora diz que confia nos leitores e que quase todos os livros "
     "voltam.",
     "Uma professora aposentada transformou a garagem de casa numa biblioteca comunitária que hoje tem mais de quatro "
     "mil livros doados.",
     "Ela começou doando os próprios livros e abriu o portão para os vizinhos. A biblioteca funciona três tardes por "
     "semana, tem roda de leitura e não cobra multas.",
     ["A biblioteca nasceu numa garagem.",
      "Tem mais de quatro mil livros doados.",
      "Funciona na base da confiança."]),
    ("O Brasil tem cerca de 8.500 quilômetros de litoral, banhado pelo Oceano Atlântico do Amapá ao Rio Grande do "
     "Sul. Ao longo dessa costa, há paisagens muito diferentes: praias de dunas no Nordeste, falésias coloridas, "
     "manguezais, baías com montanhas no Sudeste e longas praias retas no Sul.\n\n"
     "Os manguezais são especialmente importantes. Eles ficam onde os rios encontram o mar e servem de berçário para "
     "peixes, caranguejos e camarões, além de proteger a costa contra a erosão. Muitas comunidades vivem da pesca e "
     "da coleta de caranguejos nesses ambientes. A ocupação desordenada e a poluição, porém, ameaçam várias partes do "
     "litoral brasileiro.",
     "O litoral brasileiro tem cerca de 8.500 quilômetros com paisagens muito variadas, e os manguezais são "
     "fundamentais para a vida marinha.",
     "Há dunas, falésias, baías e praias longas ao longo da costa. Os manguezais servem de berçário e protegem contra a "
     "erosão, mas a poluição e a ocupação os ameaçam.",
     ["O litoral tem cerca de 8.500 quilômetros.",
      "As paisagens mudam muito ao longo da costa.",
      "Os manguezais são berçários de peixes."]),
    ("Quem cozinha com óleo deve saber que ele nunca deve ser jogado na pia. Quando esfria, o óleo endurece nos canos, "
     "causa entupimentos e, ao chegar aos rios, forma uma camada que impede a entrada de oxigênio na água. Um litro de "
     "óleo pode poluir milhares de litros de água.\n\n"
     "O certo é esperar o óleo esfriar, coar e guardar numa garrafa plástica bem fechada. Muitos supermercados, "
     "escolas e cooperativas têm pontos de coleta. O óleo usado pode ser reciclado e transformado em sabão, "
     "biodiesel e até tinta. Algumas pessoas fazem sabão caseiro, mas é preciso cuidado, porque a receita usa soda "
     "cáustica, que queima a pele.",
     "O óleo de cozinha não deve ir para a pia, porque entope os canos e polui a água, e deve ser guardado em garrafas "
     "e levado a pontos de coleta.",
     "Um litro de óleo pode poluir milhares de litros de água. Reciclado, ele vira sabão, biodiesel e tinta.",
     ["Não jogue óleo na pia.",
      "Guarde-o numa garrafa fechada.",
      "Ele pode virar sabão e biodiesel."]),
    ("Fui ao show da banda que eu ouço desde a adolescência e saí com sentimentos misturados. O som estava ótimo, e o "
     "público cantou todas as músicas antigas do começo ao fim. Ver tanta gente da minha idade, com camisetas "
     "desbotadas da época, foi emocionante.\n\n"
     "Por outro lado, a banda passou quase metade do show tocando as músicas do álbum novo, que ninguém conhecia, e o "
     "público ficou parado e conversando. O ingresso também estava caro, e a fila para entrar levou mais de uma hora. "
     "No fim, quando tocaram o maior sucesso, todo mundo esqueceu os problemas. Valeu pela nostalgia, mas esperava "
     "mais.",
     "O autor gostou do som e da emoção das músicas antigas no show, mas achou que a banda tocou músicas novas demais "
     "e que o ingresso e a fila decepcionaram.",
     "O público cantou os sucessos antigos e ficou parado nas músicas do álbum novo. O maior sucesso no fim compensou "
     "em parte, mas ele esperava mais.",
     ["As músicas antigas emocionaram.",
      "Houve músicas novas demais.",
      "O ingresso caro e a fila longa decepcionaram."]),
    ("A internet chegou à comunidade ribeirinha de São Tomé, às margens de um rio da Amazônia, por meio de uma antena "
     "de satélite instalada na escola. Antes, os moradores precisavam viajar quatro horas de barco até a cidade mais "
     "próxima para usar a internet ou fazer uma ligação.\n\n"
     "Agora, os alunos fazem pesquisas para os trabalhos, os agricultores consultam o preço da farinha e do açaí antes "
     "de vender, e as famílias conversam com parentes que moram longe. O agente de saúde também passou a enviar "
     "informações sobre os pacientes ao hospital da cidade. A conexão ainda é lenta nos dias de chuva, mas os "
     "moradores dizem que a mudança foi enorme.",
     "Uma antena de satélite na escola levou internet à comunidade ribeirinha de São Tomé, que antes precisava viajar "
     "quatro horas de barco.",
     "Os alunos pesquisam, os agricultores consultam preços e o agente de saúde fala com o hospital. A conexão ainda "
     "falha na chuva, mas a vida mudou muito.",
     ["A internet chegou por satélite.",
      "Antes, era preciso viajar quatro horas.",
      "Escola, comércio e saúde se beneficiaram."]),
    ("Muitas vezes, as pessoas confundem gripe e resfriado, mas são doenças diferentes. O resfriado é mais leve: "
     "causa coriza, espirros, nariz entupido e um pouco de dor de garganta, e a pessoa costuma continuar fazendo as "
     "suas atividades. Ele é causado por vários tipos de vírus e passa em poucos dias.\n\n"
     "A gripe, causada pelo vírus influenza, começa de repente, com febre alta, dores no corpo, cansaço forte e "
     "tosse. Ela pode levar a complicações, como a pneumonia, principalmente em idosos, crianças pequenas e pessoas "
     "com doenças crônicas. Para a gripe existe vacina anual. Nos dois casos, descanso, líquidos e lavar as mãos "
     "ajudam.",
     "O resfriado é leve e passa em poucos dias, enquanto a gripe começa de repente, com febre e dores fortes, e pode "
     "ter complicações.",
     "O resfriado causa coriza e espirros, e a pessoa continua a rotina. A gripe é causada pelo influenza, tem vacina "
     "anual e é mais perigosa para idosos e crianças.",
     ["O resfriado é mais leve.",
      "A gripe dá febre alta e dores no corpo.",
      "Contra a gripe existe vacina."]),
    ("Na última reunião de pais, a escola apresentou o projeto de uma horta pedagógica no terreno ao lado do pátio. "
     "A ideia é que cada turma cuide de um canteiro e aprenda, na prática, sobre plantas, alimentação saudável, "
     "matemática e trabalho em equipe. As verduras colhidas vão para a merenda.\n\n"
     "Alguns pais ofereceram ajuda: um deles é agricultor e vai doar mudas, e outra mãe vai ensinar a fazer "
     "compostagem com os restos da cozinha. A prefeitura vai fornecer a terra e as ferramentas. Os professores contam "
     "que, em outras escolas, as hortas fizeram as crianças comer mais verduras, porque elas ficam curiosas para "
     "provar o que plantaram.",
     "A escola vai criar uma horta pedagógica em que cada turma cuida de um canteiro, com ajuda dos pais e da "
     "prefeitura.",
     "As crianças vão aprender sobre plantas, alimentação e trabalho em equipe, e as verduras irão para a merenda. Em "
     "outras escolas, as hortas fizeram os alunos comer mais verduras.",
     ["Cada turma terá um canteiro.",
      "Pais vão doar mudas e ensinar compostagem.",
      "As verduras vão para a merenda."]),
    ("A Semana de Arte Moderna aconteceu em fevereiro de 1922, no Theatro Municipal de São Paulo, e marcou o início "
     "do Modernismo no Brasil. Artistas como Anita Malfatti, Di Cavalcanti, Mário de Andrade, Oswald de Andrade e "
     "Heitor Villa-Lobos apresentaram pinturas, poemas e músicas que rompiam com os modelos tradicionais.\n\n"
     "Na época, parte do público vaiou as apresentações, achando as obras estranhas e exageradas. Os modernistas "
     "queriam uma arte mais livre e mais brasileira, que valorizasse a cultura popular, a fala do dia a dia e as "
     "misturas que formam o país. Com o tempo, as ideias do movimento influenciaram a literatura, a pintura, a música "
     "e a arquitetura brasileiras.",
     "A Semana de Arte Moderna de 1922, em São Paulo, iniciou o Modernismo brasileiro, com obras que rompiam com a "
     "arte tradicional.",
     "Artistas como Anita Malfatti e Mário de Andrade foram vaiados por parte do público. Eles defendiam uma arte livre "
     "e brasileira, que acabou influenciando várias áreas.",
     ["Aconteceu em fevereiro de 1922.",
      "Parte do público vaiou as obras.",
      "Os artistas queriam uma arte mais brasileira."]),
    ("Atenção, passageiros: devido às obras na estação Central, os trens da linha azul não vão parar nessa estação "
     "neste sábado e domingo. Quem precisar descer na Central deve desembarcar na estação Praça da Sé e seguir pelos "
     "ônibus gratuitos que farão o trajeto entre as duas estações a cada dez minutos.\n\n"
     "Nos dois dias, o intervalo entre os trens também será maior, de cerca de oito minutos. Recomendamos que os "
     "passageiros saiam de casa com antecedência. A operação volta ao normal na segunda-feira, às 4h40. Em caso de "
     "dúvida, procure os funcionários uniformizados nas estações.",
     "Por causa de obras, os trens da linha azul não vão parar na estação Central no fim de semana, e haverá ônibus "
     "gratuitos a partir da Praça da Sé.",
     "Os trens também vão passar a cada oito minutos, então é bom sair mais cedo. Tudo volta ao normal na "
     "segunda-feira de manhã.",
     ["A estação Central fica fechada no fim de semana.",
      "Haverá ônibus gratuitos a partir da Sé.",
      "Os trens passam a cada oito minutos."]),
    ("O tamanduá-bandeira é um mamífero que vive em vários biomas do Brasil, como o Cerrado e o Pantanal. Ele não tem "
     "dentes e se alimenta quase só de formigas e cupins, que captura com uma língua comprida e pegajosa, que pode "
     "passar de sessenta centímetros. Num único dia, pode comer dezenas de milhares de insetos.\n\n"
     "O tamanduá tem garras fortes, que usa para abrir cupinzeiros e para se defender. A fêmea carrega o filhote nas "
     "costas por vários meses. A espécie é considerada vulnerável, por causa das queimadas, da perda de habitat e dos "
     "atropelamentos nas estradas, que matam muitos animais todos os anos.",
     "O tamanduá-bandeira não tem dentes, come formigas e cupins com uma língua enorme e está ameaçado por queimadas e "
     "atropelamentos.",
     "Ele usa as garras fortes para abrir cupinzeiros e se defender, e a fêmea leva o filhote nas costas. A perda de "
     "habitat também deixa a espécie vulnerável.",
     ["O tamanduá não tem dentes.",
      "Come milhares de insetos por dia.",
      "Atropelamentos e queimadas o ameaçam."]),
    ("Eu sempre achei que não tinha jeito para cozinhar. Na minha casa, quem cozinhava era a minha mãe, e eu só sabia "
     "fritar ovo e fazer miojo. Quando fui morar sozinho, passei os primeiros meses comendo lanches e comida de "
     "aplicativo, e o dinheiro sumia rápido.\n\n"
     "Um dia, resolvi seguir uma receita de arroz e feijão por um vídeo. O arroz grudou e o feijão ficou duro, mas "
     "insisti. Fui aprendendo uma receita nova por semana, anotando o que dava errado. Hoje, cozinho para a semana "
     "inteira no domingo, gasto menos da metade do que gastava e até recebo os amigos para jantar.",
     "O autor achava que não sabia cozinhar, mas, morando sozinho, aprendeu uma receita por semana e hoje gasta menos "
     "e recebe os amigos.",
     "No começo, comia lanches e gastava muito, e as primeiras tentativas deram errado. Com insistência, passou a "
     "cozinhar para a semana inteira aos domingos.",
     ["Ele só sabia fritar ovo.",
      "Aprendeu uma receita por semana.",
      "Hoje gasta menos da metade."]),
    ("A doação de órgãos pode salvar várias vidas. Uma única pessoa pode doar coração, pulmões, fígado, rins, "
     "pâncreas e córneas, entre outros. No Brasil, a doação depois da morte só acontece com a autorização da família, "
     "mesmo que a pessoa tenha dito em vida que queria ser doadora.\n\n"
     "Por isso, o mais importante é conversar com os parentes e deixar clara a sua vontade. Também é possível doar em "
     "vida, por exemplo um dos rins ou parte do fígado, geralmente para um familiar. O Brasil tem um dos maiores "
     "sistemas públicos de transplantes do mundo, mas milhares de pessoas ainda esperam na fila por um órgão.",
     "A doação de órgãos pode salvar várias vidas, e, como no Brasil ela depende da família, é importante avisar os "
     "parentes da sua vontade.",
     "Uma pessoa pode doar coração, rins, fígado e córneas, entre outros, e alguns órgãos podem ser doados em vida. O "
     "país tem um grande sistema público de transplantes, mas a fila ainda é longa.",
     ["Um doador pode salvar várias vidas.",
      "A família precisa autorizar.",
      "Converse com os parentes sobre isso."]),
    ("O novo parque linear da cidade foi inaugurado no domingo, ao longo de três quilômetros das margens do córrego "
     "Água Limpa. A área, que antes acumulava lixo e entulho, recebeu ciclovia, pista de caminhada, aparelhos de "
     "ginástica, brinquedos para crianças e mais de duas mil árvores nativas.\n\n"
     "A obra também incluiu a limpeza do córrego e a ligação de casas vizinhas à rede de esgoto, o que deve melhorar a "
     "qualidade da água. Moradores que acompanharam a inauguração disseram que o bairro mudou de cara. A prefeitura "
     "pede que a população ajude a conservar o parque e não jogue lixo nas margens.",
     "O novo parque linear transformou três quilômetros das margens de um córrego cheio de lixo em área de lazer com "
     "ciclovia e árvores nativas.",
     "Além dos equipamentos e das duas mil árvores, a obra limpou o córrego e ligou casas à rede de esgoto. A "
     "prefeitura pede ajuda dos moradores para conservar o lugar.",
     ["O parque tem três quilômetros.",
      "A área antes tinha lixo e entulho.",
      "O córrego foi limpo e o esgoto, ligado."]),
    ("A história da pizza moderna é muito ligada a Nápoles, na Itália, onde, no século XVIII, já se vendiam massas "
     "achatadas com tomate pelas ruas, uma comida barata para os trabalhadores. A pizza margherita, com tomate, "
     "muçarela e manjericão, nas cores da bandeira italiana, ficou famosa no fim do século XIX.\n\n"
     "Com a imigração italiana, a pizza chegou ao Brasil, principalmente a São Paulo, onde ganhou sabores próprios, "
     "como a de calabresa, a portuguesa e a de frango com catupiry. Hoje, São Paulo é uma das cidades que mais "
     "consomem pizza no mundo, e o dia 10 de julho é comemorado como o Dia da Pizza.",
     "A pizza moderna nasceu em Nápoles como comida barata de rua e chegou a São Paulo com os imigrantes italianos, "
     "onde ganhou sabores próprios.",
     "A margherita ficou famosa no fim do século XIX com as cores da bandeira italiana. Em São Paulo surgiram a "
     "calabresa e a portuguesa, e o Dia da Pizza é 10 de julho.",
     ["A pizza moderna nasceu em Nápoles.",
      "Os imigrantes a trouxeram para São Paulo.",
      "O Dia da Pizza é 10 de julho."]),
    ("Se você recebeu uma mensagem de um parente pedindo dinheiro com urgência, de um número novo, desconfie. Esse é "
     "um golpe comum: o criminoso usa a foto da pessoa, diz que trocou de número e inventa uma emergência, como uma "
     "conta para pagar no mesmo dia.\n\n"
     "Antes de fazer qualquer transferência, ligue para o número antigo do parente ou faça uma pergunta que só ele "
     "saberia responder. Desconfie de pressa e de pedidos para não contar a ninguém. Se cair no golpe, avise o banco "
     "imediatamente e registre um boletim de ocorrência. Avisar a família e os amigos sobre esse tipo de fraude "
     "ajuda a proteger outras pessoas.",
     "Mensagens de parentes com número novo pedindo dinheiro urgente costumam ser golpe, e é preciso confirmar com a "
     "pessoa antes de transferir.",
     "O golpista usa a foto do parente e inventa uma emergência. Ligue para o número antigo ou faça uma pergunta "
     "pessoal e, se cair no golpe, avise o banco.",
     ["Desconfie de número novo pedindo dinheiro.",
      "Confirme pelo número antigo.",
      "Avise o banco se cair no golpe."]),
    ("O Dia Internacional da Mulher, 8 de março, tem origem nas lutas de trabalhadoras no começo do século XX, na "
     "Europa e nos Estados Unidos, por melhores condições de trabalho, salários justos e o direito ao voto. A data "
     "foi oficializada pela ONU em 1975.\n\n"
     "No Brasil, as mulheres conquistaram o direito de votar em 1932. Desde então, houve muitos avanços, como o "
     "acesso à educação e a leis de proteção contra a violência, como a Lei Maria da Penha, de 2006. Mas ainda existem "
     "desafios, como a diferença de salários entre homens e mulheres na mesma função e a violência doméstica. Por "
     "isso, a data é mais um dia de reflexão do que de festa.",
     "O Dia Internacional da Mulher nasceu das lutas das trabalhadoras por direitos e, no Brasil, lembra avanços como "
     "o voto e a Lei Maria da Penha.",
     "A ONU oficializou a data em 1975, e as brasileiras votam desde 1932. A diferença de salários e a violência "
     "doméstica ainda são desafios.",
     ["A data vem das lutas das trabalhadoras.",
      "As brasileiras votam desde 1932.",
      "Ainda há desigualdade e violência."]),
    ("No último inverno, uma onda de frio fez as temperaturas caírem abaixo de zero em várias cidades da serra "
     "catarinense. Em São Joaquim, os termômetros marcaram seis graus negativos, e houve geada forte nos campos e nos "
     "carros. Turistas de outros estados viajaram até lá na esperança de ver neve, que acabou não caindo.\n\n"
     "O frio intenso também trouxe problemas: produtores rurais perderam parte das plantações de verduras, e os "
     "abrigos para pessoas em situação de rua ficaram lotados. A Defesa Civil distribuiu cobertores e pediu cuidado "
     "com o uso de aquecedores a gás em ambientes fechados, que podem causar intoxicação.",
     "Uma onda de frio levou a serra catarinense a temperaturas negativas, com geada forte, perdas na agricultura e "
     "abrigos lotados.",
     "São Joaquim chegou a seis graus negativos, e os turistas não viram neve. A Defesa Civil distribuiu cobertores e "
     "alertou para o perigo dos aquecedores a gás.",
     ["São Joaquim teve seis graus negativos.",
      "Houve geada, mas não neve.",
      "O frio prejudicou plantações e pessoas sem teto."]),
    ("A tecnologia do Pix, sistema de pagamentos instantâneos criado pelo Banco Central, começou a funcionar em "
     "novembro de 2020. Com ele, é possível transferir dinheiro a qualquer hora, inclusive de madrugada e nos fins de "
     "semana, e o valor cai na conta em poucos segundos. Para pessoas físicas, em geral, não há cobrança.\n\n"
     "Para receber, basta ter uma chave cadastrada, como o número do celular, o e-mail ou o CPF. Em pouco tempo, o Pix "
     "se tornou uma das formas de pagamento mais usadas do Brasil, do pagamento de contas à compra no camelô. A "
     "facilidade, porém, também atraiu golpistas, e por isso é importante conferir o nome de quem vai receber antes "
     "de confirmar.",
     "O Pix, criado pelo Banco Central em 2020, permite transferências em segundos a qualquer hora e virou uma das "
     "formas de pagamento mais usadas do país.",
     "Basta uma chave, como o celular ou o CPF, e em geral não há cobrança para pessoas físicas. Como também atraiu "
     "golpes, é preciso conferir o nome do recebedor.",
     ["O Pix começou em novembro de 2020.",
      "O dinheiro cai em segundos.",
      "Confira o nome antes de pagar."]),
    ("Na semana passada, a turma do 9º ano visitou uma estação de tratamento de água da cidade. Os alunos viram que "
     "a água chega do rio cheia de terra e folhas e passa por várias etapas antes de chegar às torneiras. Primeiro, "
     "recebe produtos que fazem a sujeira se juntar em flocos, que depois afundam em grandes tanques.\n\n"
     "Em seguida, a água atravessa filtros de areia e carvão e recebe cloro, para matar os micróbios, e flúor, que "
     "ajuda a proteger os dentes. Um técnico explicou que todo o processo leva algumas horas e que amostras são "
     "analisadas em laboratório o tempo todo. Muitos alunos disseram que passaram a desperdiçar menos água depois de "
     "ver o trabalho que dá para tratá-la.",
     "Numa visita a uma estação de tratamento, os alunos viram as etapas que deixam a água do rio pronta para beber e "
     "passaram a desperdiçar menos.",
     "A sujeira forma flocos que afundam, a água passa por filtros e recebe cloro e flúor. Amostras são analisadas o "
     "tempo todo, e o processo leva algumas horas.",
     ["A água do rio chega suja.",
      "Ela é filtrada e recebe cloro e flúor.",
      "Os alunos aprenderam a economizar água."]),
    ("Dona Teresa costura bonecas de pano há quarenta anos numa pequena cidade do Vale do Jequitinhonha, em Minas "
     "Gerais. Ela aprendeu com a mãe, usando retalhos que sobravam das roupas da família. Cada boneca leva dois dias "
     "para ficar pronta e tem um rosto bordado à mão, diferente de todas as outras.\n\n"
     "Por muito tempo, ela vendia as bonecas só na feira da cidade. Há alguns anos, uma associação de artesãs passou "
     "a levar o trabalho dela para exposições em São Paulo e para lojas na internet, e hoje as encomendas chegam até "
     "de fora do país. Dona Teresa ensinou o ofício a seis mulheres da comunidade, que agora também vivem do "
     "artesanato.",
     "Dona Teresa faz bonecas de pano à mão há quarenta anos e, com a ajuda de uma associação, passou a vender até "
     "para fora do país.",
     "Ela aprendeu com a mãe e borda um rosto diferente em cada boneca. Hoje, também ensinou seis mulheres da "
     "comunidade, que vivem do artesanato.",
     ["Cada boneca leva dois dias.",
      "Uma associação ampliou as vendas.",
      "Ela ensinou o ofício a outras mulheres."]),
    ("O teclado que usamos nos computadores e celulares, com as letras Q, W, E, R, T e Y na primeira fileira, foi "
     "criado no século XIX para as máquinas de escrever. Nas primeiras máquinas, as hastes das letras se enroscavam "
     "quando a pessoa digitava rápido demais duas letras vizinhas.\n\n"
     "Uma das explicações mais conhecidas é que a disposição foi pensada para afastar as letras que costumam aparecer "
     "juntas em inglês, diminuindo esses enroscos. Com o tempo, as máquinas melhoraram e os computadores dispensaram "
     "as hastes, mas o modelo continuou, porque as pessoas já estavam acostumadas. Existem outros arranjos, "
     "considerados mais eficientes, mas eles nunca se popularizaram.",
     "O teclado QWERTY foi criado para as máquinas de escrever do século XIX e continua até hoje porque as pessoas se "
     "acostumaram com ele.",
     "A explicação mais conhecida é que as letras foram espalhadas para as hastes não se enroscarem. Outros arranjos "
     "mais eficientes existem, mas não pegaram.",
     ["O QWERTY nasceu nas máquinas de escrever.",
      "As letras evitavam que as hastes se enroscassem.",
      "O costume manteve o modelo."]),
    ("Na madrugada de terça-feira, um temporal derrubou árvores e deixou cerca de vinte mil casas sem energia elétrica "
     "na zona sul da cidade. Os ventos passaram de 80 quilômetros por hora, e a chuva forte alagou ruas e "
     "cruzamentos. Uma árvore caiu sobre dois carros estacionados, mas ninguém se feriu.\n\n"
     "As equipes da companhia de energia trabalharam o dia inteiro, e a luz voltou na maior parte dos bairros até o "
     "fim da tarde. A Defesa Civil pediu que os moradores não se aproximem de fios caídos e liguem para o 199 em caso "
     "de emergência. A previsão é de mais chuva no fim de semana, mas com menos vento.",
     "Um temporal com ventos fortes derrubou árvores e deixou cerca de vinte mil casas sem luz na zona sul, sem "
     "feridos.",
     "A chuva alagou ruas, e uma árvore caiu sobre dois carros. A energia voltou até o fim da tarde, e a Defesa Civil "
     "pediu distância dos fios caídos.",
     ["Os ventos passaram de 80 km/h.",
      "Vinte mil casas ficaram sem luz.",
      "Não chegue perto de fios caídos."]),
    ("O hábito de lavar as mãos parece simples, mas só se tornou comum na medicina no século XIX. Em 1847, o médico "
     "húngaro Ignaz Semmelweis percebeu que muitas mulheres morriam de infecção depois do parto num hospital de "
     "Viena, e que os médicos iam direto da sala de autópsias para a maternidade, sem lavar as mãos.\n\n"
     "Ele passou a exigir que todos lavassem as mãos com uma solução de cloro, e as mortes caíram muito. Mesmo assim, "
     "muitos colegas rejeitaram a ideia, porque ainda não se conheciam os micróbios. Só anos depois, com os estudos de "
     "Louis Pasteur e de outros cientistas, a importância da higiene foi aceita. Hoje, lavar as mãos é uma das formas "
     "mais eficazes de evitar doenças.",
     "Em 1847, o médico Ignaz Semmelweis mostrou que lavar as mãos reduzia as mortes nas maternidades, mas a ideia só "
     "foi aceita anos depois.",
     "Ele notou que os médicos saíam das autópsias para os partos sem se lavar e passou a exigir cloro nas mãos. Os "
     "colegas resistiram até que os estudos sobre micróbios confirmassem a sua ideia.",
     ["Semmelweis estudou as mortes após o parto.",
      "Lavar as mãos reduziu as infecções.",
      "A ideia só foi aceita com a descoberta dos micróbios."]),
]
