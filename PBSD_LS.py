import PySimpleGUI as sg
import numpy as np
import pandas as pd
from pickle import load
from PIL import Image, ImageTk
from PIL import Image, ImageOps
import io

# Import the dataset
df = pd.read_excel('data.xlsx', sheet_name='data')[['icolDia', 'aspect_ratio', 'iaxialloadratio', 'ifc',
                                                     'ivf', 'ify', 'iroh_long', 'irohst', 'DS1', 'DS2', 'DS3', 'DS4']]
data = df.iloc[:, :8]
resp = df.iloc[:, 8:]

filename = 'model.pkl'
model = load(open(filename, 'rb'))
def check_value(value, range):
    try:
        float_value = float(value)
        if range[0] <= float_value <= range[1]:
            return True
    except ValueError:
        pass
    return False
def normalize(input_df, data_df):
    return (input_df - data_df.min()) / (data_df.max() - data_df.min())
def denormalize(prediction, feature_name, resp_df):
    min_val = resp_df[feature_name].min()
    max_val = resp_df[feature_name].max()
    return prediction * (max_val - min_val) + min_val
def get_img_data(f, scale):
    # Open the image file
    img = Image.open(f)
    img.thumbnail((img.size[0]//scale, img.size[1]//scale), Image.ANTIALIAS)
    # Convert the PIL image to bytes
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        data = output.getvalue()
    return data
parameters = ['icolDia', 'aspect_ratio', 'iaxialloadratio', 'ifc',
              'ivf', 'ify', 'iroh_long', 'irohst']
ranges = {param: [round(data[param].min(), 4), round(data[param].max(), 4)] for param in parameters}
prediction_placeholders = {
    'DS1': sg.Text(size=(20, 1), key='-PREDICTION-DS1-'),
    'DS2': sg.Text(size=(20, 1), key='-PREDICTION-DS2-'),
    'DS3': sg.Text(size=(20, 1), key='-PREDICTION-DS3-'),
    'DS4': sg.Text(size=(20, 1), key='-PREDICTION-DS4-')
}
sg.theme('DefaultNoMoreNagging')
layout = [
    [sg.Text('Define the input parameters', text_color='blue', font=('Helvetica', 13))],
    [
        sg.Column(layout=[
            [sg.Frame(layout=[
                [sg.Text('Column diameter, D (mm)', size=(38, 1)), sg.Input(key='-D-', size=(15, 1), enable_events=True)],
                [sg.Text('Aspect ratio, L/D', size=(38, 1)), sg.Input(key='-AR-', size=(15, 1), enable_events=True)],
                [sg.Text('Axial load ratio, P/fcAg (%)', size=(38, 1)), sg.Input(key='-ALR-', size=(15, 1), enable_events=True)],
                [sg.Text('Concrete compressive strength, fc (MPa)', size=(38, 1)), sg.Input(key='-FC-', size=(15, 1), enable_events=True)],
                [sg.Text('Volume fraction of UHPC fibers, Vf (%)', size=(38, 1)), sg.Input(key='-VF-', size=(15, 1), enable_events=True)],
                [sg.Text('Yield strength of reinforcement bars, fy (MPa)', size=(38, 1)), sg.Input(key='-FY-', size=(15, 1), enable_events=True)],
                [sg.Text('Longitudinal rienforcement raito, ρsl (%)', size=(38, 1)), sg.Input(key='-ROHSL-', size=(15, 1), enable_events=True)],
                [sg.Text('Volumetric ratio of spirals, ρst (%)', size=(38, 1)), sg.Input(key='-ROHST-', size=(15, 1), enable_events=True)]],
            title='Input parameters')], 
        ], justification='left'),

        sg.Column(layout=[
            [sg.Frame(layout=[
                [sg.Text(f'{ranges["icolDia"][0]} ≤ D (mm) ≤ {ranges["icolDia"][1]}')],
                [sg.Text(f'{ranges["aspect_ratio"][0]} ≤ L/D ≤ {ranges["aspect_ratio"][1]}')],
                [sg.Text(f'{100*ranges["iaxialloadratio"][0]} ≤ P/fcAg (%) ≤ {100*ranges["iaxialloadratio"][1]}')],
                [sg.Text(f'{ranges["ifc"][0]} ≤ fc (MPa) ≤ {ranges["ifc"][1]}')],
                [sg.Text(f'{ranges["ivf"][0]} ≤ Vf (%) ≤ {ranges["ivf"][1]}')],                
                [sg.Text(f'{ranges["ify"][0]} ≤ fy (MPa) ≤ {ranges["ify"][1]}')],
                [sg.Text(f'{100*ranges["iroh_long"][0]} ≤ ρsl (%) ≤ {100*ranges["iroh_long"][1]}')],
                [sg.Text(f'{round(100*ranges["irohst"][0],2)} ≤ ρst (%) ≤ {100*ranges["irohst"][1]}')]],

            title='Range of applications of the model')],             
        ], justification='center')
    ], 
 
]
sg.theme('DefaultNoMoreNagging')
image_filename = 'fig_DS.png'
img_data = get_img_data(image_filename, scale=2.5)
scaled_fig_DS = sg.Image(data=img_data, key='-IMAGE-')
layout += [
    [sg.Column([[sg.Button('Predict'), sg.Button('Cancel')]], justification='center')],
    [sg.Text('_'*100)],  # Just a line to separate sections
]
layout += [
    [
        sg.Column([
            [sg.Text('Predicted Response Variables', text_color='red', font=('Helvetica', 13))],
            [sg.Text('Drift ratio at DS1 (%) = ', font=('Helvetica', 10)), prediction_placeholders['DS1']],
            [sg.Text('Drift ratio at DS2 (%) = ', font=('Helvetica', 10)), prediction_placeholders['DS2']],
            [sg.Text('Drift ratio at DS3 (%) = ', font=('Helvetica', 10)), prediction_placeholders['DS3']],
            [sg.Text('Drift ratio at DS4 (%) = ', font=('Helvetica', 10)), prediction_placeholders['DS4']],
        ], vertical_alignment='top'),
        sg.Column([
            [scaled_fig_DS]
        ], vertical_alignment='top')
    ]
]
img2 = Image.open('image2.png')
img4 = Image.open('image4.png')
widths = [img2.width, img4.width]
heights = [img2.height,  img4.height]
min_width = min(widths)
min_height = min(heights)
img2 = ImageOps.fit(img2, (min_width, min_height))
img4 = ImageOps.fit(img4, (min_width, min_height))
scale_factor = 0.25
img2 = img2.resize((int(min_width * scale_factor), int(min_height * scale_factor)))
img4 = img4.resize((int(min_width * scale_factor), int(min_height * scale_factor)))
img2.save('image22.png')
img4.save('image44.png')
fig2 = sg.Image(filename='image22.png', key='-fig2-', size=(min_width * scale_factor, min_height * scale_factor))
fig4 = sg.Image(filename='image44.png', key='-fig4-', size=(min_width * scale_factor, min_height * scale_factor))
layout += [
    [sg.Text('')],
    [sg.Column([
    [sg.Text('Authors: Wakjira T. and Alam M.'+ '\n'
             '             The University of British Columbia, Okanagan')],
    [
     sg.Button('www.tadessewakjira.com/Contact', key='WEBSITE', button_color=('white', 'gray')),
     sg.Button('https://alams.ok.ubc.ca', key='WEBSITE', button_color=('white', 'gray')),
    ]
    ],
    element_justification='left'
    ),
        sg.Column(
            [   [fig2,
                fig4,
                ],
            ],
            element_justification='center'
        ),
    ],
    [sg.Text("   If you utilize this software for your work, we kindly request that you cite the corresponding paper as a reference.", 
             size=(90, 1), 
             border_width=1, 
             relief=sg.RELIEF_SUNKEN, 
             background_color='white',
             text_color='black',
             font=('Helvetica', 8, 'bold'))],
]
window = sg.Window('XAI-based drift ratio limit states for UHPC bridge columns', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    elif event == 'Predict':
        # Input data from the user
        input_data1 = np.array([[float(values.get('-D-', 0)),
                                 float(values.get('-AR-', 0)),
                                 float(values.get('-ALR-', 0)) * 0.01,
                                 float(values.get('-FC-', 0)),
                                 float(values.get('-VF-', 0)),
                                 float(values.get('-FY-', 0)),
                                 float(values.get('-ROHSL-', 0)) * 0.01,
                                 float(values.get('-ROHST-', 0)) * 0.01
                                ]])
        input_data = pd.DataFrame(input_data1, columns=data.columns)
        input_data = normalize(input_data, data)
        predictions = model.predict(input_data).flatten()  # Flatten the predictions array
        denormalized_predictions = [denormalize(pred, resp.columns[i], resp) for i, pred in enumerate(predictions)]
        for i, pred in enumerate(denormalized_predictions):
            window[f'-PREDICTION-DS{i+1}-'].update(f"{pred:.4f}") 
window.close()

