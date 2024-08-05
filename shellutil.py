from asrann.models import Record, Dataset, ActiveDataset
import tarfile
import csv
from django.utils import timezone
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
_tar_map = {}

def load_all_datasets():
    actives = ActiveDataset.objects.all()
    for active_ds in actives:
        dataset_name = active_ds.dataset.name
        print('loading dataset', dataset_name)
        _load_metadata(dataset_name)

def _load_tar_mem(dataset_name):
    dset = Dataset.objects.get(name=dataset_name)
    path = os.getenv('MEDIA_FOLDER') + dset.data_folder + "/"
    for i in tqdm(range(1, len([x for x in os.listdir(path) if x.endswith('.tar')])+1)): 
        tar_file_name = "clips_" + "{:03d}".format(i) + ".tar"
        tar_file_path = path + tar_file_name
        tar = tarfile.open(tar_file_path)
        audios = tar.getmembers()
        #print('tar_file: ', i)
        for audio in audios:
            audio_file_name = audio.name
            _tar_map[audio_file_name] = i
    
def _load_metadata(dataset_name):
    _load_tar_mem(dataset_name)
    print('tar content files:', len(_tar_map.keys()))
    asrd = Dataset.objects.get(name=dataset_name)
    file = os.getenv('MEDIA_FOLDER') + asrd.data_folder + "/" + "metadata.csv"
    with open(file, encoding="utf-8") as csvfile:
        metadata = csv.reader(csvfile, delimiter='\t')
        now = timezone.now()
        delta = 0
        for i, row in enumerate(metadata):
            if i != 0:
                rec = Record(
                    audio_file=row[1],
                    transcription=row[2],
                    dataset=asrd,
                    add_date=now + timezone.timedelta(seconds=delta),
                    tar_file=_tar_map[row[1]])
                rec.save()
                #print(row)
            #if i == 30000:
                #break
            if i % 20000 == 0:
                print('done: ', i/20000, '>>20k', sep='')
            delta += 1