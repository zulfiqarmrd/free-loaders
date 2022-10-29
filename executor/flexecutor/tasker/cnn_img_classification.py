import sys
import time
import torch
# Implementation of CNN/ConvNet Model using PyTorch
# ref: https://towardsdatascience.com/convolutional-neural-network-for-image-classification-with-implementation-on-python-using-pytorch-7b88342c9ca9

class CNN(torch.nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # L1 ImgIn shape=(?, 28, 28, 1)
        #    Conv     -> (?, 28, 28, 32)
        #    Pool     -> (?, 14, 14, 32)
        self.layer1 = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2),
            torch.nn.Dropout(p=0.9))
        # L2 ImgIn shape=(?, 14, 14, 32)
        #    Conv      ->(?, 14, 14, 64)
        #    Pool      ->(?, 7, 7, 64)
        self.layer2 = torch.nn.Sequential(
            torch.nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2),
            torch.nn.Dropout(p=0.9))
        # L3 ImgIn shape=(?, 7, 7, 64)
        #    Conv      ->(?, 7, 7, 128)
        #    Pool      ->(?, 4, 4, 128)
        self.layer3 = torch.nn.Sequential(
            torch.nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=1),
            torch.nn.Dropout(p=0.9))

        # L4 FC 4x4x128 inputs -> 625 outputs
        self.fc1 = torch.nn.Linear(4 * 4 * 128, 625, bias=True)
        torch.nn.init.xavier_uniform(self.fc1.weight)
        self.layer4 = torch.nn.Sequential(
            self.fc1,
            torch.nn.ReLU(),
            torch.nn.Dropout(p=0.9))
        # L5 Final FC 625 inputs -> 10 outputs
        self.fc2 = torch.nn.Linear(625, 10, bias=True)
        torch.nn.init.xavier_uniform_(self.fc2.weight) # initialize parameters

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.view(out.size(0), -1)   # Flatten them for FC
        out = self.fc1(out)
        out = self.fc2(out)
        return out


# instantiate CNN model
# model = CNN()

def profile_img_classification_task():
    dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    image_dim = 28
    batch_size = 7500

    print(dev)
    print("using gpu")
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    # unsqueeze: 3072 -> 1x3072
    # images = torch.tensor(input_data["image"]).unsqueeze(0).to(dev)
    images = torch.rand(batch_size, 1, image_dim, image_dim).to(dev)
    classifier = CNN().to(dev)
    output_class_weights = classifier(images).exp()
    output_class = torch.argmax(output_class_weights).item()
    end.record()
    torch.cuda.synchronize()
    print(f'time(ms) = {start.elapsed_time(end)}')

    print("using cpu")
    start = time.time()
    images = torch.rand(batch_size, 1, image_dim, image_dim)
    classifier = CNN()
    output_class_weights = classifier(images).exp()
    output_class = torch.argmax(output_class_weights).item()
    print(f'time(ms) = {(time.time() - start)*1000}')
    return output_class

def run_img_classification_task(task_id, input_data):
    using_cuda = torch.cuda.is_available()
    dev = torch.device("cuda") if using_cuda else torch.device("cpu")
    channels = 1
    image_dim = 28
    batch_size = 7500 + (task_id - 100)

    images = torch.rand(batch_size, channels, image_dim, image_dim).to(dev)
    classifier = CNN().to(dev)
    output_class_weights = classifier(images).exp()
    if using_cuda:
        torch.cuda.synchronize()

    # return a constant sized array
    output_size = 1000
    return output_class_weights.tolist()[:output_size]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("needs task_id, input as arg")
        sys.exit(1)

    run_img_classification_task(int(sys.argv[1]), sys.argv[2])
