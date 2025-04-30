import os
import time
from typing import Dict
from filelock import FileLock
from PIL import Image
import ray
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import Normalize, ToTensor
from tqdm import tqdm

# 定义 batch 大小
train_batch_size = {{ training.batch_size }}
# 定义训练次数
train_epoch = {{ training.epoch }}

# 推理数据预处理函数
def preprocess_for_inference(image_path):
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize(28),
        transforms.CenterCrop(28),
        ToTensor(),
        Normalize((0.28604,), (0.32025,))
    ])
    image = Image.open(image_path).convert('L')
    return transform(image).unsqueeze(0)

# 推理函数
def run_inference(model, device):
    model.eval()
    processed_input = preprocess_for_inference("/tmp/inference.png").to(device)
    with torch.no_grad():
        output = model(processed_input)
    _, predicted = torch.max(output.data, 1)
    return predicted.item()

# FashionMNIST 数据集类别名称
class_names = [
    'T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
    'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'
]

# 获取训练和测试数据加载器
def get_dataloaders(batch_size):
    transform = transforms.Compose([ToTensor(), Normalize((0.28604,), (0.32025,))])
    with FileLock(os.path.expanduser("~/data.lock")):
        training_data = datasets.FashionMNIST(
            root="~/data", train=True, download=True, transform=transform)
        test_data = datasets.FashionMNIST(
            root="~/data", train=False, download=True, transform=transform)
    return (
        DataLoader(training_data, batch_size=batch_size, shuffle=True),
        DataLoader(test_data, batch_size=batch_size)
    )

# 定义神经网络模型结构
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28 * 28, 512), nn.ReLU(), nn.Dropout(0.25),
            nn.Linear(512, 512), nn.ReLU(), nn.Dropout(0.25),
            nn.Linear(512, 10), nn.ReLU(),
        )
    def forward(self, x):
        x = self.flatten(x)
        return self.linear_relu_stack(x)

# 训练 worker 的主函数
def train_func_per_worker(config: Dict):
    # 训练参数
    lr = config["lr"]
    epochs = config["epochs"]
    batch_size = config["batch_size_per_worker"]
    
    # 获取数据加载器
    train_dataloader, test_dataloader = get_dataloaders(batch_size)
    train_dataloader = ray.train.torch.prepare_data_loader(train_dataloader)
    test_dataloader = ray.train.torch.prepare_data_loader(test_dataloader)
    
    # 初始化模型
    model = NeuralNetwork()
    model = ray.train.torch.prepare_model(model)
    
    # 训练准备
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)

    # 记录训练开始时间
    start_time = time.time()

    # 训练循环
    for epoch in range(epochs):
        if ray.train.get_context().get_world_size() > 1:
            train_dataloader.sampler.set_epoch(epoch)
        
        # 训练阶段
        model.train()
        for X, y in tqdm(train_dataloader, desc=f"Train Epoch {epoch}"):
            optimizer.zero_grad()
            pred = model(X)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
        
        # 验证阶段
        model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in tqdm(test_dataloader, desc=f"Test Epoch {epoch}"):
                pred = model(X)
                test_loss += loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        
        # 打印每个 epoch 的耗时
        if ray.train.get_context().get_world_rank() == 0:
            elapsed_time = time.time() - start_time
            print(f"Epoch {epoch} ended, elapsed time: {elapsed_time:.2f} s")
        
        # 报告指标
        metrics = {
            "loss": test_loss / len(test_dataloader),
            "accuracy": correct / len(test_dataloader.dataset)
        }

        # 推理结果
        if epoch == epochs-1 and ray.train.get_context().get_world_rank() == 0:
            device = next(model.parameters()).device
            metrics["inference_result"] = run_inference(model, device)
        ray.train.report(metrics)

# 主训练函数
def train_fashion_mnist(num_workers=2, use_gpu=False):
    global_batch_size = train_batch_size
    train_config = {
        "lr": 1e-3,
        "epochs": train_epoch,
        "batch_size_per_worker": global_batch_size // num_workers,
    }
    scaling_config = ScalingConfig(num_workers=num_workers, use_gpu=use_gpu)
    trainer = TorchTrainer(
        train_loop_per_worker=train_func_per_worker,
        train_loop_config=train_config,
        scaling_config=scaling_config,
    )
    result = trainer.fit()
    print(f"Final training results: {result.metrics}")
    if "inference_result" in result.metrics:
      print(f"\n=== Inference result ===")
      print(f"Target picture belongs to class: {class_names[result.metrics['inference_result']]}")

if __name__ == "__main__":
    train_fashion_mnist(num_workers=4, use_gpu=False)