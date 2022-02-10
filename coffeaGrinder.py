#!/usr/bin/env python3
# for job submission i got heavily inspired by the code von BTVNanoCommisions nice runner script:
# https://github.com/cms-btv-pog/BTVNanoCommissioning/blob/master/runner.py


from coffea.util import load,save
from coffea import processor

import sys,os



if(__name__ == "__main__"):
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--processor",default="VBSAnalysisNote")
    parser.add_argument("--info",action="store_true")
    parser.add_argument("--condor", action="store_true")
    parser.add_argument("--parsl", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--workers",default=4,type=int)
    parser.add_argument("--scaleout","-s",default=6,type=int)
    parser.add_argument("--output","-o",default="VBSAnalysisNote.coffea")
    parser.add_argument("--samples",type=str, default="data/SM_UL17.json")
    parser.add_argument("--workdir",type=str, default='coffeaGrinderWorkdir')
    parser.add_argument("--chunk",type=int,default=50000)
    parser.add_argument("--brutondor",action='store_true',help='brute force splitting and submitting to condor in case dask parsl or any other very nice framework does not work on your site (i.e. i can not get it to work consistently @ DESY).')
    parser.add_argument("--maxfiles",type=int, default=100,help='maximum files to be processed (in case of brutondor max files per job!!)')
    parser.add_argument("--jobindex",type=int, default=0)
    parser.add_argument("--addHists", action="store_true")
    
    
    args = parser.parse_args()

    if(args.addHists):
        print("attempting to add Hists in workdir", args.workdir)
        print("This will only work on workdirs created in brutondor mode!!")
        import glob
        fnames = glob.glob(f"{args.workdir}/output_*.coffea")

        print(f"Number of files to be added: {len(fnames)}")
        hists = None
        
        for fname in fnames:
            file_ = None
            try:
                file_ = load(fname)
                if hists is None:
                    hists = load(fname)
                else:
                    hists += load(fname)
                del file_
            except:
                print(f'Failed to open {fname}!')
        workdir_abs = os.path.abspath(args.workdir)
        hists_outname = f"{os.path.dirname(workdir_abs)}/{os.path.basename(workdir_abs)}.coffea"
        print('saving added hists to ',hists_outname)
        save(hists,hists_outname)
            
        exit(0)

    
    __import__(args.processor)
    processor_instance = sys.modules[args.processor].NanoProcessor()

    print(f'using NanoProcessor from {args.processor} {processor_instance}')
    import json
    # if(os.path.isfile(args.samples)):
    samples = json.load(open(args.samples))
    # else:
    #     samples = eval(args.samples)

    
    tidy_dataset = {
        '_TuneCP5_13TeV-madgraph-madspin-pythia8':'',
        '_TuneCP5_13TeV-madgraph-pythia8':'',
        '-NANOAODSIMv9':'',
    }
    def clean_dataset_name(s):
        for k,v in tidy_dataset.items():
            s = s.replace(k,v)
        return s
    
    
    samples = {clean_dataset_name(k):v for k,v in samples.items()}

    if(args.info):
        print("args", args)
        # import uproot
        # print('opening one file for each dataset to estimate total number of events...')
        # tree_names = ['Events','AnalysisTree']
        # n_one_file = 0
        # for tree_name in tree_names:
        #     if(True):
        #         n_one_file = len(uproot.open(samples[list(samples.keys())[0]][0])[tree_name])
        #         break
        #     else:
        #         print(f"tried to access tree \"{tree_name}\"...that didn't work. Trying next provided option ({', '.join(tree_names)}).")
        # n_files = {s:len(samples[s]) for s in samples.keys()}
        # print(n_one_file)
        # print(n_files)
        # max_length = max([len(s) for s in samples.keys()]) +3
        # for s in samples.keys():
        #     print(f"{s:<{max_length}}-> NFiles={n_files[s]}")
        # n_total=sum(n_files.values())
        # print("---> total number of files to be processed:",n_total)
        
        exit(0)
    _x509_path='/afs/desy.de/user/a/albrechs/.globus/voms.dat'
    
    if(args.condor):
        
        env_extra = []
        condor_extra = []
        
    
        env_extra = [
            'echo "hellow world"',
            'export XRD_RUNFORKHANDLER=1',
            'export XRD_STREAMTIMEOUT=10',
            f'export X509_USER_PROXY={_x509_path}',
            f'export X509_CERT_DIR={os.environ["X509_CERT_DIR"]}',
            f"export PYTHONPATH=$PYTHONPATH:{os.getcwd()}",
            #f'source {os.environ["HOME"]}/.bashrc',
        ]

        # env_extra = [
        #     # 'export XRD_RUNFORKHANDLER=1',
        #     # f'export X509_USER_PROXY={_x509_path}',
        #     # f'export X509_CERT_DIR={os.environ["X509_CERT_DIR"]}',
        #     # f"export PYTHONPATH=$PYTHONPATH:{os.getcwd()}",
        # ]

        condor_extra = [
            f'source {os.environ["HOME"]}/.bashrc',
        ]
    
        if(args.parsl):
            import parsl
            from parsl.providers import CondorProvider
            from parsl.config import Config
            from parsl.executors import HighThroughputExecutor
            from parsl.launchers import SrunLauncher
            from parsl.addresses import address_by_hostname, address_by_query

            htex_config = Config(
                executors=[
                    HighThroughputExecutor(
                        label='coffea_parsl_condor',
                        address=address_by_query(),
                        max_workers=1,
                        provider=CondorProvider(
                            nodes_per_block=1,
                            init_blocks=1,
                            max_blocks=1,
                            worker_init="\n".join(env_extra + condor_extra),
                            walltime="00:20:00",
                        ),
                    )
                ]
            )

            dfk = parsl.load(htex_config)

            output = processor.run_uproot_job(samples,
                                              treename='Events',
                                              processor_instance=processor_instance,
                                              executor=processor.parsl_executor,
                                              executor_args={
                                                  'skipbadfiles': True,
                                                  'schema': processor.NanoAODSchema,
                                                  'config': None,
                                              },
                                              # chunksize=args.chunk,
                                              # maxchunks=args.max
                                              )
        else:
            from dask_jobqueue import HTCondorCluster
            from distributed import Client
            from dask.distributed import performance_report
            log_dir = "/afs/desy.de/user/a/albrechs/xxl/af-cms/VBS/dask-worker-logs/"
            if(not os.path.isdir(log_dir)):
                os.makedirs(log_dir)
            else:
                print(f"log dir already exists!!!\n -> {log_dir}")
            cluster = HTCondorCluster(
                cores     =  args.workers,
                death_timeout=60,
                memory    =  str(args.workers*4)+'GB',
                disk      =  '10GB',
                env_extra =  env_extra,
                job_extra={
                    # 'log': 'dask_job_output.log',
                    # 'output': 'dask_job_output.out',
                    # 'error': 'dask_job_output.err',
                    # 'should_transfer_files': 'Yes',
                    # 'when_to_transfer_output': 'ON_EXIT',
                    'getenv':'True'
                },
                log_directory=log_dir,
                local_directory="$_CONDOR_SCRATCH_DIR/"
            )
        
            dask_arguments = {
                'skipbadfiles': True,
                'schema': processor.NanoAODSchema,
                'retries': (args.workers*args.scaleout)//10, #allow ~10% of jobs fail
            }

        
            print('HTCondorCluster created')
            print(f'scale out to {args.scaleout}*{args.workers} threads.')
            if(args.debug):
                print(cluster.job_script())
                print("dask_arguments:",dask_arguments)
                exit(0)
            # cluster.adapt(minimum=args.scaleout*args.workers)
            cluster.scale(jobs=args.scaleout)
            print('submitted jobs to spawn dask-workers')
            client = Client(cluster)
            print('waiting for at least 1 dask-worker to have started...')
            dask_arguments.update({'client': client})
            client.wait_for_workers(1)

            
            with performance_report(filename=f"{os.environ['HOME']}/www/dask-report.html"):
                output = processor.run_uproot_job(samples,
                                                  treename="Events",
                                                  processor_instance = processor_instance,
                                                  executor=processor.dask_executor,
                                                  executor_args=dask_arguments,
                                                  chunksize=args.chunk,
                                                  # maxchunks=args.max
                                                  )
    elif(args.brutondor):
        workdir = args.workdir
        if(not os.path.isdir(workdir)):
            os.makedirs(workdir)
        json.dump(vars(args),open(workdir+'/coffeaGrinderConfig.json','w'))

        script_dir = os.getcwd()        
        files_to_transfer = list(map(lambda d: f"{script_dir}/{d}",['coffeaGrinder.py',args.processor+'.py']))

        json.dump({s:samples[s][:(args.scaleout+1)*args.maxfiles] for s in samples},open(f"{workdir}/samples.json","w"))
        files_to_transfer.append(f"{workdir}/samples.json")
        
        # for i in range(args.scaleout):
        #     print(args.maxfiles*i,"..",args.maxfiles*i + args.maxfiles-1)

        
        wrapper = open(workdir + "/wrapper.sh","w")
        # ./wrapper.sh <index> 
        wrapper.write("#!/bin/bash\n")
        wrapper.write("cd ${_CONDOR_SCRATCH_DIR}\n")
        wrapper.write(f"echo 'starting coffea processor in'"+" ${PWD}\n")
        wrapper.write("echo 'arguments:'\n")
        wrapper.write("echo $*\n")
        # wrapper.write(f"export X509_USER_PROXY={_x509_path}\n")
        # wrapper.write(f"source {os.environ['HOME']}/miniconda3/etc/profile.d/conda.sh\n")
        # wrapper.write("conda activate coffea\n")                
        wrapper.write(f"python3 coffeaGrinder.py --output {workdir}/output_$1.coffea --maxfiles={args.maxfiles} --jobindex=$1 --processor={args.processor} --workdir={workdir} --samples=samples.json \n")
        

        wrapper.close()
        os.system(f"chmod +x {workdir}/wrapper.sh")

        files_to_transfer.append(f"{workdir}/wrapper.sh")
        
        # arguments = "\n".join([f"{sample_workdir} {initial_seed+i}" for i in range(jobs)])
        htc_jdl_name = workdir+'/CoffeaHists.jdl'
        with open(htc_jdl_name, 'w') as condor_submit_jdl:
            condor_submit_jdl.write("""Requirements = ( OpSysAndVer == "CentOS7" )
universe          = vanilla
# #Running in local mode with 8 cpu slots
# universe          =  local
# request_cpus      =  8
notification      = Error
notify_user       = steffen.albrecht@desy.de
output            = """+workdir+"""/CoffeaHists.o$(ClusterId).$(Process)
error             = """+workdir+"""/CoffeaHists.e$(ClusterId).$(Process)
log               = """+workdir+"""/CoffeaHists.$(Cluster).log
#Requesting CPU and DISK Memory - default +RequestRuntime of 3h stays unaltered
#+RequestRuntime   = 18000
#+RequestJobRuntime = 18000
RequestMemory     = 4G
RequestDisk       = 4G
getenv           = True
Transfer_Input_Files = """+','.join(files_to_transfer)+"""
should_transfer_files = Yes
JobBatchName      = CoffeaHists
executable        = wrapper.sh
transfer_executable = True
arguments         = $(ProcId)
queue  """+str(args.scaleout)+"""
""")
            condor_submit_jdl.close()

        from subprocess import call
        os.chdir(workdir)
        if(args.debug):
            call(f"condor_submit {htc_jdl_name} --dry-run dryrun.log ",shell=True)
        else:
            call(f"condor_submit {htc_jdl_name}",shell=True)

        exit(0)
        
    else:
        print('processing files: ',args.maxfiles*args.jobindex,args.maxfiles*(1+args.jobindex) -1)
        samples = {s:samples[s][args.maxfiles*args.jobindex:args.maxfiles*(1+args.jobindex)] for s in samples}
        print("samples,files:", samples)
        output = processor.run_uproot_job(samples,
                                              treename="Events",
                                              processor_instance = processor_instance,
                                              executor=processor.futures_executor,
                                              executor_args={
                                                  'workers': args.workers,
                                                  'schema': processor.NanoAODSchema
                                              },
                                              chunksize=args.chunk,
                                              )
                                              

    save(output,args.output)
