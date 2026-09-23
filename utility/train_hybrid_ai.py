# =====================================================
# 🧠 EDQ + Brain Hybrid Intelligence
# Author: Seriki Yakub (KUBU LEE)
# =====================================================

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
import json
import requests
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import numpy as np
import re

# =====================================================
# 1️⃣ Clone or sync your GitHub repos locally
# =====================================================
REPOS = {
    "EDQ": "https://github.com/Web4application/EDQ-AI.git",
    "Brain": "https://github.com/Web4application/Brain.git"
}

def clone_repos(base_dir="repos"):
    os.makedirs(base_dir, exist_ok=True)
    for name, url in REPOS.items():
        repo_path = os.path.join(base_dir, name)
        if not os.path.exists(repo_path):
            os.system(f"git clone {url} {repo_path}")
        else:
            os.system(f"cd {repo_path} && git pull")
    print("✅ Repos synced successfully.")

clone_repos()

# =====================================================
# 2️⃣ Load / Parse Data from repos
# =====================================================

def read_texts_from_repo(repo_path):
    texts = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.txt', '.md', '.py', '.json')):
                try:
                    content = open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore').read()
                    texts.append(content)
                except:
                    pass
    return texts

def tokenize_texts(texts, vocab=None):
    if vocab is None:
        vocab = {}
    tokenized = []
    for text in texts:
        words = re.findall(r"\b\w+\b", text.lower())
        encoded = [vocab.setdefault(w, len(vocab)+1) for w in words]
        tokenized.append(encoded[:32])  # trim long samples
    return tokenized, vocab

def generate_repo_data():
    edq_texts = read_texts_from_repo("repos/EDQ")
    brain_texts = read_texts_from_repo("repos/Brain")
    all_texts = edq_texts + brain_texts
    tokenized, vocab = tokenize_texts(all_texts)
    vocab_size = len(vocab) + 1

    # convert text to torch tensors
    max_len = max(len(t) for t in tokenized)
    text_data = torch.zeros(len(tokenized), max_len, dtype=torch.long)
    for i, t in enumerate(tokenized):
        text_data[i, :len(t)] = torch.tensor(t)

    # Numeric data (synthetic from EDQ style)
    numeric_data = torch.randn(len(tokenized), 16)
    targets = torch.randn(len(tokenized), 8)
    return numeric_data, text_data, targets, vocab_size

numeric_data, text_data, targets, vocab_size = generate_repo_data()
print(f"Loaded {len(text_data)} samples, vocab size = {vocab_size}")

# =====================================================
# 3️⃣ Define new hybrid model
# =====================================================

class EDQBranch(nn.Module):
    def __init__(self, input_dim=16):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        for layer in [self.fc1, self.fc2]:
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)
    def forward(self, x):
        return F.relu(self.fc2(F.relu(self.fc1(x))))

class BrainBranch(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        for name, param in self.rnn.named_parameters():
            if "weight" in name: nn.init.xavier_uniform_(param)
            else: nn.init.zeros_(param)
    def forward(self, x):
        x = self.embedding(x)
        _, h = self.rnn(x)
        return h.squeeze(0)

class EDQBrainFusion(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.edq = EDQBranch()
        self.brain = BrainBranch(vocab_size)
        self.fc_fuse = nn.Linear(96, 128)
        self.fc_out = nn.Linear(128, 8)
        for layer in [self.fc_fuse, self.fc_out]:
            nn.init.kaiming_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)
    def forward(self, numeric_input, text_input):
        f1 = self.edq(numeric_input)
        f2 = self.brain(text_input)
        fused = torch.cat((f1, f2), dim=1)
        fused = F.relu(self.fc_fuse(fused))
        return self.fc_out(fused)

# =====================================================
# 4️⃣ Train the new AI Brain
# =====================================================
def train_model(epochs=50, lr=0.001):
    model = EDQBrainFusion(vocab_size)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(numeric_data, text_data)
        loss = loss_fn(out, targets)
        loss.backward()
        optimizer.step()
        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Loss: {loss.item():.6f}")
    torch.save(model.state_dict(), "EDQ_Brain_Fusion_Weights.pth")
    print("✅ Training complete. Model saved as 'EDQ_Brain_Fusion_Weights.pth'")
    return model

if __name__ == "__main__":
    model = train_model()
    print("🧠 EDQ + Brain Hybrid AI (Repo Powered) is alive.")