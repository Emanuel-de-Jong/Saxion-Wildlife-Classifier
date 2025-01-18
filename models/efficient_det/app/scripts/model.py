import torchvision.transforms as transforms
import torch
from torch.backends import cudnn
from .efficientdet.backbone import EfficientDetBackbone
from .efficientdet.efficientdet_utils import preprocess, postprocess, STANDARD_COLORS
from .efficientdet.utils import BBoxTransform, ClipBoxes

def create_model_effdet(device):
    compound_coef = 2

    # replace this part with your project's anchor config
    anchor_scales = [2 ** (-1.0), 2 ** 0, 2 ** (1.0 / 3.0), 2 ** (2.0 / 3.0), 2 ** 1.0]
    anchor_ratios = [(1.0, 1.0), (1.5, 0.5), (0.5, 1.5), (2.0, 1.0), (1.0, 2.0)]

    cudnn.fastest = True
    cudnn.benchmark = True

    obj_list = ['miscellaneous','duck','gosling','hare','egyptian_goose','coot','swan','crow','pidgeon','magpie','cat','oystercatcher',
                'starling','jackdaw','greylag_goose','canadian_goose','moorhen','heron','pheasant']

    model = EfficientDetBackbone(compound_coef=compound_coef, num_classes=len(obj_list),
                                ratios=anchor_ratios, scales=anchor_scales)
    model.load_state_dict(torch.load('scripts/efficientdet-d2_188_63500.pth', map_location='cpu'))
    model.requires_grad_(False)
    model.to(device)

    return model

def effdet_infer_on_image(model, image, device):
    model.eval()

    print(image)

    use_cuda = True
    use_float16 = False
    force_input_size = None
    compound_coef = 2
    threshold = 0.1
    iou_threshold = 0.1

    input_sizes = [512, 640, 768, 896, 1024, 1280, 1280, 1536, 1536]
    input_size = input_sizes[compound_coef] if force_input_size is None else force_input_size
    ori_imgs, framed_imgs, framed_metas = preprocess(image, max_size=input_size)

    if use_cuda:
        x = torch.stack([torch.from_numpy(fi).cpu() for fi in framed_imgs], 0)
    else:
        x = torch.stack([torch.from_numpy(fi) for fi in framed_imgs], 0)

    x = x.to(torch.float32 if not use_float16 else torch.float16).permute(0, 3, 1, 2)

    if use_cuda:
        model = model.cpu()
    if use_float16:
        model = model.half()

    with torch.no_grad():
        features, regression, classification, anchors = model(x)

        regressBoxes = BBoxTransform()
        clipBoxes = ClipBoxes()

        out = postprocess(x,
                        anchors, regression, classification,
                        regressBoxes, clipBoxes,
                        threshold, iou_threshold)

    out=out[0]

    boxes = out['rois']
    labels = out['class_ids']
    scores = out['scores']

    return boxes, labels, scores
