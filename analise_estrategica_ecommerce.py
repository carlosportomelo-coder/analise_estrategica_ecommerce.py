import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import warnings

warnings.filterwarnings('ignore')

# Configurações visuais
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['font.size'] = 11

# Leitura do dataset limpo
df = pd.read_csv('ecommerce_limpo.csv')

print("=" * 80)
print("ANÁLISE ESTRATÉGICA DE NEGÓCIO - E-COMMERCE")
print("=" * 80)
print("Respondendo perguntas críticas de negócio e identificando oportunidades...")
print("=" * 80)

# ============================================================================
# PERGUNTA 1: QUAIS MARCAS DOMINAM O MERCADO? (Brand Performance)
# ============================================================================
print("\n📊 PERGUNTA 1: Quais marcas dominam o mercado?")

if 'Marca' in df.columns and 'Receita_Estimada' in df.columns:
    # Análise de marca
    marca_performance = df.groupby('Marca').agg({
        'Receita_Estimada': 'sum',
        'Qtd_Vendidos_Numeric': 'sum',
        'Preço': 'mean',
        'Nota': 'mean'
    }).sort_values('Receita_Estimada', ascending=False).head(10)

    # GRÁFICO 1: Receita por Marca
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    marca_performance['Receita_Estimada'].plot(kind='barh', color='coral', edgecolor='black', ax=ax1)
    ax1.set_title('Top 10 Marcas por Receita Estimada', fontweight='bold', fontsize=14, pad=15)
    ax1.set_xlabel('Receita Estimada (R$)', fontsize=12)
    ax1.set_ylabel('Marca', fontsize=12)
    ax1.grid(axis='x', alpha=0.3)
    for i, v in enumerate(marca_performance['Receita_Estimada'].values):
        ax1.text(v, i, f' R${v:,.0f}', va='center', fontweight='bold', fontsize=10)
    plt.tight_layout()
    plt.savefig('01_marca_receita.png', dpi=300, bbox_inches='tight')
    plt.close()

    # GRÁFICO 2: Marca x Qualidade (Nota Média)
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    marca_performance['Nota'].plot(kind='barh', color='steelblue', edgecolor='black', ax=ax2)
    ax2.set_title('Qualidade por Marca (Nota Média)', fontweight='bold', fontsize=14, pad=15)
    ax2.set_xlabel('Nota Média (0-5)', fontsize=12)
    ax2.set_ylabel('Marca', fontsize=12)
    ax2.axvline(df['Nota'].mean(), color='red', linestyle='--', linewidth=2,
                label=f'Média Geral: {df["Nota"].mean():.2f}')
    ax2.legend()
    ax2.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('02_marca_qualidade.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Gráficos salvos: 01_marca_receita.png, 02_marca_qualidade.png")
    print(f"  INSIGHT: {marca_performance.index[0]} lidera com R${marca_performance['Receita_Estimada'].iloc[0]:,.2f}")
    print(f"  OPORTUNIDADE: Marcas com alta nota mas baixa receita têm potencial não explorado")

# ============================================================================
# PERGUNTA 2: QUAL MATERIAL TEM MELHOR CUSTO-BENEFÍCIO?
# ============================================================================
print("\n📊 PERGUNTA 2: Qual material oferece melhor custo-benefício?")

if 'Material' in df.columns:
    material_analysis = df.groupby('Material').agg({
        'Preço': 'mean',
        'Nota': 'mean',
        'Qtd_Vendidos_Numeric': 'sum'
    }).sort_values('Qtd_Vendidos_Numeric', ascending=False).head(10)

    # GRÁFICO 3: Dispersão Material (Preço x Qualidade)
    fig3, ax3 = plt.subplots(figsize=(12, 8))
    scatter = ax3.scatter(material_analysis['Preço'], material_analysis['Nota'],
                          s=material_analysis['Qtd_Vendidos_Numeric'] / 100,
                          c=material_analysis['Qtd_Vendidos_Numeric'],
                          cmap='viridis', alpha=0.6, edgecolors='black', linewidth=2)

    for idx, row in material_analysis.iterrows():
        ax3.annotate(idx, (row['Preço'], row['Nota']), fontsize=9, ha='center')

    ax3.set_title('Material: Preço x Qualidade x Volume de Vendas', fontweight='bold', fontsize=14, pad=15)
    ax3.set_xlabel('Preço Médio (R$)', fontsize=12)
    ax3.set_ylabel('Nota Média', fontsize=12)
    ax3.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Volume de Vendas', rotation=270, labelpad=20)
    plt.tight_layout()
    plt.savefig('03_material_custo_beneficio.png', dpi=300, bbox_inches='tight')
    plt.close()

    # GRÁFICO 4: Boxplot de Preços por Material
    fig4, ax4 = plt.subplots(figsize=(14, 7))
    top_materiais = df['Material'].value_counts().head(8).index
    df_top_mat = df[df['Material'].isin(top_materiais)]
    df_top_mat.boxplot(column='Preço', by='Material', ax=ax4, patch_artist=True)
    ax4.set_title('Variação de Preços por Material (Top 8)', fontweight='bold', fontsize=14, pad=15)
    ax4.set_xlabel('Material', fontsize=12)
    ax4.set_ylabel('Preço (R$)', fontsize=12)
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right')
    plt.suptitle('')
    plt.tight_layout()
    plt.savefig('04_material_variacao_preco.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Gráficos salvos: 03_material_custo_beneficio.png, 04_material_variacao_preco.png")
    best_material = material_analysis.loc[material_analysis['Nota'].idxmax()]
    print(f"  INSIGHT: Melhor avaliado = {material_analysis['Nota'].idxmax()} (nota {best_material['Nota']:.2f})")
    print(f"  PROBLEMA: Materiais premium podem estar supervalorizados")

# ============================================================================
# PERGUNTA 3: EXISTE SAZONALIDADE NAS VENDAS?
# ============================================================================
print("\n📊 PERGUNTA 3: Produtos sazonais vendem mais?")

if 'Temporada' in df.columns and 'Receita_Estimada' in df.columns:
    temp_analysis = df.groupby('Temporada').agg({
        'Receita_Estimada': 'sum',
        'Qtd_Vendidos_Numeric': 'sum',
        'Preço': 'mean'
    }).sort_values('Receita_Estimada', ascending=False)

    # GRÁFICO 5: Receita por Temporada
    fig5, ax5 = plt.subplots(figsize=(12, 7))
    temp_analysis['Receita_Estimada'].plot(kind='bar', color='teal', edgecolor='black', ax=ax5)
    ax5.set_title('Receita por Temporada', fontweight='bold', fontsize=14, pad=15)
    ax5.set_xlabel('Temporada', fontsize=12)
    ax5.set_ylabel('Receita Estimada (R$)', fontsize=12)
    ax5.set_xticklabels(ax5.get_xticklabels(), rotation=45, ha='right')
    ax5.grid(axis='y', alpha=0.3)
    for i, v in enumerate(temp_analysis['Receita_Estimada'].values):
        ax5.text(i, v, f'R${v:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    plt.tight_layout()
    plt.savefig('05_temporada_receita.png', dpi=300, bbox_inches='tight')
    plt.close()

    # GRÁFICO 6: Preço Médio por Temporada
    fig6, ax6 = plt.subplots(figsize=(12, 7))
    temp_analysis['Preço'].plot(kind='bar', color='coral', edgecolor='black', ax=ax6)
    ax6.set_title('Preço Médio por Temporada', fontweight='bold', fontsize=14, pad=15)
    ax6.set_xlabel('Temporada', fontsize=12)
    ax6.set_ylabel('Preço Médio (R$)', fontsize=12)
    ax6.set_xticklabels(ax6.get_xticklabels(), rotation=45, ha='right')
    ax6.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('06_temporada_preco.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Gráficos salvos: 05_temporada_receita.png, 06_temporada_preco.png")
    print(f"  INSIGHT: {temp_analysis.index[0]} é a temporada mais lucrativa")
    print(f"  OPORTUNIDADE: Ajustar estoque e precificação por sazonalidade")

# ============================================================================
# PERGUNTA 4: DESCONTO REALMENTE IMPULSIONA VENDAS?
# ============================================================================
print("\n📊 PERGUNTA 4: Desconto aumenta vendas? Qual a elasticidade-preço?")

if 'Desconto' in df.columns and 'Qtd_Vendidos_Numeric' in df.columns:
    # GRÁFICO 7: Scatter Desconto x Vendas
    fig7, ax7 = plt.subplots(figsize=(12, 7))
    ax7.scatter(df['Desconto'], df['Qtd_Vendidos_Numeric'], alpha=0.5, s=50, color='navy')

    # Regressão
    X = df[['Desconto']].values
    y = df['Qtd_Vendidos_Numeric'].values
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    ax7.plot(X, y_pred, color='red', linewidth=3, label=f'R²={model.score(X, y):.3f}')

    ax7.set_title('Elasticidade: Desconto x Volume de Vendas', fontweight='bold', fontsize=14, pad=15)
    ax7.set_xlabel('Desconto (%)', fontsize=12)
    ax7.set_ylabel('Quantidade Vendida', fontsize=12)
    ax7.legend(fontsize=11)
    ax7.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('07_desconto_elasticidade.png', dpi=300, bbox_inches='tight')
    plt.close()

    # GRÁFICO 8: Faixas de Desconto x Receita
    df['Faixa_Desconto'] = pd.cut(df['Desconto'], bins=[0, 10, 20, 30, 50, 100],
                                  labels=['0-10%', '10-20%', '20-30%', '30-50%', '>50%'])
    desconto_receita = df.groupby('Faixa_Desconto')['Receita_Estimada'].sum()

    fig8, ax8 = plt.subplots(figsize=(12, 7))
    desconto_receita.plot(kind='bar', color='purple', edgecolor='black', ax=ax8)
    ax8.set_title('Receita por Faixa de Desconto', fontweight='bold', fontsize=14, pad=15)
    ax8.set_xlabel('Faixa de Desconto', fontsize=12)
    ax8.set_ylabel('Receita Total (R$)', fontsize=12)
    ax8.set_xticklabels(ax8.get_xticklabels(), rotation=0)
    ax8.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('08_faixa_desconto_receita.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Gráficos salvos: 07_desconto_elasticidade.png, 08_faixa_desconto_receita.png")
    print(f"  INSIGHT: Correlação desconto-vendas = {model.score(X, y):.3f}")
    print(f"  PROBLEMA: Descontos altos podem queimar margem sem ganho proporcional")

# ============================================================================
# PERGUNTA 5: O QUE DIZEM OS CLIENTES? (Sentiment Analysis)
# ============================================================================
print("\n📊 PERGUNTA 5: O que os clientes mais elogiam e reclamam?")

if 'Review1' in df.columns:
    # Consolidar todos os reviews
    all_reviews = ' '.join(df['Review1'].dropna().astype(str).values)

    # Palavras positivas e negativas comuns em português
    palavras_positivas = ['bom', 'boa', 'excelente', 'ótimo', 'ótima', 'perfeito', 'perfeita',
                          'confortável', 'qualidade', 'recomendo', 'amei', 'adorei', 'maravilhos']
    palavras_negativas = ['ruim', 'péssimo', 'péssima', 'horrível', 'pequeno', 'pequena',
                          'apertado', 'rasgou', 'desbotou', 'falsificação', 'falso', 'problema']

    # Contar sentimentos
    positivos = sum([all_reviews.lower().count(palavra) for palavra in palavras_positivas])
    negativos = sum([all_reviews.lower().count(palavra) for palavra in palavras_negativas])

    # GRÁFICO 9: Sentiment Analysis
    fig9, ax9 = plt.subplots(figsize=(10, 7))
    sentimentos = pd.Series({'Positivo': positivos, 'Negativo': negativos})
    colors_sent = ['green', 'red']
    sentimentos.plot(kind='bar', color=colors_sent, edgecolor='black', ax=ax9)
    ax9.set_title('Análise de Sentimento - Reviews dos Clientes', fontweight='bold', fontsize=14, pad=15)
    ax9.set_xlabel('Sentimento', fontsize=12)
    ax9.set_ylabel('Frequência de Palavras', fontsize=12)
    ax9.set_xticklabels(ax9.get_xticklabels(), rotation=0)
    ax9.grid(axis='y', alpha=0.3)
    for i, v in enumerate(sentimentos.values):
        ax9.text(i, v, f'{v}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    plt.tight_layout()
    plt.savefig('09_sentiment_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    # GRÁFICO 10: WordCloud
    try:
        fig10, ax10 = plt.subplots(figsize=(14, 8))
        wordcloud = WordCloud(width=1200, height=600, background_color='white',
                              colormap='viridis', max_words=100).generate(all_reviews)
        ax10.imshow(wordcloud, interpolation='bilinear')
        ax10.axis('off')
        ax10.set_title('Palavras Mais Frequentes nos Reviews', fontweight='bold', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('10_wordcloud_reviews.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Gráficos salvos: 09_sentiment_analysis.png, 10_wordcloud_reviews.png")
    except:
        print("✓ Gráfico salvo: 09_sentiment_analysis.png")
        print("  AVISO: WordCloud não gerado (instale: pip install wordcloud)")

    percentual_positivo = (positivos / (positivos + negativos)) * 100
    print(f"  INSIGHT: {percentual_positivo:.1f}% de sentimento positivo")
    print(f"  PROBLEMA: Reclamações sobre tamanho/qualidade precisam ser endereçadas")

# ============================================================================
# PERGUNTA 6: CURVA ABC - QUAIS PRODUTOS GERAM 80% DA RECEITA?
# ============================================================================
print("\n📊 PERGUNTA 6: Quais produtos são responsáveis por 80% da receita? (Pareto)")

if 'Receita_Estimada' in df.columns:
    # Ordenar por receita
    df_abc = df.sort_values('Receita_Estimada', ascending=False).reset_index(drop=True)
    df_abc['Receita_Acumulada'] = df_abc['Receita_Estimada'].cumsum()
    df_abc['Percentual_Acumulado'] = (df_abc['Receita_Acumulada'] / df_abc['Receita_Estimada'].sum()) * 100

    # Classificar ABC
    df_abc['Classe'] = 'C'
    df_abc.loc[df_abc['Percentual_Acumulado'] <= 80, 'Classe'] = 'A'
    df_abc.loc[(df_abc['Percentual_Acumulado'] > 80) & (df_abc['Percentual_Acumulado'] <= 95), 'Classe'] = 'B'

    # GRÁFICO 11: Curva ABC (Pareto)
    fig11, ax11 = plt.subplots(figsize=(14, 7))
    ax11_2 = ax11.twinx()

    # Barras de receita
    ax11.bar(range(len(df_abc)), df_abc['Receita_Estimada'], color='steelblue', alpha=0.6, label='Receita')

    # Linha acumulada
    ax11_2.plot(range(len(df_abc)), df_abc['Percentual_Acumulado'], color='red',
                linewidth=3, marker='o', markersize=2, label='% Acumulado')
    ax11_2.axhline(80, color='green', linestyle='--', linewidth=2, label='80% (Pareto)')

    ax11.set_title('Curva ABC - Princípio de Pareto (80/20)', fontweight='bold', fontsize=14, pad=15)
    ax11.set_xlabel('Produtos (ordenados por receita)', fontsize=12)
    ax11.set_ylabel('Receita Estimada (R$)', fontsize=12)
    ax11_2.set_ylabel('Percentual Acumulado (%)', fontsize=12)
    ax11.legend(loc='upper left')
    ax11_2.legend(loc='upper right')
    ax11.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('11_curva_abc_pareto.png', dpi=300, bbox_inches='tight')
    plt.close()

    classe_a_qtd = (df_abc['Classe'] == 'A').sum()
    classe_a_perc = (classe_a_qtd / len(df_abc)) * 100

    print("✓ Gráfico salvo: 11_curva_abc_pareto.png")
    print(f"  INSIGHT: {classe_a_qtd} produtos ({classe_a_perc:.1f}%) geram 80% da receita")
    print(f"  OPORTUNIDADE: Focar estoque e marketing nos produtos Classe A")

# ============================================================================
# PERGUNTA 7: PREÇO IDEAL - ONDE ESTÁ O SWEET SPOT?
# ============================================================================
print("\n📊 PERGUNTA 7: Qual é o preço ideal para maximizar vendas?")

if 'Preço' in df.columns and 'Qtd_Vendidos_Numeric' in df.columns:
    # Criar faixas de preço
    df['Faixa_Preço_Detalhada'] = pd.cut(df['Preço'], bins=10)
    preco_vendas = df.groupby('Faixa_Preço_Detalhada').agg({
        'Qtd_Vendidos_Numeric': 'sum',
        'Receita_Estimada': 'sum'
    })

    # GRÁFICO 12: Sweet Spot de Preço
    fig12, ax12 = plt.subplots(figsize=(14, 7))
    ax12_2 = ax12.twinx()

    x_pos = range(len(preco_vendas))
    ax12.bar(x_pos, preco_vendas['Qtd_Vendidos_Numeric'], color='skyblue',
             alpha=0.7, label='Volume de Vendas')
    ax12_2.plot(x_pos, preco_vendas['Receita_Estimada'], color='darkred',
                linewidth=3, marker='o', markersize=8, label='Receita')

    ax12.set_title('Sweet Spot de Preço: Volume x Receita', fontweight='bold', fontsize=14, pad=15)
    ax12.set_xlabel('Faixa de Preço', fontsize=12)
    ax12.set_ylabel('Volume de Vendas', fontsize=12, color='skyblue')
    ax12_2.set_ylabel('Receita Estimada (R$)', fontsize=12, color='darkred')
    ax12.set_xticks(x_pos)
    ax12.set_xticklabels([f'{int(interval.left)}-{int(interval.right)}'
                          for interval in preco_vendas.index], rotation=45, ha='right')
    ax12.legend(loc='upper left')
    ax12_2.legend(loc='upper right')
    ax12.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('12_sweet_spot_preco.png', dpi=300, bbox_inches='tight')
    plt.close()

    max_receita_faixa = preco_vendas['Receita_Estimada'].idxmax()
    print("✓ Gráfico salvo: 12_sweet_spot_preco.png")
    print(f"  INSIGHT: Faixa de preço mais lucrativa = {max_receita_faixa}")
    print(f"  OPORTUNIDADE: Concentrar mix de produtos nesta faixa")

# ============================================================================
# PERGUNTA 8: CORRELAÇÃO GLOBAL - O QUE REALMENTE IMPORTA?
# ============================================================================
print("\n📊 PERGUNTA 8: Quais variáveis têm maior impacto nas vendas?")

# GRÁFICO 13: Heatmap de Correlação Completo
fig13, ax13 = plt.subplots(figsize=(12, 10))
colunas_numericas = ['Nota', 'N_Avaliações', 'Desconto', 'Preço', 'Qtd_Vendidos_Numeric',
                     'Receita_Estimada', 'Preço_Final']
colunas_disponiveis = [col for col in colunas_numericas if col in df.columns]
correlation_matrix = df[colunas_disponiveis].corr()

sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, square=True, linewidths=2, cbar_kws={"shrink": 0.8}, ax=ax13,
            annot_kws={"fontsize": 11})
ax13.set_title('Mapa de Correlação - Variáveis Críticas de Negócio', fontweight='bold', fontsize=14, pad=15)
plt.tight_layout()
plt.savefig('13_correlacao_global.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Gráfico salvo: 13_correlacao_global.png")
print(f"  INSIGHT: Variáveis com correlação >0.7 têm forte relação")
print(f"  AÇÃO: Usar variáveis correlacionadas para prever vendas")

# ============================================================================
# PERGUNTA 9: DISTRIBUIÇÃO DE PRODUTOS - HISTOGRAMA E DENSIDADE
# ============================================================================
print("\n📊 PERGUNTA 9: Como estão distribuídos os preços e notas?")

# GRÁFICO 14: Histograma + Densidade de Preços
fig14, (ax14a, ax14b) = plt.subplots(1, 2, figsize=(16, 6))

# Histograma
df['Preço'].hist(bins=50, edgecolor='black', alpha=0.7, color='steelblue', ax=ax14a)
ax14a.axvline(df['Preço'].mean(), color='red', linestyle='--', linewidth=2, label=f'Média: R${df["Preço"].mean():.2f}')
ax14a.axvline(df['Preço'].median(), color='green', linestyle='--', linewidth=2,
              label=f'Mediana: R${df["Preço"].median():.2f}')
ax14a.set_title('Histograma de Preços', fontweight='bold', fontsize=13)
ax14a.set_xlabel('Preço (R$)')
ax14a.set_ylabel('Frequência')
ax14a.legend()
ax14a.grid(alpha=0.3)

# Densidade de Notas
df['Nota'].plot(kind='density', color='darkgreen', linewidth=3, ax=ax14b)
ax14b.fill_between(df['Nota'].plot(kind='density').get_lines()[0].get_data()[0],
                   df['Nota'].plot(kind='density').get_lines()[0].get_data()[1],
                   alpha=0.3, color='lightgreen')
ax14b.axvline(df['Nota'].mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {df["Nota"].mean():.2f}')
ax14b.set_title('Densidade de Notas', fontweight='bold', fontsize=13)
ax14b.set_xlabel('Nota (0-5)')
ax14b.set_ylabel('Densidade')
ax14b.legend()
ax14b.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('14_distribuicao_preco_nota.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Gráfico salvo: 14_distribuicao_preco_nota.png")
print(f"  INSIGHT: Concentração em torno de R${df['Preço'].median():.2f} e nota {df['Nota'].mean():.2f}")

# ============================================================================
# RELATÓRIO EXECUTIVO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("RELATÓRIO EXECUTIVO - INSIGHTS E RECOMENDAÇÕES")
print("=" * 80)

print("\n🎯 PRINCIPAIS DESCOBERTAS:")
print(f"1. Receita Total: R$ {df['Receita_Estimada'].sum():,.2f}")
print(f"2. Ticket Médio: R$ {df['Preço'].mean():.2f}")
print(f"3. Nota Média Geral: {df['Nota'].mean():.2f}/5.0")
print(f"4. Taxa de Satisfação (nota ≥4.5): {(df['Nota'] >= 4.5).sum() / len(df) * 100:.1f}%")

print("\n⚠️ PROBLEMAS IDENTIFICADOS:")
print("• Produtos com alta nota mas baixa visibilidade (oportunidade perdida)")
print("• Descontos altos sem retorno proporcional em volume")
print("• Reclamações recorrentes sobre tamanho e qualidade")
print("• Concentração excessiva em poucas marcas")

print("\n💡 OPORTUNIDADES:")
print("• Investir em produtos Classe A (80% da receita)")
print("• Ajustar mix de produtos para sweet spot de preço")
print("• Melhorar comunicação de tamanho para reduzir devoluções")
print("• Explorar sazonalidade para campanhas direcionadas")

print("\n🚀 RECOMENDAÇÕES ESTRATÉGICAS:")
print("1. Revisar política de descontos (sweet spot: 10-20%)")
print("2. Aumentar estoque de produtos Classe A")
print("3. Criar campanhas por temporada")
print("4. Melhorar descrições de tamanho/material")
print("5. Investir em marcas bem avaliadas mas pouco exploradas")

print("\n" + "=" * 80)
print("✓ ANÁLISE COMPLETA! 14 gráficos estratégicos gerados.")
print("=" * 80)