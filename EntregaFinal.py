#################################################IMPORTS#################################################################################
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams
import re
#################################################CLASESyFUNCIONES######################################################
class Grafico:
    def __init__(self, df):
        # Inicializa la clase con un DataFrame y un grafo dirigido vacío
        self.df = df
        self.G = nx.DiGraph()
    def _agregar_nodo(self, nodo, color, node_type):
        # Agrega un nodo al grafo con información sobre color y tipo
        self.G.add_node(nodo, color=color, node_type=node_type)
    def _agregar_arista(self, origen, destino, n_victimas):
        # Agrega una arista al grafo con un peso dado por el número de víctimas
        if self.G.has_edge(origen, destino):
            self.G[origen][destino]['weight'] += n_victimas
        else:
            self.G.add_edge(origen, destino, weight=n_victimas)
    def _separar_nodos(self):
        # Separa los nodos del grafo en dos listas según el tipo (localidad o víctima)
        localidad_nodes = [node for node, data in self.G.nodes(data=True) if data['node_type'] == 'localidad']
        victima_nodes = [node for node, data in self.G.nodes(data=True) if data['node_type'] == 'victima']
        return localidad_nodes, victima_nodes
    def _dibujar_grafo(self, pos, edge_widths, title):
        # Dibuja el grafo con información de posición, anchos de aristas y título
        plt.figure(figsize=(12, 8))
        # Cambiado el color de las aristas según el número de víctimas
        edge_colors = ['red' if weight > 1 else 'green' for weight in edge_widths]
        nx.draw(self.G, pos, with_labels=True, font_weight='bold', node_size=700,
                node_color=nx.get_node_attributes(self.G, 'color').values(), font_size=8,
                edge_color=edge_colors, width=edge_widths, edgecolors='black', arrows=True, arrowsize=20)
        # Etiquetas de las aristas con el número de víctimas
        labels = {(localidad, victima): f"{weight} víctimas" for localidad, victima, weight in self.G.edges(data='weight')}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, font_color='red')
        # Agregar leyendas para colores y tipos de nodos
        red_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Más de una víctima')
        green_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Ninguna o una víctima')
        localidad_legend = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='mediumorchid', markersize=10, label='Localidad')
        victima_legend = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', markersize=10, label='Víctima')
        plt.legend(handles=[red_patch, green_patch, localidad_legend, victima_legend], loc='upper right')
        # Ajustes del título y muestra el gráfico
        fig = plt.gcf()
        title_font = fm.FontProperties(family='serif', style='italic', weight='bold', size=16)
        fig.suptitle(title, fontsize=16, fontproperties=title_font, color='purple')
        plt.show()
#################################################OPCION1#################################################################################
    def crear_grafo_localidades_comunas(self):
        # Itera sobre cada fila del DataFrame
        for _, row in self.df.iterrows():
            # Extrae información de la fila
            localidad = row['localidad']
            victima = row['victima']
            n_victimas = row['n_victimas']
            # Agrega nodos al grafo para localidades y víctimas
            self._agregar_nodo(localidad, 'mediumorchid', 'localidad')
            self._agregar_nodo(victima, 'lightcoral', 'victima')
            # Agrega una arista entre la localidad y la víctima
            self._agregar_arista(localidad, victima, n_victimas)
        # Separa los nodos de localidades y víctimas
        localidad_nodes, victima_nodes = self._separar_nodos()
        # Calcula la posición de los nodos en el grafo
        pos = nx.shell_layout(self.G, nlist=[localidad_nodes, victima_nodes])
        # Obtiene los pesos de las aristas para determinar el ancho de las mismas
        edge_widths = [self.G[localidad][victima]['weight'] for localidad, victima in self.G.edges]
        # Dibuja el grafo con la posición calculada, los anchos de las aristas
        self._dibujar_grafo(pos, edge_widths, 'Relación entre Localidades y Víctimas')
