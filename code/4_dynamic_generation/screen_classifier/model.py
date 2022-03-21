import torch
import torch.nn as nn
import torchvision.models as models


class ScreenClassifier(nn.Module):
    def __init__(self, bert_size=768, layout_size=4608, output_size=34):
        super().__init__()

        self.bert_size = bert_size
        self.layout_size = layout_size

        self.layer_1 = nn.Linear(self.bert_size + self.layout_size, 512)
        self.layer_2 = nn.Linear(512, 256)
        self.layer_3 = nn.Linear(256, 128)
        self.layer_out = nn.Linear(128, output_size)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.2)
        self.batchnorm1 = nn.BatchNorm1d(512)
        self.batchnorm2 = nn.BatchNorm1d(256)
        self.batchnorm3 = nn.BatchNorm1d(128)

    def forward(self, text_emb, layout_emb):
        x = torch.cat((text_emb, layout_emb), 1)

        o1 = self.layer_1(x)
        o1 = self.batchnorm1(o1)
        o1 = self.relu(o1)

        o2 = self.layer_2(o1)
        o2 = self.batchnorm2(o2)
        o2 = self.relu(o2)
        o2 = self.dropout(o2)

        o3 = self.layer_3(o2)
        o3 = self.batchnorm3(o3)
        o3 = self.relu(o3)
        o3 = self.dropout(o3)

        o = self.layer_out(o3)
        return o