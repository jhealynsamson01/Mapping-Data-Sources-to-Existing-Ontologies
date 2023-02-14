import PySimpleGUI as sg


def error_message(message):
    layout = [[sg.Text('Error Message:')],
              [sg.Text(message)],
              [sg.Button('Exit')]]

    # Task: Create the Window
    window = sg.Window('Ontology Mapping', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()
