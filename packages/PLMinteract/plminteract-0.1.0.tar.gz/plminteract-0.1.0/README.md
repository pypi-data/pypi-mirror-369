# PLM-interact: extending protein language models to predict protein-protein interactions
<a href="https://www.biorxiv.org/content/10.1101/2024.11.05.622169v2 "><img src="https://img.shields.io/badge/Paper-bioRxiv-red" style="max-width: 100%;"></a>
<a href="https://huggingface.co/danliu1226"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-blue?label=Model" style="max-width: 100%;"></a>

Computational prediction of protein structure from amino acid sequences alone has been achieved with unprecedented accuracy, yet the prediction of protein-protein interactions (PPIs) remains an outstanding challenge. Here we assess the ability of protein language models (PLMs), routinely applied to protein folding, to be retrained for PPI prediction. Existing PPI prediction models that exploit PLMs use a pre-trained PLM feature set, ignoring that the proteins are physically interacting. Our novel method, PLM-interact, goes beyond a single protein, jointly encoding protein pairs to learn their relationships, analogous to the next-sentence prediction task from natural language processing.

![PLM-interact](https://github.com/liudan111/PLM-interact/blob/main/assets/PLM-interact.png)


## Install conda environment
```
conda create -n PLMinteract python=3.10
conda activate PLMinteract
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
git clone  https://github.com/huggingface/transformers.git
cd transformers
pip install -e .
cd ..
git clone https://github.com/UKPLab/sentence-transformers.git
cd sentence-transformers
pip install -e .
cd ..
pip install datasets huggingface-hub scikit-learn
```

After creating the Conda environment, download the code from our GitHub repository and run the SLURM script on your HPC system. Please check [slurm.sh](PLMinteract/slurm.sh) for the multi-Nodes and multi-GPUs slurm script.

## Install from sources
Alternatively, you can clone the latest version from the repository and install it directly from the source code:
```
git clone https://github.com/liudan111/PLM-interact.git
cd PLM-interact
pip install -e .[dev]
```

## Install with pip
Alternatively, you can also install PLM-interact using pip.
```
python3 -m pip install PLMinteract
```
This Python package requires a Linux operating system and Python 3.10. We have tested it on A100 80GB, A100 40GB, and A40 GPUs. For testing your PPIs, we recommend using an A40/A100 GPU. To train or fine-tune our model, we recommend using A100 80GB GPUs. 


## An example to predict interaction probability between proteins
```
The parameter description for this script.

(1) folder_huggingface_download : The path to a trained PLM-interact model downloaded from Hugging Face (e.g., "PLM-interact-650M-humanV11" or "PLM-interact-650M-humanV12"). Ensure the folder contains the 'pytorch_model.bin' file (2.61 GB).

(2) model_name: The Hugging Face ID for the base ESM-2 model that the PLM-interact model was built upon. Supported options are 'facebook/esm2_t33_650M_UR50D' and 'facebook/esm2_t12_35M_UR50D'.  It is critical that this base model matches the one specified in 'folder_huggingface_download'.
  - Use 'esm2_t33_650M_UR50D' for 650M-parameter models (e.g., PLM-interact-650M-humanV11, PLM-interact-650M-humanV12).
  - Use 'esm2_t12_35M_UR50D' for the 35M-parameter model (e.g., PLM-interact-35M-humanV11).

(3) embedding_size: The corresponding embedding dimension of the specified ESM-2 model. Use 1280 for 'facebook/esm2_t33_650M_UR50D' or 480 for 'facebook/esm2_t12_35M_UR50D'.

(4) max_length: The maximum sequence length for the model. This value should be the combined length of the input paired protein plus three (special tokens).
```

### Download models from Huggingface 

```python
from huggingface_hub import snapshot_download
import os

# The ID of the repository you want to download
repo_id = "danliu1226/PLM-interact-650M-humanV11" # Or any other repo

# The local directory where you want to save the folder
local_dir = "../offline/PLM-interact-650M-humanV11"

# Create the directory if it doesn't exist
os.makedirs(local_dir, exist_ok=True)

print(f"Downloading repository '{repo_id}' to '{local_dir}'...")

# Use snapshot_download with force_download=True
snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    force_download=True  # <-- ADD THIS LINE
)
print("\nDownload complete!")
print(f"All files for {repo_id} are saved in the '{local_dir}' folder.")
``` 

### Run a simple test

```python
import torch
import torch.nn as nn
from transformers import AutoModel,AutoModelForMaskedLM,AutoTokenizer
import os
import torch.nn.functional as F

class PLMinteract(nn.Module):
  def __init__(self,model_name,num_labels,embedding_size): 
    super(PLMinteract,self).__init__() 
    self.esm_mask = AutoModelForMaskedLM.from_pretrained(model_name) 
    self.embedding_size=embedding_size
    self.classifier = nn.Linear(embedding_size,1) # embedding_size 
    self.num_labels=num_labels

  def forward_test(self,features):
    embedding_output = self.esm_mask.base_model(**features, return_dict=True)
    embedding=embedding_output.last_hidden_state[:,0,:] #cls token
    embedding = F.relu(embedding)
    logits = self.classifier(embedding)
    logits=logits.view(-1)
    probability = torch.sigmoid(logits)
    return  probability

folder_huggingface_download='download_huggingface_folder/'
model_name= 'facebook/esm2_t33_650M_UR50D'
embedding_size =1280

protein1 ="EGCVSNLMVCNLAYSGKLEELKESILADKSLATRTDQDSRTALHWACSAGHTEIVEFLLQLGVPVNDKDDAGWSPLHIAASAGRDEIVKALLGKGAQVNAVNQNGCTPLHYAASKNRHEIAVMLLEGGANPDAKDHYEATAMHRAAAKGNLKMIHILLYYKASTNIQDTEGNTPLHLACDEERVEEAKLLVSQGASIYIENKEEKTPLQVAKGGLGLILKRMVEG"

protein2= "MGQSQSGGHGPGGGKKDDKDKKKKYEPPVPTRVGKKKKKTKGPDAASKLPLVTPHTQCRLKLLKLERIKDYLLMEEEFIRNQEQMKPLEEKQEEERSKVDDLRGTPMSVGTLEEIIDDNHAIVSTSVGSEHYVSILSFVDKDLLEPGCSVLLNHKVHAVIGVLMDDTDPLVTVMKVEKAPQETYADIGGLDNQIQEIKESVELPLTHPEYYEEMGIKPPKGVILYGPPGTGKTLLAKAVANQTSATFLRVVGSELIQKYLGDGPKLVRELFRVAEEHAPSIVFIDEIDAIGTKRYDSNSGGEREIQRTMLELLNQLDGFDSRGDVKVIMATNRIETLDPALIRPGRIDRKIEFPLPDEKTKKRIFQIHTSRMTLADDVTLDDLIMAKDDLSGADIKAICTEAGLMALRERRMKVTNEDFKKSKENVLYKKQEGTPEGLYL"

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
tokenizer = AutoTokenizer.from_pretrained(model_name) 
PLMinter= PLMinteract(model_name, 1, embedding_size)
load_model = torch.load(f"{folder_huggingface_download}pytorch_model.bin")
PLMinter.load_state_dict(load_model,strict=False)

texts=[protein1, protein2]
tokenized = tokenizer(*texts, padding=True, truncation='longest_first', return_tensors="pt", max_length=1603)       
tokenized = tokenized.to(DEVICE)

PLMinter.eval()
PLMinter.to(DEVICE)
with torch.no_grad():
    probability = PLMinter.forward_test(tokenized)
    print(probability.item())
```

## Model checkpoints are available on 🤗 Hugging Face
#### 1. Trianing on human PPIs from https://d-script.readthedocs.io/en/stable/data.html
Dataset:
[danliu1226/cross_species_benchmarking](https://huggingface.co/datasets/danliu1226/cross_species_benchmarking/tree/main)

Trained models:
[danliu1226/PLM-interact-650M-humanV11](https://huggingface.co/danliu1226/PLM-interact-650M-humanV11/tree/main)

[danliu1226/PLM-interact-35M-humanV11](https://huggingface.co/danliu1226/PLM-interact-35M-humanV11/tree/main)

#### 2. Trianing on virus-human PPIs from http://kurata35.bio.kyutech.ac.jp/LSTM-PHV/download_page
Dataset:
[danliu1226/virus_human_benchmarking](https://huggingface.co/datasets/danliu1226/virus_human_benchmarking)

Trained model:
[danliu1226/PLM-interact-650M-VH](https://huggingface.co/danliu1226/PLM-interact-650M-VH/tree/main)

#### 3. Training on Human PPIs obtained from a leakage-free dataset (https://doi.org/10.6084/m9.figshare.21591618.v3)
Dataset:
[danliu1226/Bernett_benchmarking](https://huggingface.co/datasets/danliu1226/Bernett_benchmarking)

Trained model:
[danliu1226/PLM-interact-650M-Leakage-Free-Dataset](https://huggingface.co/danliu1226/PLM-interact-650M-Leakage-Free-Dataset/tree/main)

#### 4. Fine-tuning PLM-inetract with a mutation dataset (https://ftp.ebi.ac.uk/pub/databases/intact/current/various/mutations.tsv).
Dataset:
[danliu1226/Mutation_effect_dataset](https://huggingface.co/datasets/danliu1226/Mutation_effect_dataset)

Trained model:
[danliu1226/PLM-interact-650M-Mutation](https://huggingface.co/danliu1226/PLM-interact-650M-Mutation/tree/main)

#### 5. Trianing on Human PPIs from STRING V12 (https://stringdb-downloads.org/download/protein.physical.links.v12.0.txt.gz)
[danliu1226/PLM-interact-650M-humanV12](https://huggingface.co/danliu1226/PLM-interact-650M-humanV12/tree/main)


# Inference, train and evaluation 
We provide a setup script to run PLM-interact for training, validation and test. It can be found at the following path: PLMinteract/script/slurm.sh. We list the commands for inference, triaing and evalaution. Please read the [PLMinteract/README.md](PLMinteract/README.md) for details on parameter descriptions.

```
git clone https://github.com/liudan111/PLM-interact.git

cd PLM-interact/PLMinteract
```

## PPI inference
### (1) PPI inference with multi-GPUs
To test a list of protein pairs, you must provide a CSV file using the --test_filepath argument. The file requires the following two columns:
```
query: The sequence of protein 1.
text: The sequence of protein 2.
```

```
srun -u python inference_PPI.py --seed 2 --batch_size_val 16 --test_filepath $test_filepath --model_name 'esm2_t33_650M_UR50D' --embedding_size 1280 --output_filepath $output_filepath --resume_from_checkpoint $resume_from_checkpoint --max_length 1603 --offline_model_path $offline_model_path
```
* Example : 
srun -u python inference_PPI.py --seed 2 --batch_size_val 16 --test_filepath '../ppi_seq.csv' --model_name 'esm2_t33_650M_UR50D' --embedding_size 1280 --output_filepath '../output/' --resume_from_checkpoint '../PLM-interact-650M-humanV12/pytorch_model.bin' --max_length 1603 --offline_model_path '../offline/test/esm2_t33_650M_UR50D'

### (2) PPI inference with a single GPU
```
srun -u python inference_PPI_singleGPU.py --seed 2 --batch_size_val 16 --test_filepath $test_filepath --model_name 'esm2_t33_650M_UR50D' --embedding_size 1280 --output_filepath $output_filepath --resume_from_checkpoint $resume_from_checkpoint --max_length 1603 --offline_model_path $offline_model_path
```

## PLM-interact training and evaluation
The efficient batch size is 128, which is equal to  batch_size_train * gradient_accumulation_steps * the number of gpus.

Required Input (--train_filepath,--dev_filepath, --test_filepath): A CSV file with the following three columns:
```
query: The sequence of the first protein.
text: The sequence of the second protein.
label: The ground truth label, where 1 indicates a positive interaction and 0 indicates a negative one.
```

### (1) PLM-interact training with mask loss and binary classification loss optimize
```
srun -u python train_mlm.py --epochs 20 --seed 2 --data 'human_V11' --task_name '1vs10' --batch_size_train 1 --train_filepath $train_filepath --model_name 'esm2_t33_650M_UR50D' --embedding_size 1280 --output_filepath $outputfilepath --warmup_steps 2000 --gradient_accumulation_steps 8 --max_length 2146 --weight_loss_mlm 1 --weight_loss_class 10 --offline_model_path $offline_model_path 
```
### (2) PLM-interact training with binary classification loss optimize

```
srun -u python train_binary.py --epochs 20 --seed 2 --data 'human_V11' --task_name 'binary' --batch_size_train 1 --batch_size_val 32 --train_filepath $train_filepath  --dev_filepath $dev_filepath  --test_filepath $test_filepath --output_filepath $outputfilepath --warmup_steps 2000 --gradient_accumulation_steps 32  --model_name 'esm2_t33_650M_UR50D' --embedding_size 1280 --max_length 1600 --evaluation_steps 5000 --sub_samples 5000 --offline_model_path $offline_model_path 
```

### (3) PLM-interact validation and test
```
srun -u python predict_ddp.py --seed 2 --batch_size_val 32 --dev_filepath $dev_filepath --test_filepath $test_filepath --output_filepath $output_filepath --resume_from_checkpoint $resume_from_checkpoint --model_name esm2_t33_650M_UR50D --embedding_size 1280 --max_length 1603 --offline_model_path $offline_model_path 
```

## Acknowledgements
Thanks to the following open-source projects:
- [sentence_transformers](https://github.com/UKPLab/sentence-transformers)
- [esm](https://github.com/facebookresearch/esm)
- [transformers](https://github.com/huggingface/transformers)

<img src="https://github.com/liudan111/PLM-interact/blob/main/assets/Logo.png" width="550" />
