"""
Training PPI models using mask and binary classification losses.
"""
import os
from datasets import Dataset
from torch.utils.data import WeightedRandomSampler,DataLoader,SubsetRandomSampler
from torch.utils.data import RandomSampler
from sentence_transformers import LoggingHandler, util
from sentence_transformers import InputExample
import logging
from datetime import datetime
import numpy as np
import argparse

from torch.distributed import init_process_group, destroy_process_group
from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
import torch
import random
import math
import sys
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from transformers import AutoModel,AutoModelForMaskedLM
from transformers import DataCollatorForLanguageModeling
from sentence_transformers import SentenceTransformer, util

from typing import Dict, Type, Callable, List, NamedTuple
import torch
from torch import nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader
import csv
import torch.nn.functional as F
from .utils.ddp import ddp_setup
from .utils.data_load import load_train_objs, load_val_objs

logger = logging.getLogger(__name__)

class PLMinteract(nn.Module):
  def __init__(self,checkpoint,num_labels,config,device,embedding_size,weight_loss_class,weight_loss_mlm): 
    super(PLMinteract,self).__init__() 
    self.esm_mask = AutoModelForMaskedLM.from_pretrained(checkpoint,config=config) 
    self.embedding_size=embedding_size
    self.classifier = nn.Linear(embedding_size,1) # embedding_size 
    self.num_labels=num_labels
    self.device=device
    self.weight_loss_class=weight_loss_class
    self.weight_loss_mlm=weight_loss_mlm

  def forward(self, label,lm_dataloader):
    for idx, lm_features in enumerate(lm_dataloader):
        lm_features = lm_features.to(self.device) 
        features ={'input_ids':lm_features['input_ids'],'attention_mask':lm_features['attention_mask']}
    outputs = self.esm_mask(**lm_features)
    MLM_loss = outputs.loss

    embedding_output = self.esm_mask.base_model(**features, return_dict=True)
    embedding=embedding_output.last_hidden_state[:,0,:] #cls token
    embedding = F.relu(embedding)
    logits = self.classifier(embedding)
    logits=logits.view(-1)

    pos_weight = torch.tensor([10]).to(self.device)
    loss_fct = nn.BCEWithLogitsLoss(pos_weight= pos_weight) if self.num_labels == 1 else nn.CrossEntropyLoss()
    loss = loss_fct(logits, label.view(-1))
    loss_value= self.weight_loss_class * loss+ self.weight_loss_mlm * MLM_loss
  
    return loss_value, loss, MLM_loss,logits

''' The trianing code is modified based on the CrossEncoder function from the Sentence-Transformers library: 
https://github.com/UKPLab/sentence-transformers/blob/master/sentence_transformers/cross_encoder/CrossEncoder.py 
Original license: Apache License 2.0
'''

