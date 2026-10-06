# Classificação de emails de clientes com Jev

Classificação automática de emails de clientes (serviço de águas) em 15 categorias, usando o **Jev**, um modelo System One da [TypeSafe](https://typesafe.ai). O modelo não é treinado: recebe o assunto e o corpo do email, mais uma descrição de cada categoria, e devolve a categoria escolhida com uma confiança entre 0 e 1. A melhoria da accuracy vem de **afinar as descrições** das categorias em `labels.py`.

## Resultado final

| Conjunto | Emails com referência crab team | Accuracy (crab team) | Accuracy com confiança ≥ 90% |
|---|---|---|---|
| **Test** (nunca usado para afinar) | 50 | **92,0%** (46/50) | 97,7% em 88% dos emails |
| Dev (usado para afinar) | 109 | 85,3% (93/109) | 93,1% em 80% dos emails |
| Total (dev + test) | 159 | 87,4% (139/159) | |

- Com só 50 emails no test, cada erro vale 2 pontos percentuais. O intervalo de confiança a 95% fica em **~81% – 97%**.
- Contra a coluna `LastClassifications` a accuracy fica nos **~57–59%**. Esta referência é pouco consistente (por exemplo, emails com o mesmo pedido aparecem em categorias diferentes), por isso a referência principal é a do crab team.

## Dados

- **Origem:** `data/raw/exemplos_pseudonymized(Sheet1).csv`, com 588 emails pseudonimizados.
- **Colunas usadas:** `Subject_masked`, `BodyPlainText_masked`, `LastClassifications` e `potencial_classificação_crab_team`.
- **Referências:**
  - **crab team** é a classificação revista manualmente e a mais fiável, mas só existe em 159 emails.
  - **LastClassifications** existe em mais emails, mas tem muito ruído. "Triagem Manual" não conta como categoria.

## Passo a passo do que foi feito

1. **Categorias.** Criou-se `labels.py`, com as 15 categorias e uma descrição de cada uma.
2. **Primeiro teste com 20 emails.** Deu 85% de accuracy (17/20) e serviu para validar a abordagem.
3. **Interface para testar um a um.** A app Streamlit (`app.py`) permite ver como o modelo se porta em casos concretos, com as probabilidades de cada categoria.
4. **Limpeza do dataset** (`data.ipynb`). Removeram-se os avisos automáticos ("Este e-mail vem de fora da organização…", "External information…"), mesmo dentro de respostas citadas e com acentos estragados. Removeu-se também 1 email duplicado. O resultado, com 587 emails, está em `data/clean.csv`.
5. **Classificação dos 587 emails.** Deu 81,8% contra o crab team (130/159).
6. **Primeira afinação das descrições.** O erro mais comum era "2ª via" classificada como "Envio das faturas". Reescreveram-se as duas descrições: pedir faturas concretas é "2ª via", e a forma de receber as faturas é "Envio". A "2ª via" passou de 8 para 13 acertos em 15, e o total subiu para 83,6%.
7. **Divisão em dev e test** (`split.py`). Dentro de cada categoria, 70% dos emails vão para o dev e 30% para o test, ficando 410 no dev e 177 no test. O dev serve para afinar e o test só para medir no fim. Se se afinasse a olhar para todos os emails, seria como dar ao aluno as perguntas do exame: a accuracy subia, mas não saberíamos se o modelo generaliza.
8. **Afinação no dev.**
   - **Base:** 79,8% (87/109).
   - **v2:** o crab team classifica como "Contratos" qualquer alteração de dados do cliente (IBAN/NIB, email de contacto ou de envio de faturas). Acrescentou-se isso à descrição de "Contratos" e retirou-se de "Envio" e "Pagamento das faturas". Resultado: 86,2%.
   - **v3 (final):** o débito direto voltou para "Pagamento das faturas", porque o LastClassifications o põe sempre lá e o próprio crab team estava dividido. Resultado: 85,3% no crab, e o LastClassifications recuperou de 54,6% para 56,9%.
9. **Medição final no test.** Correu-se uma única vez e deu 92,0% (46/50).

### Evolução

| Etapa | Conjunto | Crab team | LastClassifications |
|---|---|---|---|
| Primeiro teste | 20 emails | 85,0% | — |
| Descrições originais | todos (587) | 81,8% | 59,5% |
| Afinação "2ª via" / "Envio" | todos (587) | 83,6% | 59,8% |
| Base no dev | dev | 79,8% | 58,4% |
| v2: alterações de dados em "Contratos" | dev | 86,2% | 54,6% |
| **v3: débito direto em "Pagamento"** | dev | **85,3%** | **56,9%** |
| **Final** | **test** | **92,0%** | **58,8%** |

## Erros no test

| Assunto | Crab team | Previsão | Confiança |
|---|---|---|---|
| Pagamentos de faturas | Emissão de 2ª vias | Dados Pagamento | 0,87 |
| Valores elevados no preço da água | Tarifa social | FW E-mail EDOC | 0,81 |
| Re: FW: Reclamação da qualidade da água | FW E-mail EDOC | Elogio | 0,99 |
| Fatura de consumo | Dados Pagamento | Pagamento | 0,53 |

Estes erros **não** foram usados para mexer nas descrições, para o test continuar a ser uma medição "às cegas".

## O que é a confiança

Para cada email, o Jev dá uma probabilidade a cada categoria. A `confidence` é a probabilidade da categoria escolhida.

- **Perto de 1,0:** o modelo não teve dúvidas.
- **Perto de 0,4–0,5:** o modelo estava dividido entre categorias.

Os erros concentram-se nos casos de baixa confiança. Isso permite um uso prático: classificar automaticamente quando a confiança é ≥ 90% (no test, 97,7% de acerto em 88% dos emails) e mandar o resto para revisão humana.

## Limitações

- **Pouca referência fiável.** Só 159 emails têm classificação do crab team, e categorias como Tarifa social, Tarifa familiar, Elogio e Acordo de Pagamento têm entre 1 e 5 exemplos. Nessas categorias não há dados suficientes para saber como o modelo se porta.
- **Test pequeno.** Os 92% têm uma margem larga (~81–97%).
- **Referências inconsistentes.** O débito direto, por exemplo, aparece em categorias diferentes conforme quem classificou.

## Estrutura

```
labels.py          categorias e descrições (o que se afina)
classify.py        limpeza do texto, chamada ao Jev, avaliação e relatório
split.py           divisão dev/test estratificada → data/split.csv
data.ipynb         limpeza do dataset → data/clean.csv; análise dos resultados
app.py             interface Streamlit para testar emails um a um
requirements.txt   dependências Python
pyproject.toml     configuração do Black e do pylint (linhas até 100 caracteres)
SKILL.md           documentação da TypeSafe sobre o Jev (licença MIT), para referência
data/              (não incluída no repo: emails de clientes)
  raw/             dataset original
  clean.csv        dataset limpo (587 emails)
  split.csv        divisão dev/test
  resultados/      uma pasta por etapa, cada uma com predictions.csv e report.txt
    01_amostra_20_emails/          85,0%  primeiro teste (20 emails)
    02_todos_descricoes_originais/ 81,8%  587 emails, descrições originais
    03_todos_afinacao_2via/        83,6%  587 emails, após afinar 2ª via / Envio
    04_dev_base/                   79,8%  dev, ponto de partida
    05_dev_v2_contratos/           86,2%  dev, alterações de dados em Contratos
    06_dev_v3_final/               85,3%  dev, débito direto em Pagamento (final)
    07_test_final/                 92,0%  test, medição final
    ultima_corrida/                onde o classify.py grava cada nova corrida
```

## Como correr

Requisitos: instalar as dependências com `pip install -r requirements.txt` e criar um ficheiro `.env` com `TYPESAFE_API_KEY=...`.

A pasta `data/` não está no repositório, porque contém emails de clientes. Para correr, coloca o dataset original em `data/raw/` e corre o `data.ipynb` para gerar o `clean.csv`.

```bash
python split.py                     # gera data/split.csv (só uma vez)
python classify.py --split dev      # avalia no dev → data/resultados/ultima_corrida/report_dev.txt
python classify.py --split test     # avalia no test (só no fim)
streamlit run app.py                # interface para testar emails um a um
```

Cada corrida grava em `data/resultados/ultima_corrida/` e substitui a anterior. Para guardar um resultado, copia essa pasta para `data/resultados/` com o próximo número e um nome curto.

Outras opções do `classify.py`:
- `--only-crab` classifica só os emails com referência do crab team.
- `--limit N` classifica uma amostra de N emails.
- `--workers N` define quantos pedidos correm em paralelo.
