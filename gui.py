import PySimpleGUI as sg
import downloader

if __name__ == '__main__':
    sg.change_look_and_feel('Dark Blue 3')
    layout = [[sg.Text("start_url"), sg.Input('', key='start')],
              [sg.Text('end_url'), sg.Input('', key='end')],
              [sg.Text('output_filename(optional)'), sg.Input(key='out')],
              [sg.Text('title_selector(optional)'),sg.Input(key='title'), sg.Text('body_selector(optinal)'), sg.Input(key='body')],
              [sg.Button('download')]]

    window = sg.Window('Web Novel Downloader', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):  
            break
        if event == 'download':
           
            out = values['out'] 
            title = values['title'] 
            body = values['body'] 
            start = values['start']
            end = values['end']
            downloader.parse(start_url=start, end_url=end, title=title, body=body, out=out)
            downloader.download()
            sg.Popup('Download Completed!')

    window.close()
    
