
# for job submission i got heavily inspired by the code von BTVNanoCommisions nice runner script:
# https://github.com/cms-btv-pog/BTVNanoCommissioning/blob/master/runner.py


from coffea.util import save
from coffea import processor

import sys,os



if(__name__ == "__main__"):
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--processor",default="VBSAnalysisNote")
    parser.add_argument("--condor", action="store_true")
    parser.add_argument("--workers",default=4,type=int)
    parser.add_argument("--scaleout","-s",default=6,type=int)
    parser.add_argument("--output","-o",default="VBSAnalysisNote.coffea")
    parser.add_argument("--samples",type=str,required=True)
    parser.add_argument("--chunk",type=int,default=50000000)

    
    args = parser.parse_args()

    # __import__(args.processor)
    # processor_instance = sys.modules[args.processor].NanoProcessor
    import VBSAnalysisNote
    processor_instance = VBSAnalysisNote.NanoProcessor()

    print(f'using NanoProcessor from {args.processor} {processor_instance}')
    import json
    samples = json.load(open(args.samples))

    tidy_dataset = {
        '_TuneCP5_13TeV-madgraph-madspin-pythia8':'',
        '-NANOAODSIMv9':'',
    }
    def clean_dataset_name(s):
        for k,v in tidy_dataset.items():
            s = s.replace(k,v)
        return s
    
    
    samples = {clean_dataset_name(k):v for k,v in samples.items()}

    _x509_path='/afs/desy.de/user/a/albrechs/.globus/voms.dat'
    
    if(args.condor):
        from dask_jobqueue import HTCondorCluster
        from distributed import Client
        from dask.distributed import performance_report
        
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
    
        cluster = HTCondorCluster(
            cores     =  args.workers,
            # death_timeout=240,
            memory    =  '4GB',
            disk      =  '4GB',
            env_extra =  env_extra,
            job_extra={
                'log': 'dask_job_output.log',
                'output': 'dask_job_output.out',
                'error': 'dask_job_output.err',
                # 'should_transfer_files': 'Yes',
                # 'when_to_transfer_output': 'ON_EXIT',
                'getenv':'True'
                    },
        )
        
        
        print('HTCondorCluster created')
        print(cluster.job_script())
        cluster.adapt(minimum=args.scaleout*args.workers)
        print('submitted jobs to spawn dask-workers')
        client = Client(cluster)
        print('waiting for at least 1 dask-worker to have started...')
        client.wait_for_workers(1)

        with performance_report(filename="/afs/desy.de/user/a/albrechs/www/dask-report.html"):
            output = processor.run_uproot_job(samples,
                                              treename="Events",
                                              processor_instance = processor_instance,
                                              executor=processor.dask_executor,
                                              executor_args={
                                                  'client': client,
                                                  # 'skipbadfiles': args.skipbadfiles,
                                                  'schema': processor.NanoAODSchema,
                                                  'retries': 3,
                                              },
                                              chunksize=args.chunk,
                                              # maxchunks=args.max
                                              )
        
    else:
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
