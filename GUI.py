from PySimpleGUI import PySimpleGUI as sg
import importlib.util
import json
import sys
import os
import AeroGA.AeroGA

############################################################
########################## Configs #########################
############################################################

theme = 'DarkBlue12'
# theme = 'Reddit'

# Verificar se existe um arquivo de configuração
config_file = 'config.json'
try:
    with open(config_file, 'r') as file:
        config = json.load(file)
except FileNotFoundError:
    config = {'usuario': '', 'senha': '', 'salvar_login': False}

# Inputs iniciais
classes_list = ['Regular', 'Micro']
selection_list = ['Tournament', 'Roulette','Rank']
crossover_list = ['SBX', '1-Point','2-Point']
mutation_list = ['Gaussian', 'Polynomial']
elitism_list = ['Global', 'Local']
users_list = {
    'teste': '0000',
    'albatroz': '0000',
    '': ''
}

############################################################
######################## Funções Aux #######################
############################################################

def converte_to_list(string):
    # retira os colchetes
    string = string.strip('[]')

    # Separa os valores usando a vírgula como delimitador
    valores = string.split(',')

    # Converte cada valor para float ou int
    lista = []
    for valor in valores:
        if '.' in valor:
            lista.append(float(valor))
        else:
            lista.append(int(valor))

    return lista

############################################################
############################ GUI ###########################
############################################################

# Layout
sg.theme(theme)
layout_login = [
    [sg.Text('User:'), sg.Input(key='usuario', size=(20, 1), default_text=config['usuario'])],
    [sg.Text('Password:'), sg.Input(key='senha', password_char='*', size=(16, 1), default_text=config['senha'])],
    [sg.Checkbox('Save Login?', key='salvar_login', default=config['salvar_login'])],
    [sg.Checkbox('Use Setup File?', key='use_setup', default=False)],
    [sg.Button('Sign In')]
]

# Janela de Login
janela_login = sg.Window('AeroGA - Login', layout_login)