'''
The gradient_accumulation_steps in this code is inspired by https://github.com/huggingface/transformers/blob/main/examples/pytorch/language-modeling/run_mlm_no_trainer.py 
Original license: Apache License 2.0
# Copyright 2021 The HuggingFace Inc. team. All rights reserved.
#xx
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''
class CrossEncoder():
    def __init__(self, model_name:str, num_labels:int = None, max_length:int = None, tokenizer_args:Dict = {}, automodel_args:Dict = {}, default_activation_function = None, embedding_size:int=None,weight_loss_class:int=0,weight_loss_mlm:int=0,checkpoint :str=None):
        self.config = AutoConfig.from_pretrained(model_name)
        if 'SLURM_PROCID' in os.environ:
            os.environ['RANK'] = os.environ['SLURM_PROCID']
            self.rank  = int(os.environ['RANK'])
            gpus_per_node = int(os.environ['SLURM_GPUS_ON_NODE'])
            local_rank= self.rank - gpus_per_node * (self.rank // gpus_per_node)
            os.environ['LOCAL_RANK'] = str(local_rank)
            self.local_rank = int(os.environ['LOCAL_RANK'])
            self.device = torch.device("cuda", local_rank)
            self.master_process = self.rank == 0  # Main process does logging & checkpoints.
            self.num_processes = torch.distributed.get_world_size()
            self.checkpoint=checkpoint
        else:
            self.local_rank =  int(os.environ['LOCAL_RANK'])
            self.rank = int(os.environ["RANK"])
            self.device = torch.device("cuda", self.local_rank)
            self.master_process = self.rank == 0  
            self.num_processes = torch.distributed.get_world_size()
            self.checkpoint=checkpoint

        classifier_trained = True
        if self.config.architectures is not None:
            classifier_trained = any([arch.endswith('ForSequenceClassification') for arch in self.config.architectures])

        if num_labels is None and not classifier_trained:
            num_labels = 1

        if num_labels is not None:
            self.config.num_labels = num_labels
    
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_args)
   
        self.embedding_size = embedding_size
        self.max_length = max_length
        self.weight_loss_class=weight_loss_class
        self.weight_loss_mlm=weight_loss_mlm

        self.model = PLMinteract(model_name,self.config.num_labels, config=self.config,device=self.device,embedding_size=self.embedding_size,weight_loss_class=self.weight_loss_class,weight_loss_mlm=self.weight_loss_mlm)
     
        if(checkpoint!=None): 
            load_checkpoint= torch.load(self.checkpoint,map_location='cpu')
            self.model.load_state_dict(load_checkpoint['model'])

        self.model = self.model.to(self.device)
        self.model = DDP(self.model, device_ids=[self.local_rank],find_unused_parameters=True)

        # mask language model training setting
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.data_collator = DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm_probability=0.22)
     
        if default_activation_function is not None:
            self.default_activation_function = default_activation_function
            try:
                self.config.sbert_ce_default_activation_function = util.fullname(self.default_activation_function)
            except Exception as e:
                logger.warning("Was not able to update config about the default_activation_function: {}".format(str(e)) )
        elif hasattr(self.config, 'sbert_ce_default_activation_function') and self.config.sbert_ce_default_activation_function is not None:
            self.default_activation_function = util.import_from_string(self.config.sbert_ce_default_activation_function)()
        else:
            self.default_activation_function = nn.Sigmoid() if self.config.num_labels == 1 else nn.Identity()

    def smart_batching_collate(self, batch):
        texts = [[] for _ in range(len(batch[0].texts))]
        labels = []

        for example in batch:
            for idx, text in enumerate(example.texts):
                texts[idx].append(text.strip())
            labels.append(example.label)

        tokenized = self.tokenizer(*texts, padding=True, truncation='longest_first', return_tensors="pt", max_length=self.max_length,return_special_tokens_mask=True)
    
        labels = torch.tensor(labels, dtype=torch.float if self.config.num_labels == 1 else torch.long).to(self.device)

        for name in tokenized:
            tokenized[name] = tokenized[name].to(self.device)

        return tokenized, labels

    def train(self,args,
            train_dataloader: DataLoader,
            batch_size_train: int = 1,
            epochs: int = 1,
            loss_fct = None,
            activation_fct = nn.Identity(),
            scheduler: str = 'WarmupLinear',
            warmup_steps: int = 10000,
            optimizer_class: Type[Optimizer] = torch.optim.AdamW, 
            optimizer_params: Dict[str, object] = {'lr': 2e-5},
            weight_decay: float = 0.01,
            output_path: str = None,
            max_grad_norm: float = 1,
            use_amp: bool = False,
            callback: Callable[[float, int, int], None] = None,
            show_progress_bar: bool = True,
            gradient_accumulation_steps: int=1,
            ):
  
        train_dataloader.collate_fn = self.smart_batching_collate

        if use_amp:
            from torch.cuda.amp import autocast
            scaler = torch.cuda.amp.GradScaler()

        self.model = self.model.to(self.device)
        if output_path is not None and self.master_process:
            os.makedirs(output_path, exist_ok=True)
            
        self.best_score = -9999999

        num_train_steps = int(len(train_dataloader) * epochs)
        # Prepare optimizers
        param_optimizer = list(self.model.named_parameters())
        no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': weight_decay},
            {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer = optimizer_class(optimizer_grouped_parameters, **optimizer_params)

        if isinstance(scheduler, str):
            scheduler = SentenceTransformer._get_scheduler(optimizer, scheduler=scheduler, warmup_steps=warmup_steps, t_total=num_train_steps)

        if loss_fct is None:
            pos_weight = torch.tensor([10]).to(self.device)
            loss_fct = nn.BCEWithLogitsLoss(pos_weight= pos_weight) if self.config.num_labels == 1 else nn.CrossEntropyLoss()

       # Train!
        logger.info("***** Running training *****")
        logger.info(f"  Num examples = {len(train_dataloader)}")
        logger.info(f"  Num Epochs = {args.epochs}")
        logger.info(f"  Instantaneous batch size per device = {batch_size_train}")
        logger.info(f"  Gradient Accumulation steps = {gradient_accumulation_steps}")
        # Potentially load in the weights and states from a previous save

        completed_steps = 1
        training_steps = 0
        starting_epoch = 0
        if args.resume_from_checkpoint:
            if args.resume_from_checkpoint is not None or args.resume_from_checkpoint != "":
                checkpoint_path = args.resume_from_checkpoint
                load_checkpoint= torch.load(checkpoint_path,map_location='cpu')
                optimizer.load_state_dict(load_checkpoint["optimizer"])
                scheduler.load_state_dict(load_checkpoint["scheduler"])
                starting_epoch=load_checkpoint["epoch"] + 1 
                print('starting_epoch',starting_epoch)

        skip_scheduler = False
        for epoch in range(starting_epoch, args.epochs):
            self.model.zero_grad()
            self.model.train()
            train_dataloader.sampler.set_epoch(epoch)
            for batch_idx, (features, labels) in enumerate(train_dataloader):
                features=features.to(self.device)
                labels=labels.to(self.device)
                lm_features= Dataset.from_dict(features)
                lm_dataloader = DataLoader(lm_features, shuffle=True, collate_fn=self.data_collator, batch_size=batch_size_train)
                if use_amp:
                    if batch_idx % gradient_accumulation_steps != 0:
                        with self.model.no_sync():
                            with autocast():
                                loss_value, loss_class, MLM_loss,logits = self.model.forward(labels,lm_dataloader)
                                loss_value = loss_value / gradient_accumulation_steps
                                loss_class = loss_class / gradient_accumulation_steps
                                MLM_loss = MLM_loss / gradient_accumulation_steps
                            scaler.scale(loss_value).backward()
                    else:
                        with autocast():
                            loss_value, loss_class, MLM_loss,logits = self.model.forward(labels,lm_dataloader)
                            loss_value = loss_value / gradient_accumulation_steps
                            loss_class = loss_class / gradient_accumulation_steps
                            MLM_loss = MLM_loss / gradient_accumulation_steps

                        scaler.scale(loss_value).backward()
                        # Gradient clipping.
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                        # weights update, Take gradient step,
                        scaler.step(optimizer)
                        scaler.update()
                        # skip scheduler or not
                        scale_before_step = scaler.get_scale()
                        skip_scheduler = scaler.get_scale() != scale_before_step
                          # Flush gradients. 
                        optimizer.zero_grad()
                        # update the learning rate of the optimizer based on the current epoch 
                        if not skip_scheduler:
                            scheduler.step() 
                else:
                    model_predictions = self.model(**features, return_dict=True)
                    logits = activation_fct(model_predictions.logits)
                    if self.config.num_labels == 1:
                        logits = logits.view(-1)
                    loss_value = loss_fct(logits, labels)
                    loss_value.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                    optimizer.step()
                    optimizer.zero_grad()
                    if not skip_scheduler:
                        scheduler.step()
                  
                training_steps = training_steps + 1
                if self.master_process and training_steps % 128 == 0: 
                            csv_headers = ['epoch','training_steps',"completed_steps","train_loss" ,'class_loss','MLM_loss']
                            csv_path = os.path.join(output_path, 'train_loss_resume.csv')
                            output_file_exists = os.path.isfile(csv_path)
                            with open(csv_path, mode="a" if output_file_exists else 'w', encoding="utf-8") as f:
                                writer = csv.writer(f)
                                if not output_file_exists:
                                    writer.writerow(csv_headers)
                                writer.writerow([epoch,training_steps,completed_steps,loss_value.item(), loss_class.item(), MLM_loss.item()])

                            completed_steps += 1  
            if self.master_process:
                    raw_model  = self.model.module 
                    checkpoint = {'model':raw_model.state_dict(), 'optimizer':optimizer.state_dict(), 'scheduler':scheduler.state_dict(), 'epoch':epoch,'loss':loss_value}
                    torch.save(checkpoint, os.path.join(output_path, 'epoch_' + str(epoch)+'.pt'))

        if self.master_process:
            self.tokenizer.save_pretrained(output_path)

class Train_mlm_Arguments(NamedTuple):
        epochs:int
        offline_model_path:str
        resume_from_checkpoint:str
        seed:int
        data:str
        task_name:str
        batch_size_train:int
        train_filepath:str
        output_filepath:str
        model_name:str
        warmup_steps:int
        embedding_size:int
        gradient_accumulation_steps:int
        max_length:int
        weight_loss_mlm:int
        weight_loss_class:int
        func: Callable[["Train_mlm_Arguments"], None]

def add_args_func(parser):
    parser.add_argument('--seed', type=int, default=2, help='Random seed for reproducibility (default: 2).')
    parser.add_argument('--data', type=str, default= "", help='Set the dataset name (e.g., cross_species)(default: "").')
    parser.add_argument('--task_name', type=str, default= "", help='Set the task name (e.g., 1vs10, 1vs1)(default: "").')

    data_parser = parser.add_argument_group("Input data and path of output results")
    plminteract_parser = parser.add_argument_group("PLM-interact setting")
    ESM2_parser = parser.add_argument_group("ESM2 model loading")

    data_parser.add_argument('--train_filepath', required=True,  type=str, help='Path to the training dataset (CSV format).')
    data_parser.add_argument('--output_filepath', required=True, type=str, help='Path to save trained model checkpoints and training results.')

    plminteract_parser.add_argument('--epochs', type=int, default=10, help='Total number of training epochs (default: 10)' )
    plminteract_parser.add_argument("--resume_from_checkpoint",type=str,default=None,help="Path to a checkpoint to resume training from, if continuing a previous run.")
    plminteract_parser.add_argument('--warmup_steps',type=int,  default=2000, help='Number of warmup steps for the learning rate scheduler (default: 2000).')
    plminteract_parser.add_argument('--gradient_accumulation_steps', type=int, default=8, help='Number of steps to accumulate gradients before performing an optimizer step (default: 8).')
    plminteract_parser.add_argument('--weight_loss_mlm',  type=int,default=1,help='Weight applied to the masked language modeling (MLM) loss (default: 1).')  
    plminteract_parser.add_argument('--weight_loss_class', type=int, default=10, help='Weight applied to the classification loss (default: 10).') 
    plminteract_parser.add_argument('--max_length', type=int, default=1603, help='Maximum sequence length for tokenizing paired proteins (default: 1603).')
    plminteract_parser.add_argument('--batch_size_train', type=int,default=16,  help='The training batch size on each device (default: 16).')

    ESM2_parser.add_argument('--offline_model_path', type=str, required=True, help='Path to a locally stored ESM-2 model.')
    ESM2_parser.add_argument('--model_name', type=str, required=True, help='Choose the ESM-2 model to load (esm2_t12_35M_UR50D / esm2_t33_650M_UR50D).')
    ESM2_parser.add_argument('--embedding_size', type=int, required=True, help='Set embedding vector size based on the selected ESM-2 model (480 / 1280).') 
    return parser

def main(args):
    #### Just some code to print debug information to stdout
    seed_offset,ddp_rank,ddp_local_rank,device= ddp_setup()
    init_process_group(backend='nccl')
    torch.cuda.set_device(device)

    if args.seed is not None:
        random.seed(args.seed)
    logging.basicConfig(format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO,
                            handlers=[LoggingHandler()])

    offline =args.offline_model_path
    model_path = offline + args.model_name

    output_path=args.output_filepath
    model_save_path = output_path +   args.task_name +  '_' + args.data + '_' + args.model_name.replace("/", "-")+'-'+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  + '/'

    trainer = CrossEncoder(model_path, num_labels=1, max_length=args.max_length, embedding_size=args.embedding_size,weight_loss_class=args.weight_loss_class,weight_loss_mlm=args.weight_loss_mlm,checkpoint = args.resume_from_checkpoint)

    train_samples = load_train_objs(args.train_filepath)
    train_dataloader = DataLoader(train_samples,batch_size=args.batch_size_train,shuffle=False,sampler =  DistributedSampler(train_samples))
     
    trainer.train(args,train_dataloader=train_dataloader,
            epochs = args.epochs,
            warmup_steps= args.warmup_steps,
            output_path= model_save_path,
            use_amp=True,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            )
    destroy_process_group()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_args_func(parser)
    args = parser.parse_args()
    main(args)
