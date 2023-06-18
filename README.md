# Smart Routes
Funcionalidades do código:
1. O código otimiza as rotas de entrega para vários caminhões, levando em consideração a capacidade dos caminhões e as demandas de entrega.
2. Ele recebe informações sobre a fábrica, os caminhões disponíveis e as entregas a serem feitas.
3. Utiliza a biblioteca `googlemaps` para calcular as distâncias entre os locais de entrega usando a API do Google Maps.
4. Cria um modelo de dados com base nas informações fornecidas, incluindo a matriz de distâncias entre os locais.
5. Utiliza a biblioteca `OR-Tools` para otimizar as rotas, levando em consideração as capacidades dos caminhões e as demandas de entrega.
6. Calcula as datas de partida com base na duração estimada das rotas de entrega e em uma data de retorno especificada.
7. Gera um arquivo JSON de saída com as informações otimizadas das rotas, incluindo caminhões, capacidades, datas de partida e entregas.

Tecnologias utilizadas:
1. Python: Linguagem de programação utilizada para implementar o código.
2. OR-Tools: Biblioteca de otimização desenvolvida pelo Google, utilizada para resolver o problema de roteamento de veículos.
3. Google Maps API: API fornecida pelo Google para acessar informações de mapas, como distâncias e rotas.
4. Biblioteca googlemaps: Pacote Python que fornece uma interface para a API do Google Maps.
5. JSON: Formato de arquivo usado para armazenar as configurações de entrada e os dados de saída do programa.

Exemplos: 

<h4>Entrada Json</h4>  
<img src="https://i.imgur.com/3Z9wfZQ.png" alt="json entrada" />

<h4>Saída Json</h4> 
<img src="https://i.imgur.com/Jl3QO9R.png" alt="json saida" />