# Ler os eventos
while True:
    eventos, valores = janela_login.read()
    if eventos == sg.WINDOW_CLOSED:
        break
    if eventos == 'Sign In':
        usuario = valores['usuario']
        senha = valores['senha']
        salvar_login = valores['salvar_login']
        use_setup = valores['use_setup']

        # Verificar se existe um arquivo de configuração
        setup = {'class': '', 'min_values': '','max_values': '','num_variables': '','num_generations': '','elite_count': '','elitism': '','n_threads': '','selection': '','crossover': '','mutation': ''}
        if use_setup:
            setup_file = 'setup.json'
            try:
                with open(setup_file, 'r') as file:
                    setup = json.load(file)
            except FileNotFoundError:
                print("Setup file was not found.")
                # Exibir aviso em uma janela popup personalizada
                sg.popup('Aviso: O arquivo setup.json não foi encontrado.', title='Aviso', icon='warning')


        if usuario in users_list and senha == users_list[usuario]:
            if salvar_login:
                config['usuario'] = usuario
                config['senha'] = senha
                config['salvar_login'] = salvar_login
                with open(config_file, 'w') as file:
                    json.dump(config, file)
            janela_login.close()  # Fechar a janela de login

            # Layout da janela de otimização
            sg.theme(theme)
            layout_nova_janela = [
                [sg.TabGroup([
                    [
                    sg.Tab('Genetic Algorithm', layout=[
                        [sg.Text('Optimization Inputs', font=('Helvetica', 18))],
                        [sg.Text('Class'), sg.Combo(classes_list, key='classe', default_value=setup['class']), sg.Button('Select File', key='select_dir')],
                        [sg.Text('Lower Bounds:'), sg.InputText(key='min_values', size=(60, 1), enable_events=True, default_text=setup['min_values'])],
                        [sg.Text('Upper Bounds:'), sg.InputText(key='max_values', size=(60, 1), enable_events=True, default_text=setup['max_values'])],
                        [sg.Text('Number of Variables'), sg.Input(key='num_variables', size=(5,1), default_text=setup['num_variables'])],
                        [sg.Text('Number of Generations'), sg.Input(key='num_generations', size=(5,1), default_text=setup['num_generations'])],
                        [sg.Text('Number of Elitist Solutions'), sg.Input(key='elite_count', size=(5,1), default_text=setup['elite_count'])],
                        [sg.Text('Elitism:'), sg.Combo(elitism_list, key='elitism', default_value=setup['elitism'])],
                        [sg.Text('Number of Threads'), sg.Input(key='n_threads',  size=(5,1), default_text=setup['n_threads'])],
                        [sg.Text('Selection:'), sg.Combo(selection_list, key='selection', default_value=setup['selection']),sg.Text('Crossover:'), sg.Combo(crossover_list, key='crossover', default_value=setup['crossover']),sg.Text('Mutation:'), sg.Combo(mutation_list, key='mutation', default_value=setup['mutation'])],
                        [sg.Text('Plotting Options:'), sg.Checkbox('Plot Fitness', key='plotfit', default=True), sg.Checkbox('Box Plot', key='boxplot'), sg.Checkbox('Parallel Curves', key='plotparallel')],
                        [sg.Button('Optimize')],
                        [sg.Output(size=(80, 20))],
                        [sg.Button('Exit', button_color=('white', 'red'))]
                        ]), 
                    sg.Tab('Results', layout=[[
                        sg.Text('Conteúdo da aba Plots')]]),
                    sg.Tab('Information', layout=[
                        [sg.Text('Qualquer dúvida sobre o funcionamento da interface favor contatar:')],
                        [sg.Text('Autor:'), sg.Text('Krigor Rosa')],
                        [sg.Text('Email:'), sg.Text('krigorsilva13@gmail.com')],
                        [sg.Column([[sg.Image('aero.png', pad=(100, 50), size=(400, 200))]], justification='center')],
                        ]),
                    ]
                ])]
            ]

            # Nova janela
            janela_nova = sg.Window('AeroGA - Optimization', layout_nova_janela)

            # Ler os eventos da nova janela
            while True:
                eventos2, valores_opt = janela_nova.read()
                if eventos2 == sg.WINDOW_CLOSED or eventos2 == 'Exit':
                    break
                if eventos2 == 'select_dir':
                    folder_path = sg.popup_get_file('Select a Python file', file_types=(('Python Files', '*.py'),))
                    if folder_path:
                        nome_main_fn_mdo = os.path.basename(folder_path)
                        caminho_diretorio = os.path.dirname(folder_path)
                        mdo_main, extensao = os.path.splitext(nome_main_fn_mdo)
                        sys.path.append(caminho_diretorio)
                        print("---------------------------------------------------------- INPUTS --------------------------------------------------------------------")
                        print(f"Selected directory: {folder_path}")

                        # Importar as funções do arquivo .py
                        module_path = os.path.join(caminho_diretorio, f"{str(mdo_main)}.py")
                        with open(module_path, 'r') as file:
                            code = compile(file.read(), module_path, 'exec')
                        exec(code, globals())

                        # Agora você pode usar as funções do arquivo .py importado
                        # MDOMicro()  # Substitua "nome_da_funcao" pelo nome real da função que você deseja chamar
                if eventos2 == 'Optimize':
                    classe = valores_opt['classe']
                    fitness_fn_name = 'MDO'+classe
                    min_values = converte_to_list(valores_opt['min_values'])
                    max_values = converte_to_list(valores_opt['max_values'])
                    num_variables = int(valores_opt['num_variables'])
                    num_generations = int(valores_opt['num_generations'])
                    elite_count = int(valores_opt['elite_count'])
                    n_threads = int(valores_opt['n_threads'])

                    # # Importar as funções do arquivo .py
                    # spec = importlib.util.spec_from_file_location(mdo_main, os.path.join(caminho_diretorio, f"{mdo_main}.py"))
                    # module = importlib.util.module_from_spec(spec)
                    # spec.loader.exec_module(module)

                    # # Agora você pode usar as funções do arquivo .py importado
                    # module.MDOMicro()  # Substitua "nome_da_funcao" pelo nome real da função que você deseja chamar

                    print(f"Classe Escolhida: {classe}")
                    print(f"Lower Bounds: {min_values}")
                    print(f"Upper Bounds: {max_values}")
                    print(f"Number of Variables: {num_variables}")
                    print(f"Number of Generations: {num_generations}")
                    print(f"Number of Threads: {n_threads}")
                    print("--------------------------------------------------------------------------------------------------------------------------------------------")

            janela_nova.close()  # Fechar a nova janela

janela_login.close()  # Fechar a janela de login