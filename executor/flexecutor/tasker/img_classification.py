import torch
from torch import nn
#from torchvision import transforms
#from PIL import Image

class Classifier(nn.Module):
    def __init__(self, hidden_layer_neurons):
        super(Classifier, self).__init__()
        # Linear transformation layer.
        # This computes a = wx + b where:
        # a is a vector of size 10
        # x: is a vector of size 3 x 32 x 32
        # b: is a vector of size 10
        # w: is a matrrix of size 10 x (3 * 32 * 32)
        num_of_classes = 10

        self.linear_1 = nn.Linear(3 * 32 * 32, hidden_layer_neurons)
        self.linear_2 = nn.Linear(hidden_layer_neurons, num_of_classes)

        # Softmax operator.
        # This is log(exp(a_i) / sum(exp(a)))
        self.log_softmax = nn.LogSoftmax(dim = 1)

    def forward(self, x):
        gx_1 = self.linear_1(x)
        gx_2 = self.linear_2(gx_1)

        yhat = self.log_softmax(gx_2)
        return yhat

# input_data: {"image": [flattened 3x32x32 = 3072]}
def run_img_classification_task(task_id, input_data):
    # unsqueeze: 3072 -> 1x3072
    images = torch.tensor(input_data["image"]).unsqueeze(0)

    dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    hidden_layer_neurons = (task_id - 99) * 100

    classifier = Classifier(hidden_layer_neurons).to(dev)

    # dummy_images = torch.rand(1, 3 * 32 * 32).to(dev)
    # print(dummy_images)
    # print(dummy_images.size())

    output_class_weights = classifier(images).exp()
    output_class = torch.argmax(output_class_weights).item()
    return output_class

# if __name__ == '__main__':
    # getting the image tensor from image
    # img = Image.open("0000.jpg")
    # convert_tensor = transforms.ToTensor()
    # tensor_obj = convert_tensor(img).flatten() # 3x32x32 -> 1x3072
    # print(tensor_obj)
    # print(tensor_obj.size())
    # print(run_img_classification_task(100, {"image": tensor_obj.numpy().tolist()}))