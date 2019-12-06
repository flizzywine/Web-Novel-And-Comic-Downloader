import PySimpleGUI as sg
import downloader

if __name__ == '__main__':
    sg.change_look_and_feel('Dark Blue 3')
    layout = [[sg.Text("url1"), sg.Input('', key='url1')],
              [sg.Text('url2'), sg.Input('', key='url2')],
              [sg.Button('download')]]

    window = sg.Window('Web Novel Downloader', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):  
            break
        if event == 'download':
            urls = []
            if values['url1']:
                urls.append(values['url1'])
            if values['url2']:
                urls.append(values['url2'])
            
            downloader.download(urls)
            window.close()

    window.close()
    
