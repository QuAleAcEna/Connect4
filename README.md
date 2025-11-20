# Connect4
Notebook em Python que explora IA para o jogo Connect Four usando Monte Carlo Tree Search (MCTS) e árvores de decisão ID3 treinadas em dados gerados pelo próprio agente.

## O que há no notebook
- Lógica completa do jogo (criar tabuleiro, validar jogadas, checar vitória) com funções críticas aceleradas por Numba.
- Agentes: aleatório (baseline), MCTS configurável (iterações, constante UCB, critérios de expansão/backpropagação), e agente ID3 que carrega modelo salvo.
- Ferramentas interativas em Jupyter (ipywidgets) para Jogador vs Jogador/IA, IA vs IA e menu de benchmark que registra vitórias/empates/tempo médio por jogada.
- Geração de dados: exporta estados do MCTS para CSV com 42 colunas `s0`…`s41` (tabuleiro 6×7 achatado) + coluna `move`.
- Análises e resultados: comparação de estratégias de best-child/backprop, impacto do parâmetro `c`, frequência de estados e tamanho do conjunto gerado.
- Implementação própria do ID3: discretização, divisão treino/teste, métricas (acurácia, precisão/recall/F1, matriz de confusão, curva ROC multiclasses, AUC), impressão textual da árvore e salvamento via pickle.
- Pipelines de treino: `trainIris()` (gera `iris_model.pkl`) e `trainconnect4()` (treina a partir de `mcts_moves.csv`, gera `connect4.pkl`), além de busca simples de hiperparâmetros.

## Pré-requisitos
- Python 3.10+ com Jupyter Notebook/Lab.
- Bibliotecas: `pandas`, `numpy`, `matplotlib`, `seaborn`, `numba`, `ipywidgets` (demais dependências são da biblioteca padrão).
- Instalação rápida: `pip install pandas numpy matplotlib seaborn numba ipywidgets`

## Como executar
1. (Opcional) Crie um ambiente: `python3 -m venv .venv && source .venv/bin/activate`
2. Instale as dependências: `pip install pandas numpy matplotlib seaborn numba ipywidgets`
3. Abra o notebook: `jupyter notebook connect4_notebook.ipynb`
4. Rode as células conforme o objetivo:
   - Jogar: `play_game()` permite PvP ou humano vs IA.
   - Confrontos automáticos: `simulate_game()` ou `benchmark_menu_jupyter()` para comparar agentes.
   - Gerar dados: habilite o salvamento no benchmark para criar `mcts_moves.csv` (formato `s0`…`s41`, `move`).
   - Treinar ID3: execute `trainconnect4()` após gerar/carregar o CSV; use `get_id3_move()` para jogar com o modelo salvo (`connect4.pkl`).

## Estrutura
- `connect4_notebook.ipynb`: notebook principal com lógica do jogo, agentes e análises.
- `README.md`: este guia.

## Observações
- `trainIris()` assume a presença de `iris.csv` no diretório de trabalho (use o dataset público de Fisher).
- Curvas ROC, matrizes de confusão e impressão da árvore só aparecem após rodar as células de treino/avaliação.
- Aumentar muitas iterações do MCTS melhora a força do agente, mas eleva bastante o tempo por jogada; ajuste conforme o hardware.
