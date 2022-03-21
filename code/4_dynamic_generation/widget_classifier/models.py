import torch
import torch.nn as nn
import torchvision.models as models


class EncoderCNN(nn.Module):
    def __init__(self, hidden_size):
        super(EncoderCNN, self).__init__()
        resnet = models.resnet18(pretrained=True)
        self.resnet = resnet

        self.hidden_size = hidden_size
        self.linear = nn.Linear(1000, 100)
        self.bn = nn.BatchNorm1d(100, momentum=0.01)

    def forward(self, images):
        with torch.no_grad():
            features = self.resnet(images)
        features = features.reshape(features.size(0), -1)
        features = self.bn(self.linear(features))
        return features


class UIEmbedder(nn.Module):
    def __init__(self, bert_size=768, num_classes=26, class_emb_size=6, num_screens=33, screen_emb_size=7,
                 output_size=71, num_locations=10, location_emb_size=3):
        super().__init__()
        self.class_embedder = nn.Embedding(num_classes, class_emb_size)
        self.screen_embedder = nn.Embedding(num_screens, screen_emb_size)
        self.location_embedder = nn.Embedding(num_locations, location_emb_size)
        self.bert_size = bert_size
        self.class_size = class_emb_size
        self.screen_size = screen_emb_size
        self.location_size = location_emb_size
        self.image_emb_size = 100
        self.image_encoder = EncoderCNN(self.image_emb_size)

        self.layer_1 = nn.Linear(
            self.bert_size + self.class_size + self.screen_size + self.image_emb_size + self.location_size, 512)
        self.layer_2 = nn.Linear(512, 256)
        self.layer_3 = nn.Linear(256, 128)
        self.layer_out = nn.Linear(128, output_size)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.2)
        self.batchnorm1 = nn.BatchNorm1d(512)
        self.batchnorm2 = nn.BatchNorm1d(256)
        self.batchnorm3 = nn.BatchNorm1d(128)

    def forward(self, text_emb, class_name, screen_name, image, loc):
        # text_emb = torch.as_tensor(self.text_embedder.encode(text))
        class_emb = self.class_embedder(class_name)
        screen_emb = self.screen_embedder(screen_name)
        image_emb = self.image_encoder(image)
        location_emb = self.location_embedder(loc)
        x = torch.cat((text_emb, class_emb, screen_emb, image_emb, location_emb), 1)

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