#################################################OPCION2#################################################################################
def crear_grafo_comunas(df):
    # Definir las columnas relevantes
    columna_localidad = 'comuna'
    columna_victimas = 'n_victimas'
    # Crear un grafo dirigido vacío
    G = nx.DiGraph()
    # Agregar nodos al grafo a partir de las comunas únicas en el DataFrame
    G.add_nodes_from(df[columna_localidad].unique())
    # Iterar sobre todas las combinaciones únicas de comunas
    for localidad_origen in G.nodes():
        df_origen = df[df[columna_localidad] == localidad_origen]
        for localidad_destino in G.nodes():
            if localidad_origen != localidad_destino:
                df_destino = df[df[columna_localidad] == localidad_destino]
                # Calcular el peso como la suma de las víctimas en las comunas de origen y destino
                peso = df_origen[columna_victimas].sum() + df_destino[columna_victimas].sum()
                # Agregar una arista ponderada al grafo
                G.add_edge(localidad_origen, localidad_destino, weight=peso, label=f'{peso}')
    # Obtener el tamaño de los nodos basado en la cantidad de víctimas
    sizes = [sum(G[x][y]['weight'] for y in G.successors(x)) for x in G.nodes()]
    # Escalar los tamaños para que estén en un rango adecuado
    sizes = [size * 10 for size in sizes]
    # Calcular la disposición de los nodos utilizando el algoritmo de disposición 'spring_layout'
    pos = nx.spring_layout(G)
    # Obtener etiquetas de peso para las aristas
    labels = nx.get_edge_attributes(G, 'label')
    # Crear y mostrar el gráfico
    plt.figure(figsize=(12, 8))
    nx.draw(
        G, pos, with_labels=True, font_weight='bold', node_size=sizes, node_color='skyblue',
        edge_color='orange', linewidths=2, edgecolors='black', arrows=True, arrowsize=20
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red')
    fig = plt.gcf()
    fig.suptitle('Relación de Comunas por Cantidad de Víctimas', fontsize=16, y=1.0, color='mediumorchid', fontweight='bold', fontstyle='italic')
    plt.show()
#################################################OPCION3#################################################################################
def crear_grafo_comunas_tipo(df, tipo_victima):
    # Filtrar el DataFrame por tipo de víctima
    df = df[df['victima'] == tipo_victima]
    # Definir las columnas relevantes
    columna_localidad = 'comuna'
    columna_victimas = 'n_victimas'
    # Crear un grafo dirigido vacío
    G = nx.DiGraph()
    # Agregar nodos al grafo a partir de las comunas únicas en el DataFrame
    G.add_nodes_from(df[columna_localidad].unique())
    # Iterar sobre todas las combinaciones únicas de comunas
    for localidad_origen in G.nodes():
        df_origen = df[df[columna_localidad] == localidad_origen]
        for localidad_destino in G.nodes():
            if localidad_origen != localidad_destino:
                df_destino = df[df[columna_localidad] == localidad_destino]
                # Calcular el peso como la suma de las víctimas en las comunas de origen y destino
                peso = df_origen[columna_victimas].sum() + df_destino[columna_victimas].sum()
                # Agregar una arista ponderada al grafo
                G.add_edge(localidad_origen, localidad_destino, weight=peso, label=f'{peso}')
    # Obtener el tamaño de los nodos basado en la cantidad de víctimas
    sizes = [sum(G[x][y]['weight'] for y in G.successors(x)) for x in G.nodes()]
    # Escalar los tamaños para que estén en un rango adecuado
    sizes = [size * 10 for size in sizes]
    # Calcular la disposición de los nodos utilizando el algoritmo de disposición 'spring_layout'
    pos = nx.spring_layout(G)
    # Obtener etiquetas de peso para las aristas
    labels = nx.get_edge_attributes(G, 'label')
    # Crear y mostrar el gráfico
    plt.figure(figsize=(12, 8))
    nx.draw(
        G, pos, with_labels=True, font_weight='bold', node_size=sizes, node_color='skyblue',
        edge_color='orange', linewidths=2, edgecolors='black', arrows=True, arrowsize=20
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red')
    fig = plt.gcf()
    fig.suptitle(f'Relación de Comunas por Cantidad de Víctimas de {tipo_victima.capitalize()}', fontsize=16, y=1.0, color='mediumorchid', fontweight='bold', fontstyle='italic')
    plt.show()
#################################################OPCION4#################################################################################
def crear_grafo_localidades(df):
    # Definir las columnas relevantes
    columna_localidad = 'localidad'
    columna_victimas = 'n_victimas'
    # Eliminar filas con valores nulos en las columnas relevantes
    df = df.dropna(subset=[columna_localidad, columna_victimas])
    # Crear un grafo dirigido vacío
    G = nx.DiGraph()
    # Agregar nodos al grafo a partir de las localidades únicas en el DataFrame
    localidades_unicas = df[columna_localidad].unique()
    G.add_nodes_from(localidades_unicas)
    # Iterar sobre cada fila del DataFrame
    for _, row in df.iterrows():
        # Extraer información de la fila
        localidad_origen = row[columna_localidad]
        localidad_destino = row['localidad']
        cantidad_victimas = row[columna_victimas]
        # Agregar una arista ponderada al grafo
        if G.has_edge(localidad_origen, localidad_destino):
            G[localidad_origen][localidad_destino]['weight'] += cantidad_victimas
        else:
            G.add_edge(localidad_origen, localidad_destino, weight=cantidad_victimas)
    # Ordenar las localidades según la suma de las víctimas en las aristas
    localidades_ordenadas = sorted(G.nodes(), key=lambda x: sum(G[x][y]['weight'] for y in G.successors(x)))
    # Crear un gráfico de barras
    fig, ax = plt.subplots(figsize=(12, 6))
    # Agregar barras para cada localidad
    for localidad in localidades_ordenadas:
        barras = ax.bar(localidad, sum(G[localidad][y]['weight'] for y in G.successors(localidad)),
                        color='red', edgecolor='black')
    # Configurar etiquetas y título del gráfico
    ax.set_xlabel('Localidad', fontsize=12, color='orange', fontweight='bold', fontstyle='italic')
    ax.set_ylabel('Número de Víctimas', fontsize=12, color='orange', fontweight='bold', fontstyle='italic')
    ax.set_title('Número de Víctimas por Localidad', fontsize=16, color='mediumorchid', fontweight='bold', fontstyle='italic')
    # Configuraciones adicionales del gráfico
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # Añadir etiquetas a las barras
    for barra in barras:
        yval = barra.get_height()
        plt.text(barra.get_x() + barra.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom', fontsize=8)
    # Ajustar el diseño del gráfico y mostrarlo
    plt.tight_layout()
    plt.show()
#################################################MENU#########################################################
def mostrar_grafico(opcion, df):
    grafo_creator = Grafico(df)
    if opcion == '1':
        grafo_creator.crear_grafo_localidades_comunas()
    elif opcion == '2':
        crear_grafo_comunas(df)
    elif opcion == '3':
        tipo_victima = input("Ingresa el tipo de víctima (MOTO, AUTO, CICLISTA, CAMIONETA, PEATON, TRANSPORTE PUBLICO): ").upper()
        crear_grafo_comunas_tipo(df, tipo_victima)
    elif opcion == '4':   
        crear_grafo_localidades(df)  
# Lee el CSV
file_path = 'lesiones.csv'
try:
    # Lee el archivo CSV en un DataFrame
    df = pd.read_csv(file_path, sep=',', encoding='ISO-8859-1')
    # Define el patrón regular para buscar "sd" en cualquier columna
    pattern_sd = re.compile(r'.*sd.*', re.IGNORECASE)
    # Define el valor a remover, en este caso, "No Especificada"
    value_to_remove = "No Especificada"
    # Elimina las filas que cumplen con los patrones del DataFrame
    df = df[~(df.apply(lambda x: re.search(pattern_sd, str(x), flags=re.IGNORECASE).any(), axis=1) | df['columna_a_eliminar'].str.contains(value_to_remove))]
    # Manipulaciones con expresiones regulares, borra espacios en la columna localidad
    df['localidad'] = df['localidad'].apply(lambda x: re.sub(r'\s+', ' ', x.strip()))
    # Muestra el DataFrame
    print(df)

except FileNotFoundError:
    print(f"Error: El archivo '{file_path}' no se encuentra.")
except pd.errors.EmptyDataError:
    print(f"Error: El archivo '{file_path}' está vacío.")
except pd.errors.ParserError:
    print(f"Error: No se puede parsear el archivo '{file_path}'. Verifica el formato y los delimitadores.")
except Exception as e:
    print(f"Error desconocido al leer el archivo '{file_path}': {e}")

# Menú de selección de gráficos
while True:
    print("\n****************************************************")
    print("************** MENÚ DE GRÁFICOS *********************")
    print("****************************************************\n")
    print("Selecciona el gráfico a mostrar:")
    print("1. Relación de Localidades y tipo de Víctimas")
    print("2. Relación de Comunas por Cantidad de Víctimas")
    print("3. Relación de Comunas por tipo de Víctimas")
    print("4. Relación de Localidades por Cantidad de Víctimas")
    print("0. Salir")

    opcion = input("\nIngresa el número de la opción: ")

    if opcion == '0':
        print("\n****************************************************")
        print("*************** Gracias por usar el sistema *********")
        print("****************************************************")
        print("*******************Miembros del equipo:**************")
        print("******************PRIETO SEBASTIAN ISIDRO***********")
        print("********************REY BRIENZA AGUSTINA************")
        print("********************FERRETTI EMILIANO***************")
        print("*************************UNSAM**********************")
        print("*******************2do Cuatrimestre 2023************")
        break
    else:
        mostrar_grafico(opcion, df)
#################################################FIN MENU#########################################################
#################################################INTEGRANTES#########################################################
#########################PRIETO SEBASTIAN ISIDRO/REY BRIENZA AGUSTINA/FERRETTI EMILIANO##########################
#################################################INTEGRANTES#########################################################