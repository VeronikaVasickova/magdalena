import json

def get_1D_input_list(fill, times, device_type, specific_device_name, err_in_percent):
    input_list=[]
    for time in times:
        with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{time:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
        model_dict = hl_dict['model']
        imp = model_dict['impedance_hl_hc']
        sr = model_dict['sr_hl_hc']
        type_dict = hl_dict[device_type]
        hl = type_dict[specific_device_name]
        err = hl *err_in_percent / 100
        input_list.append([hl,err,time,imp,sr])
    return input_list

def get_2D_input_list(fill, times, device_type, specific_device_name, err_in_percent):
    input_list=[]
    for time in times:
        with open(f"/eos/project/e/ecloud-simulations/vesedlak/output/meas_hl_Fill{fill}_T{time:.2f}.json", "r") as json_file:
            hl_dict = json.load(json_file)
        model_dict = hl_dict['model']
        imp = model_dict['impedance_hl_hc']
        sr = model_dict['sr_hl_hc']
        type_dict = hl_dict[device_type]
        hl = type_dict[specific_device_name]
        err = hl *err_in_percent / 100
        input_list.append([hl,err,imp,sr,time])
    return input_list


