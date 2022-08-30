import os
import shutil as sht
import numpy as np
import glob
import replaceline as rl


def run_config_scan(fill):
    
    tag_prefix = 'lhc'
        
    tobecopied = 'job.job beam.beam machine_parameters.input secondary_emission_parameters.input simulation_parameters.input cos_sq_inv_CDF.mat'
    
    current_dir = os.getcwd()
    study_folder =  current_dir.split('/config')[0]
    
    scan_folder = study_folder+'/simulations'
    
    from scenarios_NxNy_Dt import machines
    
    #VERONIKA: NEED TO RUN CERTAIN FILLS AND TIMES FOR HIGHER SEY
    del_max_vect = np.arange(1.,2.21,.05)
    #del_max_vect = np.arange(2.25, 3.01, .05)    

    fact_beam_vect = np.arange(0.1e11, 2.51e11, 0.1e11)
    
    bl_4_sigma_s_vect = [1.2e-9]
    beams_list = ['450GeV']
    
    
    if not os.path.exists(scan_folder):
        os.mkdir(scan_folder)
    if not os.path.exists(scan_folder + '/progress'):
        os.mkdir(scan_folder+'/progress')
    
    launch_file_lines = []
    launch_file_lines +=['#!/bin/bash\n']
    device_list = ['ArcDipReal', 'ArcQuadReal']
    
    #snapshot_name = "Beam1_450GeV_Fill7774_T1.70h.mat"
    
    prog_num=0
    
    #VERONIKA: NEEDS TO TAKE THE BEAM SNAPSHOTS FROM THE FOLDER THAT ONLY HAS THE FIRST TIME FOR EACH BEAM 
    folder_snapshots="/home/HPC/vesedlak/sim_workspace/matthew/beam_snapshots_one_time/"
    path_to_beam = glob.glob(folder_snapshots + f"Beam*Fill{fill}*.mat")
    snapshot_list = [path.split('/')[-1] for path in path_to_beam]
    
    
    for snapshot_name in snapshot_list:
        for machine_name in machines.keys():
            machine = machines[machine_name]
            beams = machine['beams']
            devices = machine['devices']
            for device_name in device_list:
                device = devices[device_name]
                for beam_name in beams_list:
                    beam = beams[beam_name]
                    ener_curr = beam['energy']
                    #sigmaz = beam['sigmaz']
                    config = device['config'][beam_name]
                    for del_max in del_max_vect:
                        prog_num +=1
                        snapshot_tag = snapshot_name[:-4] #	 is this the time ?
                        current_sim_ident= '%s_%s_%s_sey%1.2f_%s'%(machine_name, device_name, beam_name, del_max, snapshot_tag)
                        #current_sim_ident= '%s_%s_%s_sey%1.2f_%.1fe11ppb_bl_%.2fns'%(machine_name, device_name, beam_name, del_max,fact_beam/1e11,bl_4_sigma_s/1e-9)
                        sim_tag = tag_prefix+'%03d'%prog_num
                        print(sim_tag, current_sim_ident)
                        current_sim_folder = scan_folder+'/'+current_sim_ident
                        os.mkdir(current_sim_folder)
                        
                        rl.replaceline_and_save(fname = 'secondary_emission_parameters.input',
                         findln = 'del_max =', newline = 'del_max = %f\n'%del_max)
                         
                        #~ rl.replaceline_and_save(fname = 'beam.beam',
                         #~ findln = 'sigmaz =', newline = 'sigmaz = %e\n'%sigmaz)
                         
                        # rl.replaceline_and_save(fname = 'beam.beam',
                        #  findln = 'sigmaz =', newline = 'sigmaz = %e/4.*299792458.\n'%bl_4_sigma_s)           
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'sigmaz =', newline = 'sigmaz = 0\n')           
        
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'fact_beam =', newline = 'fact_beam = %e\n'%(1.))                          
                        
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'filling_pattern_file =', newline = "filling_pattern_file = \'%s\'\n"%(snapshot_name))                          
        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'betafx =', newline = 'betafx = %.2f\n'%(device['betafx']))
        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'betafy =', newline = 'betafy = %.2f\n'%(device['betafy']))
                        
                        B_multip = [device['B0y_per_eV']*ener_curr]
                        
                        if device['fact_Bmap_per_eV']>0.:
                            B_multip.append(device['fact_Bmap_per_eV']*ener_curr)
                        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'B_multip =', newline = 'B_multip = %s\n'%repr(B_multip))
        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'chamb_type =', newline = 'chamb_type = %s\n'%repr(device['chamb_type']))                         
                        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'x_aper =', newline = 'x_aper = %e\n'%device['x_aper'])                       
                        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'y_aper =', newline = 'y_aper = %e\n'%device['y_aper'])                       
                        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'filename_chm =', newline = 'filename_chm = %s\n'%repr(device['filename_chm']))                           
                                                        #rl.replaceline_and_save(fname = 'machine_parameters.input',
                                                        # findln = 'k_pe_st =', newline = 'k_pe_st = %e\n'%k_pe_st_curr)
        
                                                        #rl.replaceline_and_save(fname = 'machine_parameters.input',
                                                        # findln = 'refl_frac =', newline = 'refl_frac = %e\n'%refl_frac_curr)                              
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'beam_field_file =', newline = 'beam_field_file = %s\n'%repr(config['beam_field_file']))
                        
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'Nx =', newline = 'Nx = %s\n'%repr(config['Nx']))                 
                        
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'Ny =', newline = 'Ny = %s\n'%repr(config['Ny']))                     
                        
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'nimag =', newline = 'nimag = %s\n'%repr(config['nimag']))                        
                        
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'Dh_beam_field =', newline = 'Dh_beam_field = %s\n'% repr(config['Dh_beam_field']))
                                                
                        rl.replaceline_and_save(fname = 'beam.beam',
                         findln = 'energy_eV = ', newline = 'energy_eV = %e\n'%ener_curr)                       
                        
                        rl.replaceline_and_save(fname = 'machine_parameters.input',
                         findln = 'N_sub_steps =', newline = 'N_sub_steps = %d\n'%config['N_sub_steps'])
                        
                        rl.replaceline_and_save(fname = 'simulation_parameters.input',
                         findln = 'Dt =', newline = 'Dt = %e\n'%config['Dt'])
        
                     
                         
                        rl.replaceline_and_save(fname = 'simulation_parameters.input',
                         findln = 'logfile_path =', newline = 'logfile_path = '+'\''+ current_sim_folder+'/logfile.txt'+'\''+'\n')
                         
                        rl.replaceline_and_save(fname = 'simulation_parameters.input',
                         findln = 'progress_path =', newline = 'progress_path = '+'\'' + scan_folder+'/progress/' +sim_tag+'\''+ '\n')
                        
                        rl.replaceline_and_save(fname = 'simulation_parameters.input',
                         findln = 'stopfile =', newline = 'stopfile = \''+scan_folder+'/progress/stop\'\n')
        
        
                        if type(device['B_map_file']) is str:
                            if '.mat' in device['B_map_file']:
                                sht.copy(device['B_map_file'],current_sim_folder)
                            
                        if type(device['filename_chm']) is str:
                            if '.mat' in device['filename_chm']:
                                sht.copy(device['filename_chm'],current_sim_folder)
        
                        rl.replaceline_and_save(fname = 'job.job',
                                             findln = 'CURRDIR=/',
                                             newline = 'CURRDIR='+current_sim_folder)
                        
                        #VERONIKA: change the name of each job to match the folder it's executed in
                        rl.replaceline_and_save(fname = 'job.job', 
                                              findln = '#SBATCH --job-name=',
                                              newline = '#SBATCH --job-name='+current_sim_ident)
                        #VERONIKA: change the name of the beam profile to load         
                        rl.replaceline_and_save(fname = 'job.job',
                                               findln = 'cp ${SNAPSHOTDIR}/',
                                               newline = 'cp ${SNAPSHOTDIR}/'+snapshot_name+' .')
    
                        os.system('cp -r %s %s'%(tobecopied, current_sim_folder))
                        launch_file_lines += ['bsub -L /bin/bash -J '+ sim_tag + 
                                ' -o '+ current_sim_folder+'/STDOUT',
                                ' -e '+ current_sim_folder+'/STDERR',
                                ' -q 2nd < '+current_sim_folder+'/job.job\n', 'bjobs\n']
                                                
    #"a":  The texts will be inserted at the current file stream position, default at the end of the file.
    #file_with_folders = open('list_of_directories.txt', 'w')
    #file_with_folders.writelines(list_of_dirs)
    #file_with_folders.close()
    
    with open(study_folder+'/run', 'w') as fid:
        fid.writelines(launch_file_lines)
    os.chmod(study_folder+'/run',755)
    
    
    #import htcondor_config as htcc
    #htcc.htcondor_config(scan_folder, time_requirement_days=2.)
    
    
    #path_to_mat = glob.glob('/home/HPC/vesedlak/sim_workspace/matthew/beam_snapshots/Beam*.mat')
    #path_to_mat[0].split('/')[-1]
    return    
###################################################################################################################################

#Specify which fill this should be done for here
#fills = [7881,7902,7904,7905,7906,7907,7909,7932,7933,7934,7935,7936,7937,7938,7939,7940,7943,7944,7945,7949,7950,7951,7952,7953,7954,7955,7956,7983,7984,7985,7986,7987,7988]#,8000,8002,8003,8004,8005]
#fills = [8000,8002,8003,8004,8005]

fills = [7793,7795,7797,7799,7800]

for fill in fills:
    run_config_scan(fill)

