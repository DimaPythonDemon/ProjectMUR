import PySimpleGUI as sg

sg.theme('DarkAmber')
layout = [  [sg.Text('Команды для беспилотника')],
            [sg.Text('Введите команду'), sg.InputText("1")],
            [sg.Button('Ввод'), sg.Button('Отмена')] ]

window = sg.Window('Дистанционное управление', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Отмена': break
    if event == "Ввод":
        with open("settings.txt", "w") as file: file.write(values[0])
window.close()
