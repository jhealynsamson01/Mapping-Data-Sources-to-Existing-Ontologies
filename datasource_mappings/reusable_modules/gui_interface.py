import PySimpleGUI as sg

def main_interface():
    try:
        options = {
            'font': ('Helvetica', 15, 'bold'),
            'enable_events': True,
            'tab_location': 'topleft',
        }

        semantic_list = ['', 'SEMANCO', 'SAREF4ENER for Smart Applications']

        layout_tab0 = [
            [sg.Text('Select the datasource')],
            [sg.Combo(['CSV', 'RDBSM', 'JSON', 'Text', 'Images', '3D-Images'], default_value='CSV', key='datasource')],
            [sg.Text('Enter the Ontology URI'), sg.InputText(key='ontology_url_empty')],
            [sg.Text('Or Select from the option below')],
            [sg.Combo(semantic_list, default_value='', key='ontology')],
            [sg.Button('Next')]]

        layout_tab1 = [
            [sg.Button('Back')],
            [sg.Text('Select the CSV file'), sg.FileBrowse()],
            [sg.Button('Submit CSV file')]]

        layout_tab2 = [
            [sg.Button('Back')],
            [sg.Text('Enter the details below to connect and fetch the relational database')],
            [sg.Text('Host Name'), sg.InputText(key='uri')],
            [sg.Text('Database'), sg.InputText(key='database_name')],
            [sg.Text('Username'), sg.InputText(key='user')],
            [sg.Text('Password'), sg.InputText(key='password')],
            [sg.Button('Submit RDBSM details')]]

        layout_tab3 = [
            [sg.Button('Back')],
            [sg.Text('Select the JSON file'), sg.FileBrowse()],
            [sg.Button('Submit JSON file')]]

        layout_tab4 = [
            [sg.Button('Back')],
            [sg.Text('This functionality is still not ready')]]

        layout_tab5 = [
            [sg.Button('Back')],
            [sg.Text('This functionality is still not ready')]]

        layout_tab6 = [
            [sg.Button('Back')],
            [sg.Text('This functionality is still not ready')]]

        layout_tab = [[
            sg.Tab('', layout_tab0, key='instruction'),
            sg.Tab('', layout_tab1, key='csv'),
            sg.Tab('', layout_tab2, key='sql'),
            sg.Tab('', layout_tab3, key='json'),
            sg.Tab('', layout_tab4, key='text'),
            sg.Tab('', layout_tab5, key='image'),
            sg.Tab('', layout_tab6, key='3dimage')
        ]]

        layout = [[sg.TabGroup(layout_tab, **options, key='tabs')]]

        window = sg.Window('Map Data Source to Ontology', layout, font=('Helvetica', 12), finalize=True)
        window['instruction'].select()

        while True:
            event, main_gui_values = window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Submit CSV file" or event == "Submit JSON file" or event == "Submit RDBSM details":
                break
            elif event == 'Next' and main_gui_values['datasource'] == 'CSV':
                window['csv'].select()
            elif event == 'Next' and main_gui_values['datasource'] == 'RDBSM':
                window['sql'].select()
            elif event == 'Next' and main_gui_values['datasource'] == 'JSON':
                window['json'].select()
            elif event == 'Next' and main_gui_values['datasource'] == 'Text':
                window['text'].select()
            elif event == 'Next' and main_gui_values['datasource'] == 'Images':
                window['image'].select()
            elif event == 'Next' and main_gui_values['datasource'] == '3D-Images':
                window['3dimage'].select()
            elif event == 'Back':
                window['instruction'].select()

        return main_gui_values
        window.close()
    except Exception as main_gui:
        error_message(main_gui)

def right_class_mapping(choices, create_class, result, temp_class):
    tempdictionary = {}
    layout = []

    layout.append([sg.Text('Matched Keywords-Class pair with 80% confidence', font=(12), p=(0, 0 or (5, 5)))])
    for i in temp_class:
        layout.append([sg.Text(i + " : " + temp_class[i])])

    if any(v is not None for v in choices):
        for i in range(len(choices)):
            tempkeyword = choices[i][0]
            if tempkeyword in tempdictionary:
                tempdictionary[tempkeyword].append(choices[i][1])
            else:
                tempdictionary[tempkeyword] = [choices[i][1]]

        layout.append([sg.Text('Confirm if the matched Keyword-Class pair is right', font=(12))])

        for i in tempdictionary:
            layout.append([[sg.Text(i, p=(0, 0 or (5, 0)))],
                           [sg.Combo([tempdictionary[i][0], tempdictionary[i][1], tempdictionary[i][2],
                                      tempdictionary[i][3], tempdictionary[i][4]],
                                     default_value=tempdictionary[i][0],
                                     key=i,
                                     size=(20, 20))]])

        if any(v is not None for v in create_class.keys()):
            layout.append([sg.Text('New classes made for keyword/class pairings:', font=(12), p=(0, 0 or (5, 5)))])
            for newval in create_class:
                layout.append([sg.Text(newval)])

        layout.append([sg.Button('SAVE', font=(12))])

        # Define Window
        win = sg.Window('Mapping data source to ontology', layout)
        e, value = win.read()
        win.close()

    else:
        layout.append([sg.Text('New classes made for keyword/class pairings:', font=(12), p=(0, 0 or (5, 5)))])
        for newval in create_class:
            layout.append([sg.Text(newval)])
        layout.append([sg.Button('SAVE', font=(12))])
        win = sg.Window('Customise your Journey', layout)
        e, value = win.read()
        win.close()

    for i in value:
        result.update({i: value[i]})

    return tempdictionary

def upload_neo4j_gui():
    layout = [[sg.Text('Upload to neo4j. Enter the following details:')],
              [sg.Text('URI:'), sg.InputText(key="uri")],
              [sg.Text('User:'), sg.InputText(key="user")],
              [sg.Text('Password:'), sg.InputText(key="password")],
              [sg.Text('Database name:'), sg.InputText(key="database_name")],
              [sg.Button('Save')]]

    # Task: Create the Window
    window = sg.Window('Ontology Mapping', layout)
    while True:
        event, values_neo4j = window.read()
        if event == sg.WIN_CLOSED or event == 'Save':
            break
    return values_neo4j
    window.close()
